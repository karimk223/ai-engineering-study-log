import io
import unittest
from contextlib import redirect_stdout
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest.mock import patch

import cv2
import numpy as np

import process_image


class ProcessImageTests(unittest.TestCase):
    def test_resize_and_grayscale(self):
        with TemporaryDirectory() as temp_dir:
            folder = Path(temp_dir)
            input_path = folder / "input.png"
            output_dir = folder / "output"

            image = np.full((8, 10, 3), 128, dtype=np.uint8)
            self.assertTrue(cv2.imwrite(str(input_path), image))

            with (
                patch.object(process_image, "INPUT_PATH", input_path),
                patch.object(process_image, "OUTPUT_DIR", output_dir),
                redirect_stdout(io.StringIO()),
            ):
                process_image.main()

            resized = cv2.imread(
                str(output_dir / "resized.png"), cv2.IMREAD_UNCHANGED
            )
            grayscale = cv2.imread(
                str(output_dir / "grayscale.png"), cv2.IMREAD_UNCHANGED
            )

            self.assertIsNotNone(resized)
            self.assertIsNotNone(grayscale)
            self.assertEqual(resized.shape, (4, 5, 3))
            self.assertEqual(grayscale.shape, (8, 10))

            original = cv2.imread(str(input_path), cv2.IMREAD_UNCHANGED)
            np.testing.assert_array_equal(original, image)

    def test_missing_input(self):
        with TemporaryDirectory() as temp_dir:
            folder = Path(temp_dir)
            input_path = folder / "missing.jpg"
            output_dir = folder / "output"

            with (
                patch.object(process_image, "INPUT_PATH", input_path),
                patch.object(process_image, "OUTPUT_DIR", output_dir),
                self.assertRaises(FileNotFoundError),
            ):
                process_image.main()

            self.assertFalse(output_dir.exists())

    def test_unreadable_input(self):
        with TemporaryDirectory() as temp_dir:
            folder = Path(temp_dir)
            input_path = folder / "broken.jpg"
            output_dir = folder / "output"
            input_path.write_bytes(b"not an image")

            with (
                patch.object(process_image, "INPUT_PATH", input_path),
                patch.object(process_image, "OUTPUT_DIR", output_dir),
                self.assertRaises(ValueError),
            ):
                process_image.main()

            self.assertFalse(output_dir.exists())


if __name__ == "__main__":
    unittest.main()