from sqlalchemy import (
    Boolean, Column, CheckConstraint, DateTime, Integer, func
)


class CharityDonationMixin:
    full_amount = Column(Integer, nullable=False)
    invested_amount = Column(Integer, default=0, nullable=False)
    fully_invested = Column(Boolean, default=False, nullable=False)
    create_date = Column(DateTime, server_default=func.now(), nullable=False)
    close_date = Column(DateTime, nullable=True)

    __table_args__ = (
        CheckConstraint(
            "full_amount > 0",
            name="check_full_amount_gt_0_field"
        ),
    )
