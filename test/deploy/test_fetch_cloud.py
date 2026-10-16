import importlib.util
from pathlib import Path
import tempfile
import unittest


SCRIPT = Path(__file__).resolve().parents[2] / "docker" / "kin-kvm" / "fetch-cloud.py"
SPEC = importlib.util.spec_from_file_location("fetch_cloud", SCRIPT)
fetch_cloud = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(fetch_cloud)


class SourceValidationTests(unittest.TestCase):
    def test_accepts_regular_image_sized_file(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "cloud.img"
            with path.open("wb") as image:
                image.truncate(10_000_000)
            self.assertEqual(fetch_cloud.validate_source(str(path)), str(path))

    def test_rejects_directory(self):
        with tempfile.TemporaryDirectory() as directory:
            with self.assertRaisesRegex(SystemExit, "regular, non-symlink"):
                fetch_cloud.validate_source(directory)

    def test_rejects_symlink(self):
        with tempfile.TemporaryDirectory() as directory:
            target = Path(directory) / "target"
            target.write_bytes(b"image")
            link = Path(directory) / "cloud.img"
            try:
                link.symlink_to(target)
            except (OSError, NotImplementedError):
                self.skipTest("symlinks are unavailable on this platform")
            with self.assertRaisesRegex(SystemExit, "regular, non-symlink"):
                fetch_cloud.validate_source(str(link))

    def test_rejects_small_file(self):
        with tempfile.NamedTemporaryFile() as image:
            with self.assertRaisesRegex(SystemExit, "too small"):
                fetch_cloud.validate_source(image.name)


if __name__ == "__main__":
    unittest.main()
