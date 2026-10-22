from pathlib import Path

import cv2

BASE_DIR = Path(__file__).resolve().parent
INPUT_PATH = BASE_DIR / "private_data" / "input.jpg"
OUTPUT_DIR = BASE_DIR / "storage"


def main():
    if not INPUT_PATH.is_file():
        raise FileNotFoundError(f"Image not found: {INPUT_PATH}")

    image = cv2.imread(str(INPUT_PATH), cv2.IMREAD_COLOR)
    if image is None:
        raise ValueError("OpenCV could not read the image. Use a valid JPG photo.")

    height, width, channels = image.shape
    print(f"Original: width={width}, height={height}, channels={channels}")

    new_size = (max(1, width // 2), max(1, height // 2))
    resized = cv2.resize(image, new_size, interpolation=cv2.INTER_AREA)
    grayscale = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    for filename, result in [
        ("resized.png", resized),
        ("grayscale.png", grayscale),
    ]:
        output_path = OUTPUT_DIR / filename
        if not cv2.imwrite(str(output_path), result):
            raise OSError(f"Could not save: {output_path}")
        print(f"Saved {output_path.name}: shape={result.shape}")


if __name__ == "__main__":
    main()