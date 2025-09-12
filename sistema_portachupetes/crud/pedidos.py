from logic.verificador import verificar_confeccion_portachupetes
from sqlalchemy import select
from sqlalchemy.orm import Session
from database.models import Stock, Material, Pedido, MaterialPedido
from datetime import datetime
from database.engine import engine

#Continuar con la Creacion de las siguientes Funciones para los pedidos

def obtener_materiales_utilizados(data: dict) -> list[tuple]:  # type: ignore
    """
    Función auxiliar que devuelve una lista de tuplas con los materiales usados y sus cantidades.
    """
    try:
        result = verificar_confeccion_portachupetes(data)

        if result["success"] == True:
            materiales = []

            # Broche
            if "broche" in data:
                materiales.append((data["broche"], 1))
            else:
                print("No se encontró ningún broche en el portachupetes. FATAL ERROR")

            # Letras del nombre
            if "nombre" in data:
                nombre = data["nombre"].upper()
                letras_recuento = {}
                for letra in nombre:
                    letras_recuento[letra] = letras_recuento.get(letra, 0) + 1

                for letra, cantidad in letras_recuento.items():
                    materiales.append((letra, cantidad))

            # Dijes
            if "dije_normal" in data and data["dije_normal"]:
                materiales.append((data["dije_normal"], 1))

            if "dije_especial" in data and data["dije_especial"]:
                materiales.append((data["dije_especial"], 1))

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
    

def delete_all():

    session = Session(bind=engine)
    results = session.query(Pedido).all()

    for result in results:
        session.delete(result)
        session.commit()
        session.close()
