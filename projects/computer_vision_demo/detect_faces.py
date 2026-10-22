from pathlib import Path

import cv2

BASE_DIR = Path(__file__).resolve().parent
INPUT_PATH = BASE_DIR / "storage" / "resized.png"
MODEL_PATH = BASE_DIR / "storage" / "models" / "face_detection_yunet_2026may.onnx"
OUTPUT_PATH = BASE_DIR / "storage" / "faces_detected.png"


def main():
    for path in (INPUT_PATH, MODEL_PATH):
        if not path.is_file():
            raise FileNotFoundError(f"Required file not found: {path}")

    image = cv2.imread(str(INPUT_PATH), cv2.IMREAD_COLOR)
    if image is None:
        raise ValueError("OpenCV could not read the input image.")

    height, width = image.shape[:2]
    detector = cv2.FaceDetectorYN.create(
        model=str(MODEL_PATH),
        config="",
        input_size=(width, height),
        score_threshold=0.9,
        nms_threshold=0.3,
    )

    _, faces = detector.detect(image)
    result = image.copy()
    count = 0 if faces is None else len(faces)

    if faces is not None:
        for face in faces:
            x, y, face_width, face_height = map(int, face[:4])
            cv2.rectangle(
                result,
                (x, y),
                (x + face_width, y + face_height),
                (0, 255, 0),
                2,
            )

    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    if not cv2.imwrite(str(OUTPUT_PATH), result):
        raise OSError(f"Could not save: {OUTPUT_PATH}")

    print(f"Faces detected: {count}")
    print(f"Saved: {OUTPUT_PATH}")


if __name__ == "__main__":
    main()