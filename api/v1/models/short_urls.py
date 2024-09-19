from sqlalchemy import Column, String, ForeignKey, Integer
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from api.v1.models.base_model import BaseTableModel


class ShortUrl(BaseTableModel):
    __tablename__ = "short_urls"

    user_id = Column(String, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    target_url = Column(String, nullable=False)
    short_code = Column(String, nullable=False)
    access_count = Column(Integer, nullable=True)

    user = relationship("User", back_populates="short_urls")
