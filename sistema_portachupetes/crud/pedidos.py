from logic.verificador import verificar_confeccion_portachupetes
from sqlalchemy.orm import Session
from sqlalchemy import func
from database.models import Stock, Material, Pedido, MaterialPedido
from datetime import datetime
from database.engine import engine
from crud.stock import _incrementar_stock
import pandas as pd

def obtener_materiales_utilizados(data: dict) -> list[tuple]:  # type: ignore
    """
    Función auxiliar que devuelve una lista de tuplas con los materiales usados y sus cantidades.
    """
    try:
        result = verificar_confeccion_portachupetes(data)

        if result["success"]:
            materiales = []

            # Broche
            if "broche" in data:
                materiales.append((data["broche"], 1))
            else:
                return "No se encontró ningún broche en el portachupetes. FATAL ERROR" # type: ignore

            # Letras del nombre
            if "nombre" in data:
                nombre = data["nombre"].upper()
                letras_recuento = {}
                for letra in nombre:
                    letras_recuento[letra] = letras_recuento.get(letra, 0) + 1

                for letra, cantidad in letras_recuento.items():
                    materiales.append((letra, cantidad))

            # Dijes normales (puede haber varios)
            for dije in data.get("dijes_normales", []):
                materiales.append((dije["codigo"], 1))

            # Dijes especiales (puede haber varios)
            for dije in data.get("dijes_especiales", []):
                materiales.append((dije["codigo"], 1))

            # Bolitas
            for bolita in data.get("bolitas", []):
                materiales.append((bolita["codigo"], bolita["cantidad"]))

            # Lentejas
            for lenteja in data.get("lentejas", []):
                materiales.append((lenteja["codigo"], lenteja["cantidad"]))

            return materiales

        else:
            return []  # No hay stock suficiente, no devolvemos nada

    except Exception as e:
        print(f'Ocurrió un error en "obtener_materiales_utilizados": {e}')
        return []
    
def crear_pedido(cliente: str, materiales_portachupete: dict, estado="En proceso", fecha_pedido=datetime.today(), telefono=""):
    """
    Genera un nuevo pedido y descuenta materiales del stock si hay suficiente.
    """
    try:
        session = Session(bind=engine)

        # Verificar si se puede confeccionar
        result = verificar_confeccion_portachupetes(materiales_portachupete)

        if not result["success"]:
            return f"No se puede confeccionar el portachupetes porque no hay stock suficiente. Detalle:\n{result['faltantes']}"

        # Crear el pedido
        nuevo_pedido = Pedido(cliente=cliente, telefono=telefono, fecha_pedido=fecha_pedido, estado=estado)
        session.add(nuevo_pedido)
        session.flush()  # Permite obtener el ID del pedido antes del commit

        # Obtener materiales y asociarlos
        materiales_usados = obtener_materiales_utilizados(materiales_portachupete)

        for codigo, cantidad in materiales_usados:
            material_pedido = MaterialPedido(pedido_id=nuevo_pedido.id, codigo_material=codigo.upper(), cantidad_usada=cantidad)
            session.add(material_pedido)

            # Descontar del stock
            stock = session.query(Stock).filter(Stock.codigo_material == codigo.upper()).first()

            if stock:
                stock.cantidad -= cantidad

        session.commit()
        return f"Pedido generado con éxito para {cliente.capitalize()} (ID: {nuevo_pedido.id})"

    except Exception as e:
        return f"Ocurrió un error al generar un nuevo pedido para el cliente {cliente.capitalize()}. DETALLE: {e}"
    
