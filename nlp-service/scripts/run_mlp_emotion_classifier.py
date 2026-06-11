import argparse
import csv
from pathlib import Path

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics import accuracy_score, classification_report, confusion_matrix
from sklearn.model_selection import StratifiedKFold, cross_val_score, train_test_split
from sklearn.neural_network import MLPClassifier
from sklearn.pipeline import Pipeline


LABELS = [
    "lonely",
    "anxious",
    "stressed",
    "tired",
    "sad",
    "calm",
    "healed",
    "secure",
    "happy",
    "hopeful",
]


def read_dataset(path: Path) -> tuple[list[str], list[str]]:
    with path.open("r", encoding="utf-8", newline="") as file:
        rows = list(csv.DictReader(file))
    return [row["text"].strip() for row in rows], [row["emotion_type"].strip() for row in rows]


def build_pipeline(seed: int) -> Pipeline:
    return Pipeline(
        steps=[
            (
                "tfidf",
                TfidfVectorizer(
                    analyzer="char",
                    ngram_range=(2, 4),
                    min_df=1,
                    sublinear_tf=True,
                    max_features=6000,
                ),
            ),
            (
                "mlp",
                MLPClassifier(
                    hidden_layer_sizes=(128,),
                    activation="relu",
                    alpha=0.001,
                    batch_size=32,
                    learning_rate_init=0.001,
                    max_iter=300,
                    early_stopping=True,
                    validation_fraction=0.15,
                    n_iter_no_change=20,
                    random_state=seed,
                ),
            ),
        ]
    )


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("dataset", type=Path)
    parser.add_argument("--test-size", type=float, default=0.2)
    parser.add_argument("--seed", type=int, default=42)
    args = parser.parse_args()

    texts, labels = read_dataset(args.dataset)
    train_texts, test_texts, train_labels, test_labels = train_test_split(
        texts,
        labels,
        test_size=args.test_size,
        random_state=args.seed,
        stratify=labels,
    )

    model = build_pipeline(args.seed)
    model.fit(train_texts, train_labels)
    train_predictions = model.predict(train_texts)
    predictions = model.predict(test_texts)

    print(f"train_size: {len(train_texts)}")
    print(f"test_size: {len(test_texts)}")
    print(f"train_accuracy: {accuracy_score(train_labels, train_predictions):.4f}")
    print(f"accuracy: {accuracy_score(test_labels, predictions):.4f}")
    print()

    cv = StratifiedKFold(n_splits=5, shuffle=True, random_state=args.seed)
    scores = cross_val_score(build_pipeline(args.seed), texts, labels, cv=cv)
    print(f"cv_accuracy_mean: {scores.mean():.4f}")
    print(f"cv_accuracy_scores: {','.join(f'{score:.4f}' for score in scores)}")
    print()

    print(
        classification_report(
            test_labels,
            predictions,
            labels=LABELS,
            digits=4,
            zero_division=0,
        )
    )
    print("confusion_matrix rows=true cols=pred:")
    print("," + ",".join(LABELS))
    matrix = confusion_matrix(test_labels, predictions, labels=LABELS)
    for label, row in zip(LABELS, matrix):
        print(label + "," + ",".join(str(value) for value in row))


if __name__ == "__main__":
    main()
