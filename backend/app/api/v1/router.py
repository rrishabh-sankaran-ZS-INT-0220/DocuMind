from fastapi import APIRouter

from backend.app.api.v1 import auth, documents, health, qa, collections

api_router = APIRouter()

api_router.include_router(health.router)
api_router.include_router(auth.router)
api_router.include_router(documents.router)
api_router.include_router(collections.router)
api_router.include_router(qa.router)