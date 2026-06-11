import argparse
import csv
import json
import random
from dataclasses import dataclass
from pathlib import Path

import numpy as np
import paddle
from paddlenlp.transformers import AutoModelForSequenceClassification, AutoTokenizer
from sklearn.metrics import accuracy_score, classification_report, confusion_matrix
from sklearn.model_selection import train_test_split


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

LABEL_TO_ID = {label: index for index, label in enumerate(LABELS)}
ID_TO_LABEL = {index: label for label, index in LABEL_TO_ID.items()}


@dataclass
class Sample:
    text: str
    label: int


class EmotionDataset(paddle.io.Dataset):
    def __init__(self, samples: list[Sample], tokenizer, max_seq_len: int):
        self.samples = samples
        self.tokenizer = tokenizer
        self.max_seq_len = max_seq_len

    def __len__(self) -> int:
        return len(self.samples)

    def __getitem__(self, index: int) -> dict[str, np.ndarray]:
        sample = self.samples[index]
        encoded = self.tokenizer(
            sample.text,
            max_seq_len=self.max_seq_len,
            truncation=True,
        )
        token_type_ids = encoded.get("token_type_ids", [0] * len(encoded["input_ids"]))
        return {
            "input_ids": np.array(encoded["input_ids"], dtype="int64"),
            "token_type_ids": np.array(token_type_ids, dtype="int64"),
            "labels": np.array(sample.label, dtype="int64"),
        }


def set_seed(seed: int) -> None:
    random.seed(seed)
    np.random.seed(seed)
    paddle.seed(seed)


def read_samples(path: Path) -> list[Sample]:
    with path.open("r", encoding="utf-8", newline="") as file:
        rows = list(csv.DictReader(file))
    return [
        Sample(text=row["text"].strip(), label=LABEL_TO_ID[row["emotion_type"].strip()])
        for row in rows
    ]


def split_samples(
    samples: list[Sample],
    dev_size: float,
    test_size: float,
    seed: int,
) -> tuple[list[Sample], list[Sample], list[Sample]]:
    labels = [sample.label for sample in samples]
    train_dev, test = train_test_split(
        samples,
        test_size=test_size,
        random_state=seed,
        stratify=labels,
    )
    train_dev_labels = [sample.label for sample in train_dev]
    relative_dev_size = dev_size / (1.0 - test_size)
    train, dev = train_test_split(
        train_dev,
        test_size=relative_dev_size,
        random_state=seed,
        stratify=train_dev_labels,
    )
    return train, dev, test


def collate_batch(batch: list[dict[str, np.ndarray]], pad_token_id: int) -> dict[str, paddle.Tensor]:
    max_len = max(len(item["input_ids"]) for item in batch)
    input_ids = []
    token_type_ids = []
    labels = []

    for item in batch:
        pad_len = max_len - len(item["input_ids"])
        input_ids.append(np.pad(item["input_ids"], (0, pad_len), constant_values=pad_token_id))
        token_type_ids.append(np.pad(item["token_type_ids"], (0, pad_len), constant_values=0))
        labels.append(item["labels"])

    return {
        "input_ids": paddle.to_tensor(np.array(input_ids, dtype="int64")),
        "token_type_ids": paddle.to_tensor(np.array(token_type_ids, dtype="int64")),
        "labels": paddle.to_tensor(np.array(labels, dtype="int64")),
    }


def build_loader(samples: list[Sample], tokenizer, args, shuffle: bool) -> paddle.io.DataLoader:
    dataset = EmotionDataset(samples, tokenizer, args.max_seq_len)
    pad_token_id = getattr(tokenizer, "pad_token_id", 0) or 0
    return paddle.io.DataLoader(
        dataset,
        batch_size=args.batch_size,
        shuffle=shuffle,
        collate_fn=lambda batch: collate_batch(batch, pad_token_id),
    )


