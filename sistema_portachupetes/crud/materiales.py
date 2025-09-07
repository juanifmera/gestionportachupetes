from sqlalchemy.orm import Session
from sqlalchemy import select
from database.models import Materiales
from database.engine import engine
from datetime import datetime

#Agrego Material
def agregar_material(id_material:int, codigo_material:str, descripcion:str, color:str, categoria:str, subcategoria:str, comentarios:str, fecha_ingreso=datetime.now()):

    '''
    Funcion para agregar un nuevo Material a la Tabla Materiales
    '''
    
    try:
        session = Session(bind=engine)

        nuevo_material = Materiales(id_material=id_material, codigo_material=codigo_material.upper(), descripcion=descripcion.capitalize(), color=color.capitalize(), categoria=categoria.capitalize(), subcategoria=subcategoria.capitalize(), fecha_ingreso=fecha_ingreso, comentarios=comentarios.capitalize())

        session.add(nuevo_material)
        session.commit()
        print(f'Nuevo material {nuevo_material.categoria} con codigo {nuevo_material.codigo_material} generado con exito el dia {fecha_ingreso.date()}')

    except Exception as e:
        print(f'Ocurrio un error a la hora de generar un nuevo Material. Archivo --> CRUD - Material - Funcion "agregar_material". DETALLE: {e}')

#Actualizar Material
def actualizar_material(codigo_material:str, nombre_columna:str, nuevo_valor):

    '''
    Funcion para modificar un  Material de la Tabla Materiales utilizando su codigo_material
    '''
    
    try:
        session = Session(bind=engine)

        session.query(Materiales).where(Materiales.codigo_material == codigo_material.upper()).update({nombre_columna.lower():nuevo_valor}) #Tener cuidado con el nuevo valor y su capitalizacion, ya que si se cambia el codigo, debera ser upper(), si es su fecha de ingreso seria datetime, su id es int y por ulñtimos sus otros campos capitalize()
        session.commit()
        print(f'Material codigo: {codigo_material.upper()} sufrio una actualizacion de su campo: {nombre_columna.lower()}. El nuevo valor es {nuevo_valor}')

    except Exception as e:
        print(f'Ocurrio un error a la hora de actualizar un Material. Archivo --> CRUD - Material - Funcion "actualizar_material". DETALLE: {e}')

#Elimino Material
def eliminar_material(codigo_material:str):

    '''
    Funcion para eliminar un  Material de la Tabla Materiales utilizando su codigo_material
    '''
    
    try:
        session = Session(bind=engine)

        result = session.query(Materiales).where(Materiales.codigo_material == codigo_material.upper()).delete()

        if result:
            session.commit()
            print(f'Material codigo: {codigo_material.upper()} fue eliminado de la Tabla Materiales de forma Exitosa')
        
        else:
            print(f'No se encontro ningun material con el codigo: {codigo_material.upper()}. Porfavor volve a intentarlo')
        
    except Exception as e:
        print(f'Ocurrio un error a la hora de eliminar un Material. Archivo --> CRUD - Material - Funcion "eliminar_material". DETALLE: {e}')

#Listo Todos los Materiales
def listo_todo():

    '''
    Funcion para Listar todos los materiales de la Tabla Materiales
    '''
    
    try:
        session = Session(bind=engine)
        materiales = session.query(Materiales).all()
        for material in materiales:
            print(material.codigo_material)
        
    except Exception as e:
        print(f'Ocurrio un error a la hora de Listar los Materiales. Archivo --> CRUD - Material - Funcion "listo_todo". DETALLE: {e}')

#Filtro por Condicion
def listo_con_filtro(nombre_columna:str, valor):

    '''
    Funcion para Listar todos los materiales de la Tabla Materiales en funcion a una condicion
    '''
    
    try:
        session = Session(bind=engine)
        columna = getattr(Materiales, nombre_columna)
        result = session.query(Materiales).filter(columna == valor).all()

        if result:
            for item in result:
                print(item.codigo_material, item.color, item.categoria)

        else:
            print(f'No se encontraron resultados para la busqueda seleccionada')
        
    except Exception as e:
        print(f'Ocurrio un error a la hora de Listar los Materiales utilizando una condicion. Archivo --> CRUD - Material - Funcion "listo_con_filtro". DETALLE: {e}')

def buscar_por_codigo(codigo_material:str):

    '''
    Funcion para validar la existencia de un Material
    '''

    try:
        session = Session(bind=engine)
        result = session.query(Materiales).where(Materiales.codigo_material == codigo_material.upper()).all()
        if result:
            return True
        else:
            return False
        
    except Exception as e:
        print(f'Ocurrio un error a la hora de buscar por Codigo un Material. Archivo --> CRUD - Material - Funcion "buscar_por_codigo". DETALLE: {e}')