from database.engine import engine
from sqlalchemy.orm import Session
from crud.materiales import eliminar_material
from crud.stock import eliminar_stock, agregar_stock
from database.models import MaterialPedido, Material, Stock

try:
    session = Session(bind=engine)

    materiales = session.query(Material).all()
    agregar_stock('A', 53)

    print('Exito')

except Exception as e:
    print(e)