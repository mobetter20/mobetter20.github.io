"""On-demand Mac cartoon publishing. No AI, watcher, or canonical checkout writes."""
from __future__ import annotations

import argparse
from contextlib import contextmanager
from datetime import datetime
import fcntl
import hashlib
from html import escape
import json
import os
from pathlib import Path
import plistlib
import shlex
import signal
import subprocess
import sys
import tempfile
import time
from zoneinfo import ZoneInfo

import build_comedy
import cartoon_displays

ROOT = Path(__file__).resolve().parents[1]
REPO = 'mobetter20/mobetter20.github.io'
STATE = Path.home() / '.local/share/cartoon-publisher'
WORKFLOW = 'Check newspaper content and generated pages'


class PublishError(Exception):
    pass


def atomic_json(path, value):
    temporary = path.with_suffix('.tmp')
    temporary.write_text(json.dumps(value, ensure_ascii=False, indent=2) + '\n')
    temporary.replace(path)


@contextmanager
def launch_lock(directory):
    directory.mkdir(parents=True, exist_ok=True)
    with (directory / 'publisher.lock').open('a+') as lock:
        try:
            fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
        except BlockingIOError as exc:
            raise PublishError('Another cartoon is being published. Please wait for its result.') from exc
        lock.seek(0)
        lock.truncate()
        lock.write(str(os.getpid()))
        lock.flush()
        try:
            yield
        finally:
            fcntl.flock(lock, fcntl.LOCK_UN)


def checked_ci(pr, expected_sha):
    """Missing checks never count as green. Return False only while still waiting."""
    if pr['headRefOid'] != expected_sha:
        raise PublishError('The release changed while it was being checked. Nothing was merged.')
    checks = pr.get('statusCheckRollup') or []
    required = [c for c in checks if c.get('name') == 'validate' and c.get('workflowName') == WORKFLOW]
    for check in checks:
        if check.get('conclusion') in ('FAILURE', 'CANCELLED', 'TIMED_OUT', 'ACTION_REQUIRED', 'STARTUP_FAILURE'):
            raise PublishError('The release checks did not pass. The saved release has not been merged.')
    return bool(required) and all(c.get('status') == 'COMPLETED' and c.get('conclusion') == 'SUCCESS' for c in required)


def cartoon_paths(catalog, slug):
    paths = {'content/image-pieces.json', f'assets/paper/pieces/{slug}.webp',
             f'is/writing/{slug}/index.html', 'is/writing/index.html',
             'is/writing/cartoons/index.html', 'is/writing/cartoons/slides/index.html', 'sitemap.xml',
             f'is/writing/cartoons/slides/{slug}/index.html'}
    paths.update(f'is/writing/cartoons/slides/{p["slug"]}/index.html' for p in catalog['pieces'])
    return paths


def validate_changes(base_catalog, catalog, old_writing, writing, paths, slug, title, alt):
    """Only one new cartoon and its generated discovery pages may be released."""
    expected = [p for p in catalog['pieces'] if p['slug'] == slug]
    if len(expected) != 1:
        raise PublishError('The new cartoon is missing or duplicated in the catalog.')
    record = expected[0]
    if (record['title'] != title or record['alt'] != alt or record['featured'] or
            record.get('show_title') or record.get('mobile_panels') or record['caption']):
        raise PublishError('The prepared cartoon differs from the requested image settings.')
    previous = {**catalog, 'pieces': [p for p in catalog['pieces'] if p['slug'] != slug]}
    if previous != base_catalog:
        raise PublishError('Another catalog entry changed. Nothing will be published.')
    entry = f'<li data-kind="image"><a href="/is/writing/{slug}/" target="_self">{escape(title)}</a></li>'
    if writing.count(entry) != 1 or writing.replace(entry, '', 1) != old_writing:
        raise PublishError('The Writing selection changed beyond the new archive entry.')
    allowed = cartoon_paths(catalog, slug)
    if "width" in record:
        allowed.update(cartoon_displays.asset_paths(record))
    unexpected = set(paths) - allowed
    if unexpected:
        raise PublishError('Unexpected file changes: ' + ', '.join(sorted(unexpected)))


