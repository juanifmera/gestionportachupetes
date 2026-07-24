"""Pedidos minoristas y mayoristas respaldados por BigQuery."""

from __future__ import annotations

from collections import Counter
from datetime import date, datetime
from decimal import Decimal
import unicodedata
import uuid

import pandas as pd
from google.cloud import bigquery

from database.client import query, query_dataframe, table
from logic.verificador import (
    verificar_confeccion_pedido_mayorista,
    verificar_confeccion_portachupetes,
)

PEDIDOS = table("pedidos")
DETALLES = table("materiales_pedidos")
MATERIALES = table("materiales")
STOCK = table("stock")
MOVIMIENTOS = table("movimientos_stock")


def obtener_materiales_utilizados(data: dict) -> list[tuple]:
    materiales = []
    if data.get("broche"):
        materiales.append((data["broche"], 1))
    nombre_normalizado = unicodedata.normalize(
        "NFD", str(data.get("nombre", "")).upper()
    )
    nombre = "".join(
        caracter for caracter in nombre_normalizado
        if caracter.isalpha() and not unicodedata.combining(caracter)
    )
    materiales.extend(Counter(nombre).items())
    for grupo in ("dijes_normales", "dijes_especiales"):
        materiales.extend((x["codigo"], 1) for x in data.get(grupo, []))
    for grupo in ("bolitas", "lentejas"):
        materiales.extend((x["codigo"], x["cantidad"]) for x in data.get(grupo, []))
    acumulado = Counter()
    for codigo, cantidad in materiales:
        acumulado[str(codigo).strip().upper()] += int(cantidad)
    return [(codigo, cantidad) for codigo, cantidad in acumulado.items() if cantidad > 0]


def obtener_materiales_mayorista(data: dict) -> list[tuple]:
    acumulado = Counter()
    for grupo in (
        "broches", "letras", "dijes_normales", "dijes_especiales",
        "bolitas", "lentejas",
    ):
        for item in data.get(grupo, []):
            acumulado[str(item["codigo"]).strip().upper()] += int(item["cantidad"])
    return [(c, q) for c, q in acumulado.items() if q > 0]


def _costo_material(codigo):
    rows = list(query(
        f"SELECT COALESCE(costo_unitario,0) costo FROM {MATERIALES} "
        "WHERE codigo_material=@codigo AND activo=TRUE LIMIT 1",
        [bigquery.ScalarQueryParameter("codigo", "STRING", codigo)],
    ))
    return float(rows[0].costo) if rows else 0.0


def _crear_pedido(
    cliente, telefono, fecha_pedido, estado, tipo, materiales, precio_venta=None
):
    if not materiales:
        return "❌ El pedido no contiene materiales."
    fecha = fecha_pedido or date.today()
    if isinstance(fecha, datetime):
        fecha = fecha.date()

    lineas = []
    costo_total = 0.0
    letras_procesadas = 0
    for codigo, cantidad in materiales:
        costo = _costo_material(codigo)
        costo_linea = costo * cantidad
        if tipo == "minorista" and len(codigo) == 1 and codigo.isalpha():
            costo_linea = 0
            for _ in range(cantidad):
                letras_procesadas += 1
                costo_linea += costo if letras_procesadas <= 5 else 500
        costo_total += costo_linea
        lineas.append((codigo, cantidad, costo, costo_linea))

    params = [
        bigquery.ScalarQueryParameter("cliente", "STRING", str(cliente).strip()),
        bigquery.ScalarQueryParameter("telefono", "STRING", str(telefono or "").strip()),
        bigquery.ScalarQueryParameter("fecha", "DATE", fecha),
        bigquery.ScalarQueryParameter("estado", "STRING", estado),
        bigquery.ScalarQueryParameter("tipo", "STRING", tipo),
        bigquery.ScalarQueryParameter(
            "costo_total", "NUMERIC", Decimal(str(costo_total))
        ),
        bigquery.ScalarQueryParameter(
            "precio_venta",
            "NUMERIC",
            Decimal(str(precio_venta or 0)),
        ),
    ]
    bloques = []
    for i, (codigo, cantidad, costo, costo_linea) in enumerate(lineas):
        params.extend([
            bigquery.ScalarQueryParameter(f"c{i}", "STRING", codigo),
            bigquery.ScalarQueryParameter(f"q{i}", "INT64", cantidad),
            bigquery.ScalarQueryParameter(
                f"cu{i}", "NUMERIC", Decimal(str(costo))
            ),
            bigquery.ScalarQueryParameter(
                f"ct{i}", "NUMERIC", Decimal(str(costo_linea))
            ),
            bigquery.ScalarQueryParameter(f"d{i}", "STRING", str(uuid.uuid4())),
            bigquery.ScalarQueryParameter(f"m{i}", "STRING", str(uuid.uuid4())),
        ])
        bloques.append(f"""
        ASSERT (
          SELECT COALESCE(MAX(cantidad),0) FROM {STOCK}
          WHERE codigo_material=@c{i}
        ) >= @q{i} AS 'Stock insuficiente';
        INSERT INTO {DETALLES}
        VALUES(@d{i},nuevo_id,@c{i},@q{i},@cu{i},@ct{i},CURRENT_TIMESTAMP());
        INSERT INTO {MOVIMIENTOS}
        SELECT @m{i},@c{i},CURRENT_TIMESTAMP(),'CONSUMO_PEDIDO',-@q{i},
               cantidad,cantidad-@q{i},nuevo_id,'Pedido generado',SESSION_USER()
        FROM {STOCK} WHERE codigo_material=@c{i};
        UPDATE {STOCK}
        SET cantidad=cantidad-@q{i}, fecha_modificacion=CURRENT_TIMESTAMP()
        WHERE codigo_material=@c{i};
        """)
    resultados = list(query(
        f"""
        DECLARE nuevo_id INT64 DEFAULT (
          SELECT COALESCE(MAX(id), 0) + 1 FROM {PEDIDOS}
        );
        BEGIN TRANSACTION;
        INSERT INTO {PEDIDOS} (
          id, cliente, telefono, fecha_pedido, estado, costo_total,
          precio_venta, tipo, comentarios, fecha_creacion, fecha_actualizacion
        )
        VALUES(
          nuevo_id,@cliente,@telefono,@fecha,@estado,@costo_total,
          @precio_venta,@tipo,NULL,CURRENT_TIMESTAMP(),CURRENT_TIMESTAMP()
        );
        {''.join(bloques)}
        COMMIT TRANSACTION;
        SELECT nuevo_id AS pedido_id;
        """,
        params,
    ))
    pedido_id = int(resultados[0].pedido_id)
    return (
        f"✅ Pedido generado con éxito para {str(cliente).capitalize()} "
        f"(ID: {pedido_id}) - Costo Total: ${int(costo_total):,}"
    ).replace(",", ".")


