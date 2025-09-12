from database.models import Material, Stock, Base
from database.engine import engine
from sqlalchemy.orm import Session, query
from sqlalchemy import select
from datetime import datetime
from crud.materiales import agregar_material, actualizar_material, eliminar_material, listo_todo, listo_con_filtro, validar_material
from crud.stock import agregar_stock, eliminar_stock, actualizar_stock, reducir_stock, listar_stock
from logic.verificador import verificar_confeccion_portachupetes
from crud.pedidos import crear_pedido, obtener_materiales_utilizados, delete_all

try:
    session = Session(bind=engine)

    data={
    "broche": "PAZU",
    "nombre": "felipe",  # opcional
    "dije_normal": "118", # opcional
    "dije_especial":"118", # opcional
    "bolitas": [
        {"codigo": "bbla", "cantidad": 2},
        ],
    "lentejas": [
        {"codigo": "LBLA", "cantidad": 2},
        {"codigo": "LNEG", "cantidad": 2}
        ]
    }

    #print(verificar_confeccion_portachupetes(data))

    #sdelete_all()
    print(crear_pedido('Juan mera', data, telefono='1126640509'))
 

except Exception as e:
    print(f'Ocurrio un error al intentar generar los dummy entries. ERROR: {e}')