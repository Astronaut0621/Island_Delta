from uuid import uuid4

from app.schemas.chat import ChatMessageResponse
from app.services.analyzer import analyze_text


def build_chat_response(
    message: str,
    session_id: str | None = None,
    location_name: str | None = None,
) -> ChatMessageResponse:
    analysis = analyze_text(message, location_name=location_name)
    reply = _reply_for_analysis(analysis.emotion_name, analysis.temperature, analysis.safety_level)

    return ChatMessageResponse(
        session_id=session_id or f"chat_{uuid4().hex[:12]}",
        reply=reply,
        analysis=analysis,
        draft_post=analysis.suggested_content,
        actions=_actions_for_safety(analysis.safety_level),
        model_version=analysis.model_version,
    )


def _reply_for_analysis(emotion_name: str, temperature: int, safety_level: str) -> str:
    if safety_level == "crisis":
        return (
            "我听见这句话里的危险信号了。先不要急着把它发布出去，"
            "请把注意力放到眼前的安全上，联系身边可信任的人或学校/当地紧急支持。"
        )

    if safety_level == "warning":
        return (
            f"这句话里有很重的{emotion_name}，温度大约是 {temperature}℃。"
            "如果你愿意，可以先把它整理成一句更短、更安全的留言。"
        )

    if temperature < -1:
        return (
            f"听起来你现在更接近{emotion_name}，温度大约是 {temperature}℃。"
            "它不需要被解释得很完整，先留下一句真实但克制的话就可以。"
        )

    if temperature <= 1:
        return (
            f"这更像一个{emotion_name}的片刻，温度大约是 {temperature}℃。"
            "可以把这份安静留在地图上，让后来的人轻轻看见。"
        )

    return (
        f"这句话里有{emotion_name}的暖意，温度大约是 +{temperature}℃。"
        "它适合成为一条温暖的匿名留言。"
    )


def _actions_for_safety(safety_level: str) -> list[str]:
    if safety_level == "crisis":
        return ["do_not_publish", "seek_support", "edit_message"]
    return ["use_draft", "regenerate", "continue_chat"]
