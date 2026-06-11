from dataclasses import dataclass


@dataclass(frozen=True)
class SafetyResult:
    level: str
    message: str | None


CRISIS_KEYWORDS = (
    "自杀",
    "轻生",
    "不想活",
    "结束生命",
    "杀了自己",
    "伤害自己",
    "割腕",
    "跳楼",
    "想死",
    "去死",
    "伤害别人",
    "杀人",
)

WARNING_KEYWORDS = (
    "崩溃",
    "绝望",
    "撑不住",
    "活不下去",
    "没有意义",
    "没人管",
    "很痛苦",
    "好痛苦",
)


def detect_safety(text: str) -> SafetyResult:
    normalized = text.strip().lower()

    if any(keyword in normalized for keyword in CRISIS_KEYWORDS):
        return SafetyResult(
            level="crisis",
            message="这条内容更适合先获得现实中的支持，不建议直接公开发布到地图。",
        )

    if any(keyword in normalized for keyword in WARNING_KEYWORDS):
        return SafetyResult(
            level="warning",
            message="这条内容情绪温度较低，发布前建议再确认是否愿意公开展示。",
        )

    return SafetyResult(level="normal", message=None)
