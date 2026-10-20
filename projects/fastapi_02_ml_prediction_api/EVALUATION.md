# Ticket classifier — evaluation

## Frozen 11-category model

Model version: ticket-router-full-v1. Pipeline: TfidfVectorizer(ngram_range=(1, 2), min_df=2), then LogisticRegression(max_iter=1000). Only instruction text is input; category is the target. Vocabulary/IDF/classifier fitting uses the 16,991 training messages only.

The original 24,274 cleaned messages were split with stratified seed 42: training 16,991, validation 3,641, final test 3,642. Normalized exact duplicates do not cross splits. Similar generated wording/templates can still occur across sets.

| Evaluation | Method | Accuracy | Macro F1 | Incorrect / total |
| --- | --- | ---: | ---: | ---: |
| Validation | Always ACCOUNT baseline | 0.2208184565 | 0.0328867982 | 2,837 / 3,641 |
| Validation | TF-IDF + logistic regression | 0.9986267509 | 0.9987258403 | 5 / 3,641 |
| Final test | Always ACCOUNT baseline | 0.2207578254 | — | 2,838 / 3,642 |
| Final test | TF-IDF + logistic regression | 0.9969796815 | 0.9974064338 | 11 / 3,642 |

Karim ran the final-test/save/reload block on October 20, 2026. His screenshot and independent read-only evaluation of his own saved model agree: 3,631 final-test labels match, 11 disagree. Weighted final-test F1: 0.9969795596246098.

Final-test disagreements by source label -> prediction: CONTACT -> ACCOUNT (1); ORDER -> ACCOUNT (1), REFUND (1), SHIPPING (1); PAYMENT -> ACCOUNT (2), DELIVERY (1); SHIPPING -> ACCOUNT (3); SUBSCRIPTION -> ACCOUNT (1). These results are recorded, not used to retune this frozen model.

## Saved artifact

- Path: artifacts/ticket_router_full_v1.joblib.
- Size: 532,860 bytes.
- SHA256: ea4ff4b7a1edb791715952cadb8ac1ebd213b058e27ccda17edd338d5a7dfe29.
- Bundle keys: model_version, pipeline, categories, sklearn_version.
- Version: ticket-router-full-v1; scikit-learn: 1.9.1.
- Categories: ACCOUNT, CANCEL, CONTACT, DELIVERY, FEEDBACK, INVOICE, ORDER, PAYMENT, REFUND, SHIPPING, SUBSCRIPTION.
- Karim's reload assertion passes; the independently loaded model reproduces the reported final-test results. Artifact is ignored by Git.

The cleanup preserved the model settings and saved artifact. Preparation now reads the raw source directly instead of depending on the retired OTHER experiment. Verification details are recorded in the study log.

## Limitations and paused research

The [Bitext corpus](https://huggingface.co/datasets/bitext/Bitext-customer-support-llm-chatbot-training-dataset) is hybrid synthetic. These are dataset scores, not measured production accuracy on real customer messages. Supported fresh-wording probes exposed errors, including a natural card-charged-twice message predicted as ACCOUNT. A model score is not a calibrated probability that its answer is correct.

The baseline always predicts one of its known labels. It does not reliably identify unrelated, ambiguous or multiple-request input. A 0.6 score threshold and a separately trained admission gate did not establish reliable rejection. They are not integrated into this classifier API milestone. Earlier three-class/OTHER/gate code, detailed comparison records and diagnostic training-script snapshot were preserved in the local learning archive, outside the active project.

Karim explicitly paused this detour and declined larger-model downloads. Continue model serving/logging/tests without claiming rejection is solved or changing the frozen model in response to final-test scores. Representative real-customer and independent-template evaluation remain future work, not prerequisites for this learning milestone.
