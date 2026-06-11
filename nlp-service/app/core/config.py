import os
from pathlib import Path


SERVICE_ROOT = Path(__file__).resolve().parents[2]

RULE_MODEL_VERSION = "rule-mvp-v1"
PADDLE_MODEL_VERSION = "emotion-ernie-mini-local-v1"
PADDLE_EMOTION_MODEL_DIR = Path(
    os.getenv(
        "NLP_EMOTION_MODEL_DIR",
        SERVICE_ROOT / "models" / "emotion-ernie-mini" / "best",
    )
)
PADDLE_INFERENCE_DEVICE = os.getenv("NLP_PADDLE_DEVICE", "auto")

MODEL_VERSION = RULE_MODEL_VERSION

EMOTION_LABELS = {
    "lonely": "孤独",
    "anxious": "焦虑",
    "stressed": "压力",
    "tired": "疲惫",
    "sad": "失落",
    "calm": "平静",
    "healed": "治愈",
    "secure": "安心",
    "happy": "快乐",
    "hopeful": "希望",
}

EMOTION_SENTIMENTS = {
    "lonely": "negative",
    "anxious": "negative",
    "stressed": "negative",
    "tired": "negative",
    "sad": "negative",
    "calm": "neutral",
    "healed": "positive",
    "secure": "positive",
    "happy": "positive",
    "hopeful": "positive",
}

EMOTION_COLORS = {
    "lonely": "#4f46e5",
    "anxious": "#7c3aed",
    "stressed": "#dc2626",
    "tired": "#64748b",
    "sad": "#2563eb",
    "calm": "#14b8a6",
    "healed": "#22c55e",
    "secure": "#0f766e",
    "happy": "#f59e0b",
    "hopeful": "#eab308",
}

EMOTION_DESCRIPTIONS = {
    "lonely": "一个人、没人陪、不被理解的孤独感",
    "anxious": "担心未来、不确定、心慌或害怕结果",
    "stressed": "考试、DDL、任务或工作量带来的压迫感",
    "tired": "身体或心理能量耗尽，觉得撑不动",
    "sad": "难过、委屈、失落或想哭",
    "calm": "情绪稳定、安静，没有强烈正负波动",
    "healed": "被环境、风景、音乐或一句话缓解和治愈",
    "secure": "安心、踏实、安全或被接住",
    "happy": "明确的开心、快乐、幸福或兴奋",
    "hopeful": "对之后仍有期待，觉得还能继续",
}

EMOTION_ORDER = [
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

REACTION_SAFE_MAX_LENGTH = 80
