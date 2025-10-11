from logic.verificador import verificar_confeccion_portachupetes, verificar_confeccion_pedido_mayorista
from sqlalchemy.orm import Session
from sqlalchemy import func, select
from database.models import Stock, Material, Pedido, MaterialPedido
from datetime import datetime
from database.engine import engine
from crud.stock import _incrementar_stock
import pandas as pd
import time

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
    
def crear_pedido(cliente: str, materiales_portachupete: dict, estado="En proceso", fecha_pedido=datetime.today(), telefono="", tipo='minorista'):
    try:
        session = Session(bind=engine)

        # Verificar stock
        result = verificar_confeccion_portachupetes(materiales_portachupete)
        if not result["success"]:
            return f"No se puede confeccionar el portachupetes porque no hay stock suficiente. Detalle:\n{result['faltantes']}"

        # Crear pedido
        nuevo_pedido = Pedido(cliente=cliente, telefono=telefono, fecha_pedido=fecha_pedido, estado=estado, tipo=tipo)
        session.add(nuevo_pedido)
        session.flush()
        session.refresh(nuevo_pedido)

        # Obtener materiales usados
        materiales_usados = obtener_materiales_utilizados(materiales_portachupete)

        costo_total = 0.0
        letras_procesadas = 0
        cargo_extra_letra = 500

        for codigo, cantidad in materiales_usados:
            session.add(MaterialPedido(
                pedido_id=nuevo_pedido.id,
                codigo_material=codigo.upper(),
                cantidad_usada=cantidad
            ))

            # Descontar stock
            stock = session.query(Stock).filter(Stock.codigo_material == codigo.upper()).first()
            if stock:
                stock.cantidad -= cantidad

            # Buscar costo unitario
            mat = session.query(Material).filter(Material.codigo_material == codigo.upper()).first()

            if len(codigo) == 1 and codigo.isalpha():  # 🔠 Es una letra
                for _ in range(cantidad):  # por si vienen varias del mismo código
                    letras_procesadas += 1
                    if letras_procesadas <= 5:
                        if mat and mat.costo_unitario is not None:
                            costo_total += mat.costo_unitario
                    else:
                        costo_total += cargo_extra_letra
            else:
                # Material normal (no letra)
                if mat and mat.costo_unitario is not None:
                    costo_total += mat.costo_unitario * cantidad

        # Guardar costo total
        nuevo_pedido.costo_total = float(costo_total)
        session.add(nuevo_pedido)
        session.commit()

        return f"✅ Pedido generado con éxito para {cliente.capitalize()} (ID: {nuevo_pedido.id}) - Costo Total: ${int(costo_total):,}".replace(",", ".")

    except Exception as e:
        session.rollback()
        return f"❌ Error al generar pedido: {e}"
    
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

