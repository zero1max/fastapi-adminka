from fastapi import FastAPI
from sqlalchemy import  select, update

from fastadmin import (
    SqlAlchemyInlineModelAdmin, SqlAlchemyModelAdmin,
    WidgetType, action, display, fastapi_app as admin_app, register
)
from models import User, Event, Tournament, BaseEvent, Base
from database import sqlalchemy_engine, sqlalchemy_sessionmaker, verify_password, hash_password


@register(User, sqlalchemy_sessionmaker=sqlalchemy_sessionmaker)
class UserModelAdmin(SqlAlchemyModelAdmin):
    list_display = ("id", "username", "is_superuser")
    list_display_links = ("id", "username")
    list_filter = ("id", "username", "is_superuser")
    search_fields = ("username",)
    formfield_overrides = {
        "username": (WidgetType.SlugInput, {"required": True}),
        "password": (WidgetType.PasswordInput, {"passwordModalForm": True}),
        "avatar_url": (WidgetType.Upload, {"required": False}),
    }

    async def authenticate(self, username, password):
        sessionmaker = self.get_sessionmaker()
        async with sessionmaker() as session:
            stmt = select(User).where(User.username == username)
            result = await session.scalars(stmt)
            user = result.first()
            if user and verify_password(password, user.password) and user.is_superuser:
                return user.id
            return None

    async def change_password(self, user_id, password):
        sessionmaker = self.get_sessionmaker()
        async with sessionmaker() as session:
            hashed_pw = hash_password(password)
            await session.execute(update(User).where(User.id == user_id).values(password=hashed_pw))
            await session.commit()


class EventInlineModelAdmin(SqlAlchemyInlineModelAdmin):
    model = Event


@register(Tournament, sqlalchemy_sessionmaker=sqlalchemy_sessionmaker)
class TournamentModelAdmin(SqlAlchemyModelAdmin):
    list_display = ("id", "name")
    inlines = (EventInlineModelAdmin,)


@register(BaseEvent, sqlalchemy_sessionmaker=sqlalchemy_sessionmaker)
class BaseEventModelAdmin(SqlAlchemyModelAdmin):
    pass


@register(Event, sqlalchemy_sessionmaker=sqlalchemy_sessionmaker)
class EventModelAdmin(SqlAlchemyModelAdmin):
    actions = ("make_is_active", "make_is_not_active")
    list_display = ("id", "name_with_price", "rating", "event_type", "is_active", "started")

    @action(description="Make user active")
    async def make_is_active(self, ids):
        sessionmaker = self.get_sessionmaker()
        async with sessionmaker() as session:
            await session.execute(update(Event).where(Event.id.in_(ids)).values(is_active=True))
            await session.commit()

    @action
    async def make_is_not_active(self, ids):
        sessionmaker = self.get_sessionmaker()
        async with sessionmaker() as session:
            await session.execute(update(Event).where(Event.id.in_(ids)).values(is_active=False))
            await session.commit()

    @display
    async def started(self, obj):
        return bool(obj.start_time)

    @display()
    async def name_with_price(self, obj):
        return f"{obj.name} - {obj.price}"

app = FastAPI()


@app.on_event("startup")
async def startup():
    async with sqlalchemy_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    async with sqlalchemy_sessionmaker() as session:
        exists = await session.scalar(select(User).where(User.username == "admin"))
        if not exists:
            user = User(
                username="admin",
                password=hash_password("admin"),
                is_superuser=True,
            )
            session.add(user)
            await session.commit()


app.mount("/admin/", admin_app)