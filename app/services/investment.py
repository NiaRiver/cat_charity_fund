from datetime import datetime as dt
from typing import Union

from app.models import CharityProject, Donation


def invest(
        target: Union[CharityProject, Donation],
        sources: list[Union[CharityProject, Donation]]
) -> tuple[
    Union[CharityProject, Donation], list[Union[CharityProject, Donation]]
]:
    results_data = []
    income_amount = target.full_amount
    close_date = dt.now()
    if sources:
        first_source = sources.pop(0)
        remaining_full = [source.full_amount for source in sources]
        remaining_sum = sum(remaining_full)
        first_remaining = (
            first_source.full_amount - first_source.invested_amount
        )
        if income_amount < first_remaining:
            first_source.invested_amount += income_amount
            target.invested_amount = target.full_amount
            target.fully_invested = True
            target.close_date = close_date
            return target, [first_source]
        first_source.invested_amount = first_source.full_amount
        first_source.fully_invested = True
        first_source.close_date = close_date
        target.invested_amount = first_remaining
        income_remaining = income_amount - first_remaining
        if income_remaining >= remaining_sum:
            for source in sources:
                source.invested_amount += source.full_amount
                source.fully_invested = True
                results_data.append(source)
            target.invested_amount += remaining_sum
            target.fully_invested = (
                target.invested_amount == target.full_amount
            )
            if target.fully_invested:
                target.close_date = close_date
            results_data.append(first_source)
            return target, results_data

        for index, full in enumerate(remaining_full):
            if full <= income_remaining:
                target.invested_amount += full
                sources[index].invested_amount = full
                sources[index].fully_invested = True
                sources[index].close_date = close_date
                results_data.append(sources[index])
                income_remaining -= full
                target.fully_invested = (
                    target.invested_amount == target.full_amount
                )
                if target.fully_invested:
                    target.close_date = close_date
                    break
                continue
            sources[index].invested_amount = income_remaining
            results_data.append(sources[index])
            target.invested_amount = target.full_amount
            target.fully_invested = True
            target.close_date = close_date
            break
        results_data.append(first_source)
    return target, results_data