def crear_pedido(
    cliente: str, materiales_portachupete: dict, estado="En proceso",
    fecha_pedido=None, telefono="", tipo="minorista", precio_venta=None,
):
    try:
        validacion = verificar_confeccion_portachupetes(materiales_portachupete)
        if not validacion["success"]:
            return f"❌ Stock insuficiente: {validacion['faltantes']}"
        return _crear_pedido(
            cliente, telefono, fecha_pedido, estado, tipo,
            obtener_materiales_utilizados(materiales_portachupete), precio_venta,
        )
    except Exception as exc:
        return f"❌ Error al generar pedido: {exc}"


def crear_pedido_mayorista(
    cliente: str, materiales: dict, estado="En proceso",
    fecha_pedido=None, tipo="mayorista", telefono="", precio_venta=None,
):
    try:
        validacion = verificar_confeccion_pedido_mayorista(materiales)
        if not validacion["success"]:
            return f"❌ Stock insuficiente: {validacion['faltantes']}"
        return _crear_pedido(
            cliente, telefono, fecha_pedido, estado, tipo,
            obtener_materiales_mayorista(materiales), precio_venta,
        )
    except Exception as exc:
        return f"❌ Error al generar pedido: {exc}"


def listar_todos_pedidos():
    try:
        return query_dataframe(
            f"""
            SELECT id AS ID, cliente AS Cliente, telefono AS Telefono,
                   fecha_pedido AS `Fecha Creación`, estado AS Estado,
                   costo_total AS `Costo Total`, precio_venta AS `Precio Venta`
            FROM {PEDIDOS} ORDER BY fecha_pedido DESC, fecha_creacion DESC
            """
        )
    except Exception as exc:
        raise RuntimeError(f"No se pudieron consultar los pedidos: {exc}") from exc


def obtener_pedido(id: int):
    df = query_dataframe(
        f"""
        SELECT id AS ID, cliente AS Cliente, estado AS Estado,
               fecha_pedido AS `Fecha Pedido`, telefono AS `Teléfono`,
               costo_total AS `Costo Total`, precio_venta AS `Precio Venta`
        FROM {PEDIDOS} WHERE id=@id LIMIT 1
        """,
        [bigquery.ScalarQueryParameter("id", "INT64", int(id))],
    )
    return df.iloc[0].to_dict() if not df.empty else f"No se encontró pedido {id}"


def listar_materiales_pedido(id: int):
    return query_dataframe(
        f"""
        SELECT codigo_material AS `Código`, cantidad_usada AS `Cantidad`,
               costo_unitario AS `Costo Unitario`
        FROM {DETALLES} WHERE pedido_id=@id ORDER BY codigo_material
        """,
        [bigquery.ScalarQueryParameter("id", "INT64", int(id))],
    )


def terminar_pedido(id: int):
    pedido = obtener_pedido(id)
    if not isinstance(pedido, dict):
        return f"⚠️ No se encontró el pedido {id}."
    if pedido["Estado"] == "Cancelado":
        return "⚠️ No se puede terminar un pedido cancelado."
    query(
        f"UPDATE {PEDIDOS} SET estado='Terminado', "
        "fecha_actualizacion=CURRENT_TIMESTAMP() WHERE id=@id",
        [bigquery.ScalarQueryParameter("id", "INT64", int(id))],
    )
    return f"✅ Pedido {id} terminado con éxito."


