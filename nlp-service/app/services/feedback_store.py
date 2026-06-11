import json
import threading
from datetime import datetime, timezone
from uuid import uuid4

from app.core.config import FEEDBACK_LOG_PATH
from app.schemas.nlp import FeedbackRequest


_write_lock = threading.Lock()


def store_feedback(request: FeedbackRequest, model_version: str) -> bool:
    record = {
        "id": f"fb_{uuid4().hex[:16]}",
        "created_at": datetime.now(timezone.utc).isoformat(),
        "model_version": model_version,
        **request.model_dump(),
    }

    try:
        FEEDBACK_LOG_PATH.parent.mkdir(parents=True, exist_ok=True)
        line = json.dumps(record, ensure_ascii=False, separators=(",", ":"))
        with _write_lock:
            with FEEDBACK_LOG_PATH.open("a", encoding="utf-8") as file:
                file.write(line + "\n")
    except OSError:
        return False

    return True
