"""Release integrity failures must stop publication, including forged manifests."""

import hashlib
import json
from pathlib import Path
import tempfile
import unittest

from check_bird_to_bird import FIXED_FILES, allowed_payload_path, check_release


class BirdToBirdReleaseTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.directory = Path(self.temp.name) / "release"
        self.directory.mkdir()
        self.pin = Path(self.temp.name) / "expected.sha256"
        self.manifest = {"schemaVersion": 1, "generator": "bird-to-bird-local-release-v1", "files": []}
        for name in sorted(FIXED_FILES):
            self.add_file(name, f"fixture: {name}\n".encode())
        self.write_manifest(update_pin=True)

    def add_file(self, name, payload):
        path = self.directory / name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(payload)
        self.manifest["files"].append({"path": name, "bytes": len(payload), "sha256": hashlib.sha256(payload).hexdigest()})

    def write_manifest(self, update_pin=False):
        data = (json.dumps(self.manifest, sort_keys=True) + "\n").encode()
        (self.directory / "manifest.json").write_bytes(data)
        if update_pin:
            self.pin.write_text(hashlib.sha256(data).hexdigest() + "\n")

    def check(self):
        return check_release(self.directory, self.pin)

    def test_complete_pinned_candidate_passes(self):
        self.assertEqual(self.check()["files"], len(FIXED_FILES) + 1)
        self.assertTrue(self.check()["verified"])

    def test_changed_file_fails_even_at_the_same_size(self):
        path = self.directory / "daily/app.js"
        path.write_bytes(b"x" * path.stat().st_size)
        with self.assertRaisesRegex(ValueError, "File hash differs"):
            self.check()

    def test_missing_and_unlisted_files_fail(self):
        path = self.directory / "daily/app.js"
        original = path.read_bytes()
        path.unlink()
        with self.assertRaisesRegex(ValueError, "file set differs"):
            self.check()
        path.write_bytes(original)
        (self.directory / "daily/assets/birds").mkdir(parents=True)
        (self.directory / "daily/assets/birds/avibase-12345678.jpg").write_bytes(b"unlisted")
        with self.assertRaisesRegex(ValueError, "file set differs"):
            self.check()

    def test_forged_payload_hash_needs_separate_pin_update(self):
        payload = b"unaudited replacement"
        (self.directory / "daily/app.js").write_bytes(payload)
        row = next(row for row in self.manifest["files"] if row["path"] == "daily/app.js")
        row.update(bytes=len(payload), sha256=hashlib.sha256(payload).hexdigest())
        self.write_manifest()
        with self.assertRaisesRegex(ValueError, "approved SHA-256 pin"):
            self.check()

    def test_private_path_fails_even_with_a_new_matching_pin(self):
        self.add_file("daily/note-review.json", b"private evidence")
        self.write_manifest(update_pin=True)
        with self.assertRaisesRegex(ValueError, "Disallowed release path"):
            self.check()

    def test_symlinked_file_and_directory_fail(self):
        path = self.directory / "daily/app.js"
        path.unlink()
        path.symlink_to(self.directory / "daily/boot.js")
        with self.assertRaisesRegex(ValueError, "Symlink"):
            self.check()
        path.unlink()
        (self.directory / "linked").symlink_to(self.directory / "daily", target_is_directory=True)
        with self.assertRaisesRegex(ValueError, "Symlink"):
            self.check()

    def test_manifest_cannot_omit_required_files(self):
        self.manifest["files"] = [row for row in self.manifest["files"] if row["path"] != "daily/boot.js"]
        (self.directory / "daily/boot.js").unlink()
        self.write_manifest(update_pin=True)
        with self.assertRaisesRegex(ValueError, "omits required runtime"):
            self.check()

    def test_only_the_explicit_public_paths_are_accepted(self):
        for name in ["../secret", "/daily/app.js", "daily//app.js", "daily/./app.js", "daily\\app.js", "route/corpus/source.json", ".git/config", ".qa/report.json", "README.md", "daily/release-lock.json", "daily/assets/birds/source.txt"]:
            with self.subTest(path=name):
                self.assertFalse(allowed_payload_path(name))
        for name in ["daily/assets/birds/avibase-01BFAE61.jpg", "daily/assets/birds/avibase-01BFAE61-thumb.png", "route/assets/name-notes/common-gull.jpg"]:
            self.assertTrue(allowed_payload_path(name))


if __name__ == "__main__":
    unittest.main()
