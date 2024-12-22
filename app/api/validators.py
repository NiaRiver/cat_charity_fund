from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.crud import charity_projects_crud
from app.models import CharityProject


async def check_charity_project_exists(
        charity_id: int,
        session: AsyncSession,
) -> CharityProject:
    charity = await charity_projects_crud.get(
        charity_id, session
    )
    if charity is None:
        raise HTTPException(
            status_code=422,
            detail='Сбор не найден!'
        )
    return charity


async def check_charity_name_is_unique(
        project_name: str,
        session: AsyncSession,
) -> CharityProject:
    charity = await charity_projects_crud.get_charity_project_by_name(
        project_name, session
    )
    if charity is not None:
        raise HTTPException(
            status_code=400,
            detail=(
                'Проект с таким именем уже существует!'
            )
        )


async def check_charity_is_open(
        charity_obj
) -> CharityProject:
    if charity_obj.fully_invested is True:
        raise HTTPException(
            status_code=400,
            detail=(
                'Закрытый проект нельзя редактировать!'
            )
        )


async def check_charity_new_ammout_ge_invested(
        charity_obj,
        new_amount: int,
) -> CharityProject:
    if charity_obj.invested_amount > new_amount:
        raise HTTPException(
            status_code=400,
            detail=(
                'Нелья установить значение ' +
                'full_amount меньше уже вложенной суммы.'
            )
        )


async def check_project_not_invested_yet(
        charity_id: int,
        session: AsyncSession,
) -> CharityProject:
    charity: CharityProject = await charity_projects_crud.get(
        charity_id, session
    )
    if charity.invested_amount > 0:
        raise HTTPException(
            status_code=400,
            detail=(
                'Нелья установить значение ' +
                'full_amount меньше уже вложенной суммы.'
            )
        )
    return charity
