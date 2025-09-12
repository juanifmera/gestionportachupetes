from sqlalchemy.orm import Session
from database.engine import engine
from database.models import Stock


def verificar_confeccion_portachupetes(data: dict) -> dict: # type: ignore
    """
    Valida si hay suficiente stock para confeccionar un portachupetes según los materiales solicitados.
    Recibe un diccionario con los siguientes posibles campos:
        - broche: str (obligatorio)
        - nombre: str (opcional)
        - dije_normal: str (opcional)
        - dije_especial: str (opcional)
        - bolitas: list[{'codigo': str, 'cantidad': int}]
        - lentejas: list[{'codigo': str, 'cantidad': int}]

    Devuelve un diccionario con:
        - 'success': bool
        - 'faltantes': list[str]
        - 'detalles': list[str]
    """
    try:
        session = Session(bind=engine)

        faltantes = []
        detalles = []
        success = True

        def verificar_material(codigo: str, cantidad_requerida: int, etiqueta: str):
            nonlocal success
            material = session.query(Stock).filter(Stock.codigo_material == codigo.upper()).first()

            if material:
                if material.cantidad >= cantidad_requerida:
                    detalles.append(f"{etiqueta.upper()}: OK ({material.cantidad} disponibles, se requieren {cantidad_requerida})")
                else:
                    faltantes.append(f"{etiqueta.upper()}: Stock insuficiente ({material.cantidad} disponibles, se requieren {cantidad_requerida})")
                    success = False
            else:
                faltantes.append(f"{etiqueta.upper()}: No encontrado en la base de datos")
                success = False

        # Broche (obligatorio)
        if "broche" in data:
            verificar_material(data["broche"], 1, "Broche")
        else:
            faltantes.append("Falta seleccionar un broche")
            success = False

        # Nombre (opcional)
        if "nombre" in data:
            nombre = data["nombre"].upper()
            letras_recuento = {}
            for letra in nombre:
                letras_recuento[letra] = letras_recuento.get(letra, 0) + 1

            for letra, cantidad in letras_recuento.items():
                verificar_material(letra, cantidad, f"Letra '{letra.upper()}'")

        # Dije normal (opcional)
        if "dije_normal" in data and data["dije_normal"]:
            verificar_material(data["dije_normal"], 1, "Dije normal")

        # Dije especial (opcional)
        if "dije_especial" in data and data["dije_especial"]:
            verificar_material(data["dije_especial"], 1, "Dije especial")

        # Bolitas (pueden ser varias)
        for bolita in data.get("bolitas", []):
            verificar_material(bolita["codigo"], bolita["cantidad"], f"Bolita {bolita['codigo']}")

        # Lentejas (pueden ser varias)
        for lenteja in data.get("lentejas", []):
            verificar_material(lenteja["codigo"], lenteja["cantidad"], f"Lenteja {lenteja['codigo']}")

        return {
            "success": success,
            "faltantes": faltantes,
            "detalles": detalles
        }
    
    except Exception as e:
        print(f'Ocurrio algun problema a la hora de validar la confeccion del pedido del portachupetes. Carpeta Logic - Archivo verificador2 - Funcion "verificar_confeccion". ERROR: {e}')