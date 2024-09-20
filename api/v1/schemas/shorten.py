from typing import Optional

from datetime import datetime
from pydantic import BaseModel
from api.v1.schemas.base_schema import BaseResponseModel


class CreateShortUrl(BaseModel):
    target_url: str
    length: int = 7
    custom_alias: Optional[str] = None


class ShortUrlData(BaseModel):
    id: str
    target_url: str
    short_code: str
    created_at: datetime
    updated_at: datetime


class CreateShortUrlResponse(BaseResponseModel):
    data: ShortUrlData
