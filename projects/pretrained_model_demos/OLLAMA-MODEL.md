# Observed Ollama model artifact

Recorded October 23, 2026, from the learner's completed download and local cache metadata. This is a model identity record, not model weights, a prediction-quality certificate or an immutable pin used by the client.

- Runtime observed: Ollama 0.40.9.
- Requested local tag: `qwen3:4b`.
- Model family/type: Qwen3, approximately four billion learned parameters.
- Quantization recorded in the local configuration: `Q4_K_M`.
- Model layer size: 2,497,280,480 bytes (about 2.5 GB).
- Source: [Ollama model listing](https://ollama.com/library/qwen3:4b); [Qwen model announcement](https://qwenlm.github.io/blog/qwen3/).

## Observed SHA256 identifiers

| Artifact | SHA256 |
| --- | --- |
| Local manifest envelope | `31d9857b5705086d352d4d6db04e86c5d0f6a2b5d59a4dc7ce5cdb271ccf9141` |
| Original manifest referenced by that envelope | `359d7dd4bcdab3d86b87d73ac27966f4dbb9f5efdfcc75d34a8764a09474fae7` |
| Model-weight layer listed in the manifest | `3e4cb14174460404e7a233e531675303b2fbf7749c02f91864fe311ab6344e4f` |
| Configuration layer listed in the manifest | `e18a783aae5525fd2852fc94c985541a77e791e034abc2d3056474d59de336fc` |
| Chat-template layer listed in the manifest | `2d54db2b9bb29ce7db54fea63a891f5859603813c555b1f88b5e0994652897f9` |

The local manifest file was independently hashed. The learner's `ollama pull` output reported digest verification and success; the weight-layer digest above was read from the manifest, not independently recalculated over the whole weights file. The envelope and original manifest have different hashes because they are different metadata artifacts; do not replace one with the other.

The observed chat template opens an assistant thinking section. This may contribute to the unwanted planning-like text seen despite `think=false`, but the full server/parser cause was not established. No cached template or model was modified to hide that behavior.

## Reproduction boundary

`ollama_demo.py` requests the tag `qwen3:4b`. A later pull can resolve to changed files, and an identical artifact does not guarantee identical sampled output. The Python dependency snapshot does not install or pin the Ollama application or its model cache.

The four-file `models.sha256` manifest in this project covers only the local Hugging Face sentiment files under `storage`. It does not cover the separate Ollama cache. Keep both models' weights, private Ollama configuration and any credentials out of this repository.
