import io
import unittest
from contextlib import redirect_stdout
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest.mock import Mock, patch

import cv2
import numpy as np

import detect_faces


class DetectFacesTests(unittest.TestCase):
    def _run_with_faces(self, faces):
        with TemporaryDirectory() as temp_dir:
            folder = Path(temp_dir)
            input_path = folder / "input.png"
            model_path = folder / "fake_model.onnx"
            output_path = folder / "output" / "faces.png"

            image = np.full((20, 30, 3), 128, dtype=np.uint8)
            self.assertTrue(cv2.imwrite(str(input_path), image))
            model_path.touch()

            detector = Mock()
            detector.detect.return_value = (None, faces)
            factory = Mock()
            factory.create.return_value = detector
            messages = io.StringIO()

            with (
                patch.object(detect_faces, "INPUT_PATH", input_path),
                patch.object(detect_faces, "MODEL_PATH", model_path),
                patch.object(detect_faces, "OUTPUT_PATH", output_path),
                patch.object(detect_faces.cv2, "FaceDetectorYN", factory),
                redirect_stdout(messages),
            ):
                detect_faces.main()

            factory.create.assert_called_once_with(
                model=str(model_path),
                config="",
                input_size=(30, 20),
                score_threshold=0.9,
                nms_threshold=0.3,
            )
            detector.detect.assert_called_once()
            np.testing.assert_array_equal(
                detector.detect.call_args.args[0], image
            )

            output = cv2.imread(str(output_path), cv2.IMREAD_UNCHANGED)
            self.assertIsNotNone(output)
            np.testing.assert_array_equal(
                cv2.imread(str(input_path), cv2.IMREAD_UNCHANGED), image
            )
            return image, output, messages.getvalue()

    def test_no_faces(self):
        image, output, messages = self._run_with_faces(None)
        np.testing.assert_array_equal(output, image)
        self.assertIn("Faces detected: 0", messages)

    def test_one_face(self):
        faces = np.zeros((1, 15), dtype=np.float32)
        faces[0, :4] = (5, 5, 10, 12)
        faces[0, -1] = 0.99

        image, output, messages = self._run_with_faces(faces)
        expected = image.copy()
        cv2.rectangle(expected, (5, 5), (15, 17), (0, 255, 0), 2)
        np.testing.assert_array_equal(output, expected)
        self.assertIn("Faces detected: 1", messages)


if __name__ == "__main__":
    unittest.main()