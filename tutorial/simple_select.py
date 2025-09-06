from persisting import session
from sqlalchemy import select
from models import User, Comment
from main import session

'''statement = select(User).where(User.username.in_(['Juan', 'cathy']))
result = session.scalars(statement)
for user in result:
    print(user)'''

users = session.query(User).all()

for user in users:
    print(user.username)