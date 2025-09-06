from main import session
from connect import engine
from models import User

juan = session.query(User).filter_by(username = 'Morcilla Macias').first()

