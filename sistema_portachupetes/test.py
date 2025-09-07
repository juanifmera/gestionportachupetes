from database.models import Materiales, Stock, Base
from database.engine import engine
from sqlalchemy.orm import Session, query
from sqlalchemy import select
from datetime import datetime
from crud.materiales import agregar_material, actualizar_material, eliminar_material, listo_todo, listo_con_filtro, buscar_por_codigo
from crud.stock import agregar_stock, eliminar_stock

try:
    session = Session(bind=engine)

    lentaja_negra = Materiales(id_material=1, codigo_material='LNEG', descripcion='Lenteja de 12 mm', color='Negro', categoria='Lenteja', subcategoria='Normal', comentarios='Nuevo Ingreso de Lentejas Negras Medio Pelo')
    stock_lenteja_negra = Stock(codigo_material=lentaja_negra.codigo_material, cantidad=5)

    '''result = session.query(Stock).where(Stock.codigo_material == 'LNEG').update({'cantidad':29})
    session.commit()'''

    '''stmt = select(Materiales).join(Stock, Materiales.codigo_material == Stock.codigo_material)

    result = session.execute(stmt).scalars().all()

    for item in result:
        print(item.codigo_material, item.descripcion, item.stock.cantidad)'''

    '''session.add(stock_lenteja_negra)
    session.commit()
    print('Exito')'''

    '''session.query(Stock).where(Stock.codigo_material=='BBLA').update({'cantidad':15})
    session.commit()
    print('Exito')'''
    
    #agregar_material(5, 'lbla', 'lenteja blanca', 'blanco', 'lentejas', 'normales', 'LENTEJAS BLANCAS MEDIO PELO')
    agregar_stock('lbla', 1)
    #eliminar_stock('pazu')

except Exception as e:
    print(f'Ocurrio un error al intentar generar los dummy entries. ERROR: {e}')