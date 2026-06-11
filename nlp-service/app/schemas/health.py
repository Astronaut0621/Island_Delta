from pydantic import BaseModel


class HealthResponse(BaseModel):
    status: str
    service: str
    version: str
    model_version: str


class ModelVersionResponse(BaseModel):
    model_name: str
    model_version: str
    engine: str
    paddle_available: bool
    model_path: str
    fallback_reason: str | None = None
    labels: dict[str, str]
    label_metadata: dict[str, dict[str, str | int]]
    capabilities: list[str]
