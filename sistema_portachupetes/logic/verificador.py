"""Validaciones de disponibilidad independientes de la interfaz."""

from collections import Counter

from crud.stock import obtener_stock


def _validar(requeridos):
    faltantes, detalles = [], []
    agrupados = Counter()
    for codigo, cantidad in requeridos:
        codigo = str(codigo).strip().upper()
        if codigo and int(cantidad) > 0:
            agrupados[codigo] += int(cantidad)
    for codigo, cantidad in agrupados.items():
        stock = obtener_stock(codigo)
        disponible = int(stock["Cantidad"]) if isinstance(stock, dict) else 0
        if disponible < cantidad:
            faltantes.append(
                f"{codigo}: stock insuficiente ({disponible} disponibles, "
                f"se requieren {cantidad})"
            )
        else:
            detalles.append(
                f"{codigo}: OK ({disponible} disponibles, se requieren {cantidad})"
            )
    return {
        "success": not faltantes,
        "faltantes": faltantes,
        "detalles": detalles,
    }


def verificar_confeccion_portachupetes(data: dict) -> dict:
    requeridos = []
    if data.get("broche"):
        requeridos.append((data["broche"], 1))
    requeridos.extend(Counter(str(data.get("nombre", "")).upper()).items())
    for grupo in ("dijes_normales", "dijes_especiales"):
        requeridos.extend((x["codigo"], 1) for x in data.get(grupo, []))
    for grupo in ("bolitas", "lentejas"):
        requeridos.extend(
            (x["codigo"], x["cantidad"]) for x in data.get(grupo, [])
        )
    return _validar(requeridos)


def verificar_confeccion_pedido_mayorista(data: dict) -> dict:
    requeridos = []
    for grupo in (
        "broches", "letras", "dijes_normales", "dijes_especiales",
        "bolitas", "lentejas",
    ):
        requeridos.extend(
            (x["codigo"], x["cantidad"]) for x in data.get(grupo, [])
        )
    return _validar(requeridos)
