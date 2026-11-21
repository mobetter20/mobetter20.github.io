"""Offline essay publisher regressions; all release files and locks are temporary."""
from contextlib import ExitStack, redirect_stdout
import copy
import io
import json
import os
from pathlib import Path
import select
import subprocess
import sys
import tempfile
import time
import unittest
from unittest.mock import patch

from writes_publisher import publish_watcher as watcher


WATCHER_PATH = Path(watcher.__file__).resolve()
LOCK_HOLDER = r'''
import importlib.util
import json
import os
from pathlib import Path
import sys
import time

spec = importlib.util.spec_from_file_location("isolated_lock_holder", sys.argv[1])
watcher = importlib.util.module_from_spec(spec)
sys.modules[spec.name] = watcher
spec.loader.exec_module(watcher)
watcher.STATE_DIR = Path(sys.argv[2])
watcher.LOCK_PATH = watcher.STATE_DIR / "lock.json"
watcher.log = lambda message: None
if not watcher.acquire_lock():
    raise SystemExit("child could not acquire fixture lock")
metadata = {"pid": os.getpid(), "at": time.time() - 1800}
watcher.LOCK_PATH.write_text(json.dumps(metadata))
print("held", flush=True)
sys.stdin.readline()
# Deliberately exit without release_lock: the kernel must release the held lock.
'''


