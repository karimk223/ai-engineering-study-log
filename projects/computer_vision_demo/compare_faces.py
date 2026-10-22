from pathlib import Path
import os

BASE_DIR = Path(__file__).resolve().parent
WEIGHTS_DIR = BASE_DIR / "storage" / ".deepface" / "weights"


def main():
    first_photo = BASE_DIR / "private_data" / "input.jpg"
    second_photo = BASE_DIR / "private_data" / "second.jpg"

    for path in (
        first_photo,
        second_photo,
        WEIGHTS_DIR / "arcface_weights.onnx",
        WEIGHTS_DIR / "haarcascade_frontalface_default.xml",
        WEIGHTS_DIR / "haarcascade_eye.xml",
    ):
        if not path.is_file():
            raise FileNotFoundError(f"Required file not found: {path}")

    os.environ["DEEPFACE_HOME"] = str(BASE_DIR / "storage")
    os.environ["DEEPFACE_BACKEND_ENGINE"] = "onnx"
    os.environ["DEEPFACE_ONNX_PROVIDERS"] = "cpu"

    from deepface import DeepFace

    result = DeepFace.verify(
        img1_path=str(first_photo),
        img2_path=str(second_photo),
        model_name="ArcFace",
        detector_backend="opencv",
        distance_metric="cosine",
        enforce_detection=True,
        align=True,
        silent=True,
    )

    print("Model:", result["model"])
    print("Vector size:", DeepFace.build_model("ArcFace").output_shape)
    print(f"Distance: {result['distance']:.6f}")
    print("Threshold:", result["threshold"])
    print("Predicted match:", result["verified"])


if __name__ == "__main__":
    main()