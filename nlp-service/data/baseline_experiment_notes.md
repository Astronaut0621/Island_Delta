# Campus Emotion Baseline Notes

## Dataset v1

- File: `data/campus_emotion_samples_v1.csv`
- Rows: 200
- Labels: 10
- Rows per label: 20
- Source: `ai_generated`

TF-IDF char n-gram + LogisticRegression:

```text
train_size: 160
test_size: 40
train_accuracy: 1.0000
test_accuracy: 0.3250
cv_accuracy_mean: 0.3700
cv_accuracy_scores: 0.3250,0.3750,0.3500,0.4000,0.4000
```

Interpretation: 20 rows per label is too small. The baseline memorizes training data but generalizes poorly.

## Dataset v2

- File: `data/campus_emotion_samples_v2.csv`
- Rows: 500
- Labels: 10
- Rows per label: 50
- Source: `ai_generated`

TF-IDF char n-gram + LogisticRegression:

```text
train_size: 400
test_size: 100
train_accuracy: 1.0000
test_accuracy: 0.6200
cv_accuracy_mean: 0.5860
cv_accuracy_scores: 0.5400,0.5900,0.5900,0.5800,0.6300
```

Interpretation: expanding to 50 rows per label helps substantially. The dataset is usable for pipeline testing, but the score is still not good enough to treat the model as reliable. Manual review and non-AI samples are still needed.

## Current Recommendation

1. Use `v2` for training-script development and API integration tests.
2. Ask teammates to add or replace rows with manually collected campus-style expressions.
3. Keep the same CSV schema: `id,text,emotion_type,source`.
4. Re-run:

```powershell
python scripts\validate_emotion_dataset.py data\campus_emotion_samples_v2.csv
python scripts\run_baseline_emotion_classifier.py data\campus_emotion_samples_v2.csv --test-size 0.2 --seed 42
```

5. Do not evaluate final quality only on AI-generated data. It gives a useful pipeline signal but can overstate real-world performance.

## MLP Baseline On Dataset v2

TF-IDF char n-gram + MLPClassifier:

```text
train_size: 400
test_size: 100
train_accuracy: 0.9400
test_accuracy: 0.5300
cv_accuracy_mean: 0.5180
cv_accuracy_scores: 0.4700,0.5000,0.6100,0.4700,0.5400
```

Interpretation: this non-linear neural baseline did not beat LogisticRegression on the current small dataset. More complex models are not automatically better when the training set is small and synthetic. A pretrained Chinese language model may still improve results, but it needs a working PaddleNLP or PyTorch/Transformers environment.
