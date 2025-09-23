from sqlalchemy.orm import Session
import pandas as pd
from database.models import Material
from database.engine import engine
from datetime import datetime

#Agrego Material
def agregar_material(codigo_material:str, descripcion:str, color:str, categoria:str, subcategoria:str, comentarios:str, costo_unitario:int, fecha_ingreso=datetime.today()) -> str:
    '''
    Funcion para agregar un nuevo Material a la Tabla Materiales
    '''
    
    try:
        session = Session(bind=engine)
        
        # Valido si el material ya existe en la lista de materiales por su Codigo (Primary Key)
        nuevo_material = Material(codigo_material=codigo_material.upper(), descripcion=descripcion.capitalize(), color=color.capitalize(), categoria=categoria, subcategoria=subcategoria.capitalize(), fecha_ingreso=fecha_ingreso, costo_unitario=costo_unitario, comentarios=comentarios.capitalize())
        result = session.query(Material).filter(Material.codigo_material == nuevo_material.codigo_material).first()

        if result:
            return f'⚠️ Ya existe el material {result.codigo_material} en la lista de Materiales. Detalle del material: {result.descripcion}. Porfavor verificar esta informacion y actualizar de forma correspondiente'

        session.add(nuevo_material)
        session.commit()

        return f'✅ Nuevo material "{nuevo_material.descripcion}" con código {nuevo_material.codigo_material} agregado con éxito el {fecha_ingreso.strftime('%d/%m/%Y')}'

    except Exception as e:
        return(f'❌ Ocurrio un error a la hora de generar un nuevo Material. Archivo --> CRUD - Material - Funcion "agregar_material". DETALLE: {e}')

#Actualizar Material
def actualizar_material(codigo_material: str, columna: str, nuevo_valor):
    """
    Función para modificar un Material de la tabla Materiales utilizando su codigo_material
    """
    try:
        session = Session(bind=engine)

        if not hasattr(Material, columna):
            return f'❌ La columna "{columna}" no existe en la tabla Materiales.'

        columna_attr = getattr(Material, columna)
        result = session.query(Material).filter(Material.codigo_material == codigo_material.upper()).update({columna_attr: nuevo_valor})
        session.commit()

        if result:
            return f'✅ Material {codigo_material.upper()} actualizado correctamente. Campo "{columna}" = "{nuevo_valor}"'
        else:
            return f'⚠️ No se encontró material con código {codigo_material.upper()}'

    except Exception as e:
        return(f'❌ Ocurrio un error a la hora de actualizar un Material. Archivo --> CRUD - Material - Funcion "actualizar_material". DETALLE: {e}')

#Elimino Material
def eliminar_material(codigo_material:str):
    '''
    Funcion para eliminar un  Material de la Tabla Materiales utilizando su codigo_material
    '''
    
    try:
        session = Session(bind=engine)
        result = session.query(Material).filter(Material.codigo_material == codigo_material.upper()).delete()

        if result:
            session.commit()
            return f'✅ Material {codigo_material.upper()} eliminado correctamente'
        else:
            return f'⚠️ No se encontró material con código {codigo_material.upper()}'
        
    except Exception as e:
        return(f'❌ Ocurrio un error a la hora de eliminar un Material. Archivo --> CRUD - Material - Funcion "eliminar_material". DETALLE: {e}')

#Listo Todos los Materiales
def listar_todos_materiales():
    '''
    Funcion para Listar todos los materiales de la Tabla Materiales
    '''
    
    try:
        session = Session(bind=engine)
        materiales = session.query(Material).all()

        data = [
            {
                "Código": m.codigo_material,
                "Descripción": m.descripcion,
                "Color": m.color,
                "Categoría": m.categoria,
                "Subcategoría": m.subcategoria,
                "Fecha Ingreso": datetime.date(m.fecha_ingreso).strftime('%d/%m/%Y'), # type: ignore
                "Costo Unitario": m.costo_unitario,
                "Comentarios": m.comentarios
            }
            
            for m in materiales
        ]

        return pd.DataFrame(data)
        
    except Exception as e:
        return(f'❌ Ocurrio un error a la hora de Listar los Materiales. Archivo --> CRUD - Material - Funcion "listo_todo". DETALLE: {e}')

