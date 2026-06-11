from app.core.config import REACTION_SAFE_MAX_LENGTH
from app.services.safety import detect_safety


def compact_text(text: str) -> str:
    return " ".join(text.strip().split())


def generate_public_post(
    text: str,
    emotion_name: str,
    temperature: int,
    location_name: str | None = None,
) -> str:
    safety = detect_safety(text)
    if safety.level == "crisis":
        return "今晚的温度很低，先把自己放在更安全的地方。"

    cleaned = compact_text(text)
    if len(cleaned) <= REACTION_SAFE_MAX_LENGTH:
        return cleaned

    place_prefix = f"在{location_name}，" if location_name else ""
    tone = _temperature_tone(temperature)
    return f"{place_prefix}我把一点{emotion_name}和{tone}留在这里。"


def _temperature_tone(temperature: int) -> str:
    if temperature <= -7:
        return "很冷的心情"
    if temperature <= -2:
        return "有点低的温度"
    if temperature <= 1:
        return "平静的片刻"
    if temperature <= 6:
        return "一点暖意"
    return "很亮的心情"
