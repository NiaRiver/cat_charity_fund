from datetime import datetime as dt

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.validators import (
    check_charity_is_open,
    check_charity_name_is_unique,
    check_charity_new_ammout_ge_invested,
    check_project_not_invested_yet,
    check_charity_project_exists
)
from app.core.db import get_async_session
from app.core.user import current_superuser
from app.crud import charity_projects_crud, dontions_crud
from app.schemas.charity_projects import (
    CharityRepresintation, CharityCreate, CharityUpdate
)
from app.services.investment import invest

router = APIRouter()


@router.post(
    "/",
    response_model=CharityRepresintation,
    response_model_exclude_none=True,
    dependencies=[Depends(current_superuser)]
)
async def create_new_charity_project(
    charity_project_obj: CharityCreate,
    session: AsyncSession = Depends(get_async_session)
):
    await check_charity_name_is_unique(charity_project_obj.name, session)
    charity_project_obj = await charity_projects_crud.create(
        charity_project_obj, False, session=session
    )
    open_donations = await dontions_crud.get_all_open(session)
    updated_donations = invest(
        charity_project_obj, open_donations
    )
    session.add_all(updated_donations)
    # for donation in updated_donations:
    #     session.add(donation)
    await session.commit()
    await session.refresh(charity_project_obj)
    return charity_project_obj


@router.get(
    "/",
    response_model=list[CharityRepresintation],
)
async def get_charity_projects(
    session: AsyncSession = Depends(get_async_session)
):
    return await charity_projects_crud.get_all(session)


@router.patch(
    "/{charity_id}",
    response_model=CharityRepresintation,
    response_model_exclude_none=True,
    dependencies=[Depends(current_superuser)]
)
async def partialy_update_charity_project(
    charity_id: int,
    obj_in: CharityUpdate,
    session: AsyncSession = Depends(get_async_session)
):
    charity_project = await check_charity_project_exists(charity_id, session)
    check_charity_is_open(charity_project)
    if obj_in.name is not None:
        await check_charity_name_is_unique(obj_in.name, session)

    if obj_in.full_amount is not None:
        check_charity_new_ammout_ge_invested(
            charity_project,
            obj_in.full_amount
        )
    if obj_in.full_amount == charity_project.invested_amount:
        charity_project.fully_invested = True
        charity_project.close_date = dt.now()
    charity_project = await charity_projects_crud.update(
        charity_project, obj_in, session
    )
    return charity_project


@router.delete(
    "/{project_id}",
    dependencies=[Depends(current_superuser)]
)
async def remove_charity_project(
    project_id: int,
    session: AsyncSession = Depends(get_async_session)
):
    charity_project = await check_charity_project_exists(project_id, session)
    await check_project_not_invested_yet(project_id, session)
    charity_project = await charity_projects_crud.remove(
        charity_project,
        session
    )
    return charity_project
