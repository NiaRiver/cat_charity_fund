from sqlalchemy import Column, String, Text

from app.core.db import Base
from .mixins import CharityDonationMixin


class CharityProject(Base, CharityDonationMixin):
    name = Column(String(100), unique=True, nullable=False)
    description = Column(Text, nullable=False)
