from pydantic import BaseModel, Field

from app.schemas.nlp import AnalyzeResponse


class ChatMessageRequest(BaseModel):
    message: str = Field(..., min_length=1, max_length=800)
    session_id: str | None = Field(default=None, max_length=64)
    location_name: str | None = Field(default=None, max_length=128)


class ChatMessageResponse(BaseModel):
    session_id: str
    reply: str
    analysis: AnalyzeResponse
    draft_post: str
    actions: list[str]
    # 附近更温暖的地点推荐。负向且非危机情绪时才需要，依赖 backend 地点数据，
    # 当前服务不持有，暂返回空列表占位，对接后填充。
    nearby_warmer_locations: list[str] = Field(default_factory=list)
    model_version: str
