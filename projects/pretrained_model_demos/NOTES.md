# Sentiment demo — learning notes

## What did we build?

A program that reads six English sentences and predicts whether each sounds positive or negative. Other people already trained the model. We downloaded their learned settings and used them; our script does not teach it anything new.

Hugging Face Hub is where the files come from. Transformers helps load and prepare the model. PyTorch performs its calculations. Installing the libraries is like getting the tools; downloading weights supplies the trained model's learned numbers.

## What happens to a sentence?

The tokenizer splits text into pieces and looks up a fixed number for each piece. For our tokenizer, `I really enjoyed this movie.` becomes:

```text
[CLS]  i     really  enjoyed  this  movie  .     [SEP]
101    1045  2428    5632     2023  3185   1012  102
```

It lowercases text and adds boundary markers. A piece can be a word, punctuation or part of a word. For example, `unaffordable` splits into `una`, `##ff`, `##ord`, `##able`; `##` marks continuation, not literal characters in the input.

An ID is like a dictionary entry number. `5632` identifies `enjoyed`; it is not a positive score or a measurement of happiness. The network looks up learned vectors for the IDs, processes them together in context, and calculates two raw class scores. Learned weights determine these calculations; they are not a handwritten list of positive/negative words.

## Where does the prediction run?

```python
logits = model(**inputs).logits
```

This is the actual prediction call. `inputs` holds the prepared text data; `**inputs` passes its named fields into the model. The call processes all six sentences together and returns two raw scores per sentence, called logits.

The steps around it have different jobs:

- `from_pretrained(...)` loads the saved tokenizer or trained network; it does not train it.
- `tokenizer(...)` prepares numbers for the model. Padding makes the sentences' arrays equally long; an attention mask distinguishes text from padding.
- `model.eval()` switches off training-only behavior such as dropout. `torch.inference_mode()` avoids tracking calculations for training gradients. Neither measures accuracy.
- `softmax(...)` converts the two raw scores into scores that sum to one. `argmax()` chooses the bigger one; `id2label` supplies its name.
- The final loop prints already-calculated results. It does not run another prediction for each sentence.

## Why the 512 limit and input checks?

This checkpoint can read at most 512 token positions, including special markers. That means pieces, not words or characters. In the length experiment, a repeated sentence produced 752 tokens. Truncation kept 512 and cut the overflow; it did not summarize the text, change the original string or retrain the model. We only counted/tokenized that long example, not predicted it.

The final demo deliberately refuses blank or overlong text. `validate_texts` checks each sentence and raises a clear error if it fails. That stops the whole batch before the model's prediction call. Although the later tokenizer still has truncation enabled as a backstop, the input check runs first and rejects overflow instead of silently losing part of a review.

Moving those checks into a function changed organization, not predictions: tests can call just that function without loading weights. The current script still loads weights before validating, so an expected input error may follow a loading progress bar.

## What do the four tests prove?

The tests give the check function a pretend tokenizer whose answer we control: 10, 512 or 513 token IDs. This isolates the rule we want to check. Short text and exactly 512 pass; blank/whitespace and 513 fail. Blank text is rejected before even calling the tokenizer.

`Mock` is that pretend dependency, not another AI model. `assertRaises` checks that the intended error happens. The `if __name__ == "__main__"` guard prevents the demo from running when a test imports the helper.

Passing tests means those Python rules behaved as expected. It does not mean that real sentences always split correctly, the network is accurate, or the native runtime works for every input shape.

## How should we interpret the results?

The ordinary positive/negative and “not” examples gave sensible outputs. But a neutral fact was called negative with a high score, and a likely sarcastic complaint was called positive. The model only has two labels and can be confidently wrong.

Six examples help us see behavior; they are not a representative evaluation dataset. A model score such as `0.9999` is not measured accuracy or a guarantee of truth. The current environment also has an unresolved single-sentence native inference crash; successful multi-sentence batches do not erase that limitation.

## What makes a run reproducible?

The model revision identifies the selected upstream snapshot. `models.sha256` checks all four local files. `requirements.lock.txt` records installed Python package versions, while `requirements.txt` lists direct dependencies constrained by that snapshot. These are different from model weights.

The four downloaded files hold learned parameters (`model.safetensors`), network/label settings (`config.json`), token vocabulary (`vocab.txt`) and tokenization settings (`tokenizer_config.json`). Offline loading uses them locally without a hosted prediction request. File identity, dependency compatibility, successful execution and prediction quality are separate checks.

## Interview recap

“I integrated a pinned pretrained English sentiment model for local batch inference. I prepared text with its tokenizer, ran the network, interpreted its two class scores and tested input validation separately. I did not train it, and I documented where the model or runtime could fail instead of treating a high score as guaranteed accuracy.”
