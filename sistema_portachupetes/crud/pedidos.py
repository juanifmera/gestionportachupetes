from logic.verificador import verificar_confeccion
from sqlalchemy import select
from sqlalchemy.orm import Session
from database.models import Stock, Material, Pedido
from datetime import datetime
from database.engine import engine

#Continuar con la Creacion de las siguientes Funciones para los pedidos
def generar_pedido(codigo_portachupetes:str, cliente:str, telefono='', fecha_pedido=datetime.date()):

    try:

        nuevo_pedido = Pedido(codigo_portachupetes=codigo_portachupetes, cliente=cliente, telefono=telefono, fecha_pedido=fecha_pedido)

        session = Session(bind=engine)
        session.add(nuevo_pedido)
        session.commit()
        session.close()

        print(f'Pedido Generado con Exito.\n Detalle del Pedido:')
        print(f'Codigo Pedido: {nuevo_pedido.codigo_portachupetes}')
        print(f'Cliente: {nuevo_pedido.cliente}')
        print(f'Fecha de Creacion: {nuevo_pedido.fecha_pedido}')
        print(f'Estado: {nuevo_pedido.estado}')

    except Exception as e:
        print(f'Ocurrio un error a la hora de generar un nuevo Pedido. Archivo --> CRUD - Pedidos - Funcion "generar_pedido". DETALLE: {e}')

    


def cambiar_estado():
    pass

def modificar_pedido():
    pass