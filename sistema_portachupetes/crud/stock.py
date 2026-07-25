"""Stock actual y libro de movimientos en BigQuery."""

from __future__ import annotations

from datetime import date, datetime
import getpass
import uuid

import pandas as pd
from google.cloud import bigquery

from database.client import query, query_dataframe, table
from crud.materiales import validar_material

STOCK = table("stock")
MATERIALES = table("materiales")
MOVIMIENTOS = table("movimientos_stock")


def validar_stock(codigo_material: str) -> bool:
    rows = list(query(
        f"SELECT 1 FROM {STOCK} WHERE codigo_material=@codigo LIMIT 1",
        [bigquery.ScalarQueryParameter("codigo", "STRING", codigo_material.strip().upper())],
    ))
    return bool(rows)


def _aplicar_stock(codigo_material: str, nueva_cantidad: int, tipo: str, comentario=""):
    codigo = codigo_material.strip().upper()
    if nueva_cantidad < 0:
        return f"⚠️ El stock de {codigo} no puede ser negativo."
    if not validar_material(codigo):
        return f"⚠️ No existe el material {codigo}."
    params = [
        bigquery.ScalarQueryParameter("codigo", "STRING", codigo),
        bigquery.ScalarQueryParameter("cantidad", "INT64", int(nueva_cantidad)),
        bigquery.ScalarQueryParameter("tipo", "STRING", tipo),
        bigquery.ScalarQueryParameter("movimiento", "STRING", str(uuid.uuid4())),
        bigquery.ScalarQueryParameter("comentario", "STRING", comentario),
        bigquery.ScalarQueryParameter("usuario", "STRING", getpass.getuser()),
    ]
    query(
        f"""
        BEGIN TRANSACTION;
        INSERT INTO {MOVIMIENTOS}
        SELECT @movimiento,@codigo,CURRENT_TIMESTAMP(),@tipo,
               @cantidad-COALESCE((SELECT cantidad FROM {STOCK}
                                   WHERE codigo_material=@codigo LIMIT 1),0),
               COALESCE((SELECT cantidad FROM {STOCK}
                         WHERE codigo_material=@codigo LIMIT 1),0),
               @cantidad,NULL,@comentario,@usuario;
        MERGE {STOCK} T
        USING (SELECT @codigo codigo_material, @cantidad cantidad) S
        ON T.codigo_material=S.codigo_material
        WHEN MATCHED THEN UPDATE SET cantidad=S.cantidad, fecha_modificacion=CURRENT_TIMESTAMP()
        WHEN NOT MATCHED THEN INSERT(codigo_material,cantidad,fecha_modificacion)
          VALUES(S.codigo_material,S.cantidad,CURRENT_TIMESTAMP());
        COMMIT TRANSACTION;
        """,
        params,
    )
    return f"✅ Stock actualizado para {codigo}. Cantidad actual: {nueva_cantidad}."


def agregar_stock(codigo_material: str, cantidad: int, fecha_modificacion=None):
    codigo = codigo_material.strip().upper()
    actual = obtener_stock(codigo)
    anterior = actual["Cantidad"] if isinstance(actual, dict) else 0
    return _aplicar_stock(codigo, anterior + int(cantidad), "INGRESO_MANUAL")


def incrementar_stock(codigo_material: str, cantidad: int):
    return agregar_stock(codigo_material, cantidad)


def reducir_stock(codigo_material: str, cantidad: int):
    actual = obtener_stock(codigo_material)
    if not isinstance(actual, dict):
        return actual
    return _aplicar_stock(
        codigo_material, int(actual["Cantidad"]) - int(cantidad), "EGRESO_MANUAL"
    )


def actualizar_stock(codigo_material: str, cantidad: int):
    return _aplicar_stock(codigo_material, int(cantidad), "AJUSTE_MANUAL")


def eliminar_stock(codigo_material: str):
    return _aplicar_stock(codigo_material, 0, "AJUSTE_A_CERO", "Baja manual de stock")


def listar_stock():
    try:
        return query_dataframe(
            f"""
            SELECT s.codigo_material AS `Código`, m.descripcion AS `Descripción`,
                   m.color AS `Color`, m.categoria AS `Categoría`,
                   m.subcategoria AS `Subcategoría`, s.cantidad AS `Cantidad`,
                   s.fecha_modificacion AS `Última Modificación`
            FROM {STOCK} s JOIN {MATERIALES} m USING(codigo_material)
            WHERE m.activo=TRUE
            ORDER BY m.categoria, m.subcategoria, s.codigo_material
            """
        )
    except Exception as exc:
        raise RuntimeError(f"No se pudo consultar el stock: {exc}") from exc


def obtener_stock(codigo_material: str):
    df = query_dataframe(
        f"""
        SELECT s.codigo_material AS `Código`, s.cantidad AS `Cantidad`,
               s.fecha_modificacion AS `Última Modificación`,
               m.descripcion AS `Descripción`, m.color AS `Color`,
               m.categoria AS `Categoría`, m.subcategoria AS `Subcategoría`
        FROM {STOCK} s JOIN {MATERIALES} m USING(codigo_material)
        WHERE s.codigo_material=@codigo LIMIT 1
        """,
        [bigquery.ScalarQueryParameter(
            "codigo", "STRING", codigo_material.strip().upper()
        )],
    )
    return df.iloc[0].to_dict() if not df.empty else f"⚠️ No se encontró stock."


def agregar_stock_bulk(_session, codigo_material: str, cantidad: int, fecha_modificacion=None):
    return agregar_stock(codigo_material, cantidad, fecha_modificacion)


def cargar_stock_bulk(df: pd.DataFrame) -> list[str]:
    resultados = []
    for _, fila in df.iterrows():
        resultados.append(_aplicar_stock(
            str(fila["codigo material"]),
            int(fila["cantidad"]),
            "CARGA_MASIVA",
            "Stock final informado mediante Excel",
        ))
    return resultados


def validar_stock_with_session(_session, codigo_material: str) -> bool:
    return validar_stock(codigo_material)


def validar_material_with_session(_session, codigo_material: str) -> bool:
    return validar_material(codigo_material)