class Publisher:
    def __init__(self, image, title, alt, *, root=ROOT, state_dir=STATE):
        self.root = Path(root).resolve()
        self.title, self.alt = title.strip(), alt.strip()
        self.slug = build_comedy.slugify(self.title)
        if not self.title or not self.alt or not self.slug:
            raise PublishError('Please provide a title and an image description.')
        self.image_bytes = Path(image).read_bytes()
        identity = json.dumps([hashlib.sha256(self.image_bytes).hexdigest(), self.title, self.alt], ensure_ascii=False)
        self.key = hashlib.sha256(identity.encode()).hexdigest()[:20]
        self.directory = Path(state_dir) / self.key
        self.directory.mkdir(parents=True, exist_ok=True)
        self.state_path = self.directory / 'state.json'
        self.state = json.loads(self.state_path.read_text()) if self.state_path.exists() else {}
        self.branch = 'codex/cartoon-publish-' + self.key
        self.worktree = self.directory / 'worktree'
        self.source = self.directory / 'image'
        if not self.source.exists():
            snapshot = self.directory / 'image.tmp'
            snapshot.write_bytes(self.image_bytes)
            snapshot.replace(self.source)
        if self.source.read_bytes() != self.image_bytes:
            raise PublishError('The saved upload differs from this image. Please keep the original file.')
        self.route = f'/is/writing/{self.slug}/'
        self.url = 'https://ajin.im' + self.route
        self.log_path = self.directory / 'publisher.log'

    def save(self, phase, **values):
        self.state.update(values, phase=phase, updated=datetime.now().isoformat(),
                          branch=self.branch, title=self.title, slug=self.slug, url=self.url)
        atomic_json(self.state_path, self.state)

    def call(self, args, *, cwd=None, timeout=180, allow_failure=False):
        env = {**os.environ, 'PATH': '/opt/homebrew/bin:/usr/local/bin:/usr/bin:/bin',
               'GIT_TERMINAL_PROMPT': '0', 'GH_PROMPT_DISABLED': '1'}
        with subprocess.Popen(args, cwd=cwd or self.root, env=env, text=True,
                              stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                              start_new_session=True) as process:
            try:
                out, err = process.communicate(timeout=timeout)
            except subprocess.TimeoutExpired:
                os.killpg(process.pid, signal.SIGKILL)
                out, err = process.communicate()
                raise PublishError(f'{Path(args[0]).name} took too long. Your release is saved for retry.')
        with self.log_path.open('a') as log:
            log.write(f'\n{datetime.now().isoformat()} {Path(args[0]).name}: exit {process.returncode}\n{out}{err}')
        if process.returncode and not allow_failure:
            raise PublishError((err or out or 'Command failed').strip()[-1200:])
        return subprocess.CompletedProcess(args, process.returncode, out, err)

    def git(self, *args, work=False, **kwargs):
        return self.call(['git', *args], cwd=self.worktree if work else self.root, **kwargs)

    def gh(self, *args):
        return self.call(['gh', *args, '--repo', REPO])

    def helper(self, *args, timeout=900):
        # Execute the worktree's helper. Importing canonical piece.py would bind
        # its ROOT to the user's checkout and invalidate isolation.
        return self.call([sys.executable, str(self.worktree / '_scripts/piece.py'), *args],
                         cwd=self.worktree, timeout=timeout).stdout

    def create_worktree(self):
        if self.worktree.exists():
            actual = self.git('branch', '--show-current', work=True).stdout.strip()
            if not actual:
                self.git('switch', self.branch, work=True)
            elif actual != self.branch:
                raise PublishError('The saved release checkout changed unexpectedly.')
            return
        local = self.git('show-ref', '--verify', 'refs/heads/' + self.branch, allow_failure=True)
        if local.returncode == 0:
            self.git('worktree', 'add', str(self.worktree), self.branch)
        else:
            self.git('worktree', 'add', '-b', self.branch, str(self.worktree), 'origin/master')

    def restore_owned_changes(self):
        """Rebuild an interrupted attempt from its immutable upload, never from edits."""
        lock = self.worktree / 'content/.piece.lock'
        scratch = set()
        if lock.exists():
            try:
                pid = int(lock.read_text().strip())
                if pid <= 0:
                    raise ValueError()
                os.kill(pid, 0)
            except ProcessLookupError:
                scratch.add('content/.piece.lock')
                scratch.update(p.relative_to(self.worktree).as_posix()
                               for p in lock.parent.glob('.piece-*.json'))
            except (ValueError, PermissionError) as exc:
                raise PublishError('The saved preparation lock cannot be safely cleared.') from exc
            else:
                raise PublishError('The saved image preparation is still running. Retry after it finishes.')
        allowed = set()
        for revision in ('HEAD', 'origin/master'):
            catalog = json.loads(self.git('show', revision + ':content/image-pieces.json', work=True).stdout)
            allowed.update(cartoon_paths(catalog, self.slug))

        def dirty_paths():
            tracked = set(filter(None, self.git('diff', '--name-only', '-z', 'HEAD', work=True).stdout.split('\0')))
            untracked = set(filter(None, self.git('ls-files', '--others', '--exclude-standard', '-z', work=True).stdout.split('\0')))
            unexpected = {p for p in (tracked | untracked) - allowed - scratch
                          if not cartoon_displays.belongs_to_slug(p, self.slug)}
            if unexpected:
                raise PublishError('Unexpected saved checkout changes were preserved: ' + ', '.join(sorted(unexpected)))
            return tracked, untracked

        # Validate before aborting a merge or touching any saved file. This
        # checkout belongs to the publisher, but unknown edits still stay intact.
        dirty_paths()
        if self.git('rev-parse', '--verify', 'MERGE_HEAD', work=True, allow_failure=True).returncode == 0:
            self.git('merge', '--abort', work=True)
        tracked, untracked = dirty_paths()
        if tracked:
            self.git('restore', '--source=HEAD', '--staged', '--worktree', '--', *sorted(tracked), work=True)
        for path in sorted(untracked):
            (self.worktree / path).unlink(missing_ok=True)
        # Git does not track directories, but the helper deliberately refuses
        # an already-existing reader route. Remove only our empty route dirs.
        for relative in (f'is/writing/{self.slug}', f'is/writing/cartoons/slides/{self.slug}'):
            directory = self.worktree / relative
            if directory.is_dir() and not any(directory.iterdir()):
                directory.rmdir()

    def prepare(self):
        base = self.git('rev-parse', 'origin/master').stdout.strip()
        base_catalog = json.loads(self.git('show', base + ':content/image-pieces.json').stdout)
        existing = next((p for p in base_catalog['pieces'] if p['slug'] == self.slug), None)
        stamp = (self.state.get('date') or (existing or {}).get('published_date')
                 or datetime.now(ZoneInfo('Asia/Seoul')).date().isoformat())
        # Pin the date before the helper can write an asset. A retry tomorrow
        # must describe the same approved release, even after a killed process.
        self.save('preparing', base=base, date=stamp)
        args = ['add', str(self.source), '--title', self.title, '--alt', self.alt, '--date', stamp]
        result = self.helper(*args)
        catalog = json.loads((self.worktree / 'content/image-pieces.json').read_text())
        record = next(p for p in catalog['pieces'] if p['slug'] == self.slug)
        self.save('prepared', date=record['published_date'])
        if existing:
            if not result.startswith('UNCHANGED'):
                raise PublishError('An existing cartoon would be changed.')
            return False
        self.helper('check')
        paths = self.git('diff', '--name-only', '-z', base, work=True).stdout.split('\0')
        paths += self.git('ls-files', '--others', '--exclude-standard', '-z', work=True).stdout.split('\0')
        paths = sorted(set(filter(None, paths)))
        validate_changes(base_catalog, catalog, self.git('show', base + ':is/writing/index.html').stdout,
                         (self.worktree / 'is/writing/index.html').read_text(), paths,
                         self.slug, self.title, self.alt)
        self.git('diff', '--check', work=True)
        if paths:
            self.git('add', '--', *paths, work=True)
        staged = self.git('diff', '--cached', '--quiet', work=True, allow_failure=True).returncode
        merging = self.git('rev-parse', '--verify', 'MERGE_HEAD', work=True, allow_failure=True).returncode == 0
        if staged or merging:
            self.git('commit', '-m', 'Publish cartoon: ' + self.title, work=True)
        if self.git('status', '--porcelain', work=True).stdout.strip():
            raise PublishError('The release checkout is not clean after its commit.')
        self.save('checked', sha=self.git('rev-parse', 'HEAD', work=True).stdout.strip())
        return True

    def refresh_base(self):
        self.git('fetch', 'origin', 'master')
        base = self.git('rev-parse', 'origin/master').stdout.strip()
        if self.git('merge-base', '--is-ancestor', base, 'HEAD', work=True, allow_failure=True).returncode == 0:
            return False
        merge = self.git('merge', '--no-commit', '--no-ff', base, work=True, allow_failure=True)
        conflicts = list(filter(None, self.git('diff', '--name-only', '--diff-filter=U', '-z', work=True).stdout.split('\0')))
        if merge.returncode and not conflicts and self.git('rev-parse', '--verify', 'MERGE_HEAD', work=True, allow_failure=True).returncode:
            raise PublishError('The saved release could not be refreshed: ' + merge.stderr.strip()[-400:])
        catalog = json.loads(self.git('show', base + ':content/image-pieces.json').stdout)
        regenerated = cartoon_paths(catalog, self.slug)
        if any(p not in regenerated and not cartoon_displays.belongs_to_slug(p, self.slug) for p in conflicts):
            self.git('merge', '--abort', work=True)
            raise PublishError('Another release conflicts with this cartoon. Nothing was merged online.')
        for path in conflicts:
            self.git('restore', '--source=' + base, '--staged', '--worktree', '--', path, work=True)
        # Reapply exactly this upload over the newest catalog, including when Git
        # could textually merge both additions but their generated pages are stale.
        (self.worktree / 'content/image-pieces.json').write_text(json.dumps(catalog, ensure_ascii=False, indent=2) + '\n')
        return True

    def find_pr(self):
        prs = json.loads(self.gh('pr', 'list', '--head', self.branch, '--state', 'all',
                                '--json', 'number,state,headRefOid,mergeCommit').stdout)
        if len(prs) > 1:
            raise PublishError('More than one release matches this upload. Nothing was merged.')
        return prs[0] if prs else None

    def existing_release(self, pr):
        if self.git('rev-parse', '--verify', 'MERGE_HEAD', work=True, allow_failure=True).returncode == 0:
            self.git('merge', '--abort', work=True)
        if pr and pr['state'] == 'OPEN':
            self.gh('pr', 'close', str(pr['number']))
        self.save('verifying', existing=True)
        return self.git('rev-parse', 'origin/master').stdout.strip()

    def wait_checks(self, number):
        deadline = time.monotonic() + 600
        while time.monotonic() < deadline:
            pr = json.loads(self.gh('pr', 'view', str(number), '--json', 'headRefOid,statusCheckRollup').stdout)
            if checked_ci(pr, self.state['sha']):
                return
            time.sleep(10)
        raise PublishError('Release checks are still pending. Run the same upload again to continue.')

    def verify_deployment(self, required_commit):
        self.save('verifying', required_commit=required_commit)
        deadline = time.monotonic() + 600
        last_error = 'The deployment is still pending.'
        while time.monotonic() < deadline:
            self.git('fetch', 'origin', 'master')
            runs = json.loads(self.gh('run', 'list', '--branch', 'master', '--limit', '20',
                                     '--json', 'headSha,name,status,conclusion').stdout)
            deployed = next((r['headSha'] for r in runs if r['name'] == 'pages build and deployment'
                             and r['status'] == 'completed' and r['conclusion'] == 'success'), None)
            if deployed and self.git('merge-base', '--is-ancestor', required_commit, deployed, allow_failure=True).returncode == 0:
                try:
                    self.git('switch', '--detach', deployed, work=True)
                    self.call([sys.executable, str(self.worktree / '_scripts/build_sections.py'), '--check'], cwd=self.worktree)
                    # Match the approved upload again at the actual deployed SHA.
                    catalog = json.loads((self.worktree / 'content/image-pieces.json').read_text())
                    p = next((p for p in catalog['pieces'] if p['slug'] == self.slug), None)
                    if not p or p['title'] != self.title or p['alt'] != self.alt:
                        raise PublishError('The deployed cartoon metadata differs from this upload.')
                    from PIL import Image
                    with Image.open(self.source) as original, Image.open(self.worktree / p['image'].lstrip('/')) as saved:
                        if original.size != saved.size or original.convert('RGBA').tobytes() != saved.convert('RGBA').tobytes():
                            raise PublishError('The deployed artwork differs from this upload.')
                    proof = self.helper('verify-live', self.route, '/is/writing/cartoons/',
                                        '/is/writing/cartoons/slides/', f'/is/writing/cartoons/slides/{self.slug}/',
                                        '--cartoon-slug', self.slug, timeout=180)
                    self.save('live-verified', deployed_sha=deployed, proof=proof.strip())
                    return
                except PublishError as exc:
                    last_error = str(exc)
            time.sleep(10)
        raise PublishError('Publication could not yet be confirmed. Retry the same upload to check again. ' + last_error)

    def cleanup(self):
        self.git('worktree', 'remove', str(self.worktree))
        self.git('branch', '-d', self.branch)
        remote = self.git('ls-remote', '--heads', 'origin', self.branch).stdout.strip()
        if remote:
            self.git('push', 'origin', '--delete', self.branch)
        self.source.unlink(missing_ok=True)

    def publish(self):
        remote = self.git('remote', 'get-url', 'origin').stdout.strip()
        if remote not in (f'https://github.com/{REPO}.git', f'git@github.com:{REPO}.git', f'https://github.com/{REPO}'):
            raise PublishError('This is not the configured ajin.im repository.')
        self.git('fetch', 'origin', 'master')
        self.create_worktree()
        self.restore_owned_changes()
        pr = self.find_pr()
        if pr and pr['state'] == 'CLOSED':
            raise PublishError('This saved release was closed without publication. It will not be reopened automatically.')
        if pr and pr['state'] == 'MERGED':
            required = pr['mergeCommit']['oid']
        else:
            self.refresh_base()
            if not self.prepare():
                required = self.existing_release(pr)
                self.verify_deployment(required)
                try:
                    self.cleanup()
                except PublishError as exc:
                    self.save('live-verified', cleanup_pending=str(exc))
                return self.url
            for attempt in range(4):
                self.git('push', '-u', 'origin', self.branch, work=True)
                if not pr:
                    body = self.directory / 'pr.md'
                    body.write_text(f'Publish the approved cartoon “{self.title}”. Complete artwork, hidden external title and newest-first archive entry. Home and curated Writing are unchanged.\n\nValidated with the existing batch check. The local publisher will verify public pages and artwork after deployment.\n')
                    self.gh('pr', 'create', '--base', 'master', '--head', self.branch,
                            '--title', 'Publish cartoon: ' + self.title, '--body-file', str(body))
                    pr = self.find_pr()
                    if not pr:
                        raise PublishError('The release request could not be confirmed. Retry this same upload.')
                self.save('pushed', pr=pr['number'])
                self.wait_checks(pr['number'])
                # Repeat this gate immediately before every merge attempt.
                if self.refresh_base():
                    if self.prepare():
                        continue
                    required = self.existing_release(pr)
                    break
                self.gh('pr', 'merge', str(pr['number']), '--squash', '--match-head-commit', self.state['sha'])
                pr = self.find_pr()
                if not pr or pr['state'] != 'MERGED':
                    raise PublishError('GitHub has not confirmed the merge.')
                required = pr['mergeCommit']['oid']
                self.save('merged', merge_sha=required)
                break
            else:
                raise PublishError('The site kept changing during release. Retry this same upload in a moment.')
        self.verify_deployment(required)
        try:
            self.cleanup()
        except PublishError as exc:
            self.save('live-verified', cleanup_pending=str(exc))
        return self.url


