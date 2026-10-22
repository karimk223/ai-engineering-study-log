# Computer vision demo

A local learning exercise in image processing, face detection and pairwise face verification. The models are pretrained; this project does not train a detector or recognition network.

| Script | Input | Result |
| --- | --- | --- |
| `process_image.py` | `private_data/input.jpg` | Half-width/half-height `storage/resized.png` and original-size `storage/grayscale.png` |
| `detect_faces.py` | `storage/resized.png` | YuNet face count and green boxes in `storage/faces_detected.png` |
| `compare_faces.py` | The original `input.jpg` and `second.jpg` | ArcFace embedding dimension, cosine distance, threshold and predicted match |

The standalone detector uses YuNet. DeepFace's separate `opencv` detector uses the face/eye Haar XML files below; it does not automatically reuse the YuNet result.

## Setup

Run commands from this project's directory. The existing environment was verified with Python 3.12.13 on Apple Silicon macOS, 26 recorded packages and ONNX Runtime CPU inference. Other platforms and a separate fresh dependency installation have not been validated. If the working environment already exists, activate it and skip installation.

```bash
cd projects/computer_vision_demo
python3.12 -m venv .venv
source .venv/bin/activate
python -m pip install --only-binary=:all: --timeout 120 --retries 10 -r requirements.txt
python -m pip check
```

The `cd` above assumes you start at the repository root. `requirements.txt` selects direct dependencies and constrains versions through `requirements.lock.txt`. Keep only `opencv-contrib-python-headless` in this environment; the other OpenCV distributions share the same `cv2` namespace. Werkzeug is explicit because this DeepFace release imports it without declaring it as a base dependency.

## Offline application tests

```bash
python -m unittest discover -v
```

Expected: **8 test methods pass**. They use synthetic images, temporary files and controlled model replies; no downloaded models, personal photographs, API keys or live provider calls are needed. The missing-file method additionally checks five subcases, not five separately counted test methods. These tests check application behavior, not real-model accuracy.

## Prepare local inputs and models

This section is for recreating the demo; do not redownload assets that are already present and checksum-valid.

```bash
mkdir -p private_data storage/models storage/.deepface/weights
```

Place two different, upright, clear photographs you own or have permission to use at `private_data/input.jpg` and `private_data/second.jpg`. Use one face per photo. Keep them local; no sample personal photos are distributed with this repository.

Download the following upstream artifacts into the exact paths shown. Use the binary YuNet download, not a Git LFS pointer or a saved HTML page.

| Artifact / upstream download | Local destination |
| --- | --- |
| [YuNet 2026may ONNX](https://media.githubusercontent.com/media/opencv/opencv_zoo/main/models/face_detection_yunet/face_detection_yunet_2026may.onnx) | `storage/models/face_detection_yunet_2026may.onnx` |
| [ArcFace ONNX, DeepFace Models v1.0](https://github.com/serengil/deepface_models/releases/download/v1.0/arcface_weights.onnx) | `storage/.deepface/weights/arcface_weights.onnx` |
| [Frontal-face Haar XML, OpenCV 4.9.0](https://raw.githubusercontent.com/opencv/opencv/4.9.0/data/haarcascades/haarcascade_frontalface_default.xml) | `storage/.deepface/weights/haarcascade_frontalface_default.xml` |
| [Eye Haar XML, OpenCV 4.9.0](https://raw.githubusercontent.com/opencv/opencv/4.9.0/data/haarcascades/haarcascade_eye.xml) | `storage/.deepface/weights/haarcascade_eye.xml` |

ArcFace is the large download (136,588,094 bytes); installing the Python library does not include these recognition weights. For an interrupted download, curl's `--continue-at -` can resume a saved partial file if the server supports it. Keep incomplete files under a `.part` name; do not run inference with them.

Verify complete downloads from this project directory:

```bash
shasum -a 256 -c models.sha256
```

All four entries must report `OK`. The manifest records the artifacts used in this exercise; ArcFace's digest also matches the [published release asset digest](https://github.com/serengil/deepface_models/releases/expanded_assets/v1.0). If a file was saved as `.part`, first calculate its hash and compare with the corresponding manifest entry; only rename it to the final filename after a successful match. Stop on a mismatch rather than replacing the expected digest blindly.

The YuNet source is [OpenCV Zoo](https://github.com/opencv/opencv_zoo/tree/main/models/face_detection_yunet); recognition weights are distributed by [DeepFace Models](https://github.com/serengil/deepface_models). Review the applicable upstream code, model and data terms before reuse. This repository does not redistribute the weights or XML files.

## Run the real local demo

```bash
python process_image.py
python detect_faces.py
python compare_faces.py
```

Run in that order: detection depends on the resized output. Comparison independently uses the two original photos, configures the ignored `storage` cache before importing DeepFace, and selects ONNX/CPU. It prints a 512-number embedding dimension, not the biometric vectors themselves. Once the packages and verified assets are cached, no further model download is needed by this workflow.

The installed ArcFace/cosine default cutoff is `0.68`; `distance <= threshold` yields a predicted match. Distance and threshold are not confidence percentages. See [learning notes](NOTES.md) for interpretation.

## Evidence, privacy and limitations

- Manual local runs completed resizing/grayscale, one-face detection and one two-photo verification. These are sample successes, not a representative accuracy or latency benchmark.
- All eight saved tests pass in the current environment. Clean-file verification uses that same environment, not a separate dependency installation.
- `.venv/`, `private_data/` and `storage/` are ignored. Generated images can still contain faces; keep them out of Git along with originals, weights and downloaded wheels. Git ignore rules are not encryption or access control.
- No authentication, gallery search, liveness/anti-spoofing, demographic analysis or security-door authorization is implemented. The wrapper does not enforce a multi-face rejection policy; keep one face per input.
- No threshold was calibrated on a labeled evaluation set. A predicted match is not proof of identity. Lighting, pose, image quality and population differences can affect performance.
- The known OpenCV target/backend warning appeared during a successful manual detection. An exception or missing output still needs investigation; do not change the threshold merely to force a desired answer.
