from fastapi import APIRouter

from api.v1.routes.auth import auth
from api.v1.routes.url_shortener import shorten

main_router = APIRouter(prefix="/api/v1")

main_router.include_router(router=auth)
main_router.include_router(router=shorten)
