from datetime import datetime

import pandas as pd
import streamlit as st

from crud.materiales import listar_todos_materiales
from crud.pedidos import (
    actualizar_varios_campos_pedido,
    cancelar_pedido,
    crear_pedido,
    crear_pedido_mayorista,
    listar_materiales_pedido,
    listar_todos_pedidos,
    obtener_pedido,
    terminar_pedido,
)
from crud.stock import listar_stock
from ui.utils.utils import proteger_pagina


@st.cache_data(ttl=30, show_spinner="Consultando stock...")
def cargar_stock():
    return listar_stock()


@st.cache_data(ttl=30, show_spinner="Consultando pedidos...")
def cargar_pedidos():
    return listar_todos_pedidos()


@st.cache_data(ttl=30, show_spinner="Consultando materiales...")
def cargar_materiales():
    return listar_todos_materiales()


def finalizar(resultado):
    if resultado.startswith("✅"):
        st.success(resultado)
        st.cache_data.clear()
    elif resultado.startswith("⚠️"):
        st.warning(resultado)
    else:
        st.error(resultado)


def codigos(stock, categoria, subcategoria=None):
    filtro = (stock["Categoría"] == categoria) & (stock["Cantidad"] > 0)
    if subcategoria:
        filtro &= stock["Subcategoría"] == subcategoria
    return sorted(stock.loc[filtro, "Código"].tolist())


proteger_pagina()
st.title("Pedidos 📝")
st.divider()

accion = st.radio(
    "Acción",
    ["Nuevo", "Mayorista", "Gestionar", "Actualizar", "Listar", "Detalle"],
    horizontal=True,
    label_visibility="collapsed",
)

if accion == "Nuevo":
    st.subheader("🧾 Generar pedido personalizado", divider="rainbow")
    stock = cargar_stock()
    if stock.empty:
        st.info("Primero debés cargar materiales y stock.")
    else:
        broches = sorted(stock.loc[
            stock["Categoría"].isin(["Broche", "Llavero", "Identificador"])
            & (stock["Cantidad"] > 0),
            "Código",
        ].tolist())
        if not broches:
            st.warning(
                "No hay broches, llaveros ni identificadores con stock. "
                "Cargá al menos uno para generar pedidos."
            )
        else:
            st.markdown("### 1. Configuración")
            c1, c2, c3, c4 = st.columns(4)
            n_bolitas = c1.number_input(
                "Bolitas distintas", 0, 10, 0, key="n_bolitas"
            )
            n_lentejas = c2.number_input(
                "Lentejas distintas", 0, 10, 0, key="n_lentejas"
            )
            n_dijes = c3.number_input(
                "Dijes normales", 0, 5, 0, key="n_dijes"
            )
            n_especiales = c4.number_input(
                "Dijes especiales", 0, 5, 0, key="n_especiales"
            )

            opciones = {
                "dijes": codigos(stock, "Dije", "Normal"),
                "especiales": codigos(stock, "Dije", "Especial"),
                "bolitas": codigos(stock, "Bolita"),
                "lentejas": codigos(stock, "Lenteja"),
            }
            faltan = []
            for cantidad, clave, nombre in (
                (n_dijes, "dijes", "dijes normales"),
                (n_especiales, "especiales", "dijes especiales"),
                (n_bolitas, "bolitas", "bolitas"),
                (n_lentejas, "lentejas", "lentejas"),
            ):
                if cantidad and not opciones[clave]:
                    faltan.append(nombre)
            if faltan:
                st.warning(
                    "No hay stock disponible para: " + ", ".join(faltan) + "."
                )
            else:
                with st.form("nuevo_pedido"):
                    st.markdown("### 2. Datos y materiales")
                    c1, c2 = st.columns(2)
                    cliente = c1.text_input("Cliente *")
                    telefono = c1.text_input("Teléfono")
                    nombre = c2.text_input("Nombre del bebé *")
                    fecha = c2.date_input(
                        "Fecha", value=datetime.today(), format="DD/MM/YYYY"
                    )
                    precio_venta = c2.number_input(
                        "Precio final de venta", min_value=0.0, value=0.0, step=100.0
                    )
                    broche = st.selectbox("Broche / base *", broches)

                    dijes_normales = [
                        {"codigo": st.selectbox(
                            f"Dije normal #{i + 1}", opciones["dijes"],
                            key=f"dn_{i}",
                        )}
                        for i in range(int(n_dijes))
                    ]
                    dijes_especiales = [
                        {"codigo": st.selectbox(
                            f"Dije especial #{i + 1}", opciones["especiales"],
                            key=f"de_{i}",
                        )}
                        for i in range(int(n_especiales))
                    ]
                    bolitas = []
                    for i in range(int(n_bolitas)):
                        c1, c2 = st.columns([2, 1])
                        codigo = c1.selectbox(
                            f"Bolita #{i + 1}", opciones["bolitas"], key=f"b_{i}"
                        )
                        cantidad = c2.number_input(
                            "Cantidad", 1, 100, 1, key=f"bq_{i}"
                        )
                        bolitas.append({"codigo": codigo, "cantidad": cantidad})
                    lentejas = []
                    for i in range(int(n_lentejas)):
                        c1, c2 = st.columns([2, 1])
                        codigo = c1.selectbox(
                            f"Lenteja #{i + 1}", opciones["lentejas"], key=f"l_{i}"
                        )
                        cantidad = c2.number_input(
                            "Cantidad", 1, 100, 1, key=f"lq_{i}"
                        )
                        lentejas.append({"codigo": codigo, "cantidad": cantidad})
                    enviar = st.form_submit_button(
                        "Generar pedido", type="primary", use_container_width=True
                    )
                if enviar:
                    if not cliente.strip() or not nombre.strip():
                        st.error("Completá cliente y nombre del bebé.")
                    else:
                        finalizar(crear_pedido(
                            cliente,
                            {
                                "broche": broche,
                                "nombre": nombre,
                                "dijes_normales": dijes_normales,
                                "dijes_especiales": dijes_especiales,
                                "bolitas": bolitas,
                                "lentejas": lentejas,
                            },
                            telefono=telefono,
                            fecha_pedido=fecha,
                            precio_venta=precio_venta,
                        ))

