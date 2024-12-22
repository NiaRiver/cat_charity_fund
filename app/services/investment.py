from datetime import datetime as dt
from typing import Union, Optional

from app.crud import dontions_crud, charity_projects_crud
from app.schemas import CharityBase, DonationBase

CRUD_DICT = {
    True: charity_projects_crud,
    False: dontions_crud
}


async def invest(
        obj_in: Union[CharityBase, DonationBase],
        *,
        db_obj=None,
        session
):
    obj_schema = isinstance(obj_in, CharityBase)
    obj_in_crud = CRUD_DICT[obj_schema]
    investing_crud = CRUD_DICT[not obj_schema]
    time = dt.now()
    investing_uninvested = await investing_crud.get_rest_uninvested(session)
    obj_in_data = obj_in.dict(exclude_unset=True)
    if investing_uninvested > 0:
        remaining_amount = investing_uninvested - obj_in.full_amount
        obj_in_data["fully_invested"] = remaining_amount >= 0
        obj_in_data["invested_amount"] = (
            obj_in_data["full_amount"] if obj_in_data["fully_invested"] else
            investing_uninvested
        )
        obj_in_data["close_date"] = (
            time if obj_in_data["fully_invested"] else None
        )
        await investing_crud.add_new_value(obj_in.full_amount, session)

    db_obj = obj_in_crud.model(**obj_in_data)
    session.add(db_obj)
    return db_obj


# async def invest(
#     obj_in: Union[CharityBase, DonationBase],
#     session,
# ) -> Optional[Union[CharityBase, DonationBase]]:
#     # Determine CRUD operations based on input type
#     obj_type = type(obj_in)
#     obj_in_crud = CRUD_DICT[obj_type]
#     investing_crud = CRUD_DICT[DonationBase if obj_type is CharityBase else CharityBase]

#     # Retrieve uninvested entities
#     uninvested_items = await investing_crud.get_rest_uninvested(session)
#     if not uninvested_items:
#         # No items to invest against
#         return None

#     # Prepare input data
#     obj_in_data = obj_in.dict(exclude_unset=True)
#     remaining_amount = obj_in.full_amount
#     time = dt.now()

#     # Perform investments
#     for item in uninvested_items:
#         investable_amount = min(remaining_amount, item.remaining_amount)
#         item.invested_amount += investable_amount
#         remaining_amount -= investable_amount

#         # Update item fully invested status
#         if item.invested_amount == item.full_amount:
#             item.fully_invested = True
#             item.close_date = time

#         if remaining_amount == 0:
#             break

#     # Update obj_in investment status
#     obj_in_data["invested_amount"] = obj_in.full_amount - remaining_amount
#     obj_in_data["fully_invested"] = remaining_amount == 0
#     obj_in_data["close_date"] = time if obj_in_data["fully_invested"] else None

#     # Create and add database object
#     db_obj = obj_in_crud.model(**obj_in_data)
#     session.add(db_obj)

#     return db_obj