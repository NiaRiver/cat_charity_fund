def invest(
    target,
    sources
):
    resulted_updates = []
    if sources:
        target_remaining = target.full_amount
        for source in sources:
            if not target.fully_invested:
                source_remaining_amount = (
                    source.full_amount - source.invested_amount
                )
                if source_remaining_amount > target_remaining:
                    target.close()
                    source.invested_amount += target.full_amount
                elif source_remaining_amount < target_remaining:
                    source.close()
                    target.invested_amount += source.full_amount
                else:
                    target.close()
                    source.close()
                resulted_updates.append(source)
    resulted_updates.append(target)
    return resulted_updates
