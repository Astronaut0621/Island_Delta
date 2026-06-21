import unittest
from unittest.mock import patch

from fastapi.testclient import TestClient

from app.main import app
from app.services.emotion_engine import EmotionEngineStatus
from app.services.chat import _reflection_line, _recommend_nearby_warmer


def fake_engine_status() -> EmotionEngineStatus:
    return EmotionEngineStatus(
        model_name="Test rule engine",
        model_version="rule-mvp-v1",
        engine="keyword-rules",
        paddle_available=False,
        model_path="test-model-path",
        fallback_reason="disabled in tests",
    )


class ChatReplyTest(unittest.TestCase):
    def setUp(self) -> None:
        self.client = TestClient(app)
        self.engine_patch = patch("app.api.routes.get_emotion_engine_status", fake_engine_status)
        self.predict_patch = patch("app.services.analyzer.predict_emotion", return_value=None)
        self.engine_patch.start()
        self.predict_patch.start()

    def tearDown(self) -> None:
        self.predict_patch.stop()
        self.engine_patch.stop()

    def _chat(self, message: str, location_name: str | None = None) -> dict:
        payload = {"message": message}
        if location_name is not None:
            payload["location_name"] = location_name
        response = self.client.post("/chat/message", json=payload)
        self.assertEqual(response.status_code, 200)
        return response.json()

    def test_response_has_nearby_warmer_locations_field(self) -> None:
        # 契约字段必须存在，即便当前是占位空列表。
        data = self._chat("晚上一个人回宿舍，路上很安静")
        self.assertIn("nearby_warmer_locations", data)
        self.assertIsInstance(data["nearby_warmer_locations"], list)

    def test_negative_emotion_reply_carries_emotion_specific_opener(self) -> None:
        data = self._chat("明天就要考试了，心里一直发慌")
        reply = data["reply"]
        # 焦虑的 opener 用"悬着心/不确定"替代标签词"焦虑"，避免标签化腔调
        self.assertIn("悬着心", reply)
        # 温度行仍带情绪描述，确保信息不丢
        self.assertIn("担心未来", reply)
        # 危机信号不能意外触发
        self.assertNotIn("危险的声音", reply)

    def test_crisis_reply_overrides_emotion_specific_content(self) -> None:
        # 安全红线：crisis 内容必须走专门的安全回复，且不允许发布。
        data = self._chat("我不想活了，想结束生命")
        self.assertEqual(data["analysis"]["safety_level"], "crisis")
        self.assertIn("危险的声音", data["reply"])
        self.assertIn("seek_support", data["actions"])
        self.assertEqual(data["nearby_warmer_locations"], [])

    def test_different_negative_emotions_get_different_replies(self) -> None:
        # 这是反模板化的核心断言：同样负向、同样 warning 之外的两类情绪，
        # 回复开头不应雷同。
        lonely_reply = self._chat("晚上一个人回宿舍，突然觉得整条路都很安静")["reply"]
        anxious_reply = self._chat("明天就要考试了，心里一直发慌")["reply"]
        self.assertNotEqual(lonely_reply, anxious_reply)
        # 两者各自落到不同的情绪 opener
        self.assertTrue(
            _reflection_line("lonely", "孤独", "这一刻") != _reflection_line("anxious", "焦虑", "这一刻")
        )

    def test_positive_emotion_does_not_recommend_warmer_locations(self) -> None:
        # 只有负向非危机情绪才需要附近温暖推荐，正向直接返回空。
        data = self._chat("今天和朋友笑了一整晚，很开心")
        self.assertEqual(data["nearby_warmer_locations"], [])


class ChatHelpersTest(unittest.TestCase):
    def test_reflection_line_distinct_for_each_emotion(self) -> None:
        codes = [
            "lonely", "anxious", "stressed", "tired", "sad",
            "calm", "healed", "secure", "happy", "hopeful",
        ]
        lines = [_reflection_line(code, "", "这里") for code in codes]
        # 十类情绪都应有专属 opener，且互不相同
        self.assertEqual(len(set(lines)), len(codes))
        for line in lines:
            self.assertGreater(len(line), 0)

    def test_reflection_line_unknown_code_falls_back(self) -> None:
        line = _reflection_line("not_a_real_emotion", "某情绪", "这里")
        self.assertIn("某情绪", line)

    def test_recommend_nearby_skips_crisis_and_positive(self) -> None:
        self.assertEqual(_recommend_nearby_warmer("sad", "crisis", "图书馆"), [])
        self.assertEqual(_recommend_nearby_warmer("happy", "normal", "操场"), [])
        # 负向非危机：当前占位仍为空列表（待 backend 对接），但调用不应报错
        self.assertEqual(_recommend_nearby_warmer("sad", "normal", "图书馆"), [])


if __name__ == "__main__":
    unittest.main()
