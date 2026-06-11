import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from fastapi.testclient import TestClient

from app.core.config import EMOTION_LABELS
from app.main import app
from app.services.emotion_engine import EmotionEngineStatus


def fake_engine_status() -> EmotionEngineStatus:
    return EmotionEngineStatus(
        model_name="Test rule engine",
        model_version="rule-mvp-v1",
        engine="keyword-rules",
        paddle_available=False,
        model_path="test-model-path",
        fallback_reason="disabled in tests",
    )


class NlpApiTest(unittest.TestCase):
    def setUp(self) -> None:
        self.client = TestClient(app)
        self.engine_patch = patch("app.api.routes.get_emotion_engine_status", fake_engine_status)
        self.predict_patch = patch("app.services.analyzer.predict_emotion", return_value=None)
        self.engine_patch.start()
        self.predict_patch.start()

    def tearDown(self) -> None:
        self.predict_patch.stop()
        self.engine_patch.stop()

    def test_health(self) -> None:
        response = self.client.get("/health")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["status"], "ok")
        self.assertEqual(response.json()["model_version"], "rule-mvp-v1")

    def test_analyze_returns_stable_shape(self) -> None:
        response = self.client.post(
            "/nlp/analyze",
            json={"text": "今天在图书馆复习到很晚，感觉压力很大", "location_name": "图书馆"},
        )

        data = response.json()
        self.assertEqual(response.status_code, 200)
        self.assertIn(data["emotion_type"], EMOTION_LABELS)
        self.assertIn(data["sentiment"], {"positive", "neutral", "negative"})
        self.assertGreaterEqual(data["temperature"], -10)
        self.assertLessEqual(data["temperature"], 10)
        self.assertIn(data["safety_level"], {"normal", "warning", "crisis"})
        self.assertIn("suggested_content", data)

    def test_crisis_content_is_not_publishable(self) -> None:
        response = self.client.post(
            "/nlp/generate-post",
            json={"text": "我不想活了，想结束生命"},
        )

        data = response.json()
        self.assertEqual(response.status_code, 200)
        self.assertEqual(data["safety_level"], "crisis")
        self.assertFalse(data["publishable"])

    def test_model_version_returns_label_metadata(self) -> None:
        response = self.client.get("/nlp/model-version")

        data = response.json()
        self.assertEqual(response.status_code, 200)
        self.assertEqual(data["engine"], "keyword-rules")
        self.assertEqual(len(data["label_metadata"]), 10)
        self.assertEqual(data["label_metadata"]["stressed"]["sentiment"], "negative")
        self.assertEqual(data["label_metadata"]["happy"]["sentiment"], "positive")

    def test_feedback_is_written_to_jsonl(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            feedback_path = Path(temp_dir) / "feedback.jsonl"
            with patch("app.services.feedback_store.FEEDBACK_LOG_PATH", feedback_path):
                response = self.client.post(
                    "/nlp/feedback",
                    json={
                        "text": "今天很开心",
                        "original_emotion": "happy",
                        "corrected_emotion": "hopeful",
                        "original_temperature": 7,
                        "corrected_temperature": 6,
                        "accepted": False,
                    },
                )

                data = response.json()
                self.assertEqual(response.status_code, 200)
                self.assertFalse(data["accepted"])
                self.assertTrue(data["stored"])

                rows = feedback_path.read_text(encoding="utf-8").splitlines()
                self.assertEqual(len(rows), 1)
                stored = json.loads(rows[0])
                self.assertEqual(stored["text"], "今天很开心")
                self.assertEqual(stored["corrected_emotion"], "hopeful")
                self.assertEqual(stored["model_version"], "rule-mvp-v1")

    def test_chat_message_returns_analysis_and_draft(self) -> None:
        response = self.client.post(
            "/chat/message",
            json={"message": "明天考试我很慌，感觉撑不住了", "location_name": "宿舍"},
        )

        data = response.json()
        self.assertEqual(response.status_code, 200)
        self.assertIn("reply", data)
        self.assertIn("analysis", data)
        self.assertIn("draft_post", data)
        self.assertIn("use_draft", data["actions"])


if __name__ == "__main__":
    unittest.main()
