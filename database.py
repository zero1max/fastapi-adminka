from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker

from passlib.context import CryptContext



sqlalchemy_engine = create_async_engine("sqlite+aiosqlite:///./test.db", echo=True)
sqlalchemy_sessionmaker = async_sessionmaker(sqlalchemy_engine, expire_on_commit=False)

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def hash_password(password: str) -> str:
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)