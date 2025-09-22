from database.engine import engine
from sqlalchemy.orm import Session
from crud.materiales import eliminar_material
from crud.stock import eliminar_stock
from database.models import MaterialPedido, Material, Stock

try:
    session = Session(bind=engine)

    materiales = session.query(Material).all()

    for item in materiales:
        if item.codigo_material == 'A':
            pass
        else:
            eliminar_material(item.codigo_material)

    print('Exito')

except Exception as e:
    print(e)