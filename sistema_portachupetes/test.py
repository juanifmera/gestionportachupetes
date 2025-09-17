from database.models import Material, Stock, Base
from database.engine import engine
from sqlalchemy.orm import Session, query
from sqlalchemy import select
from datetime import datetime
from crud.materiales import agregar_material, actualizar_material, eliminar_material, listar_todos_materiales, listo_con_filtro, validar_material
from crud.stock import agregar_stock, eliminar_stock, actualizar_stock, reducir_stock, listar_stock
from logic.verificador import verificar_confeccion_portachupetes
from crud.pedidos import crear_pedido, obtener_materiales_utilizados, cancelar_pedido, modificar_pedido, terminar_pedido, listar_todos_pedidos, listar_materiales_pedido, listar_pedidos_por_estado

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

    #print(crear_pedido('Juan mera', data))
    #print(cancelar_pedido(9))
    #print(modificar_pedido(10, 'papeles', '1126640509'))
    #print(listar_pedidos_por_estado('Cancelado'))
    # Eliminar materiales con categoría inválida
    session = Session(bind=engine)
    materiales_invalidos = session.query(Material).filter(Material.categoria == 'Dijes').all()

    for m in materiales_invalidos:
        print(f"Eliminando material inválido: {m.codigo_material} - {m.categoria}")
        session.delete(m)
        session.commit()

 
except Exception as e:
    print(f'Ocurrio un error al intentar generar los dummy entries. ERROR: {e}')