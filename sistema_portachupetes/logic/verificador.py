from database.models import Stock, Materiales
from sqlalchemy.orm import Session
from database.engine import engine

def verificar_confeccion(codigo_portachupetes:str):
    
    '''
    Funcion para validar la confeccion de un portachupetes en base a sus elementos. Estructura del codigo: "Broche-Nombre-Dije-Bolitas-Lentejas"
    '''

    try:

        session = Session(bind=engine)

        broche = codigo_portachupetes.upper().split('-')[0]
        nombre = codigo_portachupetes.upper().split('-')[1]
        dije = codigo_portachupetes.upper().split('-')[2]
        bolitas = codigo_portachupetes.upper().split('-')[3]
        lentejas = codigo_portachupetes.upper().split('-')[4]

        recuento_letras = {}
        letras_final = []
        mensajes = []
        stock_suficiente = True

        for letra in nombre:
            if letra not in recuento_letras.keys():
                recuento_letras[letra] = 1
            else:
                recuento_letras[letra] += 1

        for key, value in recuento_letras.items():
            letras_final.append((key, value))
        
        pedido = {
            'broche':(broche,1),
            'dije':(dije,1),
            'bolitas':(bolitas,2),
            'lentejas':(lentejas,2),
            'letras':letras_final,
        }

        for key, value in pedido.items():

            if key == 'letras':
                continue
            
            codigo_material = value[0].upper()
            cantidad_requerida = value[1]

            result = session.query(Stock).where(Stock.codigo_material == codigo_material).first()
            
            if result != None: #Si el codigo material en la tabla Stcok

                if result.cantidad >= cantidad_requerida:
                    mensajes.append(f'Cantidad Suficiente del {key}: {result.codigo_material}. Cantidad Actual {result.cantidad}, Cantidad Requerida {cantidad_requerida}')

                else:
                    mensajes.append(f'No hay suficientes unidades de {key}: {result.codigo_material}. Cantidad Actual: {result.cantidad}, Cantidad Requerida {cantidad_requerida}')
                    stock_suficiente = False
            
            else:
                mensajes.append(f'No se encontro el Material {key}: {codigo_material} en la tabla Stock')
                stock_suficiente = False

        for letra, cantidad_requerida in pedido['letras']:
            
            result = session.query(Stock).where(Stock.codigo_material == letra).first()
            
            if result != None: #Si el codigo material en la tabla Stcok

                if result.cantidad >= cantidad_requerida:
                    mensajes.append(f'Cantidad Suficiente de la Letra {letra}. Cantidad Actual {result.cantidad}, Cantidad Requerida {cantidad_requerida}')

                else:
                    mensajes.append(f'No hay suficientes unidades de la Letra {letra}. Cantidad Actual: {result.cantidad}, Cantidad Requerida {cantidad_requerida}')
                    stock_suficiente = False

            else:
                mensajes.append(f'No se encontro el Material {letra} en la tabla Stock')
                stock_suficiente = False

        if stock_suficiente == True:
            print(f'El pedido se puede confeccionar con el Stock Actual')

        else:
            print(f'No se puede generar el Portachupetes con el Stock Actual. Porfavor revisar los Detalles:')
            print(f'\n'.join(mensajes))

    except Exception as e:
        print(f'Ocurrio algun problema a la hora de validar la confeccion del pedido del portachupetes. Carpeta Logic - Archivo verificador - Funcion "verificar_confeccion". ERROR: {e}')