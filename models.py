from sqlalchemy.orm import DeclarativeBase, mapped_column, Mapped, relationship
from sqlalchemy import ForeignKey, Text
from typing import Optional

class Base(DeclarativeBase):
    pass

class User(Base):
    __tablename__= 'user'
    id:Mapped[int] = mapped_column(primarykey=True, autoincrement=True, nullable=False)
    username:Mapped[str] = mapped_column(nullable=False)
    email:Mapped[Optional[str]] = mapped_column(nullable=True)

class Comment(Base):
    __tablename__ = 'comments'
    id:Mapped[int] = mapped_column(primary_key=True, autoincrement=True, nullable=False)
    user_id:Mapped[int] = mapped_column(ForeignKey('user.id'), nullable=False)
    text:Mapped[str] = mapped_column(Text, nullable=False)

    