import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
MODEL_DIR = BASE_DIR / "storage" / "models" / "sentiment"

os.environ["HF_HOME"] = str(BASE_DIR / "storage" / "huggingface")
os.environ["HF_HUB_OFFLINE"] = "1"

import torch
from transformers import AutoTokenizer, AutoModelForSequenceClassification

def validate_texts(texts, tokenizer):
    for number, text in enumerate(texts, start=1):
        if not text.strip():
            raise ValueError(f"Text {number} is empty.")

        token_ids = tokenizer(
            text, truncation=False, verbose=False
        )["input_ids"]

        count = len(token_ids)

        if count > 512:
            raise ValueError(
                f"Text {number} has {count} tokens; maximum is 512."
            )

def main():
    tokenizer = AutoTokenizer.from_pretrained(
        MODEL_DIR,
        local_files_only=True,
        trust_remote_code=False,
    )

    model = AutoModelForSequenceClassification.from_pretrained(
        MODEL_DIR,
        local_files_only=True,
        trust_remote_code=False,
        use_safetensors=True,
    )
    model.eval()

    texts = [
        "I enjoyed this movie.",
        "I did not enjoy this movie.",
        "This movie was bad.",
        "This movie was not bad.",
        "The movie lasts two hours.",
        "Great, another three-hour delay.",
    ]

    validate_texts(texts, tokenizer)

    inputs = tokenizer(
        texts,
        padding=True,
        truncation=True,
        max_length=512,
        return_tensors="pt",
    )

    with torch.inference_mode():
        logits = model(**inputs).logits
        probabilities = torch.softmax(logits, dim=-1)

    for text, scores in zip(texts, probabilities):
        label_id = scores.argmax().item()
        label = model.config.id2label[label_id]
        score = scores[label_id].item()

        print(f"Text: {text}")
        print(f"Prediction: {label}")
        print(f"Model score: {score:.4f}\n")


if __name__ == "__main__":
    main()