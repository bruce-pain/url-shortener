from fastapi import APIRouter, Depends, status, Request, HTTPException
from sqlalchemy.orm import Session
from typing import Annotated

from api.db.database import get_db
from api.core.dependencies.security import get_current_user
from api.v1.services import shorten as url_service
from api.v1.schemas import shorten as url_schema
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
        access_count=short_url.access_count,
    )

    return url_schema.CreateShortUrlResponse(
        status_code=status.HTTP_201_CREATED,
        message="Short URL generated successfully!",
        data=response_data,
    )


@shorten.get(
    path="",
    response_model=url_schema.AllShortUrlsResponse,
    summary="Retrieve all short url",
    description="Endpoint to retrieve all short url data for current user",
    status_code=status.HTTP_200_OK,
)
def retrieve_all_url(
    db: Annotated[Session, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)],
):
    return url_service.get_all_short_urls(db=db, current_user=current_user)


@shorten.get(
    path="/{short_url}",
    response_model=url_schema.UpdateShortUrlResponse,
    summary="Retrieve short url",
    description="Endpoint to retrieve short url data",
    status_code=status.HTTP_200_OK,
)
def retrieve_url(
    short_url: str,
    db: Annotated[Session, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)],
):
    short_url = url_service.get_short_url(
        db=db, short_url=short_url, current_user=current_user
    )

    response_data = url_schema.ShortUrlData(
        id=short_url.id,
        target_url=short_url.target_url,
        short_code=short_url.short_code,
        created_at=short_url.created_at,
        updated_at=short_url.updated_at,
        access_count=short_url.access_count,
    )

    return url_schema.UpdateShortUrlResponse(
        status_code=status.HTTP_200_OK,
        message="Target url retrieved successfully!",
        data=response_data,
    )


@shorten.put(
    path="/{short_url}",
    response_model=url_schema.UpdateShortUrlResponse,
    summary="Update the target url",
    description="Endpoint to change the target url for a given short code",
    status_code=status.HTTP_200_OK,
)
def update_url(
    short_url: str,
    schema: url_schema.UpdateShortUrl,
    db: Annotated[Session, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)],
):
    short_url = url_service.update_target_url(
        db=db,
        current_user=current_user,
        short_url=short_url,
        new_target_url=schema.target_url,
    )

    response_data = url_schema.ShortUrlData(
        id=short_url.id,
        target_url=short_url.target_url,
        short_code=short_url.short_code,
        created_at=short_url.created_at,
        updated_at=short_url.updated_at,
        access_count=short_url.access_count,
    )

    return url_schema.UpdateShortUrlResponse(
        status_code=status.HTTP_200_OK,
        message="Target url successfully updated!",
        data=response_data,
    )


@shorten.delete(
    path="/{short_url}",
    summary="Delete the short url",
    description="Endpoint to delete the short url from the database",
    status_code=status.HTTP_204_NO_CONTENT,
)
def delete_url(
    short_url: str,
    db: Annotated[Session, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)],
):
    url_service.delete_short_url(db=db, current_user=current_user, short_url=short_url)
