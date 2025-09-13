from persisting import session
from sqlalchemy import select
from models import User, Comment
from main import session

comment = session.query(Comment).filter_by(id=2).update({'text':'Morcilla Te Amo x 3'}) 
session.commit()