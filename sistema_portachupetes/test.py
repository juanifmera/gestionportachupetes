from database.models import Material, Stock, Base
from database.engine import engine
from sqlalchemy.orm import Session, query
from sqlalchemy import select
from datetime import datetime
from crud.materiales import agregar_material, actualizar_material, eliminar_material, listo_todo, listo_con_filtro, validar_material
from crud.stock import agregar_stock, eliminar_stock, actualizar_stock, reducir_stock, listar_stock
from logic.verificador import verificar_confeccion

try:
    session = Session(bind=engine)

    verificar_confeccion('pazu-felipe-118-bbla-lbla')

except Exception as e:
    print('Ocurrio un error al intentar generar los dummy entries. ERROR: {e}')