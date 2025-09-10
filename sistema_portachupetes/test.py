from database.models import Material, Stock, Base
from database.engine import engine
from sqlalchemy.orm import Session, query
from sqlalchemy import select
from datetime import datetime
from crud.materiales import agregar_material, actualizar_material, eliminar_material, listo_todo, listo_con_filtro, validar_material
from crud.stock import agregar_stock, eliminar_stock, actualizar_stock, reducir_stock, listar_stock
from logic.verificador import verificar_confeccion
from crud.pedidos import generar_pedido, cancelar_pedido, terminar_pedido, modificar_pedido

try:
    session = Session(bind=engine)

    modificar_pedido(2, 'fecha_pedido', datetime.now())

except Exception as e:
    print(f'Ocurrio un error al intentar generar los dummy entries. ERROR: {e}')