from uuid import uuid4

from app.core.config import EMOTION_DESCRIPTIONS, EMOTION_LABELS
from app.schemas.chat import ChatMessageResponse
from app.services.analyzer import analyze_text


def build_chat_response(
    message: str,
    session_id: str | None = None,
    location_name: str | None = None,
) -> ChatMessageResponse:
    analysis = analyze_text(message, location_name=location_name)
    reply = _reply_for_analysis(
        code=analysis.emotion_type,
        emotion_name=analysis.emotion_name,
        temperature=analysis.temperature,
        safety_level=analysis.safety_level,
        location_name=location_name,
    )

    return ChatMessageResponse(
        session_id=session_id or f"chat_{uuid4().hex[:12]}",
        reply=reply,
        analysis=analysis,
        draft_post=analysis.suggested_content,
        actions=_actions_for_safety(analysis.safety_level),
        nearby_warmer_locations=_recommend_nearby_warmer(
            code=analysis.emotion_type,
            safety_level=analysis.safety_level,
            location_name=location_name,
        ),
        model_version=analysis.model_version,
    )


def _reply_for_analysis(
    code: str,
    emotion_name: str,
    temperature: int,
    safety_level: str,
    location_name: str | None,
) -> str:
    if safety_level == "crisis":
        return (
            "我听见这句话里有一个很危险的声音。先不要急着发布，也不用解释得很完整。"
            "请先把注意力放在眼前的安全上——联系身边信任的人，或学校、当地的紧急支持。"
            "你说的这些值得被一个真实的人接住，而不是被地图看见。"
        )

    place = f"在{location_name}" if location_name else "这一刻"
    emotion_desc = EMOTION_DESCRIPTIONS.get(code, "")

    if safety_level == "warning":
        return (
            f"我感觉到{place}你正扛着很重的{emotion_name}，温度掉到了 {temperature}℃。"
            "这种强度不适合直接摊开在地图上，但它确实存在。"
            "如果愿意，我们可以先把它收拢成一句更克制、更安全的话，再决定要不要留下。"
        )

    line = _reflection_line(code, emotion_name, place)
    return (
        f"{line}"
        f"温度大约是 {temperature}℃（{emotion_desc}）。"
        "不用解释得很完整，可以先留下一句真实的话，让地图轻轻接住它。"
    )


# 每种主情绪给一句不一样的反射式回应，避免负面情绪互相雷同。
_REFLECTION_OPENERS = {
    "lonely": "听起来这一刻你更像是一个人——不是不想说话，而是好像没有人能接住你想说的话。",
    "anxious": "听出来你在为还没发生的事悬着心，那种不确定比确定更难熬。",
    "stressed": "能感觉到事情压在身上的重量，被任务和截止时间推着走是很耗的。",
    "tired": "这句话里有种撑了很久的感觉，能量被抽干了，不只是想睡一觉那么简单。",
    "sad": "听起来你在经历一种落空的难过，不是闹脾气，是真的有点疼。",
    "calm": "这一刻听起来是稳的，没有大的波澜，只是安静地待着。",
    "healed": "听出来有东西轻轻托了你一下，那一点缓和是真实的。",
    "secure": "这里有一种被接住的感觉，踏实、不用紧绷，可以松一口气。",
    "happy": "这句话里有明确的亮色，是当下发生的开心，不是借来的。",
    "hopeful": "虽然不容易，但你能感觉到那条「还能继续」的线还亮着。",
}


def _reflection_line(code: str, emotion_name: str, place: str) -> str:
    opener = _REFLECTION_OPENERS.get(code)
    if opener is None:
        return f"我听出这里有{emotion_name}。"
    return opener


def _actions_for_safety(safety_level: str) -> list[str]:
    if safety_level == "crisis":
        return ["do_not_publish", "seek_support", "edit_message"]
    if safety_level == "warning":
        return ["use_draft", "regenerate", "continue_chat"]
    return ["use_draft", "regenerate", "continue_chat"]


def _recommend_nearby_warmer(
    code: str,
    safety_level: str,
    location_name: str | None,
) -> list[str]:
    # 附近温暖地点推荐依赖 backend 的地点与统计聚合数据，本服务暂不持有。
    # 负向且非危机情绪才需要推荐，positive/neutral 不返回占位，避免给前端噪音。
    if safety_level == "crisis":
        return []
    if code not in {"lonely", "anxious", "stressed", "tired", "sad"}:
        return []
    # 占位：留空列表，等 backend /nlp/analyze 或独立地点接口对接后填充。
    # 此处保留 location_name 仅供后续日志或调试，不影响响应契约。
    _ = location_name
    return []
