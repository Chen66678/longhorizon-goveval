from __future__ import annotations

import hashlib
import json
import sys
import unittest
from pathlib import Path

TOOLS = Path(__file__).resolve().parents[1] / "tools"
sys.path.insert(0, str(TOOLS))
from build_manifest import build_manifest, canonical_manifest_bytes  # noqa: E402


class ManifestTests(unittest.TestCase):
    def test_canonical_digest_is_self_excluding_payload_digest(self) -> None:
        manifest = build_manifest()
        declared = manifest.pop("canonical_manifest_sha256")
        self.assertEqual(declared, hashlib.sha256(canonical_manifest_bytes(manifest)).hexdigest())

    def test_canonical_digest_does_not_depend_on_pretty_output_formatting(self) -> None:
        manifest = build_manifest()
        declared = manifest["canonical_manifest_sha256"]
        pretty = json.dumps(manifest, indent=2, sort_keys=True) + "\n"
        compact = json.dumps(manifest, sort_keys=False, separators=(",", ":"))
        self.assertNotEqual(pretty.encode("utf-8"), compact.encode("utf-8"))
        payload = {key: value for key, value in manifest.items() if key != "canonical_manifest_sha256"}
        self.assertEqual(declared, hashlib.sha256(canonical_manifest_bytes(payload)).hexdigest())

    def test_manifest_file_paths_are_sorted_unique_and_relative(self) -> None:
        manifest = build_manifest()
        paths = [entry["path"] for entry in manifest["files"]]
        self.assertEqual(paths, sorted(paths))
        self.assertEqual(len(paths), len(set(paths)))
        self.assertTrue(all(not path.startswith("/") and ".." not in Path(path).parts for path in paths))


if __name__ == "__main__":
    unittest.main()
