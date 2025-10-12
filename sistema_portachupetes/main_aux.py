from database.engine import engine
from sqlalchemy.orm import Session
from crud.materiales import eliminar_material, actualizar_varios_campos
from crud.stock import eliminar_stock, agregar_stock, listar_stock
from crud.pedidos import crear_pedido_dummy, actualizar_varios_campos_pedido_aux, eliminar_pedido
from database.models import MaterialPedido, Material, Stock

try:
    session = Session(bind=engine)
    
    '''print(crear_pedido_dummy(
        cliente="EJEMPLO",
        materiales_portachupete={
            "broche": "LLAVERO",
            "nombre": "AMANDA",
            "dijes_normales": [{'codigo': '120'}],
            "dijes_especiales": [{'codigo': '001'}],
            "bolitas": [{"codigo": "BBLA", "cantidad": 3}, 
                        {"codigo": "BAZU", "cantidad": 3}],
            "lentejas": [{"codigo": "LNEG", "cantidad": 2},
                        {"codigo": "LBEI", "cantidad": 2}],
        },
        telefono="123456789",
    ))'''
    
except Exception as e:
    print(e)
    