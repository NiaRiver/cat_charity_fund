# app/api/meeting_room.py
from datetime import datetime as dt
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.validators import (
    check_charity_project_exists,
    check_charity_new_ammout_ge_invested,
    check_project_not_invested_yet,
    check_charity_name_is_unique,
    check_charity_is_open
)
from app.core.db import get_async_session
from app.core.user import current_superuser
from app.crud.charity_project import charity_projects_crud
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
    charity_project: CharityCreate,
    session: AsyncSession = Depends(get_async_session)
):
    await check_charity_name_is_unique(charity_project.name, session)
    charity_obj = await invest(charity_project, session=session)
    await session.commit()
    await session.refresh(charity_obj)
    return charity_obj


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
    await check_charity_is_open(charity_project)
    if obj_in.name is not None:
        await check_charity_name_is_unique(obj_in.name, session)

    if obj_in.full_amount is not None:
        await check_charity_new_ammout_ge_invested(
            charity_project,
            obj_in.full_amount
        )
    if obj_in.full_amount == charity_project.invested_amount:
        charity_project.fully_invested = True
        charity_project.close_date = dt.now()
    charity_project = await charity_projects_crud.update(
        charity_project, obj_in, session
    )
    await session.commit()
    await session.refresh(charity_project)
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