elif accion == "Mayorista":
    st.subheader("📦 Generar pedido mayorista", divider="rainbow")
    stock = cargar_stock()
    disponibles = stock.loc[stock["Cantidad"] > 0, "Código"].tolist()
    if not disponibles:
        st.info("No hay materiales con stock.")
    else:
        cantidad_lineas = st.number_input(
            "Cantidad de materiales distintos", 1, 50, 1
        )
        with st.form("pedido_mayorista"):
            c1, c2 = st.columns(2)
            cliente = c1.text_input("Cliente *")
            telefono = c1.text_input("Teléfono")
            fecha = c2.date_input(
                "Fecha", value=datetime.today(), format="DD/MM/YYYY"
            )
            precio_venta = c2.number_input(
                "Precio final de venta", min_value=0.0, value=0.0, step=100.0
            )
            seleccionados = []
            for i in range(int(cantidad_lineas)):
                c1, c2 = st.columns([2, 1])
                codigo = c1.selectbox(
                    f"Material #{i + 1}", disponibles, key=f"may_c_{i}"
                )
                cantidad = c2.number_input(
                    "Cantidad", 1, 10000, 1, key=f"may_q_{i}"
                )
                seleccionados.append({"codigo": codigo, "cantidad": cantidad})
            enviar = st.form_submit_button(
                "Generar pedido mayorista",
                type="primary",
                use_container_width=True,
            )
        if enviar:
            if not cliente.strip():
                st.error("Completá el nombre del cliente.")
            else:
                por_categoria = {
                    "broches": [], "letras": [], "dijes_normales": [],
                    "dijes_especiales": [], "bolitas": [], "lentejas": [],
                }
                mapa = stock.set_index("Código")
                for item in seleccionados:
                    fila = mapa.loc[item["codigo"]]
                    categoria = fila["Categoría"]
                    if categoria in ("Broche", "Llavero", "Identificador"):
                        por_categoria["broches"].append(item)
                    elif categoria == "Letra":
                        por_categoria["letras"].append(item)
                    elif categoria == "Dije":
                        clave = (
                            "dijes_especiales"
                            if fila["Subcategoría"] == "Especial"
                            else "dijes_normales"
                        )
                        por_categoria[clave].append(item)
                    elif categoria == "Bolita":
                        por_categoria["bolitas"].append(item)
                    elif categoria == "Lenteja":
                        por_categoria["lentejas"].append(item)
                finalizar(crear_pedido_mayorista(
                    cliente,
                    por_categoria,
                    telefono=telefono,
                    fecha_pedido=fecha,
                    precio_venta=precio_venta,
                ))

