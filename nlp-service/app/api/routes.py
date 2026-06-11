from fastapi import APIRouter

from app.core.config import (
    EMOTION_COLORS,
    EMOTION_DESCRIPTIONS,
    EMOTION_LABELS,
    EMOTION_ORDER,
    EMOTION_SENTIMENTS,
    MODEL_VERSION,
)
from app.schemas.chat import ChatMessageRequest, ChatMessageResponse
from app.schemas.health import HealthResponse, ModelVersionResponse
from app.schemas.nlp import (
    AnalyzeRequest,
    AnalyzeResponse,
    FeedbackRequest,
    FeedbackResponse,
    GeneratePostRequest,
    GeneratePostResponse,
)
from app.services.analyzer import analyze_text
from app.services.chat import build_chat_response
from app.services.emotion_engine import get_emotion_engine_status
from app.services.feedback_store import store_feedback
from app.services.generator import generate_public_post
from app.services.safety import detect_safety

router = APIRouter()


@router.get("/health", response_model=HealthResponse)
async def health() -> HealthResponse:
    engine_status = get_emotion_engine_status()
    return HealthResponse(
        status="ok",
        service="island-delta-nlp-service",
        version="0.1.0",
        model_version=engine_status.model_version,
    )


@router.post("/nlp/analyze", response_model=AnalyzeResponse)
async def analyze(request: AnalyzeRequest) -> AnalyzeResponse:
    return analyze_text(request.text, location_name=request.location_name)


@router.post("/nlp/generate-post", response_model=GeneratePostResponse)
async def generate_post(request: GeneratePostRequest) -> GeneratePostResponse:
    analysis = analyze_text(request.text, location_name=request.location_name)
    emotion_name = EMOTION_LABELS.get(request.emotion_type or analysis.emotion_type, analysis.emotion_name)
    temperature = request.temperature if request.temperature is not None else analysis.temperature
    safety = detect_safety(request.text)

    return GeneratePostResponse(
        suggested_content=generate_public_post(
            text=request.text,
            emotion_name=emotion_name,
            temperature=temperature,
            location_name=request.location_name,
        ),
        safety_level=safety.level,
        publishable=safety.level != "crisis",
        model_version=analysis.model_version,
    )


@router.post("/chat/message", response_model=ChatMessageResponse)
async def chat_message(request: ChatMessageRequest) -> ChatMessageResponse:
    return build_chat_response(
        message=request.message,
        session_id=request.session_id,
        location_name=request.location_name,
    )


@router.get("/nlp/model-version", response_model=ModelVersionResponse)
async def model_version() -> ModelVersionResponse:
    engine_status = get_emotion_engine_status()
    return ModelVersionResponse(
        model_name=engine_status.model_name,
        model_version=engine_status.model_version,
        engine=engine_status.engine,
        paddle_available=engine_status.paddle_available,
        model_path=engine_status.model_path,
        fallback_reason=engine_status.fallback_reason,
        labels=EMOTION_LABELS,
        label_metadata={
            code: {
                "name": EMOTION_LABELS[code],
                "sentiment": EMOTION_SENTIMENTS[code],
                "color": EMOTION_COLORS[code],
                "description": EMOTION_DESCRIPTIONS[code],
                "order": index,
            }
            for index, code in enumerate(EMOTION_ORDER)
        },
        capabilities=[
            "emotion_classification",
            "sentiment_analysis",
            "optional_temperature_recommendation",
            "safety_detection",
            "post_generation",
            "basic_agent_chat",
        ],
    )


@router.post("/nlp/feedback", response_model=FeedbackResponse)
async def feedback(request: FeedbackRequest) -> FeedbackResponse:
    engine_status = get_emotion_engine_status()
    stored = store_feedback(request, model_version=engine_status.model_version)
    return FeedbackResponse(
        accepted=request.accepted,
        stored=stored,
        model_version=engine_status.model_version,
    )
