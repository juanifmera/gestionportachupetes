from connect import engine
from main import session
from models import User, Comment
from sqlalchemy import select

statement = select(Comment).join(Comment.user).where(
    User.username == 'Juan'
).where(
    Comment.text == 'Morcilla te Amo'
)
result = session.scalars(statement).one()
print(result)