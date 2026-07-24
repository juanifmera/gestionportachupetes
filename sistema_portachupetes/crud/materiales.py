"""Operaciones de materiales en BigQuery."""

from __future__ import annotations

from datetime import date, datetime
from decimal import Decimal

import pandas as pd
from google.cloud import bigquery

from database.client import query, query_dataframe, table

T = table("materiales")
COLUMNAS = {
    "descripcion": "descripcion",
    "color": "color",
    "categoria": "categoria",
    "subcategoria": "subcategoria",
    "fecha_ingreso": "fecha_ingreso",
    "comentarios": "comentarios",
    "costo_unitario": "costo_unitario",
    "activo": "activo",
}


def _texto(valor, *, upper=False):
    if valor is None or pd.isna(valor):
        return ""
    texto = str(valor).strip()
    return texto.upper() if upper else texto


def agregar_material(
    codigo_material: str,
    descripcion: str,
    color: str,
    categoria: str,
    subcategoria: str,
    costo_unitario: float = 0,
    comentarios=None,
    fecha_ingreso=None,
) -> str:
    try:
        codigo = _texto(codigo_material, upper=True)
        if not codigo:
            return "⚠️ El código del material es obligatorio."
        if validar_material(codigo):
            return f"⚠️ Ya existe el material {codigo}."
        fecha = fecha_ingreso or date.today()
        if isinstance(fecha, datetime):
            fecha = fecha.date()
        costo = 0 if costo_unitario is None or pd.isna(costo_unitario) else costo_unitario
        params = [
            bigquery.ScalarQueryParameter("codigo", "STRING", codigo),
            bigquery.ScalarQueryParameter("descripcion", "STRING", _texto(descripcion)),
            bigquery.ScalarQueryParameter("color", "STRING", _texto(color)),
            bigquery.ScalarQueryParameter("categoria", "STRING", _texto(categoria)),
            bigquery.ScalarQueryParameter("subcategoria", "STRING", _texto(subcategoria)),
            bigquery.ScalarQueryParameter("fecha", "DATE", fecha),
            bigquery.ScalarQueryParameter("comentarios", "STRING", _texto(comentarios)),
            bigquery.ScalarQueryParameter(
                "costo", "NUMERIC", Decimal(str(costo))
            ),
        ]
        query(
            f"""
            INSERT INTO {T}
            (codigo_material, descripcion, color, categoria, subcategoria,
             fecha_ingreso, comentarios, costo_unitario, activo,
             fecha_creacion, fecha_actualizacion)
            SELECT @codigo, @descripcion, @color, @categoria, @subcategoria,
                   @fecha, @comentarios, @costo, TRUE,
                   CURRENT_TIMESTAMP(), CURRENT_TIMESTAMP()
            WHERE NOT EXISTS (
              SELECT 1 FROM {T} WHERE codigo_material = @codigo
            )
            """,
            params,
        )
        if not validar_material(codigo):
            return f"❌ No se pudo agregar el material {codigo}."
        return f'✅ Nuevo material "{_texto(descripcion)}" con código {codigo} agregado con éxito.'
    except Exception as exc:
        return f"❌ Error al agregar material. Detalle: {exc}"


def listar_todos_materiales():
    try:
        df = query_dataframe(
            f"""
            SELECT codigo_material AS `Código`, descripcion AS `Descripción`,
                   color AS `Color`, categoria AS `Categoría`,
                   subcategoria AS `Subcategoría`, fecha_ingreso AS `Fecha Ingreso`,
                   costo_unitario AS `Costo Unitario`, comentarios AS `Comentarios`
            FROM {T}
            WHERE activo = TRUE
            ORDER BY categoria, subcategoria, codigo_material
            """
        )
        return df
    except Exception as exc:
        raise RuntimeError(f"No se pudieron consultar los materiales: {exc}") from exc