def install_app(directory, *, root=ROOT):
    target = Path(directory).expanduser() / 'Publish Cartoon.app'
    if target.exists():
        raise PublishError(f'{target} already exists. Keep it until an explicit replacement is requested.')
    target.parent.mkdir(parents=True, exist_ok=True)
    template = (root / '_scripts/cartoon-publisher.applescript').read_text()
    command = shlex.join([sys.executable, str(root / '_scripts/cartoon_publisher.py')])
    script = template.replace('__RUNNER__', json.dumps(command, ensure_ascii=False))
    with tempfile.TemporaryDirectory(prefix='.cartoon-install-', dir=target.parent) as temporary:
        bundle = Path(temporary) / target.name
        subprocess.run(['/usr/bin/osacompile', '-o', str(bundle), '-'], input=script, text=True, check=True)
        info = bundle / 'Contents/Info.plist'
        metadata = plistlib.loads(info.read_bytes())
        metadata.update(CFBundleIdentifier='im.ajin.cartoonpublisher', CFBundleShortVersionString='1.0')
        info.write_bytes(plistlib.dumps(metadata))
        subprocess.run(['/usr/bin/codesign', '--force', '--sign', '-', str(bundle)], check=True, capture_output=True)
        bundle.rename(target)
    return target


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--image', type=Path)
    parser.add_argument('--title')
    parser.add_argument('--alt')
    parser.add_argument('--suggest-title', type=Path)
    parser.add_argument('--install-app', type=Path)
    args = parser.parse_args()
    if args.suggest_title:
        stem = args.suggest_title.stem.replace('-', ' ').replace('_', ' ')
        print('' if stem.lower().startswith(('chatgpt', 'codex clipboard')) else stem[:1].upper() + stem[1:])
        return 0
    publisher = None
    try:
        if args.install_app:
            print(install_app(args.install_app))
            return 0
        if args.image is None or args.title is None or args.alt is None:
            parser.error('--image, --title and --alt are required')
        with launch_lock(STATE):
            publisher = Publisher(args.image, args.title, args.alt)
            print(publisher.publish())
        return 0
    except (PublishError, OSError, ValueError, subprocess.SubprocessError) as exc:
        if publisher:
            publisher.save('failed', error=str(exc))
        print(str(exc), file=sys.stderr)
        if publisher:
            print(f'Your upload is saved. Details: {publisher.log_path}', file=sys.stderr)
        return 1


if __name__ == '__main__':
    raise SystemExit(main())
