import io
import os
import sys
import unittest
from contextlib import redirect_stdout
from pathlib import Path
from tempfile import TemporaryDirectory
from types import ModuleType
from unittest.mock import Mock, patch

import compare_faces


class CompareFacesTests(unittest.TestCase):
    def setUp(self):
        temp = TemporaryDirectory()
        self.addCleanup(temp.cleanup)
        self.base = Path(temp.name)
        self.weights = self.base / "storage" / ".deepface" / "weights"
        self.required = [
            self.base / "private_data" / "input.jpg",
            self.base / "private_data" / "second.jpg",
            self.weights / "arcface_weights.onnx",
            self.weights / "haarcascade_frontalface_default.xml",
            self.weights / "haarcascade_eye.xml",
        ]
        for path in self.required:
            path.parent.mkdir(parents=True, exist_ok=True)
            path.touch()

        self.api = Mock()
        self.api.build_model.return_value.output_shape = 512
        self.module = ModuleType("deepface")
        self.module.DeepFace = self.api

    def _check_result(self, verified, distance):
        def fake_verify(**kwargs):
            self.assertEqual(
                os.environ["DEEPFACE_HOME"], str(self.base / "storage")
            )
            self.assertEqual(os.environ["DEEPFACE_BACKEND_ENGINE"], "onnx")
            self.assertEqual(os.environ["DEEPFACE_ONNX_PROVIDERS"], "cpu")
            return {
                "model": "ArcFace",
                "distance": distance,
                "threshold": 0.68,
                "verified": verified,
            }

        self.api.verify.side_effect = fake_verify
        messages = io.StringIO()

        with (
            patch.object(compare_faces, "BASE_DIR", self.base),
            patch.object(compare_faces, "WEIGHTS_DIR", self.weights),
            patch.dict(sys.modules, {"deepface": self.module}),
            patch.dict(os.environ),
            redirect_stdout(messages),
        ):
            compare_faces.main()

        self.api.verify.assert_called_once_with(
            img1_path=str(self.required[0]),
            img2_path=str(self.required[1]),
            model_name="ArcFace",
            detector_backend="opencv",
            distance_metric="cosine",
            enforce_detection=True,
            align=True,
            silent=True,
        )
        self.api.build_model.assert_called_once_with("ArcFace")
        output = messages.getvalue()
        self.assertIn("Model: ArcFace", output)
        self.assertIn("Vector size: 512", output)
        self.assertIn(f"Distance: {distance:.6f}", output)
        self.assertIn("Threshold: 0.68", output)
        self.assertIn(f"Predicted match: {verified}", output)

    def test_reports_match(self):
        self._check_result(True, 0.20)

    def test_reports_nonmatch(self):
        self._check_result(False, 0.90)

    def test_missing_required_files(self):
        for path in self.required:
            with self.subTest(missing=path.name):
                path.unlink()
                try:
                    with (
                        patch.object(compare_faces, "BASE_DIR", self.base),
                        patch.object(compare_faces, "WEIGHTS_DIR", self.weights),
                        patch.dict(sys.modules, {"deepface": self.module}),
                        patch.dict(os.environ),
                        self.assertRaises(FileNotFoundError),
                    ):
                        compare_faces.main()

                    self.api.verify.assert_not_called()
                    self.api.build_model.assert_not_called()
                finally:
                    path.touch()


if __name__ == "__main__":
    unittest.main()
