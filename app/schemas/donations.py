# app/schemas/meeting_room.py
from datetime import datetime as dt
from typing import Optional

from pydantic import BaseModel, Field


class DonationBase(BaseModel):
    full_amount: int = Field(gt=0)
    comment: Optional[str] = Field(min_length=1)


class DonationCreate(DonationBase):
    pass


class DonationUpdate(DonationCreate):
    pass

    # @validator("name")
    # def validate_name_is_not_none(cls, value):
    #     if value is None:
    #         # При ошибке валидации можно выбросить
    #         # ValueError, TypeError или AssertionError.
    #         # В нашем случае подходит ValueError.
    #         # В аргумент передаём сообщение об ошибке.
    #         raise ValueError("Имя переговорки не может быть пустым!")
    #     # Если проверка пройдена, возвращаем значение поля.
    #     return value


class DonationRepresintation(DonationBase):
    id: int
    create_date: dt

    class Config:
        orm_mode = True


class SUDonationRepresintation(DonationRepresintation):
    user_id: int
    invested_amount: int
    fully_invested: bool
    close_date: Optional[dt] = None

    class Config:
        orm_mode = True