def cancelar_pedido(id: int):
    try:
        pedido = obtener_pedido(id)
        if not isinstance(pedido, dict):
            return f"⚠️ No se encontró el pedido {id}."
        if pedido["Estado"] in ("Cancelado", "Terminado"):
            return f"⚠️ No se puede cancelar un pedido {pedido['Estado']}."
        detalles = listar_materiales_pedido(id)
        params = [bigquery.ScalarQueryParameter("id", "INT64", int(id))]
        bloques = []
        for i, row in detalles.iterrows():
            params.extend([
                bigquery.ScalarQueryParameter(f"c{i}", "STRING", row["Código"]),
                bigquery.ScalarQueryParameter(f"q{i}", "INT64", int(row["Cantidad"])),
                bigquery.ScalarQueryParameter(f"m{i}", "STRING", str(uuid.uuid4())),
            ])
            bloques.append(f"""
            INSERT INTO {MOVIMIENTOS}
            SELECT @m{i},@c{i},CURRENT_TIMESTAMP(),'DEVOLUCION_CANCELACION',@q{i},
                   cantidad,cantidad+@q{i},@id,'Pedido cancelado',SESSION_USER()
            FROM {STOCK} WHERE codigo_material=@c{i};
            UPDATE {STOCK} SET cantidad=cantidad+@q{i},
                   fecha_modificacion=CURRENT_TIMESTAMP()
            WHERE codigo_material=@c{i};
            """)
        query(
            f"""
            BEGIN TRANSACTION;
            UPDATE {PEDIDOS} SET estado='Cancelado',
              fecha_actualizacion=CURRENT_TIMESTAMP() WHERE id=@id;
            {''.join(bloques)}
            COMMIT TRANSACTION;
            """,
            params,
        )
        return f"✅ Pedido {id} cancelado y materiales devueltos al stock."
    except Exception as exc:
        return f"❌ Error al cancelar pedido: {exc}"


def actualizar_varios_campos_pedido(id: int, cambios: dict) -> str:
    permitidos = {
        "cliente": "cliente", "telefono": "telefono",
        "fecha_pedido": "fecha_pedido", "costo_total": "costo_total",
        "precio_venta": "precio_venta", "comentarios": "comentarios",
    }
    pedido = obtener_pedido(id)
    if not isinstance(pedido, dict):
        return f"❌ No se encontró el pedido {id}."
    if pedido["Estado"] in ("Cancelado", "Terminado"):
        return f"⚠️ No se puede modificar un pedido {pedido['Estado']}."
    partes, params = [], [bigquery.ScalarQueryParameter("id", "INT64", int(id))]
    tipos = {
        "fecha_pedido": "DATE",
        "costo_total": "NUMERIC",
        "precio_venta": "NUMERIC",
    }
    for i, (campo, valor) in enumerate(cambios.items()):
        if campo not in permitidos:
            continue
        partes.append(f"{permitidos[campo]}=@v{i}")
        if campo in ("costo_total", "precio_venta"):
            valor = Decimal(str(valor or 0))
        params.append(bigquery.ScalarQueryParameter(f"v{i}", tipos.get(campo, "STRING"), valor))
    if not partes:
        return "⚠️ No hay campos válidos para actualizar."
    query(
        f"UPDATE {PEDIDOS} SET {', '.join(partes)}, "
        "fecha_actualizacion=CURRENT_TIMESTAMP() WHERE id=@id",
        params,
    )
    return f"✅ Pedido {id} actualizado correctamente."


def modificar_pedido(id: int, columna: str, valor):
    return actualizar_varios_campos_pedido(id, {columna: valor})


def listar_pedidos_por_estado(estado: str):
    df = listar_todos_pedidos()
    return df[df["Estado"] == estado]


def eliminar_pedido(id: int):
    return "⚠️ Los pedidos no se eliminan: deben cancelarse para conservar la auditoría."


def listar_materiales_pedido_completo():
    return query_dataframe(
        f"""
        SELECT d.codigo_material AS `Código`, m.descripcion AS `Descripción`,
               m.categoria AS `Categoría`, m.subcategoria AS `Subcategoría`,
               m.color AS `Color`, m.costo_unitario AS `Costo Unitario`,
               SUM(d.cantidad_usada) AS `Cantidad Usada`
        FROM {DETALLES} d
        JOIN {MATERIALES} m USING(codigo_material)
        JOIN {PEDIDOS} p ON p.id=d.pedido_id
        WHERE p.estado != 'Cancelado'
        GROUP BY 1,2,3,4,5,6 ORDER BY 7 DESC
        """
    )


def calcular_costo_total_pedido(pedido_id: int) -> float:
    pedido = obtener_pedido(pedido_id)
    return float(pedido["Costo Total"] or 0) if isinstance(pedido, dict) else 0.0


def crear_pedido_dummy(
    cliente: str, materiales_portachupete: dict, estado="En proceso",
    fecha_pedido=None, telefono="", tipo="minorista",
):
    return "⚠️ La creación de pedidos dummy quedó deshabilitada para proteger el stock."


def actualizar_varios_campos_pedido_aux(id: int, cambios: dict) -> str:
    return actualizar_varios_campos_pedido(id, cambios)
