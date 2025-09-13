from sqlalchemy.orm import DeclarativeBase, mapped_column, Mapped, relationship
from sqlalchemy import ForeignKey, Text
from typing import Optional, List

class Base(DeclarativeBase):
    pass

class User(Base):
    __tablename__= 'user'
    id:Mapped[int] = mapped_column(primary_key=True, autoincrement=True, nullable=False)
    username:Mapped[str] = mapped_column(nullable=False)
    email:Mapped[Optional[str]] = mapped_column(nullable=True)
    comments:Mapped[List['Comment']] = relationship(back_populates='user')

    def __repr__(self):
        return f'<User username:{self.username}>'

class Comment(Base):
    __tablename__ = 'comments'
    id:Mapped[int] = mapped_column(primary_key=True, autoincrement=True, nullable=False)
    user_id:Mapped[int] = mapped_column(ForeignKey('user.id'), nullable=False)
    text:Mapped[str] = mapped_column(Text, nullable=False)
    user:Mapped['User'] = relationship(back_populates='comments')

    def __repr__(self):
        return f'<Comment {self.text}, created by {self.user}'