def modificar_pedido(id: int, columna: str, valor):
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

        if pedido.estado in estados_prohibidos:
            return f'No se pueden modificar pedidos en estado {pedido.estado}'

        if not hasattr(Pedido, columna):
            return f'La columna \"{columna}\" no existe en el modelo Pedido'

        columna_attr = getattr(Pedido, columna)

        # 🧠 Cast específico para costo_total
        if columna == "costo_total":
            try:
                valor = float(valor)
            except:
                return "⚠️ El valor ingresado para el costo no es válido (debe ser numérico)"
            
        pedido.columna_attr = valor #type:ignore
        session.commit()
        return f'Pedido con ID {id} modificado correctamente. El nuevo valor para el campo \"{columna}\" es \"{valor}\"'

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
                "Fecha Creación": datetime.date(pedido.fecha_pedido).strftime('%d/%m/%Y'), # type: ignore
                "Estado": pedido.estado,
                "Costo Total": pedido.costo_total
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

        #Genero un Join pata traerme el detalle del material utilizado con su costo unitario
        stm = select(MaterialPedido.codigo_material, MaterialPedido.cantidad_usada, Material.costo_unitario).join(Material, MaterialPedido.codigo_material == Material.codigo_material).filter(MaterialPedido.pedido_id == id)
        materiales = session.execute(stm).all()

        # Siempre devolver un DataFrame, incluso vacío
        if not materiales:
            return pd.DataFrame(columns=["Código", "Cantidad"])

        data = [
            {"Código": m.codigo_material, "Cantidad": m.cantidad_usada, "Costo Unitario": m.costo_unitario}
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

def calcular_costo_total_pedido(pedido_id: int) -> float:
    """
    Calcula el costo total de un pedido sumando (costo_unitario * cantidad_usada).
    Ignora materiales con costo_unitario NULL.
    """
    try:
        session = Session(bind=engine)

        total = session.query(
            func.sum(
                func.coalesce(Material.costo_unitario, 0) * MaterialPedido.cantidad_usada
            )
        ).select_from(MaterialPedido).join(
            Material, Material.codigo_material == MaterialPedido.codigo_material
        ).filter(
            MaterialPedido.pedido_id == pedido_id
        ).scalar()

        return float(total) if total else 0.0

    except Exception as e:
        print(f"❌ Error al calcular el costo del pedido {pedido_id}: {e}")
        return 0.0

def actualizar_varios_campos_pedido(id: int, cambios: dict) -> str:
    """
    Permite modificar múltiples campos de un pedido activo (no cancelado ni terminado).
    """
    try:
        session = Session(bind=engine)
        pedido = session.query(Pedido).filter(Pedido.id == id).first()

        if not pedido:
            return f"❌ No se encontró ningún pedido con ID {id}"

        if pedido.estado in ["Cancelado", "Terminado"]:
            return f"⚠️ No se pueden modificar pedidos en estado {pedido.estado}"

        errores = []

        for campo, valor in cambios.items():
            if campo == "estado":
                errores.append("No se puede cambiar el estado del pedido mediante esta función.")
                continue

            if hasattr(pedido, campo):
                # Cast para campos específicos
                if campo == "costo_total":
                    try:
                        valor = float(valor)
                    except:
                        errores.append(f"⚠️ El valor de '{campo}' debe ser numérico.")
                        continue

                setattr(pedido, campo, valor)
            else:
                errores.append(f"⚠️ La columna '{campo}' no existe en el modelo Pedido.")

        if errores:
            return "\n".join(errores)

        session.commit()
        return f"✅ Pedido con ID {id} actualizado correctamente."

    except Exception as e:
        return f"❌ Ocurrió un problema al actualizar el Pedido con ID {id}. Detalle: {e}"

def crear_pedido_mayorista(cliente:str,  materiales:dict, estado='En proceso', fecha_pedido=datetime.today(), tipo='mayorista', telefono=''):
    try:
        session = Session(bind=engine)

        # Verificar stock
        result = verificar_confeccion_pedido_mayorista(materiales)
        if not result["success"]:
            return f"No se puede confeccionar el portachupetes porque no hay stock suficiente. Detalle:\n{result['faltantes']}"

        # Crear pedido
        nuevo_pedido_mayorista = Pedido(cliente=cliente, fecha_pedido=fecha_pedido, estado=estado, tipo=tipo, telefono=telefono)
        session.add(nuevo_pedido_mayorista)
        session.flush()
        session.refresh(nuevo_pedido_mayorista)

        # Obtener materiales usados
        materiales_usados = obtener_materiales_mayorista(materiales)

        costo_total = 0.0

        for codigo, cantidad in materiales_usados:
            session.add(MaterialPedido(
                pedido_id=nuevo_pedido_mayorista.id,
                codigo_material=codigo.upper(),
                cantidad_usada=cantidad
            ))

            # Descontar stock
            stock = session.query(Stock).filter(Stock.codigo_material == codigo.upper()).first()
            if stock:
                stock.cantidad -= cantidad

            # Buscar costo unitario
            mat = session.query(Material).filter(Material.codigo_material == codigo.upper()).first() 
            
            if mat and mat.costo_unitario is not None:
                costo_total += mat.costo_unitario * cantidad

        # Guardar costo total
        nuevo_pedido_mayorista.costo_total = float(costo_total)
        session.add(nuevo_pedido_mayorista)
        session.commit()

        return f"✅ Pedido generado con éxito para {cliente.capitalize()} (ID: {nuevo_pedido_mayorista.id}) - Costo Total: ${int(costo_total):,}".replace(",", ".")

    except Exception as e:
        session.rollback()
        return f"❌ Error al generar pedido: {e}"
    
def obtener_materiales_mayorista(data: dict) -> list[tuple]:  # type: ignore
    """
    Función auxiliar que devuelve una lista de tuplas con los materiales usados y sus cantidades.
    """
    try:
        result = verificar_confeccion_pedido_mayorista(data)

        if result["success"]:
            materiales = []

            # Broche
            for broche in data.get("broches", []):
                materiales.append((broche["codigo"], broche["cantidad"]))

            # Letras del nombre
            for letra in data.get("letras", []):
                materiales.append((letra["codigo"], letra["cantidad"]))

            # Dijes normales (puede haber varios)
            for dije in data.get("dijes_normales", []):
                materiales.append((dije["codigo"], dije["cantidad"]))

            # Dijes especiales (puede haber varios)
            for dije in data.get("dijes_especiales", []):
                materiales.append((dije["codigo"], dije['cantidad']))

            # Bolitas
            for bolita in data.get("bolitas", []):
                materiales.append((bolita["codigo"], bolita["cantidad"]))

            # Lentejas
            for lenteja in data.get("lentejas", []):
                materiales.append((lenteja["codigo"], lenteja["cantidad"]))

            return materiales

        else:
            return []

    except Exception as e:
        print(f'Ocurrió un error en "obtener_materiales_utilizados": {e}')
        return []
    
def crear_pedido_dummy(cliente: str, materiales_portachupete: dict, estado="En proceso", fecha_pedido=datetime.today(), telefono="", tipo='minorista'):

    try:
        session = Session(bind=engine)

        # Verificar stock
        result = verificar_confeccion_portachupetes(materiales_portachupete)
        if not result["success"]:
            return f"No se puede confeccionar el portachupetes porque no hay stock suficiente. Detalle:\n{result['faltantes']}"

        # Crear pedido
        nuevo_pedido = Pedido(cliente=cliente, telefono=telefono, fecha_pedido=fecha_pedido, estado=estado, tipo=tipo)
        session.add(nuevo_pedido)
        session.flush()
        session.refresh(nuevo_pedido)

        # Obtener materiales usados
        materiales_usados = obtener_materiales_utilizados(materiales_portachupete)

        costo_total = 0.0
        letras_procesadas = 0
        cargo_extra_letra = 500

        for codigo, cantidad in materiales_usados:
            session.add(MaterialPedido(
                pedido_id=nuevo_pedido.id,
                codigo_material=codigo.upper(),
                cantidad_usada=cantidad
            ))
            
            # Buscar costo unitario
            mat = session.query(Material).filter(Material.codigo_material == codigo.upper()).first()

            if len(codigo) == 1 and codigo.isalpha():  # 🔠 Es una letra
                for _ in range(cantidad):  # por si vienen varias del mismo código
                    letras_procesadas += 1
                    if letras_procesadas <= 5:
                        if mat and mat.costo_unitario is not None:
                            costo_total += mat.costo_unitario
                    else:
                        costo_total += cargo_extra_letra
            else:
                # Material normal (no letra)
                if mat and mat.costo_unitario is not None:
                    costo_total += mat.costo_unitario * cantidad

        # Guardar costo total
        nuevo_pedido.costo_total = float(costo_total)
        session.add(nuevo_pedido)
        session.commit()

        return f"✅ Pedido generado con éxito para {cliente.capitalize()} (ID: {nuevo_pedido.id}) - Costo Total: ${int(costo_total):,}".replace(",", ".")

    except Exception as e:
        session.rollback()
        return f"❌ Error al generar pedido: {e}"
    
def actualizar_varios_campos_pedido_aux(id: int, cambios: dict) -> str:
    """
    USO INTERNO
    """
    try:
        session = Session(bind=engine)
        pedido = session.query(Pedido).filter(Pedido.id == id).first()

        if not pedido:
            return f"❌ No se encontró ningún pedido con ID {id}"

        errores = []

        for campo, valor in cambios.items():

            if hasattr(pedido, campo):
                # Cast para campos específicos
                if campo == "costo_total":
                    try:
                        valor = float(valor)
                    except:
                        errores.append(f"⚠️ El valor de '{campo}' debe ser numérico.")
                        continue

                setattr(pedido, campo, valor)
            else:
                errores.append(f"⚠️ La columna '{campo}' no existe en el modelo Pedido.")

        if errores:
            return "\n".join(errores)

        session.commit()
        return f"✅ Pedido con ID {id} actualizado correctamente."

    except Exception as e:
        return f"❌ Ocurrió un problema al actualizar el Pedido con ID {id}. Detalle: {e}"