class WritesPublisherFixture(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.drop = self.root / 'releases'
        self.site = self.root / 'site'
        self.src = self.site / 'is/writing/essays/_src'
        self.state_dir = self.root / 'state'
        self.drop.mkdir()
        self.src.mkdir(parents=True)
        self.now = 2_000_000_000.0
        self.stack = ExitStack()
        self.addCleanup(self.stack.close)
        for name, value in {
            'DROP': self.drop, 'SITE': self.site, 'SRC': self.src,
            'STATE_DIR': self.state_dir, 'STATE_PATH': self.state_dir / 'state.json',
            'LOCK_PATH': self.state_dir / 'lock.json', 'LOG_PATH': self.state_dir / 'publisher.log',
            'MAINTENANCE_PATH': self.state_dir / 'maintenance', '_lock_handle': None,
        }.items():
            self.stack.enter_context(patch.object(watcher, name, value, create=True))
        self.addCleanup(watcher.release_lock)
        self.notify = self.stack.enter_context(patch.object(watcher, 'notify'))
        self.log = self.stack.enter_context(patch.object(watcher, 'log'))
        self.git = self.stack.enter_context(patch.object(watcher, 'git',
            side_effect=AssertionError('unexpected Git access from isolated fixture')))
        self.process = self.stack.enter_context(patch.object(watcher.subprocess, 'run',
            side_effect=AssertionError('unexpected subprocess from isolated fixture')))
        self.preflight = self.stack.enter_context(patch.object(watcher, 'preflight',
            side_effect=AssertionError('an excluded or unstable candidate reached preflight')))
        self.publish = self.stack.enter_context(patch.object(watcher, 'run_publish',
            side_effect=AssertionError('unexpected publishing from isolated fixture')))
        self.verify = self.stack.enter_context(patch.object(watcher, 'verify_published',
            side_effect=AssertionError('unexpected publication proof from isolated fixture')))

    def state(self):
        return {'version': 1, 'published': {}, 'pending': {}, 'errors': {}, 'last_run': ''}

    def candidate(self, name, *, slug='shared', title='Shared title', body='Approved text.'):
        path = self.drop / name
        path.write_text(f'---\ntitle: {title}\nslug: {slug}\npublish: true\n'
                        f'date: 2026-11-20\n---\n\n{body}\n')
        os.utime(path, (self.now - 3600, self.now - 3600))
        return watcher.Candidate(path, slug, title, '2026-11-20', '', body)

    def stable_state(self, *candidates):
        state = self.state()
        state['pending'] = {c.path.name: {'hash': c.content_hash,
                                         'first_seen': self.now - watcher.STABILITY_SECONDS - 1}
                            for c in candidates}
        return state

    def tick(self, at=None):
        with patch.object(watcher.time, 'time', return_value=self.now if at is None else at):
            return watcher.tick()

    def main(self, *args):
        with patch.object(sys, 'argv', ['publish_watcher.py', *args]):
            return watcher.main()

    def snapshot(self):
        return {p.relative_to(self.root).as_posix(): p.read_bytes()
                for p in self.root.rglob('*') if p.is_file() and not p.is_symlink()}


class WritesPublisherCollisionTest(WritesPublisherFixture):
    def test_collision_filter_excludes_every_claimant_and_clears_only_their_pending_entries(self):
        first = self.candidate('Alpha.md')
        second = self.candidate('Beta.md', body='A different approved release.')
        unique = self.candidate('Unique.md', slug='unique', title='Unique')
        state = self.stable_state(first, second, unique)
        state['published']['historic'] = {'source': 'Historic.md', 'content_hash': 'keep'}
        published = copy.deepcopy(state['published'])
        pending_unique = copy.deepcopy(state['pending'][unique.path.name])
        self.assertEqual(watcher.exclude_slug_collisions(state, [first, unique, second]), [unique])
        self.assertEqual(state['pending'], {unique.path.name: pending_unique})
        self.assertEqual(state['published'], published)
        self.assertTrue(self.notify.called)

    def test_identical_text_in_two_drop_files_still_has_two_url_claimants(self):
        first = self.candidate('Alpha.md')
        second = self.candidate('Beta.md')
        state = self.stable_state(first, second)
        self.assertEqual(first.content_hash, second.content_hash)
        self.assertEqual(watcher.exclude_slug_collisions(state, [first, second]), [])
        self.assertEqual(state['pending'], {})

    def test_tick_filters_collisions_immediately_after_scan_before_reconcile_and_readiness(self):
        first = self.candidate('Alpha.md')
        second = self.candidate('Beta.md', body='Another version.')
        unique = self.candidate('Unique.md', slug='unique', title='Unique')
        events = []

        def observe(name, function):
            def call(*args):
                events.append(name)
                if name in ('reconcile', 'ready'):
                    self.assertEqual(args[1], [unique])
                return function(*args)
            return call

        with patch.object(watcher, 'scan_drop', side_effect=observe('scan', watcher.scan_drop)), \
             patch.object(watcher, 'exclude_slug_collisions',
                          side_effect=observe('exclude', watcher.exclude_slug_collisions)), \
             patch.object(watcher, 'reconcile', side_effect=observe('reconcile', watcher.reconcile)), \
             patch.object(watcher, 'ready_to_publish', side_effect=observe('ready', watcher.ready_to_publish)):
            self.assertEqual(self.tick(), 0)
        self.assertEqual(events, ['scan', 'exclude', 'reconcile', 'ready'])
        self.preflight.assert_not_called()

    def test_stable_collision_never_reaches_git_and_published_state_stays_unchanged(self):
        first = self.candidate('Alpha.md')
        second = self.candidate('Beta.md', body='Another version.')
        state = self.stable_state(first, second)
        state['published']['historic'] = {'source': 'Historic.md', 'content_hash': 'keep'}
        published = copy.deepcopy(state['published'])
        watcher.save_state(state)
        self.assertEqual(self.tick(), 0)
        after = watcher.load_state()
        self.assertEqual(after['pending'], {})
        self.assertEqual(after['published'], published)
        self.assertEqual(list(self.src.iterdir()), [])
        self.preflight.assert_not_called()
        self.git.assert_not_called()
        self.publish.assert_not_called()

    def test_lost_state_does_not_adopt_one_of_two_colliding_candidates(self):
        first = self.candidate('Alpha.md')
        self.candidate('Beta.md', body='Another version.')
        source = self.src / 'shared.md'
        source.write_text(first.src_text(7))
        before = source.read_bytes()
        self.assertFalse(watcher.STATE_PATH.exists())
        self.assertEqual(self.tick(), 0)
        state = watcher.load_state()
        self.assertEqual(state['published'], {})
        self.assertEqual(state['pending'], {})
        self.assertEqual(source.read_bytes(), before)
        self.preflight.assert_not_called()
        self.verify.assert_not_called()

    def test_matching_local_source_is_not_adopted_when_push_proof_fails(self):
        candidate = self.candidate('Ready.md', slug='ready', title='Ready')
        text = candidate.src_text(7)
        source = self.src / 'ready.md'
        source.write_text(text)
        with patch.object(watcher, 'verify_published', return_value='local commit is not on origin') as verify:
            self.assertEqual(self.tick(), 0)
            self.assertEqual(self.tick(self.now + 60), 0)
        self.assertEqual(verify.call_count, 2)
        verify.assert_called_with({'ready': text})
        self.assertEqual(watcher.load_state()['published'], {})
        self.assertEqual(source.read_text(), text)
        self.notify.assert_called_once()
        self.preflight.assert_not_called()
        self.publish.assert_not_called()

    def test_matching_source_is_adopted_only_after_successful_push_proof(self):
        candidate = self.candidate('Ready.md', slug='ready', title='Ready')
        text = candidate.src_text(7)
        (self.src / 'ready.md').write_text(text)
        watcher.save_state(self.stable_state(candidate))
        with patch.object(watcher, 'verify_published', return_value=None) as verify:
            self.assertEqual(self.tick(), 0)
        verify.assert_called_once_with({'ready': text})
        state = watcher.load_state()
        self.assertEqual(state['published']['ready']['source'], 'Ready.md')
        self.assertEqual(state['published']['ready']['content_hash'], candidate.content_hash)
        self.assertEqual(state['published']['ready']['src_hash'], watcher.sha(text))
        self.assertEqual(state['pending'], {})
        self.preflight.assert_not_called()
        self.publish.assert_not_called()

    def test_resolving_collision_restarts_the_full_stability_window(self):
        first = self.candidate('Alpha.md')
        second = self.candidate('Beta.md', body='Another version.')
        watcher.save_state(self.stable_state(first, second))
        self.assertEqual(self.tick(), 0)
        second.path.unlink()
        resumed_at = self.now + 1
        self.assertEqual(self.tick(resumed_at), 0)
        state = watcher.load_state()
        self.assertEqual(state['pending'], {first.path.name: {
            'hash': first.content_hash, 'first_seen': resumed_at}})
        with patch.object(watcher.time, 'time', return_value=resumed_at + watcher.STABILITY_SECONDS - 1):
            self.assertEqual(watcher.ready_to_publish(state, [first]), [])
        with patch.object(watcher.time, 'time', return_value=resumed_at + watcher.STABILITY_SECONDS):
            self.assertEqual(watcher.ready_to_publish(state, [first]), [first])
        self.preflight.assert_not_called()


class WritesPublisherRemoteProofTest(unittest.TestCase):
    """A stale local HEAD cannot prove content still exists at the remote tip."""

    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.site = self.root / 'site'
        self.upstream = self.root / 'upstream'
        self.remote = self.root / 'origin.git'
        self.drop = self.root / 'releases'
        self.src = self.site / 'is/writing/essays/_src'
        self.state_dir = self.root / 'state'
        self.site.mkdir()
        self.drop.mkdir()
        self.stack = ExitStack()
        self.addCleanup(self.stack.close)
        self.stack.enter_context(patch.dict(os.environ, GIT_CONFIG_GLOBAL=os.devnull,
            GIT_CONFIG_NOSYSTEM='1', GIT_ALLOW_PROTOCOL='file', GIT_TERMINAL_PROMPT='0'))
        for name, value in {
            'DROP': self.drop, 'SITE': self.site, 'SRC': self.src,
            'STATE_DIR': self.state_dir, 'STATE_PATH': self.state_dir / 'state.json',
        }.items():
            self.stack.enter_context(patch.object(watcher, name, value))
        self.notify = self.stack.enter_context(patch.object(watcher, 'notify'))
        self.stack.enter_context(patch.object(watcher, 'log'))
        self.preflight = self.stack.enter_context(patch.object(watcher, 'preflight',
            side_effect=AssertionError('source reconciliation unexpectedly reached publication')))
        self.stack.enter_context(patch.object(watcher, 'run_publish',
            side_effect=AssertionError('source reconciliation attempted publication')))

        self.git('init', '--bare', '--initial-branch=master', str(self.remote), repo=self.root)
        self.git('init', '--initial-branch=master')
        release = self.drop / 'Approved.md'
        release.write_text('---\ntitle: Approved\nslug: approved\npublish: true\n'
                           'date: 2026-11-20\n---\n\nOriginal approved words.\n')
        self.candidate = watcher.Candidate(release, 'approved', 'Approved', '2026-11-20', '',
                                           'Original approved words.')
        self.source_text = self.candidate.src_text(7)
        self.write(self.site, 'is/writing/essays/_src/approved.md', self.source_text)
        self.write(self.site, 'writes/approved/index.html', '<article>Original approved words.</article>\n')
        self.write(self.site, 'is/writing/index.html',
                   '<ol id="writing-list"><li><a href="/writes/approved/">Approved</a></li></ol>\n')
        self.git('add', '--all')
        self.git('commit', '-m', 'Initial approved essay')
        self.base = self.git('rev-parse', 'HEAD').stdout.strip()
        self.git('remote', 'add', 'origin', str(self.remote))
        self.git('push', '-u', 'origin', 'master')
        self.git('clone', '--quiet', str(self.remote), str(self.upstream), repo=self.root)

    def git(self, *args, repo=None):
        return subprocess.run(['git', '-c', 'user.name=Publisher regression',
                               '-c', 'user.email=publisher-tests@example.invalid',
                               '-C', str(repo or self.site), *args],
                              text=True, capture_output=True, check=True, timeout=20)

    def write(self, repo, relative, content):
        target = repo / relative
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(content)

    def publish_upstream(self):
        self.git('add', '--all', repo=self.upstream)
        self.git('commit', '-m', 'Independent upstream change', repo=self.upstream)
        self.git('push', 'origin', 'master', repo=self.upstream)
        revision = self.git('rev-parse', 'HEAD', repo=self.upstream).stdout.strip()
        self.assertNotEqual(revision, self.base)
        # The local clone has not fetched this descendant yet.
        self.assertEqual(self.git('rev-parse', 'origin/master').stdout.strip(), self.base)
        return revision

    def assert_reconciliation(self, revision, *, adopts):
        self.assertFalse(watcher.STATE_PATH.exists())
        self.assertEqual(self.git('rev-parse', 'HEAD').stdout.strip(), self.base)
        self.assertEqual((self.src / 'approved.md').read_text(), self.source_text)
        self.assertEqual(watcher.tick(), 0)
        state = watcher.load_state()
        if adopts:
            self.assertEqual(state['published']['approved']['source'], 'Approved.md')
            self.assertEqual(state['published']['approved']['src_hash'], watcher.sha(self.source_text))
            self.assertEqual(state['published']['approved']['content_hash'], self.candidate.content_hash)
        else:
            self.assertEqual(state['published'], {})
        self.preflight.assert_not_called()
        self.assertEqual(self.git('rev-parse', 'origin/master').stdout.strip(), revision)
        self.assertEqual(self.git('rev-parse', 'master', repo=self.remote).stdout.strip(), revision)
        self.assertEqual(self.git('rev-parse', 'HEAD').stdout.strip(), self.base)
        self.assertEqual(self.git('status', '--porcelain').stdout, '')
        self.assertEqual((self.src / 'approved.md').read_text(), self.source_text)

    def test_remote_descendant_retraction_prevents_lost_state_adoption(self):
        self.git('rm', '--', 'is/writing/essays/_src/approved.md', 'writes/approved/index.html',
                 repo=self.upstream)
        self.write(self.upstream, 'is/writing/index.html', '<ol id="writing-list"></ol>\n')
        self.assert_reconciliation(self.publish_upstream(), adopts=False)

    def test_remote_descendant_source_change_prevents_lost_state_adoption(self):
        self.write(self.upstream, 'is/writing/essays/_src/approved.md',
                   self.source_text.replace('Original approved words.', 'A separately revised release.'))
        self.write(self.upstream, 'writes/approved/index.html', '<article>A separately revised release.</article>\n')
        self.assert_reconciliation(self.publish_upstream(), adopts=False)

    def test_remote_descendant_missing_reader_prevents_lost_state_adoption(self):
        self.git('rm', '--', 'writes/approved/index.html', repo=self.upstream)
        self.assert_reconciliation(self.publish_upstream(), adopts=False)

    def test_unrelated_remote_descendant_still_allows_verified_adoption(self):
        self.write(self.upstream, 'unrelated.txt', 'An unrelated upstream change.\n')
        self.assert_reconciliation(self.publish_upstream(), adopts=True)


class WritesPublisherLockTest(WritesPublisherFixture):
    def child_holding_lock(self):
        child = subprocess.Popen([sys.executable, '-c', LOCK_HOLDER, str(WATCHER_PATH), str(self.state_dir)],
                                 stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)

        def cleanup():
            if child.poll() is None:
                child.kill()
            child.communicate(timeout=5)

        self.addCleanup(cleanup)
        readable, _, _ = select.select([child.stdout], [], [], 10)
        self.assertTrue(readable, 'child did not report holding the temporary lock')
        self.assertEqual(child.stdout.readline().strip(), 'held')
        return child

    def test_old_metadata_cannot_steal_a_live_child_lock_and_exit_releases_it(self):
        child = self.child_holding_lock()
        lock = watcher.LOCK_PATH
        inode, content = lock.stat().st_ino, lock.read_bytes()
        metadata = json.loads(content)
        self.assertGreater(time.time() - metadata['at'], 900)
        self.assertFalse(watcher.acquire_lock())
        self.assertIsNone(watcher._lock_handle)
        self.assertEqual(watcher.lock_activity(), 'active')
        self.assertEqual(lock.stat().st_ino, inode)
        self.assertEqual(lock.read_bytes(), content)
        _, errors = child.communicate('\n', timeout=10)
        self.assertEqual(child.returncode, 0, errors)
        self.assertEqual(watcher.lock_activity(), 'idle')
        self.assertEqual(lock.read_bytes(), content)
        self.assertTrue(watcher.acquire_lock())
        self.assertIsNotNone(watcher._lock_handle)
        self.assertEqual(lock.stat().st_ino, inode)
        self.assertEqual(watcher.lock_activity(), 'active')
        held_content = lock.read_bytes()
        watcher.release_lock()
        self.assertIsNone(watcher._lock_handle)
        self.assertEqual(lock.stat().st_ino, inode)
        self.assertEqual(lock.read_bytes(), held_content)
        self.assertEqual(watcher.lock_activity(), 'idle')
        self.assertEqual(lock.read_bytes(), held_content)

    def test_lock_probe_does_not_create_a_missing_state_directory(self):
        before = self.snapshot()
        self.assertFalse(self.state_dir.exists())
        self.assertEqual(watcher.lock_activity(), 'idle')
        self.assertFalse(self.state_dir.exists())
        self.assertEqual(before, self.snapshot())

    def test_lock_probe_uses_the_os_lock_even_with_invalid_metadata(self):
        self.state_dir.mkdir()
        watcher.LOCK_PATH.write_text('not JSON and not a process claim\n')
        inode, content = watcher.LOCK_PATH.stat().st_ino, watcher.LOCK_PATH.read_bytes()
        self.assertEqual(watcher.lock_activity(), 'idle')
        self.assertEqual(watcher.LOCK_PATH.stat().st_ino, inode)
        self.assertEqual(watcher.LOCK_PATH.read_bytes(), content)

    def test_lock_probe_reports_unknown_for_an_unreadable_entry_without_changing_it(self):
        watcher.LOCK_PATH.mkdir(parents=True)
        inode = watcher.LOCK_PATH.stat().st_ino
        self.assertEqual(watcher.lock_activity(), 'unknown')
        self.assertTrue(watcher.LOCK_PATH.is_dir())
        self.assertEqual(watcher.LOCK_PATH.stat().st_ino, inode)


class WritesPublisherCommunicationTest(WritesPublisherFixture):
    def test_success_notification_reports_push_and_pending_deployment(self):
        candidate = self.candidate('Ready.md', slug='ready', title='Ready')
        watcher.save_state(self.stable_state(candidate))
        with patch.object(watcher, 'preflight', return_value=None), \
             patch.object(watcher, 'run_publish', return_value=(True, 'fixture push succeeded')), \
             patch.object(watcher, 'verify_published', return_value=None):
            self.assertEqual(self.tick(), 0)
        subject, body = self.notify.call_args.args
        self.assertIn('pushed', subject.lower())
        self.assertRegex(body.lower(), r'(?:deployment[^.\n]*pending|still needs to deploy)')
        self.assertIn('/writes/ready/', body)
        self.assertEqual(watcher.load_state()['published']['ready']['content_hash'], candidate.content_hash)
        self.git.assert_not_called()
        self.process.assert_not_called()

    def test_failure_never_claims_that_nothing_is_live_after_a_possible_push(self):
        candidate = self.candidate('Ready.md', slug='ready', title='Ready')
        for pushed in (False, True):
            with self.subTest(push_command_succeeded=pushed):
                (self.src / 'ready.md').unlink(missing_ok=True)
                watcher.save_state(self.stable_state(candidate))
                self.notify.reset_mock()
                with patch.object(watcher, 'preflight', return_value=None), \
                     patch.object(watcher, 'run_publish', return_value=(pushed, 'fixture failure')), \
                     patch.object(watcher, 'verify_published', return_value='push proof unavailable'), \
                     patch.object(watcher, 'revert_staged') as revert:
                    self.assertEqual(self.tick(), 1)
                subject, body = self.notify.call_args.args
                self.assertNotIn('nothing is live', (subject + ' ' + body).lower())
                self.assertEqual(watcher.load_state()['published'], {})
                revert.assert_called_once_with(['ready'])
                (self.src / 'ready.md').unlink(missing_ok=True)
        self.git.assert_not_called()
        self.process.assert_not_called()

    def test_status_is_read_only_and_does_not_recommend_effectful_dry_run(self):
        state = self.state()
        state['errors']['file:Held.md'] = 'refusal fingerprint'
        watcher.save_state(state)
        before = self.snapshot()
        output = io.StringIO()
        with redirect_stdout(output), \
             patch.object(watcher, 'acquire_lock', side_effect=AssertionError('status acquired a publisher lock')), \
             patch.object(watcher, 'rotate_log', side_effect=AssertionError('status touched logs')):
            self.assertEqual(self.main('--status'), 0)
        self.assertNotIn('--dry-run', output.getvalue())
        self.assertIn('Held.md', output.getvalue())
        self.assertEqual(before, self.snapshot())
        self.assertFalse(watcher.LOCK_PATH.exists())
        self.git.assert_not_called()
        self.process.assert_not_called()
        self.publish.assert_not_called()
        self.preflight.assert_not_called()


class WritesPublisherMaintenanceTest(WritesPublisherFixture):
    def assert_main_has_no_effects(self, expected):
        with patch.object(watcher, 'load_state', side_effect=AssertionError('maintenance read state')), \
             patch.object(watcher, 'rotate_log', side_effect=AssertionError('maintenance touched logs')), \
             patch.object(watcher, 'acquire_lock', side_effect=AssertionError('maintenance acquired a lock')), \
             patch.object(watcher, 'tick', side_effect=AssertionError('maintenance ran a tick')), \
             patch.object(watcher, 'cmd_status', side_effect=AssertionError('maintenance ran status')), \
             patch.object(watcher, 'cmd_selftest', side_effect=AssertionError('maintenance ran selftest')):
            for args in ((), ('--dry-run',), ('--status',), ('--selftest',)):
                self.assertEqual(self.main(*args), expected)
        self.git.assert_not_called()
        self.process.assert_not_called()
        self.notify.assert_not_called()
        self.log.assert_not_called()

    def test_present_and_dangling_maintenance_markers_stop_all_modes_before_side_effects(self):
        self.state_dir.mkdir()
        marker = watcher.MAINTENANCE_PATH
        marker.write_text('operator hold\n')
        before = self.snapshot()
        self.assert_main_has_no_effects(0)
        self.assertEqual(before, self.snapshot())
        marker.unlink()
        marker.symlink_to(self.root / 'absent-marker-target')
        self.assert_main_has_no_effects(0)
        self.assertTrue(marker.is_symlink())
        self.assertFalse(watcher.STATE_PATH.exists())
        self.assertFalse(watcher.LOCK_PATH.exists())

    def test_unknown_maintenance_marker_state_fails_closed_without_side_effects(self):
        before = self.snapshot()
        with patch.object(Path, 'lstat', side_effect=PermissionError('fixture marker is inaccessible')):
            self.assert_main_has_no_effects(75)
        self.assertEqual(before, self.snapshot())


if __name__ == '__main__':
    unittest.main()
