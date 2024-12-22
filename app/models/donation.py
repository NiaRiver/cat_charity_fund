from sqlalchemy import Column, ForeignKey, Integer, Text

from app.core.db import Base
from .mixins import CharityDonationMixin


class Donation(Base, CharityDonationMixin):
    comment = Column(Text, nullable=True)
    user_id = Column(Integer, ForeignKey('user.id'), nullable=False)