#Filtro por Condicion
def listo_con_filtro(columna:str, valor):
    '''
    Funcion para Listar todos los materiales de la Tabla Materiales en funcion a una condicion
    '''
    
    try:
        session = Session(bind=engine)

        if not hasattr(Material, columna):
            return pd.DataFrame([{"Error": f'❌ La columna "{columna}" no existe en Material'}])

        columna_attr = getattr(Material, columna)
        result = session.query(Material).filter(columna_attr == valor).all()

        if not result:
            return pd.DataFrame([{"Mensaje": f'⚠️ No se encontraron materiales con {columna} = {valor}'}])

        data = [
            {
                "Código": m.codigo_material,
                "Descripción": m.descripcion,
                "Color": m.color,
                "Categoría": m.categoria,
                "Subcategoría": m.subcategoria,
                "Fecha Ingreso": datetime.date(m.fecha_ingreso), # type: ignore
                "Costo Unitario": m.costo_unitario,
                "Comentarios": m.comentarios
            }
            for m in result
        ]

        return pd.DataFrame(data)
        
    except Exception as e:
        return(f'❌ Ocurrio un error a la hora de Listar los Materiales utilizando una condicion. Archivo --> CRUD - Material - Funcion "listo_con_filtro". DETALLE: {e}')

#Validar Material
def validar_material(codigo_material: str) -> bool:
    """
    Función para validar la existencia de un Material
    """
    try:
        session = Session(bind=engine)
        result = session.query(Material).filter(Material.codigo_material == codigo_material.upper()).first()
        return bool(result)
        
    except Exception as e:
        return(f'❌ Ocurrio un error a la hora de buscar por Codigo un Material. Archivo --> CRUD - Material - Funcion "buscar_por_codigo". DETALLE: {e}') # type: ignore
        return False

# Obtener material puntual
def obtener_material(codigo_material: str):
    """
    Función para obtener los detalles de un Material por su código
    """
    try:
        session = Session(bind=engine)
        m = session.query(Material).filter(Material.codigo_material == codigo_material.upper()).first()

        if not m:
            return f'⚠️ No se encontró material con código {codigo_material.upper()}'

        return {
            "Código": m.codigo_material,
            "Descripción": m.descripcion,
            "Color": m.color,
            "Categoría": m.categoria,
            "Subcategoría": m.subcategoria,
            "Fecha Ingreso": datetime.date(m.fecha_ingreso), # type: ignore
            "Costo Unitario":m.costo_unitario,
            "Comentarios": m.comentarios
        }

    except Exception as e:
        return f'❌ Error al obtener material: {e}'

# Listar dg filtrado 
def listar_materiales_filtrados(categoria="Todas", subcategoria="Todas", color="Todos") -> pd.DataFrame:
    try:
        session = Session(bind=engine)
        query = session.query(Material)

        if categoria != "Todas":
            query = query.filter(Material.categoria.ilike(categoria))

        if subcategoria != "Todas":
            query = query.filter(Material.subcategoria.ilike(subcategoria))

        if color != "Todos":
            query = query.filter(Material.color.ilike(color))

        materiales = query.all()

        df = pd.DataFrame([{
            "Código": m.codigo_material,
            "Descripción": m.descripcion,
            "Color": m.color,
            "Categoría": m.categoria,
            "Subcategoría": m.subcategoria,
            "Fecha Ingreso": datetime.date(m.fecha_ingreso), # type: ignore
            "Comentarios": m.comentarios
        } for m in materiales])

        return df
    
    except Exception as e:
        print(f"Error al filtrar materiales: {e}")
        return pd.DataFrame()
    
def actualizar_varios_campos(codigo_material: str, cambios: dict):
    try:
        session = Session(bind=engine)
        material = session.query(Material).filter(Material.codigo_material == codigo_material.upper()).first()

        if not material:
            return f"❌ No se encontró material con código {codigo_material}"

        for campo, valor in cambios.items():
            if hasattr(material, campo):
                setattr(material, campo, valor)

        session.commit()
        return f"✅ Material {codigo_material.upper()} actualizado correctamente."

    except Exception as e:
        return f"❌ Error al actualizar material: {e}"