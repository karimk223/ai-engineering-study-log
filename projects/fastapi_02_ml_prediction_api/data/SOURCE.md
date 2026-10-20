# Training data source

- Provider: Bitext Innovations, 2024.
- Dataset: [Bitext customer-support corpus](https://huggingface.co/datasets/bitext/Bitext-customer-support-llm-chatbot-training-dataset).
- Pinned revision: 430d1a89bd93bd1fa23c16f29dd53e73f0087443.
- File: Bitext_Sample_Customer_Support_Training_Dataset_27K_responses-v11.csv.
- [Pinned download](https://huggingface.co/datasets/bitext/Bitext-customer-support-llm-chatbot-training-dataset/resolve/430d1a89bd93bd1fa23c16f29dd53e73f0087443/Bitext_Sample_Customer_Support_Training_Dataset_27K_responses-v11.csv).
- SHA256: 6f81102b0100b97b8468eb04368033a23206bf1fde9d53500d5806ec1001a434.
- License: [CDLA-Sharing-1.0](https://cdla.dev/sharing-1-0/).
- Provenance: hybrid synthetic generation, as described by the provider.
- Raw location: data/raw/customer_support.csv, excluded from Git.
- Model input: instruction text only. Target: category, retaining all 11 original labels.

## Current reproducible preparation

inspect_data.py verifies the pinned checksum and prints all category counts and examples. Raw source: 26,872 rows.

prepare_data_full.py reads instruction/category directly from that raw CSV. It drops missing/blank messages or labels, strips/collapses message whitespace, checks conflicting original labels using casefolded message keys, and keeps the first normalized duplicate. On this source: zero missing/blank rows, 2,598 duplicates removed, 24,274 unique rows. No dependency on earlier three-category or OTHER experiments remains.

Cleaned counts: ACCOUNT 5,358; CANCEL 941; CONTACT 1,966; DELIVERY 1,645; FEEDBACK 1,990; INVOICE 1,801; ORDER 3,067; PAYMENT 1,986; REFUND 2,577; SHIPPING 1,951; SUBSCRIPTION 992. Output: data/processed/full/support_tickets.csv.

split_data_full.py uses train_test_split with test_size=0.30, random_state=42 and stratify=category, then halves the remainder with test_size=0.50 and the same seed/stratification. Saved sizes: train 16,991; validation 3,641; test 3,642. Every original cleaned pair occurs once, all labels occur in each split, and normalized exact-message keys are disjoint.

Training fits text preprocessing and classifier weights on training only. Validation and final-test results are in [the evaluation record](../EVALUATION.md). Similar generated/paraphrased templates may span splits; no real-customer performance claim follows.

Earlier exploration/source records were retained in the local learning archive. Raw/processed data and the trained artifact are not distributed in Git. Recheck the source hash if replacing the input file, and preserve provider attribution/license when redistributing source or modified data.