def cancelar_pedido(id:int):
    '''
    Funcion para cancelar un pedido por su ID y devolver los materiales al Stock
    '''

    try:
        session = Session(bind=engine)

        pedido = session.query(Pedido).filter(Pedido.id == id).first()

        mensajes = []

        if pedido:

            if pedido.estado == 'Cancelado' or pedido.estado == 'Terminado':
                return f'No se puede cancelar un pedido ya Cancelado o Terminado. ID del Pedido {id}, Estado: {pedido.estado}'
            
            pedido.estado = 'Cancelado'
            materiales_consumidos = session.query(MaterialPedido).filter(MaterialPedido.pedido_id == pedido.id).all()

            for material in materiales_consumidos:
                _incrementar_stock(session, material.codigo_material.upper(), material.cantidad_usada)
                mensajes.append(f'El material {material.codigo_material.upper()} se incremento {material.cantidad_usada} unidades nuvamente al Stock')
                session.delete(material)
            
            session.commit()

            return f'Pedido con ID {id} Cancelado con Exito. Detalle de Materiales Devueltos al Stock:\n{mensajes}'
        
        else:
            return f'No se encontro Ningun Pedido con el ID {id}. Porfavor volver a intentarlo'

    except Exception as e:
        return f'Ocurrio un problema a la hora de Cancelar un Pedido. Carpeta CRUD - Archivo Pedidos.py. Detalle: {e}'

def terminar_pedido(id:int):
    '''
    Funcion para terminar un pedido por su ID
    '''
    try:
        session = Session(bind=engine)

        pedido = session.query(Pedido).filter(Pedido.id == id).first()

        if pedido:

            if pedido.estado == 'Cancelado':
                return f'No se puede terminado un pedido cancelado. ID del Pedido {id}, Estado: {pedido.estado}'
            
            pedido.estado = 'Terminado'
            session.commit()
            return f'ID pedido: {id} Terminado con Exito'
        
        else:
            return f'No se encontro Ningun Pedido con el ID {id}. Porfavor volver a intentarlo'

    except Exception as e:
        return f'Ocurrio un problema a la hora de Cancelar un Pedido. Carpeta CRUD - Archivo Pedidos.py. Detalle: {e}'

def modificar_pedido(id: int, columna: str, valor: str):
    '''
    Función para modificar detalles menores del pedido
    '''
    try:
        session = Session(bind=engine)

        pedido = session.query(Pedido).filter(Pedido.id == id).first()
        estados_prohibidos = ['Cancelado', 'Terminado']

        if pedido is None:
            return f'No se encontró ningún Pedido con el ID {id}'

        if columna == 'estado':
            return 'No se puede cambiar el Estado de un Pedido mediante esta función'

        if pedido.estado in estados_prohibidos:  # type: ignore
            return f'No se pueden modificar pedidos en estado {pedido.estado}'

        if not hasattr(Pedido, columna):
            return f'La columna "{columna}" no existe en el modelo Pedido'
        
        columna_attr = getattr(Pedido, columna)
        session.query(Pedido).filter(Pedido.id == id).update({columna_attr: valor})
        session.commit()
        return f'Pedido con ID {id} modificado correctamente. El nuevo valor para el campo "{columna}" es "{valor}"'

    except Exception as e:
        return f'Ocurrió un problema al modificar un Pedido. Carpeta CRUD - Archivo Pedidos.py. Detalle: {e}'

def listar_todos_pedidos():
    '''
    Función para listar todos los pedidos en un DataFrame (ideal para Streamlit)
    '''
    try:
        session = Session(bind=engine)
        pedidos = session.query(Pedido).all()

        # Convertir a lista de diccionarios
        data = [
            {
                "ID": pedido.id,
                "Cliente": getattr(pedido, "cliente", None),  # si existe el campo
                "Telefono": getattr(pedido, "telefono", None),
                "Fecha Creación": datetime.date(pedido.fecha_pedido), # type: ignore
                "Estado": pedido.estado
            }
            for pedido in pedidos
        ]

        # Pasar a DataFrame
        return pd.DataFrame(data)
    
    except Exception as e:
        return f'Ocurrió un problema a la hora de Listar todos los Pedidos. Carpeta CRUD - Archivo Pedidos.py. Detalle: {e}'
    
def obtener_pedido(id: int):
    try:
        session = Session(bind=engine)
        pedido = session.query(Pedido).filter(Pedido.id == id).first()
        if pedido:
            return {
                "ID": pedido.id,
                "Cliente": pedido.cliente,
                "Estado": pedido.estado,
                "Fecha Pedido": pedido.fecha_pedido,
                "Teléfono": pedido.telefono,
                "Costo Total": pedido.costo_total,
            }
        return f"No se encontró ningún pedido con ID {id}"
    except Exception as e:
        return f"Error al obtener pedido {id}. Detalle: {e}"

