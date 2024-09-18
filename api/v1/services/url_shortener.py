from fastapi import HTTPException, status
from uuid_extensions import uuid7
from sqlalchemy.orm import Session

from api.v1.models.short_urls import ShortUrl
from api.core import response_messages


def generate_random_short_url(length: int = 8) -> str:
    uuid = uuid7()

    return uuid.hex[:length]


def create_shortened_url(
    db: Session, length: int, target_url: str, custom_alias: str = None
) -> ShortUrl:
    if custom_alias:
        url_string = custom_alias
    else:
        url_string = generate_random_short_url(length=length)

    existing_url = db.query(ShortUrl).filter(ShortUrl.short_url == url_string).first()

    if existing_url:
        raise HTTPException(status_code=400, detail=response_messages.ALIAS_IN_USE)

    short_url = ShortUrl(target_url=target_url, short_url=url_string)

    db.add(short_url)
    db.commit()
    db.refresh(short_url)

    return short_url


def get_target_url(db: Session, short_url: str) -> str:
    short_url_object = (
        db.query(ShortUrl).filter(ShortUrl.short_url == short_url).first()
    )

    return short_url_object.target_url
