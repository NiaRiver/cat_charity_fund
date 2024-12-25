from sqlalchemy import (
    Boolean, Column, CheckConstraint, DateTime, Integer, func
)


class CharityDonationBase:
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
        CheckConstraint(
            "invested_amount >= 0",
            name="check_invested_amount_ge_0_field"
        ), CheckConstraint(
            "invested_amount <= full_amount",
            name="check_invested_amount_le_full_amount"
        )
    )

    def __repr__(self):
        return (f"{type(self).__name__}, full amount: {self.full_amount}, " +
                f"Invested amount: {self.invested_amount}, " +
                f"Create date: {self.create_date}, " +
                f"Close date: {self.close_date}, " +
                f"Is open: {not self.fully_invested}")
