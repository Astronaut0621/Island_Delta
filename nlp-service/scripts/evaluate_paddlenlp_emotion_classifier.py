import argparse
from pathlib import Path

from paddlenlp.transformers import AutoModelForSequenceClassification, AutoTokenizer
from sklearn.metrics import classification_report, confusion_matrix

from train_paddlenlp_emotion_classifier import LABELS, build_loader, evaluate, read_samples, split_samples


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--dataset", type=Path, default=Path("data/campus_emotion_samples_v2.csv"))
    parser.add_argument("--model-dir", type=Path, default=Path("models/emotion-ernie-mini/best"))
    parser.add_argument("--batch-size", type=int, default=16)
    parser.add_argument("--max-seq-len", type=int, default=96)
    parser.add_argument("--dev-size", type=float, default=0.1)
    parser.add_argument("--test-size", type=float, default=0.1)
    parser.add_argument("--seed", type=int, default=42)
    args = parser.parse_args()

    samples = read_samples(args.dataset)
    train_samples, dev_samples, test_samples = split_samples(
        samples=samples,
        dev_size=args.dev_size,
        test_size=args.test_size,
        seed=args.seed,
    )

    tokenizer = AutoTokenizer.from_pretrained(str(args.model_dir))
    model = AutoModelForSequenceClassification.from_pretrained(str(args.model_dir), num_classes=len(LABELS))
    test_loader = build_loader(test_samples, tokenizer, args, shuffle=False)

    test_accuracy, test_labels, test_predictions = evaluate(model, test_loader)
    print(f"dataset: {args.dataset}")
    print(f"model_dir: {args.model_dir}")
    print(f"train/dev/test: {len(train_samples)}/{len(dev_samples)}/{len(test_samples)}")
    print(f"test_accuracy: {test_accuracy:.4f}")
    print(
        classification_report(
            test_labels,
            test_predictions,
            labels=list(range(len(LABELS))),
            target_names=LABELS,
            digits=4,
            zero_division=0,
        )
    )
    print("confusion_matrix rows=true cols=pred:")
    print("," + ",".join(LABELS))
    matrix = confusion_matrix(test_labels, test_predictions, labels=list(range(len(LABELS))))
    for label, row in zip(LABELS, matrix):
        print(label + "," + ",".join(str(value) for value in row))


if __name__ == "__main__":
    main()
