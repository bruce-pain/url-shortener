from fastapi import APIRouter, Depends, status, Request, HTTPException
from sqlalchemy.orm import Session
from typing import Annotated

from api.db.database import get_db
from api.core.dependencies.security import get_current_user
from api.v1.services import url_shortener as url_service
from api.v1.schemas import url_shortener as url_schema
from api.v1.models import User

shorten = APIRouter(prefix="/shorten", tags=["Shortener"])


@shorten.post(
    path="",
    response_model=url_schema.CreateShortUrlResponse,
    summary="Create short url",
    description="Endpoint to generate a short url",
    status_code=status.HTTP_201_CREATED,
)
def generate_url(
    db: Annotated[Session, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)],
    schema: url_schema.CreateShortUrl,
) -> url_schema.CreateShortUrlResponse:
    """Endpoint to generate a short url

    Args:
        db (Annotated[Session, Depends): Database Session
        current_user (Annotated[User, Depends): Currently logged in user
        schema (url_schema.CreateShortUrl): ShortUrl Request Schema

    Returns:
        url_schema.CreateShortUrlResponse: ShortUrl Response Schema
    """
    short_url = url_service.create_shortened_url(
        db=db, schema=schema, current_user=current_user
    )

    response_data = url_schema.ShortUrlData(
        id=short_url.id,
        target_url=short_url.target_url,
        short_code=short_url.short_code,
        created_at=short_url.created_at,
        updated_at=short_url.updated_at,
    )

    return url_schema.CreateShortUrlResponse(
        status_code=status.HTTP_201_CREATED,
        message="Short URL generated successfully!",
        data=response_data,
    )
