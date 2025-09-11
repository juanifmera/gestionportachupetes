import os
from sqlalchemy import create_engine

DB_PATH = os.path.join(os.path.dirname(__file__), 'stock.db')
engine = create_engine(f'sqlite:///{DB_PATH}', echo=False)

morcilla = input('')