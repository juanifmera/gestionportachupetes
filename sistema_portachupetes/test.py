from database.models import Materiales, Stock, Base
from database.engine import engine
from sqlalchemy.orm import Session, query
from sqlalchemy import select
from datetime import datetime

try:
    session = Session(bind=engine)

    bolita_blanca = Materiales(id_material=1, codigo_material='BBLA', descripcion='Bolita 12 mm', color='blanco', categoria='Bolita', subcategoria='Normal', fecha_ingreso=datetime.today().date(), comentarios='Nuevo Ingreso de Bolitas Blancas Super Facheras')

    stock_bolita_blanca = Stock(codigo_material=bolita_blanca.codigo_material, cantidad=10, fecha_modificacion=datetime.today().date())

    session.query(Stock).where(Stock.codigo_material=='BBLA').update({'cantidad':15})
    session.commit()
    print('Exito')

except Exception as e:
    print(f'Ocurrio un error al intentar generar los dummy entries. ERROR: {e}')