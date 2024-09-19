import string

from fastapi import HTTPException, status
from sqlalchemy.orm import Session
from uuid import UUID
from uuid_extensions import uuid7

from api.core import response_messages
from api.v1.models.short_urls import ShortUrl
from api.v1.models.user import User
from api.v1.schemas import url_shortener

# Base62 character set
BASE62 = string.ascii_letters + string.digits


def encode_base62(num: int) -> str:
    """Function to encode an integer to a Base62 string

    Args:
        num (int): integer to encode

    Returns:
        str: Base62 encoded integer
    """
    if num == 0:
        return BASE62[0]

    encoded = []
    base = len(BASE62)

    while num > 0:
        encoded.append(BASE62[num % base])
        num //= base

    # Return the reversed list to form the correct Base62 string
    return "".join(reversed(encoded))


def generate_short_code(length: int = 7) -> str:
    """Generate a short code from uuid

    Args:
        length (int, optional): length of the short code. Defaults to 7.

    Returns:
        str: generated short code
    """
    unique_id = uuid7().int
    encoded_id = encode_base62(unique_id)
    return encoded_id[-length:]


def create_shortened_url(
    db: Session, schema: url_shortener.CreateShortUrl, current_user: User
) -> ShortUrl:
    target_url = schema.target_url
    custom_alias = schema.custom_alias
    length = schema.length

    if custom_alias:
        url_string = custom_alias
    else:
        url_string = generate_short_code(length=length)

    existing_url = db.query(ShortUrl).filter(ShortUrl.short_code == url_string).first()

    if existing_url:
        raise HTTPException(status_code=400, detail=response_messages.ALIAS_IN_USE)

    short_url = ShortUrl(
        target_url=target_url, short_code=url_string, user_id=current_user.id
    )

    db.add(short_url)
    db.commit()
    db.refresh(short_url)

    return short_url


def get_target_url(db: Session, short_url: str) -> str:
    short_url_object = (
        db.query(ShortUrl).filter(ShortUrl.short_code == short_url).first()
    )

    if not short_url_object:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Invalid short code"
        )

    return short_url_object.target_url
