from datetime import datetime
from sqlalchemy import select
from sqlalchemy.orm import Session
from database.engine import engine
from database.models import Material, Stock
from crud.materiales import validar_material
import pandas as pd

#Validar Lineas de Stock
def validar_stock(codigo_material: str) -> bool:
    """
    Verifica si existe una línea de Stock para un material dado
    """
    session = Session(bind=engine)
    result = session.query(Stock).filter(Stock.codigo_material == codigo_material.upper()).first()
    return bool(result)

#Incrementar Stock -> Publica
def incrementar_stock(codigo_material: str, cantidad: int):
    """
    Incrementa el stock de un material ya existente
    """
    try:
        session = Session(bind=engine)
        
        result = _incrementar_stock(session, codigo_material, cantidad)
        if result:
            session.commit()
            return result

    except Exception as e:
        return f'❌ Ocurrio un error a la hora de incrementar el Stock del siguiente Material: {codigo_material.upper()}. Archivo --> CRUD - Stock - Funcion "incrementar_stock". DETALLE: {e}'

#Incrementar Stock -> Interna
def _incrementar_stock(session, codigo_material: str, cantidad: int) -> bool:
    stock = session.query(Stock).filter(Stock.codigo_material == codigo_material.upper()).first()
    if stock and cantidad > 0:
        stock.cantidad += cantidad
        stock.fecha_modificacion = datetime.today()
        return f'✅ Stock actualizado para {codigo_material.upper()}. Agregaste {cantidad} unidades. Actualmente el producto tiene {stock.cantidad} unidades.' #type:ignore
    else:
        return f'⚠️ No se encontró el material {codigo_material.upper()} en el stock' #type:ignore

#Agregar Stock
def agregar_stock(codigo_material: str, cantidad: int, fecha_modificacion=datetime.today()):
    try:
        with Session(engine) as session:
            if validar_material(codigo_material) and not validar_stock(codigo_material) and cantidad > 0:
                nueva_entrada = Stock(
                    codigo_material=codigo_material.upper(),
                    cantidad=cantidad,
                    fecha_modificacion=fecha_modificacion
                )
                session.add(nueva_entrada)
                session.commit()
                return f'✅ Nuevo stock creado. Material: {codigo_material.upper()} / Cantidad: {cantidad}'

            elif validar_material(codigo_material) and validar_stock(codigo_material):
                return incrementar_stock(codigo_material, cantidad)

            else:
                return f'⚠️ No existe material en la tabla Materiales con código {codigo_material.upper()}'

    except Exception as e:
        return (f'❌ Ocurrió un error al generar una nueva entrada de Stock '
                f'para {codigo_material.upper()}. DETALLE: {e}')

#Eliminar Stock
def eliminar_stock(codigo_material: str):
    """
    Elimina por completo una línea de stock
    """
    try:
        session = Session(bind=engine)
        result = session.query(Stock).filter(Stock.codigo_material == codigo_material.upper()).first()

        if result:
            session.delete(result)
            session.commit()
            return f'✅ Stock de {codigo_material.upper()} eliminado correctamente'
        else:
            return f'⚠️ No se encontró stock para {codigo_material.upper()}'
        
    except Exception as e:
        return f'❌ Ocurrio un error a la hora de Eliminar todo el Stock para el Codigo de Material: {codigo_material.upper()}. Archivo --> CRUD - Stock - Funcion "eliminar_stock". DETALLE: {e}'

#Actualizar Stock
def actualizar_stock(codigo_material: str, cantidad: int):
    """
    Actualiza directamente el stock de un material (reemplaza cantidad)
    """
    try:
        session = Session(bind=engine)
        result = session.query(Stock).filter(Stock.codigo_material == codigo_material.upper()).first()

        if validar_material(codigo_material) and result and cantidad > 0:
            result.cantidad = cantidad
            result.fecha_modificacion = datetime.today() # type: ignore
            session.commit()
            return f'✅ Stock de {codigo_material.upper()} actualizado a {cantidad}'
        else:
            return f'⚠️ No se encontró stock para {codigo_material.upper()} o el material no existe'

    except Exception as e:
        return f'❌ Ocurrio un error a la hora de Actualizar el Stock para el Codigo de Material: {codigo_material.upper()}. Archivo --> CRUD - Stock - Funcion "actualizar_stock". DETALLE: {e}'

#Reducir Stock
def reducir_stock(codigo_material:str, cantidad:int):
    """
    Reduce stock de un material existente
    """
    try:
        session = Session(bind=engine)

        if validar_material(codigo_material) and validar_stock(codigo_material) and cantidad > 0:
            item = session.query(Stock).filter(Stock.codigo_material == codigo_material.upper()).first()

            if item.cantidad >= cantidad:  # type: ignore
                item.cantidad -= cantidad # type: ignore
                item.fecha_modificacion = datetime.today() # type: ignore
                session.commit()
                return f'✅ Stock reducido. Nuevo stock para {codigo_material.upper()}: {item.cantidad}' # type: ignore
            else:
                return f'⚠️ No hay stock suficiente para {codigo_material.upper()}. Disponible: {item.cantidad}' # type: ignore

        else:
            return f'⚠️ No se encontró stock para {codigo_material.upper()}'

    except Exception as e:
        return f'❌ Ocurrio un error a la hora de Reducir el Stock para el Codigo de Material: {codigo_material.upper()}. Archivo --> CRUD - Stock - Funcion "reducir_stock". DETALLE: {e}'

#Listar Stock Completo - Con Join en Material
def listar_stock():
    """
    Lista el stock completo con información del material
    """
    try:
        session = Session(bind=engine)
        stmt = select(Stock).join(Material, Stock.codigo_material == Material.codigo_material)
        results = session.scalars(stmt).all()

        data = [
            {
                "Código": s.codigo_material,
                "Descripción": s.material.descripcion,
                "Color": s.material.color,
                "Categoría": s.material.categoria,
                "Subcategoría": s.material.subcategoria,
                "Cantidad": s.cantidad,
                "Última Modificación": datetime.date(s.fecha_modificacion).strftime('%d/%m/%Y')#type: ignore
            }
            for s in results
        ]

        return pd.DataFrame(data)

    except Exception as e:
        return f'❌ Ocurrio un error a la hora de Listar el Stock. Archivo --> CRUD - Stock - Funcion "listar_stock". DETALLE: {e}'

# Obtener stock de un material puntual
def obtener_stock(codigo_material: str):
    """
    Devuelve el stock de un material puntual
    """
    try:
        session = Session(bind=engine)
        stock = session.query(Stock).filter(Stock.codigo_material == codigo_material.upper()).first()

        if not stock:
            return f'⚠️ No se encontró stock para {codigo_material.upper()}'

        return {
            "Código": stock.codigo_material,
            "Cantidad": stock.cantidad,
            "Última Modificación": stock.fecha_modificacion,
            "Descripción": stock.material.descripcion,
            "Color": stock.material.color,
            "Categoría": stock.material.categoria,
            "Subcategoría": stock.material.subcategoria,
        }

    except Exception as e:
        return f'❌ Error al obtener stock de {codigo_material.upper()}: {e}'