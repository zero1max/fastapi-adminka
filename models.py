import datetime
import typing as tp
from decimal import Decimal
from enum import Enum

from sqlalchemy import (
    JSON, Boolean, Column, Date, DateTime, Float, ForeignKey,
    Integer, String, Table, Text, Time, select, update
)
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship



class EventTypeEnum(str, Enum):
    PRIVATE = "PRIVATE"
    PUBLIC = "PUBLIC"


class Base(DeclarativeBase):
    pass


class BaseModel(Base):
    __abstract__ = True

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    created_at: Mapped[datetime.datetime] = mapped_column(DateTime, default=datetime.datetime.utcnow)
    updated_at: Mapped[datetime.datetime] = mapped_column(DateTime, default=datetime.datetime.utcnow,
                                                          onupdate=datetime.datetime.utcnow)


user_m2m_event = Table(
    "event_participants",
    Base.metadata,
    Column("event_id", ForeignKey("event.id"), primary_key=True),
    Column("user_id", ForeignKey("user.id"), primary_key=True),
)


class User(BaseModel):
    __tablename__ = "user"
    username: Mapped[str] = mapped_column(String(255), nullable=False)
    password: Mapped[str] = mapped_column(String(255), nullable=False)
    is_superuser: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    avatar_url: Mapped[str | None] = mapped_column(String(255), nullable=True)
    events: Mapped[list["Event"]] = relationship(secondary=user_m2m_event, back_populates="participants")

    def __str__(self):
        return self.username


class Tournament(BaseModel):
    __tablename__ = "tournament"
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    events: Mapped[list["Event"]] = relationship(back_populates="tournament")

    def __str__(self):
        return self.name


class BaseEvent(BaseModel):
    __tablename__ = "base_event"
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    event: Mapped[tp.Optional["Event"]] = relationship(back_populates="base")

    def __str__(self):
        return self.name


class Event(BaseModel):
    __tablename__ = "event"
    base_id: Mapped[int | None] = mapped_column(ForeignKey("base_event.id"), nullable=True)
    base: Mapped[tp.Optional["BaseEvent"]] = relationship(back_populates="event")

    name: Mapped[str] = mapped_column(String(255), nullable=False)
    tournament_id: Mapped[int | None] = mapped_column(ForeignKey("tournament.id"), nullable=False)
    tournament: Mapped[tp.Optional["Tournament"]] = relationship(back_populates="events")
    participants: Mapped[list["User"]] = relationship(secondary=user_m2m_event, back_populates="events")

    rating: Mapped[int] = mapped_column(Integer, default=0)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    event_type: Mapped[EventTypeEnum] = mapped_column(default=EventTypeEnum.PUBLIC)
    is_active: Mapped[bool] = mapped_column(Boolean, default=False)
    start_time: Mapped[datetime.time | None] = mapped_column(Time)
    date: Mapped[datetime.date | None] = mapped_column(Date)
    latitude: Mapped[float | None] = mapped_column(Float)
    longitude: Mapped[float | None] = mapped_column(Float)
    price: Mapped[Decimal | None] = mapped_column(Float(asdecimal=True))
    json: Mapped[dict | None] = mapped_column(JSON)

    def __str__(self):
        return self.name
