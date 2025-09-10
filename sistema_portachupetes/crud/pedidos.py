from logic.verificador import verificar_confeccion
from sqlalchemy import select
from sqlalchemy.orm import Session
from database.models import Stock, Material, Pedido
from datetime import datetime
from database.engine import engine

#Continuar con la Creacion de las siguientes Funciones para los pedidos
def generar_pedido(codigo_portachupetes:str, cliente:str, telefono='', fecha_pedido=datetime.today()):

    try:
        nuevo_pedido = Pedido(codigo_portachupetes=codigo_portachupetes.upper(), cliente=cliente.capitalize(), telefono=telefono, fecha_pedido=fecha_pedido)

        #Aca debo primero validar si se puede o no realizar el pedido en base al stock cargado. En caso de que se pueda, el pedido tiene que ser generado y luego descontar el stock correspondiente

        session = Session(bind=engine)
        session.add(nuevo_pedido)
        session.commit()

        print(f'Pedido Generado con Exito.\nDetalle:')
        print(f'Codigo Pedido: {nuevo_pedido.codigo_portachupetes.upper()}')
        print(f'Cliente: {nuevo_pedido.cliente.capitalize()}')
        print(f'Fecha de Creacion: {datetime.date(nuevo_pedido.fecha_pedido)}')
        print(f'Estado: {nuevo_pedido.estado.capitalize()}')

        session.close()

    except Exception as e:
        print(f'Ocurrio un error a la hora de generar un nuevo Pedido. Archivo --> CRUD - Pedidos - Funcion "generar_pedido". DETALLE: {e}')

def cancelar_pedido(id:int):

    try:
        session = Session(bind=engine)
        pedido = session.query(Pedido).where(Pedido.id == id).first()
        
        if pedido:
            pedido.estado = 'Cancelado'
            session.commit()
            print(f'Pedido con ID Numero: {pedido.id} Cancelado. Los materiales para confeccionar este portachupetes volvera de forma automatica al Stock')
            print(f'Detalle del Pedido:\nCodigo Portachupetes: {pedido.codigo_portachupetes}\nCliente: {pedido.cliente}')

        else:
            print(f'No se encontro resultados para la busqueda. Porfavor verificar el ID del Pedido que quiere cancelar')

            listar_pedidos()

    except Exception as e:
        print(f'Ocurrio un error a la hora de eliminar un Pedido. Archivo --> CRUD - Pedidos - Funcion "eliminar_pedido". DETALLE: {e}')
 
def terminar_pedido(id):

    try:
        session = Session(bind=engine)
        pedido = session.query(Pedido).where(Pedido.id == id).first()
        
        if pedido.estado != 'Cancelado':
            pedido.estado = 'Terminado'
            session.commit()
            print(f'Pedido con ID Numero: {pedido.id} Terminado. Avisar al cliente que lo debe retirar')
            print(f'Detalle del Pedido:\nCodigo Portachupetes: {pedido.codigo_portachupetes}\nCliente: {pedido.cliente}')

        elif pedido.estado == 'Cancelado':
            print(f'No se puede Terminar un pedido previamente Cancelado. Porfavor consultar nuevamente los pedidos para verificar el id del Pedido a Terminar')

            listar_pedidos()

        else:
            print(f'No se encontro resultados para la busqueda. Porfavor verificar el ID del Pedido que quiere cancelar')

            listar_pedidos()

    except Exception as e:
        print(f'Ocurrio un error a la hora de eliminar un Pedido. Archivo --> CRUD - Pedidos - Funcion "eliminar_pedido". DETALLE: {e}')

def modificar_pedido(id:int, campo:str, valor):

    try:
        session = Session(bind=engine)
        pedido = session.query(Pedido).where(Pedido.id == id).first()
        campos_autorizados = ['cliente', 'telefono', 'fecha_pedido']

        if pedido:

            if campo == 'estado' or campo == 'codigo_portachupetes':
                print(f'No se puede cambiar el estado  o codigo de Portacupetes de ningun Pedido a traves de esta funcion. Porfavor utilizar las funciones "terminar_pedido" o "cancelar_pedido"')

            elif pedido.estado == 'Cancelado':
                print('No se pueden modificar Pedidos Cancelados')

            elif campo not in campos_autorizados:
                print(f'No se encontro ninguna columna llamada {campo} en la tabla de Pedidos')

            elif campo in campos_autorizados:
                setattr(pedido, campo, valor) #Tener cuidado con las capitalizaciones y demas aca
                session.commit()
                print(f'Se realizo con exito la modificacion del Pedido con ID: {id} de su Campo: {campo} con el Valor: {valor}')

        else:
            print(f'No se encontro ningun Pedido con el ID Numero {id}. porfavor revisar los pedidos para ver cual se quiere modificar')

            listar_pedidos()

    except Exception as e:
        print(f'Ocurrio un error a la hora de Modificar el Pedido. Archivo --> CRUD - Pedidos - Funcion "modificar_pedido". DETALLE: {e}')

def listar_pedidos():
    
    try:
        session = Session(bind=engine)
        pedidos = session.query(Pedido).all()

        for i, pedido in enumerate(pedidos,start=1):
            print(f'Pedido Numero {i}')
            print(pedido.codigo_portachupetes)
            print(pedido.cliente)
            print(pedido.fecha_pedido)
            print(pedido.estado)
            print('---'*5)

    except Exception as e:
        print(f'Ocurrio un error a la hora de Listar todos los Pedido. Archivo --> CRUD - Pedidos - Funcion "listar_pedidos". DETALLE: {e}')