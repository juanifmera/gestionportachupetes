from datetime import datetime
from sqlalchemy import select
from sqlalchemy.orm import Session
from database.engine import engine
from database.models import Materiales, Stock
from crud.materiales import validar_material

#Validar Lineas de Stock
def validar_stock(codigo_material:str):

    '''
    Verifico que no haya ninguna linea de Stock YA EXISTENTE con un codigo de Material repetido
    '''

    session = Session(bind=engine)

    result = session.query(Stock).where(Stock.codigo_material == codigo_material.upper()).all()

    if result:
        return True
    else:
        return False

#Incrementar Stock
def incrementar_stock(codigo_material:str, cantidad:int):
    
    '''
    Funcion para incrementar el Stock Actual de un Material previamente cargado
    '''

    session = Session(bind=engine)

    stock = session.query(Stock).where(Stock.codigo_material == codigo_material.upper()).first()

    if stock:
        
        stock.cantidad += cantidad
        stock.fecha_modificacion = datetime.now() # type: ignore
        session.commit()
        print(f'Stock actualizado. Nuevo stock para {codigo_material.upper()}: {stock.cantidad}')

    else:
        print(f'No se encontraron resultados en el Stock para el Material: Codigo de Material {codigo_material.upper()}')

#Agregar Stock
def agregar_stock(codigo_material:str, cantidad:int, fecha_modificacion=datetime.now()):
    
    '''
    Funcion para Agregar Stock a la Tabla. La funcion valida que haya un Material cargado Previamente en la tabla Materiales. Esta funcion tiene dos alternativas posibles, o se generea el stock de un material desde cero, o se le incrementa la cantidad de stock a algun material ya cargado previamente.
    '''

    try:
        session = Session(bind=engine)

        #Si esxiste el material en la tabla Materiales y no Existe una entrada actual en la tabla Stock, se genera una entrada desde Cero
        if validar_material(codigo_material) == True and validar_stock(codigo_material) == False: 
            nueva_entrada = Stock(codigo_material=codigo_material.upper(), cantidad=cantidad, fecha_modificacion=fecha_modificacion)

            session.add(nueva_entrada)
            session.commit()

            print(f'Nuevo ingreso de Stock. Codigo Material: {codigo_material} / Cantidad: {cantidad}')
        
        #Caso donde el codigo_material exista en la tabla Materiales, pero ya haya una entrada de Stock
        elif validar_material(codigo_material) == True and validar_stock(codigo_material) == True: 
            incrementar_stock(codigo_material, cantidad)

        else:
            print(f'No existe ningun material en la tabla Materiales con codigo {codigo_material.upper()}. Revisar la existencia del material antes de ingresarlo al Stock')

    except Exception as e:
        print(f'Ocurrio un error a la hora de generar una nueva entrada de Stock para el Codigo de Material: {codigo_material.upper()}. Archivo --> CRUD - Stock - Funcion "agregar_stock". DETALLE: {e}')

#Eliminar Stock
def eliminar_stock(codigo_material:str):
    
    '''
    Funcion para Eliminar todo el Stock de un Material.
    '''

    try:
        session = Session(bind=engine)
        
        result = session.query(Stock).where(Stock.codigo_material == codigo_material.upper()).first()

        if result:
            session.delete(result)
            session.commit()
            print(f'Codigo de Material: {codigo_material.upper()} fue eliminado por completo del Stock')

        else:
            print(f'No se encontro ninguna coicidencia en la tabla Stock con el codigo: {codigo_material.upper()}')

    except Exception as e:
        print(f'Ocurrio un error a la hora de Eliminar todo el Stock para el Codigo de Material: {codigo_material.upper()}. Archivo --> CRUD - Stock - Funcion "eliminar_stock". DETALLE: {e}')

#Actualizar
def actualizar_stock(codigo_material, cantidad):
    
    '''
    Funcion para actualizar el Stock. Esta funcion no incrementa, ni disminuye el stock, sino que lo actualiza. Tener en cuenta esto
    '''

    try:
        session = Session(bind=engine)
        result = session.query(Stock).where(Stock.codigo_material == codigo_material.upper()).first()
        
        #Si existe el material en la tabla Materiales y el resultado de la busqueda entonces actualizo la cantidad
        if validar_material(codigo_material) == True and result:
            result.cantidad = cantidad
            session.commit()

            print(f'Actualizacion de Stock realizada con exito. El Stock del Material {codigo_material.upper()} ahora es de {cantidad}')

        else:
            print(f'No se encontro resultado para la busqueda del material {codigo_material.upper()} o este no existe en la tabla Materiales. Porfavor revisar la Tabla Materiales')

    except Exception as e:
        print(f'Ocurrio un error a la hora de Actualizar el Stock para el Codigo de Material: {codigo_material.upper()}. Archivo --> CRUD - Stock - Funcion "actualizar_stock". DETALLE: {e}')

def reducir_stock(codigo_material, cantidad):
    '''
    Funcion para reducir el Stock Actual de un Material previamente cargado.
    '''
    try:
        session = Session(bind=engine)

        stock = session.query(Stock).where(Stock.codigo_material == codigo_material.upper()).first()

        if stock:
            stock.cantidad += cantidad
            stock.fecha_modificacion = datetime.now() # type: ignore
            session.commit()
            print(f'Stock actualizado. Nuevo stock para {codigo_material.upper()}: {stock.cantidad}')

        else:
            print(f'No se encontraron resultados en el Stock para el Material: Codigo de Material {codigo_material.upper()}')

    except Exception as e:
        print(f'Ocurrio un error a la hora de Reducir el Stock para el Codigo de Material: {codigo_material.upper()}. Archivo --> CRUD - Stock - Funcion "reducir_stock". DETALLE: {e}')