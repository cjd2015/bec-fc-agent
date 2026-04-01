from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from src.api.routes import auth, users, level_test, vocab, patterns, scenes, mock_exams, content, review, health
from src.core.config import settings


def create_app() -> FastAPI:
    app = FastAPI(
        title=settings.app_name,
        debug=settings.app_debug,
        version="1.0.0",
    )

    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_allow_origins,
        allow_credentials=settings.cors_allow_credentials,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    app.include_router(health.router, prefix=settings.api_prefix, tags=["health"])
    app.include_router(auth.router, prefix=f"{settings.api_prefix}/auth", tags=["auth"])
    app.include_router(users.router, prefix=f"{settings.api_prefix}/users", tags=["users"])
    app.include_router(level_test.router, prefix=f"{settings.api_prefix}/level-test", tags=["level-test"])
    app.include_router(vocab.router, prefix=f"{settings.api_prefix}/vocab", tags=["vocab"])
    app.include_router(patterns.router, prefix=f"{settings.api_prefix}/patterns", tags=["patterns"])
    app.include_router(scenes.router, prefix=f"{settings.api_prefix}/scenes", tags=["scenes"])
    app.include_router(mock_exams.router, prefix=f"{settings.api_prefix}/mock-exams", tags=["mock-exams"])
    app.include_router(content.router, prefix=f"{settings.api_prefix}/content", tags=["content"])
    app.include_router(review.router, prefix=f"{settings.api_prefix}/review", tags=["review"])

    return app


app = create_app()
