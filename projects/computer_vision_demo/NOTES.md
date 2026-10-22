# Computer vision learning notes

## Pixels, dimensions and files

An OpenCV color image is a NumPy array shaped `(height, width, channels)`. The resize argument instead uses `(width, height)`. Our script halves each dimension with a minimum of one pixel and uses `INTER_AREA` for downsampling. Grayscale is calculated from the original image and has one intensity channel.

Resizing changes the pixel grid, not camera framing. VS Code's fit-to-window preview can make different resolutions look equally large; compare actual dimensions or the same zoom. File size also depends on compression: a smaller PNG may occupy more bytes than the source JPEG. Saving outputs under new names preserves the input.

## Detection versus verification

Detection asks **where are the faces?** The standalone YuNet model returns boxes, landmarks and detection scores. Our code reads the first four box values `(x, y, width, height)`, draws the rectangle ending at `(x + width, y + height)`, and handles a `None` result as zero faces. Its score cutoff `0.9` is a detector setting, not the later face-comparison cutoff.

Verification asks **do these two face images appear to represent the same person?** DeepFace coordinates detection, alignment, preprocessing and comparison. In our verification script its OpenCV/Haar detector is separate from the earlier YuNet demo. Alignment uses landmarks to reduce orientation variation; it does not fix every pose or lighting condition.

ArcFace takes each prepared face image and produces a **512-number embedding** directly. There is no preliminary DeepFace identity vector that ArcFace converts again. The coordinates are learned patterns, not named measurements such as nose width. Both photos must use a compatible model and preprocessing. We run a pretrained model for inference; we did not train it.

## Distance and the decision

Cosine distance compares embedding directions: lower means closer. Cosine similarity has the opposite direction. DeepFace returns the comparison result; our wrapper displays it.

The installed ArcFace/cosine default is `0.68`, not a universal cutoff. As an illustrative example, distance `0.20` is accepted under that cutoff and `0.90` is rejected. Neither value is a confidence percentage. A lower cutoff is stricter, generally reducing false accepts while increasing false rejects; a higher cutoff is more permissive. A real application needs representative labeled pairs, an error-rate target and separate evaluation. One successful pair cannot calibrate it.

This is pairwise verification, not a person-identification gallery or an access-control system. No liveness checks or access permissions were implemented. Embeddings are sensitive biometric data, not encryption or password hashes; this script does not print or persist them.

## Application tests are a different question

We ask **does our Python code behave correctly under these conditions?** Three preprocessing tests check the output dimensions/channels, unchanged input and rejection of missing/invalid files. Two detector tests supply no-face/one-box replies and check counting/drawing with real OpenCV. Three comparison tests check supplied match/non-match replies, call settings and early rejection of each missing required file.

Mocks provide controlled model replies so expected application behavior is known. They do not prove that an AI model recognizes a face correctly. Temporary directories, patched paths and restored process/module settings keep tests independent of private photos, model downloads and each other. `assertRaises` passes when the expected error occurs. `subTest` checks several cases inside one test method; eight methods is not an eight-photo accuracy score.

## Reproducibility and debugging

File-relative paths let scripts locate assets regardless of the terminal's launch directory. Settings select the local cache, ONNX engine and CPU before DeepFace is imported. Required-file checks make missing assets explicit; the checksum manifest helps detect incomplete or changed downloads.

The dependency snapshot records versions; it does not contain model weights or prove a fresh installation. Only one OpenCV distribution should provide `cv2`. An actual DeepFace import exposed an undeclared Werkzeug dependency even though `pip check` passed: package metadata checks cannot replace imports, runtime checks and application tests. Werkzeug is therefore explicit in the direct requirements.

**Interview summary:** “I built local image preprocessing, pretrained face detection and pairwise embedding comparison. I separated detection from recognition, interpreted model-specific distance thresholds, kept personal data local, and added eight isolated application tests. I did not train the models or establish production biometric accuracy.”
