"""Publication boundaries, retries and live-proof contracts. No network effects."""
import copy
from datetime import datetime, timezone
from html import escape
import json
import os
from pathlib import Path
import plistlib
import subprocess
import tempfile
import unittest
from unittest.mock import patch

from PIL import Image

import cartoon_publisher as publisher
import image_pieces
import piece


def result(out='', code=0):
    return subprocess.CompletedProcess([], code, out, '')


def green(sha='checked'):
    return dict(headRefOid=sha, statusCheckRollup=[dict(name='validate', workflowName=publisher.WORKFLOW,
                                                     status='COMPLETED', conclusion='SUCCESS')])


class CartoonPublisherTest(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.image = self.root / 'image.png'
        self.image.write_bytes(b'finished cartoon')

    def runner(self):
        return publisher.Publisher(self.image, 'The title', 'Scene and caption', root=self.root,
                                   state_dir=self.root / 'state')

    def test_input_identity_survives_renaming_and_preserves_snapshot(self):
        first = self.runner()
        first.save('prepared', date='2026-11-20')
        moved = self.root / 'renamed.jpg'
        moved.write_bytes(self.image.read_bytes())
        again = publisher.Publisher(moved, ' The title ', 'Scene and caption ', root=self.root,
                                    state_dir=self.root / 'state')
        self.assertEqual(first.key, again.key)
        self.assertEqual(again.state['date'], '2026-11-20')
        self.image.write_bytes(b'changed later')
        self.assertEqual(first.source.read_bytes(), b'finished cartoon')
        self.assertNotEqual(self.runner().key, first.key)

    def test_two_launches_cannot_publish_together(self):
        with publisher.launch_lock(self.root):
            with self.assertRaisesRegex(publisher.PublishError, 'Another cartoon'):
                with publisher.launch_lock(self.root):
                    self.fail('a second launch acquired the lock')
        with publisher.launch_lock(self.root):
            pass  # A leftover lock file is harmless after the OS releases it.

    def test_checks_require_real_success_at_the_checked_head(self):
        self.assertFalse(publisher.checked_ci(dict(headRefOid='checked', statusCheckRollup=[]), 'checked'))
        pending = green()
        pending['statusCheckRollup'][0].update(status='IN_PROGRESS', conclusion=None)
        self.assertFalse(publisher.checked_ci(pending, 'checked'))
        failed = green()
        failed['statusCheckRollup'][0]['conclusion'] = 'FAILURE'
        with self.assertRaisesRegex(publisher.PublishError, 'did not pass'):
            publisher.checked_ci(failed, 'checked')
        with self.assertRaisesRegex(publisher.PublishError, 'release changed'):
            publisher.checked_ci(green('someone-elses-head'), 'checked')
        wrong_workflow = green()
        wrong_workflow['statusCheckRollup'][0]['workflowName'] = 'An unrelated workflow'
        self.assertFalse(publisher.checked_ci(wrong_workflow, 'checked'))
        self.assertTrue(publisher.checked_ci(green(), 'checked'))

    def test_only_requested_cartoon_and_archive_entry_can_change(self):
        base = {'pieces': [{'slug': 'old', 'title': 'Keep this'}]}
        title, alt = 'A "title" <test>', 'A scene'
        new = dict(slug='new', title=title, alt=alt, featured=False, caption='')
        catalog = {'pieces': [new, *copy.deepcopy(base['pieces'])]}
        old_writing = '<ol><li>Original selection</li></ol>'
        entry = f'<li data-kind="image"><a href="/is/writing/new/" target="_self">{escape(title)}</a></li>'
        writing = old_writing.replace('<ol>', '<ol>' + entry)
        paths = ['content/image-pieces.json', 'is/writing/cartoons/slides/new/index.html']
        args = [base, catalog, old_writing, writing, paths, 'new', title, alt]
        publisher.validate_changes(*args)
        for path in ('index.html', '_scripts/paper_site.py', 'is/writing/essays/_src/private.md'):
            bad = copy.deepcopy(args)
            bad[4].append(path)
            with self.assertRaisesRegex(publisher.PublishError, 'Unexpected file'):
                publisher.validate_changes(*bad)
        bad = copy.deepcopy(args)
        bad[1]['pieces'][1]['title'] = 'Unrequested edit'
        with self.assertRaisesRegex(publisher.PublishError, 'Another catalog'):
            publisher.validate_changes(*bad)
        bad = copy.deepcopy(args)
        bad[3] = writing.replace('Original selection', 'New curation')
        with self.assertRaisesRegex(publisher.PublishError, 'Writing selection'):
            publisher.validate_changes(*bad)

    def test_helper_executes_only_in_the_job_worktree_with_literal_arguments(self):
        runner = self.runner()
        with patch.object(runner, 'call', return_value=result('READY')) as call:
            runner.helper('add', str(self.image), '--title', '$(touch nope) `nope`\n"quoted"')
        command = call.call_args.args[0]
        self.assertEqual(command[1], str(runner.worktree / '_scripts/piece.py'))
        self.assertEqual(command[-1], '$(touch nope) `nope`\n"quoted"')
        self.assertEqual(call.call_args.kwargs['cwd'], runner.worktree)

    def run_flow(self, *, pr=None, prepared=(True,), refreshed=(False, False), verification_error=False):
        runner = self.runner()
        runner.state['sha'] = 'checked'
        calls = []
        current_pr = pr
        prepared, refreshed = iter(prepared), iter(refreshed)
        def git(*args, **kwargs):
            calls.append(('git', args))
            if args[:3] == ('remote', 'get-url', 'origin'):
                return result('https://github.com/' + publisher.REPO + '.git')
            if args[:2] == ('rev-parse', '--verify'):
                return result('', 1)
            return result('base')
        def gh(*args):
            nonlocal current_pr
            calls.append(('gh', args))
            if args[:2] == ('pr', 'create'):
                current_pr = dict(number=12, state='OPEN', headRefOid='checked')
            if args[:2] == ('pr', 'merge'):
                current_pr = dict(number=12, state='MERGED', mergeCommit={'oid': 'merged'})
            return result()
        def verify(sha):
            calls.append(('verified', sha))
            if verification_error:
                raise publisher.PublishError('Public bytes still differ')
        def prepare():
            calls.append(('prepare', None))
            return next(prepared)
        def refresh():
            calls.append(('refresh', None))
            return next(refreshed)
        with patch.object(runner, 'git', side_effect=git), patch.object(runner, 'gh', side_effect=gh), \
             patch.object(runner, 'create_worktree'), patch.object(runner, 'find_pr', side_effect=lambda: current_pr), \
             patch.object(runner, 'restore_owned_changes', side_effect=lambda: calls.append(('restore', None))), \
             patch.object(runner, 'prepare', side_effect=prepare), patch.object(runner, 'refresh_base', side_effect=refresh), \
             patch.object(runner, 'wait_checks', side_effect=lambda n: calls.append(('checks', n))), \
             patch.object(runner, 'verify_deployment', side_effect=verify), \
             patch.object(runner, 'cleanup', side_effect=lambda: calls.append(('cleanup', None))):
            if verification_error:
                with self.assertRaisesRegex(publisher.PublishError, 'Public bytes'):
                    runner.publish()
            else:
                self.assertEqual(runner.publish(), runner.url)
        return calls

    def test_fresh_release_checks_before_merging_and_verifies_before_cleanup(self):
        calls = self.run_flow()
        merge = next(i for i,c in enumerate(calls) if c[0]=='gh' and c[1][:2]==('pr','merge'))
        self.assertIn(('checks', 12), calls[:merge])
        self.assertEqual(calls[-2:], [('verified', 'merged'), ('cleanup', None)])
        self.assertIn('--match-head-commit', calls[merge][1])

    def test_retry_restores_owned_work_before_preparation(self):
        calls = self.run_flow()
        self.assertEqual(calls.count(('restore', None)), 1)
        self.assertLess(calls.index(('restore', None)), calls.index(('refresh', None)))
        self.assertLess(calls.index(('refresh', None)), calls.index(('prepare', None)))

    def test_already_live_input_does_not_commit_push_or_open_a_pr(self):
        calls = self.run_flow(prepared=(False,))
        self.assertFalse(any(c[0]=='gh' for c in calls))
        self.assertFalse(any(c[0]=='git' and c[1][0] in ('commit','push') for c in calls))
        self.assertEqual(calls[-2:], [('verified', 'base'), ('cleanup', None)])

    def test_resume_after_pr_creation_reuses_the_same_pr(self):
        calls = self.run_flow(pr=dict(number=12,state='OPEN',headRefOid='checked'))
        self.assertFalse(any(c[0]=='gh' and c[1][:2]==('pr','create') for c in calls))

    def test_merged_retry_only_verifies_and_live_failure_keeps_recovery(self):
        calls = self.run_flow(pr=dict(number=12,state='MERGED',mergeCommit={'oid':'merged'}), verification_error=True)
        self.assertFalse(any(c[0] in ('cleanup','checks','gh') for c in calls))
        self.assertEqual(calls[-1], ('verified', 'merged'))

    def test_newer_master_requires_another_checked_head_before_merge(self):
        calls = self.run_flow(prepared=(True,True), refreshed=(False,True,False))
        self.assertEqual(calls.count(('checks',12)),2)
        self.assertEqual(sum(c[0]=='gh' and c[1][:2]==('pr','create') for c in calls),1)

    def test_concurrent_identical_publication_closes_owned_pr_without_merge(self):
        calls = self.run_flow(prepared=(True,False), refreshed=(False,True))
        self.assertTrue(any(c[0]=='gh' and c[1][:2]==('pr','close') for c in calls))
        self.assertFalse(any(c[0]=='gh' and c[1][:2]==('pr','merge') for c in calls))

    def test_live_proof_uses_successful_deployed_child_commit(self):
        from PIL import Image
        runner = self.runner()
        image = Image.new('RGB',(2,3),'white')
        image.save(runner.source,format='PNG')
        runner.worktree.mkdir()
        image.save(runner.worktree/'art.png')
        (runner.worktree/'content').mkdir()
        (runner.worktree/'content/image-pieces.json').write_text(json.dumps({'pieces':[dict(
            slug=runner.slug,title=runner.title,alt=runner.alt,image='/art.png')]}))
        runs = [dict(headSha='root-rebuild-child',name='pages build and deployment',status='completed',conclusion='success')]
        with patch.object(runner,'gh',return_value=result(json.dumps(runs))), \
             patch.object(runner,'git',return_value=result()) as git, \
             patch.object(runner,'call',return_value=result()), \
             patch.object(runner,'helper',return_value='LIVE: matches') as helper:
            runner.verify_deployment('merge-commit')
        git.assert_any_call('merge-base','--is-ancestor','merge-commit','root-rebuild-child',allow_failure=True)
        git.assert_any_call('switch','--detach','root-rebuild-child',work=True)
        self.assertEqual(runner.state['deployed_sha'],'root-rebuild-child')
        self.assertEqual(runner.state['phase'],'live-verified')
        self.assertEqual(helper.call_args.args[0],'verify-live')


class CartoonPublisherGitTest(unittest.TestCase):
    """Real Git merges and real image preparation in a small, offline site fixture."""

    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.directory = Path(self.temp.name)
        self.root = self.directory / 'site'
        self.root.mkdir()
        # Test repositories must not inherit a user's commit signing or hooks.
        environment = patch.dict(os.environ, GIT_CONFIG_GLOBAL=os.devnull, GIT_CONFIG_NOSYSTEM='1')
        environment.start()
        self.addCleanup(environment.stop)
        self.git('init', '--initial-branch=master')
        self.git('config', 'user.name', 'Cartoon publisher regression')
        self.git('config', 'user.email', 'cartoon-tests@example.invalid')
        (self.root / 'content').mkdir()
        (self.root / 'assets/paper').mkdir(parents=True)
        Image.new('RGB', (8, 8), 'white').save(self.root / 'assets/paper/fallback.png')
        self.image = self.directory / 'upload.png'
        art = Image.new('RGBA', (16, 8))
        art.putdata([((x * 31) % 256, (x * 47) % 256, (x * 13) % 256, 128 + x % 128)
                     for x in range(128)])
        art.save(self.image)
        self.catalog = self.root / 'content/image-pieces.json'
        self.catalog.write_text(json.dumps(dict(schema_version=1, fallback_slug='fallback', pieces=[
            dict(slug='fallback', title='Fallback', published_date='2026-11-08',
                 image='/assets/paper/fallback.png', width=8, height=8, alt='A square',
                 caption='', featured=True)
        ]), indent=2) + '\n')
        (self.root / 'index.html').write_text('Preserve the curated home.\n')
        (self.root / 'editorial.txt').write_text('Private unrelated work.\n')
        self.render(self.root)
        self.commit('Initial fixture')
        self.git('update-ref', 'refs/remotes/origin/master', 'master')
        self.runner = self.make_runner()
        self.runner.create_worktree()

    def git(self, *args, cwd=None, check=True):
        return subprocess.run(['git', *args], cwd=cwd or self.root, text=True,
                              capture_output=True, check=check)

    def commit(self, message):
        self.git('add', '--all')
        self.git('commit', '-m', message)
        return self.git('rev-parse', 'HEAD').stdout.strip()

    def make_runner(self):
        runner = publisher.Publisher(self.image, 'The title', 'Scene and caption', root=self.root,
                                     state_dir=self.directory / 'state')
        actual_git = runner.git

        def local_git(*args, **kwargs):
            if args == ('fetch', 'origin', 'master'):
                # All other commands, including merge/conflict/status handling,
                # execute unchanged. This fetch reads only our temporary repo.
                return actual_git('fetch', str(self.root), 'master:refs/remotes/origin/master', **kwargs)
            return actual_git(*args, **kwargs)

        git_patch = patch.object(runner, 'git', side_effect=local_git)
        git_patch.start()
        self.addCleanup(git_patch.stop)
        helper_patch = patch.object(runner, 'helper', side_effect=lambda *args, **kwargs:
                                    self.helper(runner, *args))
        helper_patch.start()
        self.addCleanup(helper_patch.stop)
        return runner

    def helper(self, runner, *args):
        if args[0] == 'add':
            try:
                return piece.prepare(piece.parser().parse_args(args), runner.worktree)
            except ValueError as exc:
                raise publisher.PublishError(str(exc)) from exc
        self.assertEqual(args, ('check',))
        self.render(runner.worktree)
        return 'PASS: fixture pages generated'

    def render(self, root):
        """Only the renderer is reduced; catalog, pixels and Git use production code."""
        catalog = json.loads((root / 'content/image-pieces.json').read_text())
        entries = ''.join(f'<li data-kind="image"><a href="/is/writing/{p["slug"]}/" '
                          f'target="_self">{escape(p["title"])}</a></li>' for p in catalog['pieces'])
        slugs = ','.join(p['slug'] for p in catalog['pieces'])
        outputs = {
            'is/writing/index.html': '<main>Keep this selection.</main><ol>' + entries + '</ol>\n',
            'is/writing/cartoons/index.html': 'Overview: ' + slugs + '\n',
            'is/writing/cartoons/slides/index.html': 'Slides: ' + slugs + '\n',
            'sitemap.xml': '<routes>' + slugs + '</routes>\n',
        }
        for record in catalog['pieces']:
            outputs[f'is/writing/{record["slug"]}/index.html'] = (
                image_pieces.GENERATOR_MARKER + '\n' + json.dumps(record, sort_keys=True) + '\n')
            outputs[f'is/writing/cartoons/slides/{record["slug"]}/index.html'] = (
                'Slide: ' + record['slug'] + '; neighbors: ' + slugs + '\n')
        for name, text in outputs.items():
            target = root / name
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_text(text)

    def add_to_master(self, *, title='Another cartoon', alt='Another scene', image=None,
                      date='2026-11-09', reader_suffix=''):
        args = piece.parser().parse_args(['add', str(image or self.image), '--title', title,
                                          '--alt', alt, '--date', date])
        piece.prepare(args, self.root)
        self.render(self.root)
        if reader_suffix:
            reader = self.root / f'is/writing/{publisher.build_comedy.slugify(title)}/index.html'
            reader.write_text(reader.read_text() + reader_suffix)
        return self.commit('Independent publication: ' + title)

    def snapshot(self, root):
        return {p.relative_to(root).as_posix(): p.read_bytes()
                for p in root.rglob('*') if p.is_file() and '.git' not in p.relative_to(root).parts}

    def freeze(self, stamp):
        instant = datetime.fromisoformat(stamp).replace(tzinfo=timezone.utc)

        class FrozenDateTime(datetime):
            @classmethod
            def now(cls, tz=None):
                return instant.astimezone(tz) if tz else instant.replace(tzinfo=None)

        return patch.object(publisher, 'datetime', FrozenDateTime)

    def concurrent_same_slug(self, *, image=None, alt=None):
        self.runner.state['date'] = '2026-11-10'
        self.assertTrue(self.runner.prepare())
        self.add_to_master(title=self.runner.title, alt=alt or self.runner.alt, image=image,
                           date=self.runner.state['date'], reader_suffix='Upstream reader revision.\n')
        if image is None:
            # Different lossless encoding creates a genuine binary add/add conflict
            # while retaining the approved pixels for piece.prepare to compare.
            target = self.root / f'assets/paper/pieces/{self.runner.slug}.webp'
            with Image.open(self.image) as source:
                source.save(target, format='WEBP', lossless=True, method=0, exact=True,
                            icc_profile=b'fixture-only color profile')
            self.commit('Alternative lossless encoding')
        root_before = self.snapshot(self.root)
        self.assertNotEqual(
            (self.root / f'assets/paper/pieces/{self.runner.slug}.webp').read_bytes(),
            (self.runner.worktree / f'assets/paper/pieces/{self.runner.slug}.webp').read_bytes())
        self.assertNotEqual(
            (self.root / f'is/writing/{self.runner.slug}/index.html').read_bytes(),
            (self.runner.worktree / f'is/writing/{self.runner.slug}/index.html').read_bytes())
        self.assertTrue(self.runner.refresh_base())
        merge = self.git('rev-parse', '--verify', 'MERGE_HEAD', cwd=self.runner.worktree)
        self.assertEqual(merge.returncode, 0)
        self.assertEqual(self.git('diff', '--name-only', '--diff-filter=U',
                                 cwd=self.runner.worktree).stdout, '')
        self.assertEqual(root_before, self.snapshot(self.root))
        return root_before

    def test_identical_same_slug_add_add_conflict_reuses_upstream_publication(self):
        root_before = self.concurrent_same_slug()
        self.assertFalse(self.runner.prepare())
        for path in (f'assets/paper/pieces/{self.runner.slug}.webp',
                     f'is/writing/{self.runner.slug}/index.html'):
            self.assertEqual((self.runner.worktree / path).read_bytes(), root_before[path])
        self.assertEqual(self.runner.existing_release(None), self.git('rev-parse', 'master').stdout.strip())
        self.assertNotEqual(self.git('rev-parse', '--verify', 'MERGE_HEAD', cwd=self.runner.worktree,
                                     check=False).returncode, 0)
        self.assertEqual(root_before, self.snapshot(self.root))

    def test_different_same_slug_artwork_is_rejected_after_real_add_add_conflict(self):
        other = self.directory / 'different.png'
        Image.new('RGBA', (16, 8), 'red').save(other)
        root_before = self.concurrent_same_slug(image=other)
        with self.assertRaisesRegex(publisher.PublishError, 'different content'):
            self.runner.prepare()
        self.assertEqual(root_before, self.snapshot(self.root))
        asset = f'assets/paper/pieces/{self.runner.slug}.webp'
        self.assertEqual((self.runner.worktree / asset).read_bytes(), root_before[asset])

    def test_different_same_slug_description_is_rejected_after_real_add_add_conflict(self):
        root_before = self.concurrent_same_slug(alt='A different approved description')
        with self.assertRaisesRegex(publisher.PublishError, 'different content'):
            self.runner.prepare()
        self.assertEqual(root_before, self.snapshot(self.root))

    def test_interrupted_staged_and_untracked_preparation_retries_over_advanced_master(self):
        def interrupted(*args, **kwargs):
            output = self.helper(self.runner, *args)
            if args == ('check',):
                self.git('add', '--', 'content/image-pieces.json', cwd=self.runner.worktree)
                raise publisher.PublishError('Interrupted after generating pages')
            return output

        with patch.object(self.runner, 'helper', side_effect=interrupted):
            with self.assertRaisesRegex(publisher.PublishError, 'Interrupted'):
                self.runner.prepare()
        saved_date = self.runner.state['date']
        dirty = self.git('status', '--porcelain', cwd=self.runner.worktree).stdout
        self.assertIn('M  content/image-pieces.json', dirty)
        self.assertIn(' M is/writing/index.html', dirty)
        self.assertIn('?? assets/paper/pieces/', dirty)
        master = self.add_to_master()
        root_before = self.snapshot(self.root)
        self.runner.restore_owned_changes()
        self.assertEqual(self.git('status', '--porcelain', cwd=self.runner.worktree).stdout, '')
        self.assertFalse((self.runner.worktree / f'assets/paper/pieces/{self.runner.slug}.webp').exists())
        self.assertFalse((self.runner.worktree / f'is/writing/{self.runner.slug}').exists())
        self.assertTrue(self.runner.refresh_base())
        self.assertTrue(self.runner.prepare())
        self.assertEqual(self.runner.state['date'], saved_date)
        self.assertEqual(self.git('status', '--porcelain', cwd=self.runner.worktree).stdout, '')
        self.git('merge-base', '--is-ancestor', master, 'HEAD', cwd=self.runner.worktree)
        catalog = json.loads((self.runner.worktree / 'content/image-pieces.json').read_text())
        self.assertEqual([p['slug'] for p in catalog['pieces']], ['the-title', 'another-cartoon', 'fallback'])
        self.assertEqual(root_before, self.snapshot(self.root))

    def test_unexpected_dirty_path_refuses_recovery_without_discarding_any_work(self):
        self.helper(self.runner, 'add', str(self.runner.source), '--title', self.runner.title,
                    '--alt', self.runner.alt, '--date', '2026-11-09')
        self.render(self.runner.worktree)
        for name in ('unrelated.txt', 'editorial.txt', f'is/writing/{self.runner.slug}/notes.txt'):
            with self.subTest(path=name):
                target = self.runner.worktree / name
                original = target.read_bytes() if target.exists() else None
                target.write_text('Keep this unrelated edit.\n')
                before = self.snapshot(self.runner.worktree)
                status = self.git('status', '--porcelain', cwd=self.runner.worktree).stdout
                with self.assertRaisesRegex(publisher.PublishError, '[Uu]nexpected'):
                    self.runner.restore_owned_changes()
                self.assertEqual(before, self.snapshot(self.runner.worktree))
                self.assertEqual(status, self.git('status', '--porcelain', cwd=self.runner.worktree).stdout)
                if original is None:
                    target.unlink()
                else:
                    target.write_bytes(original)

    def pending_helper_files(self, pid='424242'):
        self.helper(self.runner, 'add', str(self.runner.source), '--title', self.runner.title,
                    '--alt', self.runner.alt, '--date', '2026-11-09')
        self.render(self.runner.worktree)
        self.git('add', '--', 'content/image-pieces.json', cwd=self.runner.worktree)
        lock = self.runner.worktree / 'content/.piece.lock'
        scratch = self.runner.worktree / 'content/.piece-interrupted.json'
        lock.write_text(pid)
        scratch.write_text('{"interrupted": true}\n')
        return lock, scratch

    def test_dead_helper_lock_and_scratch_are_recovered_before_a_successful_retry(self):
        before = self.snapshot(self.runner.worktree)
        lock, scratch = self.pending_helper_files()
        with patch.object(publisher.os, 'kill', side_effect=ProcessLookupError('fixture process ended')) as kill:
            self.runner.restore_owned_changes()
        kill.assert_called_once_with(424242, 0)
        self.assertFalse(lock.exists())
        self.assertFalse(scratch.exists())
        self.assertEqual(before, self.snapshot(self.runner.worktree))
        self.assertEqual(self.git('status', '--porcelain', cwd=self.runner.worktree).stdout, '')
        self.assertTrue(self.runner.prepare())

    def test_live_helper_lock_preserves_all_pending_files(self):
        self.pending_helper_files()
        before = self.snapshot(self.runner.worktree)
        status = self.git('status', '--porcelain', cwd=self.runner.worktree).stdout
        with patch.object(publisher.os, 'kill', return_value=None) as kill:
            with self.assertRaisesRegex(publisher.PublishError, 'still running'):
                self.runner.restore_owned_changes()
        kill.assert_called_once_with(424242, 0)
        self.assertEqual(before, self.snapshot(self.runner.worktree))
        self.assertEqual(status, self.git('status', '--porcelain', cwd=self.runner.worktree).stdout)

    def test_invalid_helper_lock_never_probes_a_process_or_changes_files(self):
        lock, _ = self.pending_helper_files()
        for pid in ('', 'not a PID', '0', '-1', '42.5'):
            with self.subTest(pid=pid):
                lock.write_text(pid)
                before = self.snapshot(self.runner.worktree)
                status = self.git('status', '--porcelain', cwd=self.runner.worktree).stdout
                with patch.object(publisher.os, 'kill') as kill:
                    with self.assertRaisesRegex(publisher.PublishError, 'cannot be safely cleared'):
                        self.runner.restore_owned_changes()
                kill.assert_not_called()
                self.assertEqual(before, self.snapshot(self.runner.worktree))
                self.assertEqual(status, self.git('status', '--porcelain', cwd=self.runner.worktree).stdout)

    def test_unverifiable_helper_pid_preserves_lock_and_pending_files(self):
        self.pending_helper_files()
        before = self.snapshot(self.runner.worktree)
        status = self.git('status', '--porcelain', cwd=self.runner.worktree).stdout
        with patch.object(publisher.os, 'kill', side_effect=PermissionError('fixture process is inaccessible')) as kill:
            with self.assertRaisesRegex(publisher.PublishError, 'cannot be safely cleared'):
                self.runner.restore_owned_changes()
        kill.assert_called_once_with(424242, 0)
        self.assertEqual(before, self.snapshot(self.runner.worktree))
        self.assertEqual(status, self.git('status', '--porcelain', cwd=self.runner.worktree).stdout)

    def test_unrelated_edits_preserve_even_a_dead_helper_lock_and_scratch(self):
        lock, scratch = self.pending_helper_files()
        (self.runner.worktree / 'editorial.txt').write_text('Unrelated staged edit.\n')
        self.git('add', '--', 'editorial.txt', cwd=self.runner.worktree)
        (self.runner.worktree / f'is/writing/{self.runner.slug}/notes.txt').write_text('Keep these notes.\n')
        before = self.snapshot(self.runner.worktree)
        status = self.git('status', '--porcelain', cwd=self.runner.worktree).stdout
        with patch.object(publisher.os, 'kill', side_effect=ProcessLookupError('fixture process ended')) as kill:
            with self.assertRaisesRegex(publisher.PublishError, '[Uu]nexpected'):
                self.runner.restore_owned_changes()
        kill.assert_called_once_with(424242, 0)
        self.assertTrue(lock.exists())
        self.assertTrue(scratch.exists())
        self.assertEqual(before, self.snapshot(self.runner.worktree))
        self.assertEqual(status, self.git('status', '--porcelain', cwd=self.runner.worktree).stdout)

    def test_helper_scratch_without_a_dead_lock_is_preserved_as_unexpected(self):
        lock, _ = self.pending_helper_files()
        lock.unlink()
        before = self.snapshot(self.runner.worktree)
        status = self.git('status', '--porcelain', cwd=self.runner.worktree).stdout
        with patch.object(publisher.os, 'kill') as kill:
            with self.assertRaisesRegex(publisher.PublishError, '[Uu]nexpected'):
                self.runner.restore_owned_changes()
        kill.assert_not_called()
        self.assertEqual(before, self.snapshot(self.runner.worktree))
        self.assertEqual(status, self.git('status', '--porcelain', cwd=self.runner.worktree).stdout)

    def test_date_is_saved_before_helper_failure_and_survives_seoul_midnight(self):
        with self.freeze('2026-11-19T14:59:00'), \
             patch.object(self.runner, 'helper', side_effect=publisher.PublishError('helper interrupted')) as helper:
            with self.assertRaisesRegex(publisher.PublishError, 'helper interrupted'):
                self.runner.prepare()
        args = helper.call_args.args
        self.assertIn('--date', args)
        self.assertEqual(args[args.index('--date') + 1], '2026-11-19')
        self.assertEqual(json.loads(self.runner.state_path.read_text())['date'], '2026-11-19')
        resumed = self.make_runner()
        with self.freeze('2026-11-19T15:01:00'):
            self.assertTrue(resumed.prepare())
        self.assertEqual(resumed.state['date'], '2026-11-19')
        catalog = json.loads((resumed.worktree / 'content/image-pieces.json').read_text())
        self.assertEqual(catalog['pieces'][0]['published_date'], '2026-11-19')

    def test_new_publication_date_uses_seoul_day(self):
        with self.freeze('2026-11-19T15:01:00'):
            self.assertTrue(self.runner.prepare())
        self.assertEqual(self.runner.state['date'], '2026-11-20')

    def test_existing_publication_date_is_reused_without_saved_job_state(self):
        self.add_to_master(title=self.runner.title, alt=self.runner.alt, date='2026-11-09')
        self.assertNotIn('date', self.runner.state)
        self.assertTrue(self.runner.refresh_base())
        with self.freeze('2026-11-19T15:01:00'):
            self.assertFalse(self.runner.prepare())
        self.assertEqual(self.runner.state['date'], '2026-11-09')


class CartoonPublisherInstallTest(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        (self.root / '_scripts').mkdir()
        (self.root / '_scripts/cartoon-publisher.applescript').write_text('set runner to __RUNNER__\n')
        self.applications = self.root / 'Applications'
        self.target = self.applications / 'Publish Cartoon.app'

    def installer(self, *, failure=None):
        commands = []

        def run(args, **kwargs):
            commands.append(args)
            self.assertFalse(self.target.exists(), 'unfinished app was exposed at its final path')
            if Path(args[0]).name == 'osacompile':
                build = Path(args[2])
                self.assertNotEqual(build, self.target)
                self.assertIn(self.applications, build.parents)
                info = build / 'Contents/Info.plist'
                info.parent.mkdir(parents=True)
                info.write_bytes(plistlib.dumps({'CFBundleName': 'Publish Cartoon'}))
            else:
                self.assertEqual(Path(args[0]).name, 'codesign')
                build = Path(args[-1])
                metadata = plistlib.loads((build / 'Contents/Info.plist').read_bytes())
                self.assertEqual(metadata['CFBundleIdentifier'], 'im.ajin.cartoonpublisher')
                self.assertEqual(metadata['CFBundleShortVersionString'], '1.0')
            if Path(args[0]).name == failure:
                raise subprocess.CalledProcessError(1, args, stderr='injected failure')
            return result()

        with patch.object(publisher.subprocess, 'run', side_effect=run):
            if failure:
                with self.assertRaises(subprocess.CalledProcessError):
                    publisher.install_app(self.applications, root=self.root)
                self.assertFalse(self.target.exists())
                self.assertEqual(list(self.applications.iterdir()), [])
            else:
                self.assertEqual(publisher.install_app(self.applications, root=self.root), self.target)
                self.assertTrue((self.target / 'Contents/Info.plist').is_file())
                self.assertEqual(list(self.applications.iterdir()), [self.target])
        return commands

    def test_compile_failure_leaves_no_half_installed_app(self):
        self.assertEqual(len(self.installer(failure='osacompile')), 1)

    def test_signing_failure_leaves_no_half_installed_app(self):
        self.assertEqual(len(self.installer(failure='codesign')), 2)

    def test_success_installs_only_after_compile_and_signing_complete(self):
        self.assertEqual(len(self.installer()), 2)

    def test_existing_app_is_preserved_without_running_the_installer(self):
        self.target.mkdir(parents=True)
        sentinel = self.target / 'keep'
        sentinel.write_text('Existing installation')
        with patch.object(publisher.subprocess, 'run') as run:
            with self.assertRaisesRegex(publisher.PublishError, 'already exists'):
                publisher.install_app(self.applications, root=self.root)
        run.assert_not_called()
        self.assertEqual(sentinel.read_text(), 'Existing installation')


if __name__ == '__main__':
    unittest.main()
