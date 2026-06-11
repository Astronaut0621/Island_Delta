from dataclasses import dataclass

from app.core.config import EMOTION_LABELS, EMOTION_SENTIMENTS, MODEL_VERSION
from app.schemas.nlp import AnalyzeResponse
from app.services.emotion_engine import EmotionPrediction, predict_emotion
from app.services.generator import generate_public_post
from app.services.safety import detect_safety


@dataclass(frozen=True)
class EmotionRule:
    code: str
    keywords: tuple[str, ...]
    temperature: int


EMOTION_RULES = (
    EmotionRule("lonely", ("孤独", "一个人", "没人", "空荡", "寂寞", "孤单"), -6),
    EmotionRule("anxious", ("焦虑", "慌", "紧张", "不安", "担心", "害怕"), -5),
    EmotionRule("stressed", ("压力", "ddl", "考试", "复习", "作业", "绩点", "加班", "压得"), -6),
    EmotionRule("tired", ("累", "疲惫", "困", "熬夜", "撑着", "没力气"), -4),
    EmotionRule("sad", ("难过", "失落", "委屈", "想哭", "低落", "糟糕"), -5),
    EmotionRule("calm", ("平静", "安静", "发呆", "慢下来", "风吹", "散步"), 1),
    EmotionRule("healed", ("治愈", "舒服", "放松", "晚风", "阳光", "草坪"), 5),
    EmotionRule("secure", ("安心", "安全", "被接住", "踏实", "稳定"), 4),
    EmotionRule("happy", ("开心", "快乐", "高兴", "幸福", "好玩", "喜欢"), 7),
    EmotionRule("hopeful", ("希望", "会好的", "还能", "坚持", "期待", "明天"), 6),
)

INTENSIFIERS = ("很", "特别", "非常", "真的", "太", "极度", "超级", "完全")


def analyze_text(text: str, location_name: str | None = None) -> AnalyzeResponse:
    normalized = text.strip().lower()
    safety = detect_safety(normalized)
    model_prediction = predict_emotion(normalized)
    if model_prediction is not None:
        return _build_model_response(
            text=text,
            location_name=location_name,
            safety=safety,
            prediction=model_prediction,
        )

    matches = _score_emotions(normalized)
    rule, score = _select_rule_for_safety(matches[0], safety.level)

    sentiment = _sentiment_for_safety(EMOTION_SENTIMENTS[rule.code], safety.level)
    temperature = _temperature_for_safety(
        _adjust_temperature(rule.temperature, normalized),
        sentiment,
        safety.level,
    )
    confidence = _confidence(score, safety.level)
    suggested_content = generate_public_post(
        text=text,
        emotion_name=EMOTION_LABELS[rule.code],
        temperature=temperature,
        location_name=location_name,
    )

    return AnalyzeResponse(
        emotion_type=rule.code,
        emotion_name=EMOTION_LABELS[rule.code],
        sentiment=sentiment,
        temperature=temperature,
        safety_level=safety.level,
        confidence=confidence,
        model_version=MODEL_VERSION,
        suggested_content=suggested_content,
        safety_message=safety.message,
    )


def _build_model_response(
    text: str,
    location_name: str | None,
    safety,
    prediction: EmotionPrediction,
) -> AnalyzeResponse:
    code, confidence = _adjust_emotion_for_safety(
        prediction.code,
        prediction.confidence,
        safety.level,
    )
    sentiment = _sentiment_for_safety(EMOTION_SENTIMENTS[code], safety.level)
    temperature = _temperature_for_safety(
        _adjust_temperature(_base_temperature_for_code(code), text.strip().lower()),
        sentiment,
        safety.level,
    )
    suggested_content = generate_public_post(
        text=text,
        emotion_name=EMOTION_LABELS[code],
        temperature=temperature,
        location_name=location_name,
    )

    return AnalyzeResponse(
        emotion_type=code,
        emotion_name=EMOTION_LABELS[code],
        sentiment=sentiment,
        temperature=temperature,
        safety_level=safety.level,
        confidence=confidence,
        model_version=prediction.model_version,
        suggested_content=suggested_content,
        safety_message=safety.message,
    )


def _score_emotions(text: str) -> list[tuple[EmotionRule, int]]:
    scored: list[tuple[EmotionRule, int]] = []
    for rule in EMOTION_RULES:
        score = sum(1 for keyword in rule.keywords if keyword in text)
        scored.append((rule, score))

    scored.sort(key=lambda item: item[1], reverse=True)
    if scored[0][1] > 0:
        return scored

    return [(EmotionRule("calm", tuple(), 0), 0)]


def _select_rule_for_safety(
    match: tuple[EmotionRule, int],
    safety_level: str,
) -> tuple[EmotionRule, int]:
    rule, score = match
    if score > 0 or safety_level == "normal":
        return match

    fallback_temperature = -8 if safety_level == "crisis" else -7
    return EmotionRule("sad", tuple(), fallback_temperature), score


def _adjust_temperature(base_temperature: int, text: str) -> int:
    adjustment = 0
    if any(word in text for word in INTENSIFIERS):
        adjustment = -1 if base_temperature < 0 else 1
    if "一点" in text or "有点" in text:
        adjustment = 1 if base_temperature < 0 else -1
    return _clamp_temperature(base_temperature + adjustment)


def _temperature_for_safety(temperature: int, sentiment: str, safety_level: str) -> int:
    if safety_level == "crisis":
        return min(temperature, -8)
    if safety_level == "warning":
        return min(temperature, -7)
    if sentiment == "neutral":
        return max(-1, min(temperature, 1))
    return _clamp_temperature(temperature)


def _sentiment_for_safety(sentiment: str, safety_level: str) -> str:
    if safety_level in {"warning", "crisis"}:
        return "negative"
    return sentiment


def _confidence(score: int, safety_level: str) -> float:
    if safety_level == "crisis":
        return 0.9
    if score >= 2:
        return 0.86
    if score == 1:
        return 0.74
    return 0.52


def _clamp_temperature(value: int) -> int:
    return max(-10, min(10, value))


def _base_temperature_for_code(code: str) -> int:
    for rule in EMOTION_RULES:
        if rule.code == code:
            return rule.temperature
    return 0


def _adjust_emotion_for_safety(
    code: str,
    confidence: float,
    safety_level: str,
) -> tuple[str, float]:
    if safety_level in {"warning", "crisis"} and EMOTION_SENTIMENTS[code] != "negative":
        adjusted_confidence = 0.82 if safety_level == "crisis" else 0.74
        return "sad", adjusted_confidence

    return code, confidence
