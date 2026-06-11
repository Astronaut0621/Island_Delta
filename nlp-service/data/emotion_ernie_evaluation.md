# Emotion ERNIE Mini Evaluation

## Setup

- Dataset: `data/campus_emotion_samples_v2.csv`
- Model: `models/emotion-ernie-mini/best`
- Split seed: `42`
- Train/dev/test: `400/50/50`
- Labels: 10 dominant emotion classes
- Command:

```powershell
python scripts\evaluate_paddlenlp_emotion_classifier.py --dataset data\campus_emotion_samples_v2.csv --model-dir models\emotion-ernie-mini\best --seed 42
```

## Result

```text
test_accuracy: 0.7000
macro_f1: 0.6886
weighted_f1: 0.6886
```

Per-label report:

```text
              precision    recall  f1-score   support

      lonely     1.0000    0.6000    0.7500         5
     anxious     0.7500    0.6000    0.6667         5
    stressed     0.5000    0.8000    0.6154         5
       tired     0.7143    1.0000    0.8333         5
         sad     0.7500    0.6000    0.6667         5
        calm     0.7500    0.6000    0.6667         5
      healed     0.5000    0.4000    0.4444         5
      secure     0.6667    0.4000    0.5000         5
       happy     0.7143    1.0000    0.8333         5
     hopeful     0.8333    1.0000    0.9091         5

    accuracy                         0.7000        50
   macro avg     0.7179    0.7000    0.6886        50
weighted avg     0.7179    0.7000    0.6886        50
```

Confusion matrix, rows are true labels and columns are predicted labels:

```text
,lonely,anxious,stressed,tired,sad,calm,healed,secure,happy,hopeful
lonely,3,0,0,1,1,0,0,0,0,0
anxious,0,3,2,0,0,0,0,0,0,0
stressed,0,0,4,1,0,0,0,0,0,0
tired,0,0,0,5,0,0,0,0,0,0
sad,0,0,1,0,3,0,0,1,0,0
calm,0,0,0,0,0,3,2,0,0,0
healed,0,0,0,0,0,1,2,0,2,0
secure,0,1,1,0,0,0,0,2,0,1
happy,0,0,0,0,0,0,0,0,5,0
hopeful,0,0,0,0,0,0,0,0,0,5
```

## Interpretation

This model is usable as an MVP inference engine, but it is not final-quality.

Compared with `data/baseline_experiment_notes.md`, the ERNIE mini model improves over the current `v2` LogisticRegression baseline:

```text
LogisticRegression v2 test_accuracy: 0.6200
ERNIE mini v2 test_accuracy:          0.7000
```

Main weak spots:

1. `healed` has low recall and is confused with `calm` and `happy`.
2. `secure` has low recall and is confused with `anxious`, `stressed`, and `hopeful`.
3. `stressed` has modest precision because nearby negative classes can be pulled into it.
4. The test set has only 5 samples per class, so the numbers are useful for pipeline validation but too small for a final claim.

Data caveat:

`campus_emotion_samples_v2.csv` is still AI-generated. Before final presentation, add manually reviewed campus expressions and re-run the evaluation.
