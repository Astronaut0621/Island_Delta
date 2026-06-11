from fastapi import FastAPI

from app.api.routes import router

app = FastAPI(
    title="Island Delta NLP Service",
    version="0.1.0",
    description="Rule-based MVP for Island Delta NLP and agent features.",
)

app.include_router(router)
