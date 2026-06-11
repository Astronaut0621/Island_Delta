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
    model_version: str
