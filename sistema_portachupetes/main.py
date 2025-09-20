from database.models import Base
from database.engine import engine
from sqlalchemy.orm import Session 
from database.models import MaterialPedido, Material, Pedido, Stock

Base.metadata.create_all(engine)