from database.models import Materiales, Stock, Base
from database.engine import engine
from sqlalchemy.orm import Session, query
from sqlalchemy import select
from datetime import datetime
from crud.materiales import agregar_material, actualizar_material, eliminar_material, listo_todo, listo_con_filtro, buscar_por_codigo
from crud.stock import agregar_stock, eliminar_stock

try:
    session = Session(bind=engine)

    

except Exception as e:
    print(f'Ocurrio un error al intentar generar los dummy entries. ERROR: {e}')