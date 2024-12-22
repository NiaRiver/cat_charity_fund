from datetime import datetime as dt

from fastapi.encoders import jsonable_encoder
from sqlalchemy import select, func
from sqlalchemy.sql.functions import coalesce
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.user import User


class CRUDBase:
    def __init__(self, model):
        self.model = model

    async def get(
        self,
        obj_id: int,
        session: AsyncSession
    ):
        db_obj = await session.execute(
            select(self.model).where(self.model.id == obj_id)
        )
        return db_obj.scalars().first()

    async def get_last(
        self,
        session: AsyncSession
    ):
        db_obj = await session.execute(
            select(self.model).order_by(
                self.model.id.desc()
            )
        )
        return db_obj.scalars().first()

    async def get_all(
        self,
        session: AsyncSession
    ):
        db_objs = await session.scalars(
            select(self.model)
        )
        return db_objs.all()

    async def create(
        self,
        obj_in,
        session: AsyncSession,
        user: User
    ):
        obj_in_data = obj_in.dict()
        db_obj = self.model(**obj_in_data)
        session.add(db_obj)
        await session.commit()
        await session.refresh(db_obj)
        return db_obj

    async def update(
        self,
        db_obj,
        obj_in,
        session: AsyncSession
    ):
        obj_data = jsonable_encoder(db_obj)
        update_data = obj_in.dict(exclude_unset=True)
        for key in obj_data:
            if key in update_data:
                setattr(db_obj, key, update_data[key])
        session.add(db_obj)
        await session.commit()
        await session.refresh(db_obj)
        return db_obj

    async def remove(
        self,
        db_obj,
        session: AsyncSession
    ):
        await session.delete(db_obj)
        await session.commit()
        return db_obj


class CharityDonationCRUDBase(CRUDBase):
    async def get_last_fully_invested(
        self,
        session: AsyncSession,
    ):
        last_fully_invested = await session.scalars(
            select(self.model).order_by(self.model.id.desc()).where(
                self.model.fully_invested is True
            )
        )
        last_fully_invested = last_fully_invested.first()
        return last_fully_invested

    async def get_total_invested_amount(
        self,
        session: AsyncSession,
    ):
        total_invested_ammount = await session.scalar(
            select(func.sum(self.model.invested_amount))
        )
        return total_invested_ammount

    async def get_total_full_amount(
        self,
        session: AsyncSession,
    ):
        total_invested_ammount = await session.scalar(
            select(func.sum(self.model.full_amount))
        )
        print(total_invested_ammount)
        return total_invested_ammount

    async def get_current_investment(
        self,
        session: AsyncSession,
    ):
        current_invested = await session.scalars(
            select(
                self.model
            ).where(
                self.model.full_amount != self.model.invested_amount
            )
        )
        return current_invested.first() or await self.get_last(session)

    async def get_rest_uninvested(
        self,
        session: AsyncSession,
    ):
        current = await self.get_current_investment(session)
        if current is None:
            last_obj = await session.scalars(
                select(self.model).order_by(self.model.id.desc())
            )
            current = last_obj.first()
        sum_func = func.sum(self.model.full_amount).over(
            order_by=self.model.id
        )
        current_id = 0 if current is None else current.id
        select_stmt = select(
            self.model.id,
            self.model.full_amount,
            coalesce(sum_func, 0)
            .label("cumulative_sum"),
        ).where(self.model.id > current_id)
        select_stmt = select(
            select_stmt.c.cumulative_sum
        ).order_by(select_stmt.c.id.desc()).limit(1)
        sub_sum = await session.scalars(select_stmt)
        current_rest = 0 if current is None else (
            current.full_amount - current.invested_amount
        )
        rest_amount = current_rest + (sub_sum.first() or 0)
        return rest_amount

    async def is_ge_than_currents_rest(
        self,
        added_value: int,
        currrent_investment,
        session: AsyncSession,
    ):
        currents_rest_amount = 0 if not currrent_investment else (
            currrent_investment.full_amount -
            currrent_investment.invested_amount
        )
        return added_value >= currents_rest_amount

    async def get_cumulative_full(
        self, session
    ):
        full = await session.scalar(
            select(func.sum(self.model.full_amount))
        )
        return full or 0

    async def add_new_value(
        self,
        added_value: int,
        session: AsyncSession,
    ):
        current = await self.get_current_investment(session)
        if await self.is_ge_than_currents_rest(
            added_value,
            current,
            session
        ):
            if current is not None:
                subquery = (
                    select(
                        self.model,
                        func.sum(self.model.full_amount)
                        .over(order_by=self.model.id)
                        .label("cumulative_sum"),
                    ).subquery()
                )
                subquery = select(self.model).join(
                    subquery, self.model.id == subquery.c.id
                ).where(
                    (
                        subquery.c.cumulative_sum - current.invested_amount
                    ) <= added_value,
                    subquery.c.id >= current.id
                ).order_by(subquery.c.id.desc()).limit(1)
                result = await session.scalars(subquery)
                sub_objects = result.all()
                added_rest_value = added_value - (
                    current.full_amount - current.invested_amount
                )
                time = dt.now()
                if added_rest_value > 0:
                    current.fully_invested = True
                    current.invested_amount = current.full_amount
                    current.close_date = time
                    session.add(current)
                for object in sub_objects:
                    object.fully_invested = True
                    object.close_date = time
                    object.invested_amount = object.full_amount
                    session.add(object)
        else:
            current.invested_amount += added_value
            session.add(current)