def listar_materiales_pedido(id: int):
    try:
        session = Session(bind=engine)
        materiales = session.query(MaterialPedido).filter(MaterialPedido.pedido_id == id).all()

        # Siempre devolver un DataFrame, incluso vacío
        if not materiales:
            return pd.DataFrame(columns=["Código", "Cantidad"])

        data = [
            {"Código": m.codigo_material, "Cantidad": m.cantidad_usada}
            for m in materiales
        ]
        return pd.DataFrame(data)
    except Exception as e:
        # En caso de error, también devolver un DataFrame vacío (y loguear si querés)
        return pd.DataFrame(columns=["Código", "Cantidad"])

def listar_pedidos_por_estado(estado: str):
    try:
        session = Session(bind=engine)
        pedidos = session.query(Pedido).filter(Pedido.estado == estado).all()
        data = [
            {
                "ID": pedido.id,
                "Cliente": getattr(pedido, "cliente", None),  # si existe el campo
                "Telefono": getattr(pedido, "telefono", None),
                "Fecha Creación": datetime.date(pedido.fecha_pedido), # type: ignore
                "Estado": pedido.estado,
            }
            for pedido in pedidos
        ]
        # Pasar a DataFrame
        return pd.DataFrame(data)
    
    except Exception as e:
        return f'Ocurrió un problema a la hora de Listar todos los Pedidos. Carpeta CRUD - Archivo Pedidos.py. Detalle: {e}'

#NO SE DEBE UTILIZAR ESTA FUNCION
def eliminar_pedido(id: int):
    try:
        session = Session(bind=engine)
        pedido = session.query(Pedido).filter(Pedido.id == id).first()
        if not pedido:
            return f"No se encontró el pedido con ID {id}"
        session.delete(pedido)
        session.commit()
        return f"Pedido con ID {id} eliminado correctamente"
    except Exception as e:
        return f"Error al eliminar pedido {id}. Detalle: {e}"
    
def listar_materiales_pedido_completo():
    """
    Devuelve un DataFrame con la cantidad total de veces que cada material fue utilizado en pedidos.
    Útil para métricas como los materiales más usados.
    """
    try:
        session = Session(bind=engine)
        
        # Unir materiales y su uso en pedidos
        query = (
            session.query(
                Material.codigo_material,
                Material.descripcion,
                Material.categoria,
                Material.subcategoria,
                Material.color,
                MaterialPedido.cantidad_usada
            )
            .join(MaterialPedido, Material.codigo_material == MaterialPedido.codigo_material)
        )

        data = []
        for row in query.all():
            data.append({
                "Código": row.codigo_material,
                "Descripción": row.descripcion,
                "Categoría": row.categoria,
                "Subcategoría": row.subcategoria,
                "Color": row.color,
                "Cantidad Usada": row.cantidad_usada
            })

        df = pd.DataFrame(data)
        df_agrupado = df.groupby(["Código", "Descripción", "Categoría", "Subcategoría", "Color", 'Costo Unitario'], as_index=False)["Cantidad Usada"].sum()
        df_agrupado.sort_values("Cantidad Usada", ascending=False, inplace=True) #type:ignore
        return df_agrupado

    except Exception as e:
        return f"❌ Error al listar materiales usados: {e}"

from sqlalchemy import func, select

def calcular_costo_total_pedido(pedido_id: int) -> int:
    """
    Calcula el costo total de un pedido sumando (costo_unitario * cantidad_usada)
    """
    try:
        session = Session(bind=engine)

        total = session.query(
            func.sum(Material.costo_unitario * MaterialPedido.cantidad_usada)
        ).select_from(MaterialPedido).join(
            Material, Material.codigo_material == MaterialPedido.codigo_material
        ).filter(
            MaterialPedido.pedido_id == pedido_id
        ).scalar()

        return int(total) or 0

    except Exception as e:
        print(f"❌ Error al calcular el costo del pedido {pedido_id}: {e}")
        return 0
