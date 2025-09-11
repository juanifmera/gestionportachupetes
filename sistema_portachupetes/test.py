from database.models import Material, Stock, Base
from database.engine import engine
from sqlalchemy.orm import Session, query
from sqlalchemy import select
from datetime import datetime
from crud.materiales import agregar_material, actualizar_material, eliminar_material, listo_todo, listo_con_filtro, validar_material
from crud.stock import agregar_stock, eliminar_stock, actualizar_stock, reducir_stock, listar_stock
from logic.verificador2 import verificar_confeccion_portachupetes
from crud.pedidos import generar_pedido, cancelar_pedido, terminar_pedido, modificar_pedido

try:
    session = Session(bind=engine)

    print(verificar_confeccion_portachupetes(data={
    "broche": "PAZU",
    "nombre": "juan",  # opcional
    "dije_normal": "118", # opcional
    "dije_especial":"118", # opcional
    "bolitas": [
        {"codigo": "bbla", "cantidad": 32},
        ],
    "lentejas": [
        {"codigo": "LBLA", "cantidad": 2},
        {"codigo": "LNEG", "cantidad": 2}
        ]
    }
))

except Exception as e:
    print(f'Ocurrio un error al intentar generar los dummy entries. ERROR: {e}')