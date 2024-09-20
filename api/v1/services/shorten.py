import string

from fastapi import HTTPException, status
from sqlalchemy.orm import Session
from uuid_extensions import uuid7

from api.core import response_messages
from api.v1.models.short_urls import ShortUrl
from api.v1.models.user import User
from api.v1.schemas import shorten

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
    db: Session, schema: shorten.CreateShortUrl, current_user: User
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


def check_model_existence(db: Session, short_url: str, user: User = None):
    """Checks if a model exists by its id"""

    query = db.query(ShortUrl)

    if user:
        query = query.filter(ShortUrl.user_id == user.id)

    obj = query.filter(ShortUrl.short_code == short_url).first()

    if not obj:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Invalid short code"
        )

    return obj


def get_target_url(db: Session, short_url: str) -> str:
    short_url_object = check_model_existence(db, short_url)

    return short_url_object.target_url


def update_target_url(
    db: Session, current_user: User, short_url: str, new_target_url: str
) -> ShortUrl:
    short_url_object = check_model_existence(
        db=db, user=current_user, short_url=short_url
    )

    short_url_object.target_url = new_target_url

    db.commit()
    db.refresh(short_url_object)


def delete_short_url(db: Session, current_user: User, short_url: str):
    short_url_object = check_model_existence(
        db=db, user=current_user, short_url=short_url
    )

    db.delete(short_url_object)
    db.commit()


def increment_access_count(db: Session, short_url: str):
    short_url_object = check_model_existence(db=db, short_url=short_url)

    count = short_url_object.access_count
    short_url_object.access_count = int(count) + 1

    db.commit()
    db.refresh(short_url_object)
