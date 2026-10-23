# Pretrained model demos — learning notes

The first sections cover sentiment classification; the Ollama section below covers local text generation. Both use weights trained by others.

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

## Ollama: what did we build?

A small Python program asks a language model running on our Mac a question and prints its reply. The automation-definition question is just a connection test, not a completed automation workflow or agent.

Ollama is the runner; Qwen3:4b is the trained model. Installing Ollama gives the program that can run models. `ollama pull` downloads the model's learned numbers. `ollama run` asks it to generate text. None of these commands retrains it. The 4B name refers to roughly four billion parameters, not words or file size.

Our sentiment model chooses between two labels. Qwen generates a sequence of new tokens. Like the sentiment model it uses learned weights, but its output and task are different.

## Where does the Python question go?

`payload` describes the model, message and settings. `json.dumps(...).encode(...)` prepares JSON bytes; `Request` describes the POST we want to send.

```python
with opener.open(request, timeout=120) as response:
    result = json.load(response)
```

`opener.open` sends the request. `127.0.0.1:11434` is the Ollama service on this computer, not Groq's remote server. `json.load` reads its reply into a Python dictionary. Ollama performs the actual model calculations; our Python client does not directly call a PyTorch network here.

The proxy-free opener talks directly to the fixed local address. `stream=False` requests one complete JSON response instead of a series of small updates. `keep_alive=0` requests releasing model memory afterward; it does not delete the downloaded files. Loading weights into working memory is not another download or training session.

## Context versus output allowance

`num_ctx=2048` is the working window: instructions, question, any history actually sent, formatting and the growing reply use that space. It is not permanent conversation memory or the model's learned knowledge.

`num_predict=256` means at most 256 new generated tokens, including any unwanted planning text. It does not require exactly 256 tokens or 256 words. An answer can stop earlier; hitting the cap can cut it off mid-sentence. The 2,048-token window is not 2,048 input positions plus 256 extra output positions. We chose small limits for this short question, not to make the model more accurate.

The 120-second timeout applies to blocking I/O, not a guaranteed total duration or automatic server cancellation. Limits and completion checks do different jobs.

## Why did the first Python run fail, then a later run pass?

`get_reply` accepts only a normally finished result with nonblank string content. The earlier run did not pass its completion check, but its actual reason/count was not printed. A 256-token cutoff was plausible, not proven.

We added three print statements, which only display information. Running again made a NEW model request; it completed with `done=True`, stop reason `stop` and 246 tokens. The prints did not fix the model or raise its limit. The new error message now includes the stop metadata so a future failure needs less guessing.

## What did the four Ollama tests check?

The tests supply made-up response dictionaries directly to `get_reply`. They check that completed text is returned, unfinished and length-limited replies raise an error, and blank/whitespace/non-string content raises an error. `setUp` gives each test a fresh example dictionary.

For an invalid reply, a passing test means our code correctly refused it. The fake length/256 case does not prove the earlier real request hit that cap. The tests do not ask Qwen anything, test its knowledge, validate every server error or check whether a real generation follows instructions. This is why they finish almost instantly.

## What still needs caution?

Thinking controls did not reliably produce answer-only content in this setup. The successful request still returned planning-like text before the final answer. “Separate thinking field present: False” means no separate field was supplied; it does not mean no planning-like text was generated. We preserve the actual content rather than silently strip tags and claim the problem is fixed.

Local inference uses our own storage, memory and processing, whereas API 3 used Groq's servers. No hosted inference account is needed for this cached model, but the initial download needs internet access. Local is not automatically faster, more private in every deployment, or more accurate; we did not benchmark the different models fairly.

## Local Ollama versus the model through Groq

The terminal is just an interface, not the defining difference. Both are accessible through an API. Our Ollama Python script already calls the local HTTP API; API 3 uses a Python SDK to call Groq's remote API. A terminal, website or Python application could be a client of either. [Ollama API](https://docs.ollama.com/api/introduction), [Groq API](https://console.groq.com/docs/overview)

Keep two choices separate: WHICH model supplies the learned behavior, and WHERE/HOW it runs. Ollama is a runner and Groq is our hosted inference provider; neither name identifies the actual model. Our examples use Qwen3:4b locally and gpt-oss-120b through Groq. Different outputs do not prove that local or hosted inference is inherently smarter. The models, settings, formatting and tasks differ, and we have not performed a fair quality comparison.

The practical tradeoffs in our chosen setups are:

- **Hardware and operation:** the local model uses our Mac's memory, processing and storage, and we install/manage it. Groq operates the remote model infrastructure; our laptop sends requests rather than holding those model weights. Neither arrangement guarantees a particular speed.
- **Connectivity and availability:** our cached local model can answer without an internet connection, but depends on the Mac and local service being available. Groq requests depend on internet connectivity, the provider and account access.
- **Data path:** in this local exercise, prompts go to the service on our Mac. With Groq, prompts are sent to its servers for processing. This describes where computation happens, not a claim about provider retention or automatic security of every local deployment.
- **Usage constraints:** local generation uses our hardware/electricity and capacity rather than a hosted provider's per-request quota. Groq has account/service limits and plan-dependent pricing; the free tier is not unlimited. Exact charges/quotas are separate current-account details, not measured here. Context and output limits can exist in both setups; they are different from a provider's requests/tokens-per-minute quota. [Rate limits](https://console.groq.com/docs/rate-limits)

API 3's fictional order lookup, validation and saved chat records were features of OUR Python application. They were not features that Groq automatically built for us. A local model can also be part of a tool workflow if it supports the required behavior and Python validates/executes approved tools; we have not built or evaluated that local agent yet.

Ollama also offers cloud models. “Local” describes the downloaded Qwen model selected for this exercise, not every possible Ollama use. We did not enable its cloud service. [Ollama cloud](https://docs.ollama.com/cloud)

## Ollama interview recap

“I called a downloaded language model through Ollama's local HTTP API using Python's standard library. I bounded its context/output, checked whether replies ended normally, tested those checks offline and documented unwanted-output behavior. This was local inference, not training, a deployed agent or a representative accuracy evaluation.”
