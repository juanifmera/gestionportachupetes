from database.models import Base
from database.engine import engine
from sqlalchemy.orm import Session 
from database.models import MaterialPedido, Material, Pedido, Stock

try:
    Base.metadata.create_all(engine)
    print('Exito')

except Exception as e:
    print(e)