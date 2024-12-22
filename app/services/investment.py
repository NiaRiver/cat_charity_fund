from datetime import datetime as dt
from typing import Union

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