def validar_material(codigo_material: str) -> bool:
    codigo = _texto(codigo_material, upper=True)
    rows = list(query(
        f"SELECT 1 FROM {T} WHERE codigo_material=@codigo AND activo=TRUE LIMIT 1",
        [bigquery.ScalarQueryParameter("codigo", "STRING", codigo)],
    ))
    return bool(rows)


def obtener_material(codigo_material: str):
    codigo = _texto(codigo_material, upper=True)
    df = query_dataframe(
        f"""
        SELECT codigo_material AS `Código`, descripcion AS `Descripción`,
               color AS `Color`, categoria AS `Categoría`,
               subcategoria AS `Subcategoría`, fecha_ingreso AS `Fecha Ingreso`,
               costo_unitario AS `Costo Unitario`, comentarios AS `Comentarios`
        FROM {T} WHERE codigo_material=@codigo AND activo=TRUE LIMIT 1
        """,
        [bigquery.ScalarQueryParameter("codigo", "STRING", codigo)],
    )
    return df.iloc[0].to_dict() if not df.empty else f"⚠️ No se encontró material {codigo}"


def actualizar_varios_campos(codigo_material: str, cambios: dict):
    try:
        permitidos = {k: v for k, v in cambios.items() if k in COLUMNAS}
        if not permitidos:
            return "⚠️ No hay campos válidos para actualizar."
        asignaciones, params = [], [
            bigquery.ScalarQueryParameter("codigo", "STRING", _texto(codigo_material, upper=True))
        ]
        tipos = {
            "fecha_ingreso": "DATE", "costo_unitario": "NUMERIC", "activo": "BOOL"
        }
        for indice, (campo, valor) in enumerate(permitidos.items()):
            nombre = f"v{indice}"
            asignaciones.append(f"{COLUMNAS[campo]}=@{nombre}")
            if campo == "costo_unitario":
                valor = Decimal(str(valor or 0))
            params.append(bigquery.ScalarQueryParameter(nombre, tipos.get(campo, "STRING"), valor))
        query(
            f"UPDATE {T} SET {', '.join(asignaciones)}, fecha_actualizacion=CURRENT_TIMESTAMP() "
            "WHERE codigo_material=@codigo",
            params,
        )
        return f"✅ Material {_texto(codigo_material, upper=True)} actualizado correctamente."
    except Exception as exc:
        return f"❌ Error al actualizar material: {exc}"


def actualizar_material(codigo_material: str, columna: str, nuevo_valor):
    return actualizar_varios_campos(codigo_material, {columna: nuevo_valor})


def eliminar_material(codigo_material: str):
    """Baja lógica para preservar el historial de pedidos."""
    return actualizar_varios_campos(codigo_material, {"activo": False})


def listo_con_filtro(columna: str, valor):
    df = listar_todos_materiales()
    equivalencias = {
        "categoria": "Categoría", "subcategoria": "Subcategoría",
        "color": "Color", "codigo_material": "Código",
    }
    nombre = equivalencias.get(columna, columna)
    return df[df[nombre] == valor] if nombre in df.columns else pd.DataFrame()


def listar_materiales_filtrados(categoria="Todas", subcategoria="Todas", color="Todos"):
    df = listar_todos_materiales()
    if categoria != "Todas":
        df = df[df["Categoría"] == categoria]
    if subcategoria != "Todas":
        df = df[df["Subcategoría"] == subcategoria]
    if color != "Todos":
        df = df[df["Color"] == color]
    return df


def cargar_materiales_bulk(df: pd.DataFrame) -> list[str]:
    resultados = []
    for _, fila in df.iterrows():
        resultados.append(agregar_material(
            codigo_material=fila["codigo material"],
            descripcion=fila["descripcion"],
            color=fila["color"],
            categoria=fila["categoria"],
            subcategoria=fila["subcategoria"],
            fecha_ingreso=fila["fecha ingreso"],
            comentarios=fila.get("comentarios", ""),
            costo_unitario=fila.get("costo unitario", 0),
        ))
    return resultados
