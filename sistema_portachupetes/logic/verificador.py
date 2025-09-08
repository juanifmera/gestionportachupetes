from database.models import Stock, Materiales

def verificar_confeccion(codigo_portachupetes:str):
    
    '''
    Funcion para validar la confeccion de un portachupetes en base a sus elementos. Estructura del codigo: "Broche-Nombre-Dije-Bolitas-Lentejas"
    '''

    try:
        broche = codigo_portachupetes.upper().split('-')[0]
        nombre = codigo_portachupetes.upper().split('-')[1]
        dije = codigo_portachupetes.upper().split('-')[2]
        bolitas = codigo_portachupetes.upper().split('-')[3]
        lentejas = codigo_portachupetes.upper().split('-')[4]

        recuento_letras = {}
        letras_final = []

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

    except Exception as e:
        print(f'Ocurrio algun problema a la hora de validar la confeccion del pedido del portachupetes. Carpeta Logic - Archivo verificador - Funcion "verificar_confeccion". ERROR: {e}')