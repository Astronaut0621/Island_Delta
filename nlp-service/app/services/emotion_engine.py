from __future__ import annotations

import json
import queue
import threading
from dataclasses import dataclass
from pathlib import Path

from app.core.config import (
    EMOTION_LABELS,
    EMOTION_ORDER,
    PADDLE_EMOTION_MODEL_DIR,
    PADDLE_INFERENCE_DEVICE,
    PADDLE_MODEL_VERSION,
    RULE_MODEL_VERSION,
)


@dataclass(frozen=True)
class EmotionPrediction:
    code: str
    confidence: float
    model_version: str
    engine: str


@dataclass(frozen=True)
class EmotionEngineStatus:
    model_name: str
    model_version: str
    engine: str
    paddle_available: bool
    model_path: str
    fallback_reason: str | None


class PaddleEmotionClassifier:
    def __init__(self, model_dir: Path):
        try:
            import paddle
            from paddlenlp.transformers import AutoModelForSequenceClassification, AutoTokenizer
        except ImportError as exc:
            raise RuntimeError("paddle or paddlenlp is not installed") from exc

        if not model_dir.exists():
            raise RuntimeError(f"model directory does not exist: {model_dir}")

        self.paddle = paddle
        self.id_to_label = _read_label_map(model_dir)
        self.device = _resolve_device(paddle)
        self.tokenizer = AutoTokenizer.from_pretrained(str(model_dir))
        self.model = AutoModelForSequenceClassification.from_pretrained(
            str(model_dir),
            num_classes=len(self.id_to_label),
        )
        self.model.eval()

    def predict(self, text: str) -> EmotionPrediction:
        encoded = self.tokenizer(
            text,
            max_seq_len=96,
            truncation=True,
        )
        token_type_ids = encoded.get("token_type_ids", [0] * len(encoded["input_ids"]))
        input_ids = self.paddle.to_tensor([encoded["input_ids"]], dtype="int64")
        token_type_ids_tensor = self.paddle.to_tensor([token_type_ids], dtype="int64")

        with self.paddle.no_grad():
            outputs = self.model(
                input_ids=input_ids,
                token_type_ids=token_type_ids_tensor,
            )
            logits = outputs[0] if isinstance(outputs, tuple) else getattr(outputs, "logits", outputs)
            probabilities = self.paddle.nn.functional.softmax(logits, axis=-1).numpy()[0]

        best_index = int(probabilities.argmax())
        code = self.id_to_label[best_index]
        confidence = float(probabilities[best_index])
        return EmotionPrediction(
            code=code,
            confidence=round(confidence, 4),
            model_version=PADDLE_MODEL_VERSION,
            engine="paddle-ernie-local",
        )


@dataclass(frozen=True)
class _PredictionTask:
    text: str
    response: queue.Queue[tuple[EmotionPrediction | None, str | None]]


class _PaddleEmotionWorker:
    def __init__(self):
        self._tasks: queue.Queue[_PredictionTask | None] = queue.Queue()
        self._ready = threading.Event()
        self._thread = threading.Thread(target=self._run, name="paddle-emotion-worker", daemon=True)
        self.classifier: PaddleEmotionClassifier | None = None
        self.load_error: str | None = None
        self._thread.start()
        self._ready.wait()

    @property
    def available(self) -> bool:
        return self.classifier is not None

    def predict(self, text: str) -> tuple[EmotionPrediction | None, str | None]:
        if self.classifier is None:
            return None, self.load_error

        response: queue.Queue[tuple[EmotionPrediction | None, str | None]] = queue.Queue(maxsize=1)
        self._tasks.put(_PredictionTask(text=text, response=response))
        return response.get()

    def _run(self) -> None:
        try:
            self.classifier = PaddleEmotionClassifier(PADDLE_EMOTION_MODEL_DIR)
        except Exception as exc:  # pragma: no cover - optional dependency path.
            self.load_error = f"{type(exc).__name__}: {exc}"
            self._ready.set()
            return

        self._ready.set()
        while True:
            task = self._tasks.get()
            if task is None:
                return

            try:
                task.response.put((self.classifier.predict(task.text), None))
            except Exception as exc:  # pragma: no cover - depends on optional runtime model stack.
                error = f"{type(exc).__name__}: {exc}"
                self.load_error = error
                task.response.put((None, error))


_worker: _PaddleEmotionWorker | None = None
_worker_lock = threading.Lock()
_last_load_error: str | None = None


def predict_emotion(text: str) -> EmotionPrediction | None:
    global _last_load_error

    worker = _get_worker()
    if worker is None:
        return None

    prediction, error = worker.predict(text)
    if error is not None:
        _last_load_error = error
        return None
    return prediction


def get_emotion_engine_status() -> EmotionEngineStatus:
    worker = _get_worker()
    if worker is not None and worker.available:
        return EmotionEngineStatus(
            model_name="Island Delta ERNIE emotion classifier",
            model_version=PADDLE_MODEL_VERSION,
            engine="paddle-ernie-local",
            paddle_available=True,
            model_path=str(PADDLE_EMOTION_MODEL_DIR),
            fallback_reason=None,
        )

    return EmotionEngineStatus(
        model_name="Island Delta rule-based MVP",
        model_version=RULE_MODEL_VERSION,
        engine="keyword-rules",
        paddle_available=False,
        model_path=str(PADDLE_EMOTION_MODEL_DIR),
        fallback_reason=(worker.load_error if worker is not None else None) or _last_load_error,
    )


def _get_worker() -> _PaddleEmotionWorker | None:
    global _last_load_error, _worker

    if _worker is not None:
        return _worker

    with _worker_lock:
        if _worker is not None:
            return _worker

        _worker = _PaddleEmotionWorker()
        if _worker.load_error is not None:
            _last_load_error = _worker.load_error
        return _worker


def _read_label_map(model_dir: Path) -> dict[int, str]:
    label_map_path = model_dir / "label_map.json"
    if not label_map_path.exists():
        return {index: code for index, code in enumerate(EMOTION_ORDER)}

    data = json.loads(label_map_path.read_text(encoding="utf-8"))
    raw_id_to_label = data.get("id_to_label")
    if not raw_id_to_label:
        return {index: code for index, code in enumerate(EMOTION_ORDER)}

    id_to_label = {int(index): code for index, code in raw_id_to_label.items()}
    unknown_labels = sorted({code for code in id_to_label.values() if code not in EMOTION_LABELS})
    if unknown_labels:
        raise RuntimeError(f"unknown labels in label_map.json: {unknown_labels}")

    return id_to_label


def _resolve_device(paddle) -> str:
    if PADDLE_INFERENCE_DEVICE != "auto":
        return paddle.set_device(PADDLE_INFERENCE_DEVICE)

    device = "gpu" if paddle.is_compiled_with_cuda() else "cpu"
    return paddle.set_device(device)
