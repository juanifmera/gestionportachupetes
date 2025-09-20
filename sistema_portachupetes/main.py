from database.models import Base
from database.engine import engine

Base.metadata.create_all(engine)