@paddle.no_grad()
def evaluate(model, loader: paddle.io.DataLoader) -> tuple[float, list[int], list[int]]:
    model.eval()
    all_labels: list[int] = []
    all_predictions: list[int] = []

    for batch in loader:
        logits = model(
            input_ids=batch["input_ids"],
            token_type_ids=batch["token_type_ids"],
        )
        if isinstance(logits, tuple):
            logits = logits[0]
        predictions = paddle.argmax(logits, axis=-1).numpy().tolist()
        labels = batch["labels"].numpy().tolist()
        all_predictions.extend(predictions)
        all_labels.extend(labels)

    return accuracy_score(all_labels, all_predictions), all_labels, all_predictions


def save_label_files(output_dir: Path) -> None:
    output_dir.mkdir(parents=True, exist_ok=True)
    (output_dir / "label_map.json").write_text(
        json.dumps({"label_to_id": LABEL_TO_ID, "id_to_label": ID_TO_LABEL}, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--dataset", type=Path, default=Path("data/campus_emotion_samples_v2.csv"))
    parser.add_argument("--model-name", default="ernie-3.0-mini-zh")
    parser.add_argument("--output-dir", type=Path, default=Path("models/emotion-ernie-mini"))
    parser.add_argument("--epochs", type=int, default=8)
    parser.add_argument("--batch-size", type=int, default=16)
    parser.add_argument("--max-seq-len", type=int, default=96)
    parser.add_argument("--learning-rate", type=float, default=2e-5)
    parser.add_argument("--weight-decay", type=float, default=0.01)
    parser.add_argument("--dev-size", type=float, default=0.1)
    parser.add_argument("--test-size", type=float, default=0.1)
    parser.add_argument("--seed", type=int, default=42)
    args = parser.parse_args()

    set_seed(args.seed)
    paddle.set_device("gpu" if paddle.is_compiled_with_cuda() else "cpu")

    samples = read_samples(args.dataset)
    train_samples, dev_samples, test_samples = split_samples(
        samples=samples,
        dev_size=args.dev_size,
        test_size=args.test_size,
        seed=args.seed,
    )

    tokenizer = AutoTokenizer.from_pretrained(args.model_name)
    model = AutoModelForSequenceClassification.from_pretrained(
        args.model_name,
        num_classes=len(LABELS),
    )

    train_loader = build_loader(train_samples, tokenizer, args, shuffle=True)
    dev_loader = build_loader(dev_samples, tokenizer, args, shuffle=False)
    test_loader = build_loader(test_samples, tokenizer, args, shuffle=False)

    optimizer = paddle.optimizer.AdamW(
        learning_rate=args.learning_rate,
        parameters=model.parameters(),
        weight_decay=args.weight_decay,
    )
    criterion = paddle.nn.CrossEntropyLoss()

    best_dev_accuracy = -1.0
    best_dir = args.output_dir / "best"

    print(f"device: {paddle.get_device()}")
    print(f"model_name: {args.model_name}")
    print(f"train/dev/test: {len(train_samples)}/{len(dev_samples)}/{len(test_samples)}")

    for epoch in range(1, args.epochs + 1):
        model.train()
        losses: list[float] = []

        for batch in train_loader:
            logits = model(
                input_ids=batch["input_ids"],
                token_type_ids=batch["token_type_ids"],
            )
            if isinstance(logits, tuple):
                logits = logits[0]
            loss = criterion(logits, batch["labels"])
            loss.backward()
            optimizer.step()
            optimizer.clear_grad()
            losses.append(float(loss.numpy()))

        dev_accuracy, _, _ = evaluate(model, dev_loader)
        avg_loss = sum(losses) / max(len(losses), 1)
        print(f"epoch={epoch} train_loss={avg_loss:.4f} dev_accuracy={dev_accuracy:.4f}")

        if dev_accuracy > best_dev_accuracy:
            best_dev_accuracy = dev_accuracy
            best_dir.mkdir(parents=True, exist_ok=True)
            model.save_pretrained(best_dir)
            tokenizer.save_pretrained(best_dir)
            save_label_files(best_dir)

    print(f"best_dev_accuracy: {best_dev_accuracy:.4f}")

    tokenizer = AutoTokenizer.from_pretrained(str(best_dir))
    model = AutoModelForSequenceClassification.from_pretrained(str(best_dir), num_classes=len(LABELS))
    test_accuracy, test_labels, test_predictions = evaluate(model, test_loader)
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