elif accion == "Gestionar":
    st.subheader("✅ Gestionar pedidos en proceso", divider="rainbow")
    pedidos = cargar_pedidos()
    activos = pedidos[pedidos["Estado"] == "En proceso"]
    if activos.empty:
        st.info("No hay pedidos en proceso.")
    else:
        st.dataframe(activos, use_container_width=True)
        pedido_id = int(st.selectbox(
            "Pedido", sorted(activos["ID"].tolist(), reverse=True)
        ))
        if st.button(
            "Marcar como terminado", type="primary", use_container_width=True
        ):
            finalizar(terminar_pedido(pedido_id))
        c1, c2 = st.columns(2)
        with c1:
            confirmar = st.checkbox("Confirmar cancelación")
        with c2:
            if st.button("Cancelar y devolver stock", use_container_width=True):
                if confirmar:
                    finalizar(cancelar_pedido(pedido_id))
                else:
                    st.warning("Confirmá la cancelación.")

elif accion == "Actualizar":
    st.subheader("✏️ Actualizar pedido", divider="rainbow")
    pedidos = cargar_pedidos()
    activos = pedidos[pedidos["Estado"] == "En proceso"]
    if activos.empty:
        st.info("No hay pedidos editables.")
    else:
        pedido_id = int(st.selectbox(
            "Pedido", sorted(activos["ID"].tolist(), reverse=True)
        ))
        datos = obtener_pedido(pedido_id)
        with st.form("actualizar_pedido"):
            cliente = st.text_input("Cliente", datos["Cliente"])
            telefono = st.text_input("Teléfono", datos["Teléfono"] or "")
            fecha = st.date_input("Fecha", datos["Fecha Pedido"])
            costo = st.number_input(
                "Costo total", min_value=0.0, value=float(datos["Costo Total"] or 0)
            )
            precio_venta = st.number_input(
                "Precio final de venta",
                min_value=0.0,
                value=float(datos["Precio Venta"] or 0),
            )
            enviar = st.form_submit_button(
                "Guardar cambios", type="primary", use_container_width=True
            )
        if enviar:
            finalizar(actualizar_varios_campos_pedido(pedido_id, {
                "cliente": cliente,
                "telefono": telefono,
                "fecha_pedido": fecha,
                "costo_total": costo,
                "precio_venta": precio_venta,
            }))

elif accion == "Listar":
    st.subheader("📰 Pedidos", divider="rainbow")
    pedidos = cargar_pedidos()
    if pedidos.empty:
        st.info("Todavía no hay pedidos.")
    else:
        c1, c2 = st.columns(2)
        estado = c1.selectbox(
            "Estado", ["Todos"] + sorted(pedidos["Estado"].unique())
        )
        cliente = c2.text_input("Buscar cliente")
        filtrados = pedidos.copy()
        if estado != "Todos":
            filtrados = filtrados[filtrados["Estado"] == estado]
        if cliente:
            filtrados = filtrados[
                filtrados["Cliente"].str.contains(cliente, case=False)
            ]
        st.dataframe(filtrados, use_container_width=True)

elif accion == "Detalle":
    st.subheader("🔍 Detalle del pedido", divider="rainbow")
    pedidos = cargar_pedidos()
    if pedidos.empty:
        st.info("Todavía no hay pedidos.")
    else:
        pedido_id = int(st.selectbox(
            "Pedido", sorted(pedidos["ID"].tolist(), reverse=True)
        ))
        datos = obtener_pedido(pedido_id)
        costo_total = float(datos["Costo Total"] or 0)
        precio_estimado = costo_total * 2.75
        precio_venta = float(datos["Precio Venta"] or 0)
        st.json({
            "ID Pedido": pedido_id,
            "Cliente": datos["Cliente"],
            "Teléfono": datos["Teléfono"],
            "Fecha": str(datos["Fecha Pedido"]),
            "Estado": datos["Estado"],
            "Costo Total": costo_total,
            "Precio Estimado Venta": precio_estimado,
            "Precio Final de Venta": precio_venta,
            "Diferencia vs Estimado": precio_venta - precio_estimado,
        })
        detalles = listar_materiales_pedido(pedido_id)
        if detalles.empty:
            st.info("Este pedido no tiene materiales asociados.")
        else:
            materiales = cargar_materiales()[[
                "Código", "Descripción", "Color", "Categoría", "Subcategoría"
            ]]
            detalle = detalles.merge(materiales, on="Código", how="left")
            st.dataframe(detalle, use_container_width=True)
