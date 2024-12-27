from datetime import datetime as dt

from app.models.base import CharityDonationBase


def invest(
    target: CharityDonationBase,
    sources: list[CharityDonationBase]
) -> list[CharityDonationBase]:
    updates = []
    invest_date = dt.now()
    for source in sources:
        target_remaining_amount = (
            target.full_amount - (target.invested_amount or 0)
        )
        if target_remaining_amount > 0:
            source_remaining_amount = (
                source.full_amount - source.invested_amount
            )
            if source_remaining_amount >= target_remaining_amount:
                target.invested_amount = target.full_amount
                source.invested_amount += target_remaining_amount
            else:
                source.invested_amount = source.full_amount
                target.invested_amount += source_remaining_amount
            source.fully_invested = (
                source.invested_amount == source.full_amount
            )
            source.close_date = invest_date if source.fully_invested else None
            updates.append(source)
    target.fully_invested = (
        target.invested_amount == target.full_amount
    )
    target.close_date = invest_date if target.fully_invested else None
    return updates
