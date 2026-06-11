from pydantic import BaseModel, Field


class AnalyzeRequest(BaseModel):
    text: str = Field(..., min_length=1, max_length=500)
    location_name: str | None = Field(default=None, max_length=128)


class AnalyzeResponse(BaseModel):
    emotion_type: str
    emotion_name: str
    sentiment: str
    temperature: int
    safety_level: str
    confidence: float
    model_version: str
    suggested_content: str
    safety_message: str | None = None


class GeneratePostRequest(BaseModel):
    text: str = Field(..., min_length=1, max_length=500)
    emotion_type: str | None = Field(default=None, max_length=32)
    temperature: int | None = Field(default=None, ge=-10, le=10)
    location_name: str | None = Field(default=None, max_length=128)


class GeneratePostResponse(BaseModel):
    suggested_content: str
    safety_level: str
    publishable: bool
    model_version: str


class FeedbackRequest(BaseModel):
    text: str = Field(..., min_length=1, max_length=500)
    original_emotion: str | None = Field(default=None, max_length=32)
    corrected_emotion: str | None = Field(default=None, max_length=32)
    original_temperature: int | None = Field(default=None, ge=-10, le=10)
    corrected_temperature: int | None = Field(default=None, ge=-10, le=10)
    accepted: bool


class FeedbackResponse(BaseModel):
    accepted: bool
    stored: bool
    model_version: str
