from models import User, Comment
from sqlalchemy.orm import Session
from connect import engine
from main import session

user1 = User(
    username='Juan',
    email='juanignaciofmera@gmail.com',
    comments=[
        Comment(text='Morcilla te Amo'),
        Comment(text='Morcilla Te Amo x 2')
    ]
)

user2 = User(
    username='Morcilla Macias',
    email = 'morcillalinda123@gmail.com',
    comments=[
        Comment(text='Hola Morcillo'),
        Comment(text='Hola Morcillo, Te amo')
    ]
)

user3 = User(
    username='cathy',
    email='cathy@gmail.com'
)