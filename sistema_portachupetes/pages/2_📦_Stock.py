import io
import os

import pandas as pd
import streamlit as st

from crud.materiales import listar_todos_materiales
from crud.stock import (
    actualizar_stock,
    agregar_stock,
    cargar_stock_bulk,
    eliminar_stock,
    listar_stock,
    obtener_stock,
)
from ui.utils.utils import proteger_pagina


@st.cache_data(ttl=30, show_spinner="Consultando materiales...")
def cargar_materiales():
    return listar_todos_materiales()


@st.cache_data(ttl=30, show_spinner="Consultando stock...")
def cargar_stock():
    return listar_stock()


def finalizar(resultado):
    if resultado.startswith("✅"):
        st.success(resultado)
        st.cache_data.clear()
    elif resultado.startswith("⚠️"):
        st.warning(resultado)
    else:
        st.error(resultado)


proteger_pagina()
st.title("Stock 📦")
st.divider()

accion = st.radio(
    "Acción",
    ["Agregar", "Ajustar", "Dejar en cero", "Listar", "Carga Excel"],
    horizontal=True,
    label_visibility="collapsed",
)

if accion == "Agregar":
    st.subheader("➕ Agregar stock", divider="rainbow")
    st.caption(
        "La cantidad ingresada se suma al stock actual. Si el material todavía "
        "no tiene stock, se crea su primera existencia."
    )
    materiales = cargar_materiales()
    stock = cargar_stock()
    if materiales.empty:
        st.info("Primero debés cargar al menos un material.")
    else:
        resumen = materiales.merge(
            stock[["Código", "Cantidad"]], on="Código", how="left"
        )
        resumen["Cantidad"] = resumen["Cantidad"].fillna(0).astype(int)
        st.dataframe(
            resumen[["Código", "Descripción", "Categoría", "Cantidad"]],
            use_container_width=True,
        )
        with st.form("agregar_stock"):
            codigo = st.selectbox("Código del material", sorted(materiales["Código"]))
            cantidad = st.number_input(
                "Cantidad a ingresar", min_value=1, value=1, step=1
            )
            enviar = st.form_submit_button(
                "Agregar stock", type="primary", use_container_width=True
            )
        if enviar:
            finalizar(agregar_stock(codigo, int(cantidad)))

elif accion == "Ajustar":
    st.subheader("✏️ Ajustar stock final", divider="rainbow")
    stock = cargar_stock()
    if stock.empty:
        st.info("Todavía no existe stock para ajustar.")
    else:
        codigo = st.selectbox("Código del material", sorted(stock["Código"]))
        actual = obtener_stock(codigo)
        st.metric("Stock actual", int(actual["Cantidad"]))
        with st.form("ajustar_stock"):
            cantidad = st.number_input(
                "Nueva cantidad final",
                min_value=0,
                value=int(actual["Cantidad"]),
                step=1,
            )
            enviar = st.form_submit_button(
                "Guardar ajuste", type="primary", use_container_width=True
            )
        if enviar:
            finalizar(actualizar_stock(codigo, int(cantidad)))

elif accion == "Dejar en cero":
    st.subheader("🗑️ Dejar stock en cero", divider="rainbow")
    stock = cargar_stock()
    if stock.empty:
        st.info("Todavía no existe stock.")
    else:
        codigo = st.selectbox("Código del material", sorted(stock["Código"]))
        confirmar = st.checkbox(
            "Confirmo que deseo ajustar este material a cero unidades"
        )
        if st.button(
            "Dejar en cero", type="primary", use_container_width=True
        ):
            if confirmar:
                finalizar(eliminar_stock(codigo))
            else:
                st.warning("Marcá la confirmación antes de continuar.")

elif accion == "Listar":
    st.subheader("📰 Stock disponible", divider="rainbow")
    stock = cargar_stock()
    if stock.empty:
        st.info("Todavía no existe stock cargado.")
    else:
        col1, col2, col3 = st.columns(3)
        categoria = col1.selectbox(
            "Categoría",
            ["Todas"] + sorted(stock["Categoría"].dropna().unique()),
        )
        color = col2.selectbox(
            "Color", ["Todos"] + sorted(stock["Color"].dropna().unique())
        )
        codigo = col3.text_input("Buscar código")
        filtrado = stock.copy()
        if categoria != "Todas":
            filtrado = filtrado[filtrado["Categoría"] == categoria]
        if color != "Todos":
            filtrado = filtrado[filtrado["Color"] == color]
        if codigo:
            filtrado = filtrado[
                filtrado["Código"].str.contains(codigo.strip(), case=False)
            ]
        st.dataframe(filtrado, use_container_width=True)
        st.caption(f"{len(filtrado)} materiales con stock.")

elif accion == "Carga Excel":
    st.subheader("📥 Carga masiva de stock final", divider="rainbow")
    st.info(
        "La cantidad informada en el Excel reemplaza el stock existente; "
        "no se suma. Utilizá el recuento físico final."
    )
    ruta = os.path.abspath(os.path.join(
        os.path.dirname(__file__), "..", "ui", "static",
        "Template Stock - Udibaby.xlsx",
    ))
    plantilla = pd.read_excel(ruta)
    salida = io.BytesIO()
    with pd.ExcelWriter(salida, engine="xlsxwriter") as writer:
        plantilla.to_excel(writer, index=False, sheet_name="Stock")
    st.download_button(
        "Descargar plantilla",
        salida.getvalue(),
        file_name="Template Stock - Hito.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        use_container_width=True,
    )
    archivo = st.file_uploader("Subí el Excel de stock", type=["xlsx"])
    if archivo:
        df = pd.read_excel(archivo)
        st.dataframe(df, use_container_width=True)
        if st.button(
            "Cargar stock final", type="primary", use_container_width=True
        ):
            for resultado in cargar_stock_bulk(df):
                finalizar(resultado)
