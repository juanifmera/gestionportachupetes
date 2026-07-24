from datetime import datetime
import io
import os

import pandas as pd
import streamlit as st

from crud.materiales import (
    actualizar_varios_campos,
    agregar_material,
    cargar_materiales_bulk,
    eliminar_material,
    listar_todos_materiales,
    obtener_material,
)
from ui.utils.utils import proteger_pagina

CATEGORIAS = [
    "Broche", "Llavero", "Identificador", "Letra", "Bolita",
    "Lenteja", "Dije", "Bolsa", "Lapicera",
]


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


proteger_pagina()
st.title("Materiales 👑")
st.divider()

accion = st.radio(
    "Acción",
    ["Agregar", "Eliminar", "Actualizar", "Listar", "Carga Excel"],
    horizontal=True,
    label_visibility="collapsed",
)

if accion == "Agregar":
    st.subheader("➕ Agregar material", divider="rainbow")
    with st.form("agregar_material", clear_on_submit=True):
        col1, col2 = st.columns(2)
        with col1:
            codigo = st.text_input("Código del material", placeholder="Ej: BBLA12")
            color = st.text_input("Color", placeholder="Ej: Blanco")
            fecha = st.date_input(
                "Fecha de ingreso", value=datetime.today(), format="DD/MM/YYYY"
            )
            comentarios = st.text_area("Comentarios opcionales")
        with col2:
            descripcion = st.text_input(
                "Descripción", placeholder="Ej: Bolita blanca de 12 mm"
            )
            categoria = st.selectbox("Categoría", CATEGORIAS)
            subcategoria = st.radio(
                "Subcategoría", ["Normal", "Especial"], horizontal=True
            )
            costo = st.number_input(
                "Costo unitario promedio", min_value=0.0, value=500.0, step=10.0
            )
        enviar = st.form_submit_button(
            "Agregar material", type="primary", use_container_width=True
        )

    if enviar:
        if not all((codigo, descripcion, color, categoria, subcategoria, fecha)):
            st.error("⚠️ Completá todos los campos obligatorios.")
        else:
            finalizar(agregar_material(
                codigo, descripcion, color, categoria, subcategoria,
                costo, comentarios, fecha,
            ))

elif accion == "Eliminar":
    st.subheader("🗑️ Dar de baja un material", divider="rainbow")
    df = cargar_materiales()
    if df.empty:
        st.info("Todavía no hay materiales cargados.")
    else:
        st.dataframe(df, use_container_width=True)
        codigo = st.selectbox("Material", sorted(df["Código"].unique()))
        confirmar = st.checkbox("Confirmo la baja del material")
        if st.button("Dar de baja", type="primary", use_container_width=True):
            if confirmar:
                finalizar(eliminar_material(codigo))
            else:
                st.warning("Marcá la confirmación antes de continuar.")

elif accion == "Actualizar":
    st.subheader("✏️ Actualizar material", divider="rainbow")
    df = cargar_materiales()
    if df.empty:
        st.info("Todavía no hay materiales cargados.")
    else:
        codigo = st.selectbox("Material", sorted(df["Código"].unique()))
        material = obtener_material(codigo)
        categoria_actual = (
            material["Categoría"] if material["Categoría"] in CATEGORIAS else "Dije"
        )
        with st.form("actualizar_material"):
            descripcion = st.text_input("Descripción", material["Descripción"])
            color = st.text_input("Color", material["Color"])
            categoria = st.selectbox(
                "Categoría", CATEGORIAS, index=CATEGORIAS.index(categoria_actual)
            )
            subcategoria = st.radio(
                "Subcategoría",
                ["Normal", "Especial"],
                index=["Normal", "Especial"].index(material["Subcategoría"]),
                horizontal=True,
            )
            costo = st.number_input(
                "Costo unitario", min_value=0.0,
                value=float(material["Costo Unitario"] or 0),
            )
            comentarios = st.text_area(
                "Comentarios", value=material["Comentarios"] or ""
            )
            enviar = st.form_submit_button(
                "Guardar cambios", type="primary", use_container_width=True
            )
        if enviar:
            finalizar(actualizar_varios_campos(codigo, {
                "descripcion": descripcion,
                "color": color,
                "categoria": categoria,
                "subcategoria": subcategoria,
                "costo_unitario": costo,
                "comentarios": comentarios,
            }))

elif accion == "Listar":
    st.subheader("📰 Materiales disponibles", divider="rainbow")
    df = cargar_materiales()
    if df.empty:
        st.info("Todavía no hay materiales cargados.")
    else:
        col1, col2, col3 = st.columns(3)
        categoria = col1.selectbox(
            "Categoría", ["Todas"] + sorted(df["Categoría"].dropna().unique())
        )
        color = col2.selectbox(
            "Color", ["Todos"] + sorted(df["Color"].dropna().unique())
        )
        codigo = col3.text_input("Buscar código")
        filtrado = df.copy()
        if categoria != "Todas":
            filtrado = filtrado[filtrado["Categoría"] == categoria]
        if color != "Todos":
            filtrado = filtrado[filtrado["Color"] == color]
        if codigo:
            filtrado = filtrado[
                filtrado["Código"].str.contains(codigo.strip(), case=False)
            ]
        st.dataframe(filtrado, use_container_width=True)
        st.caption(f"{len(filtrado)} materiales encontrados.")

elif accion == "Carga Excel":
    st.subheader("📥 Carga masiva de materiales", divider="rainbow")
    ruta = os.path.abspath(os.path.join(
        os.path.dirname(__file__), "..", "ui", "static",
        "Template Materiales - Udibaby.xlsx",
    ))
    plantilla = pd.read_excel(ruta)
    salida = io.BytesIO()
    with pd.ExcelWriter(salida, engine="xlsxwriter") as writer:
        plantilla.to_excel(writer, index=False, sheet_name="Materiales")
    st.download_button(
        "Descargar plantilla", salida.getvalue(),
        file_name="Template Materiales - Hito.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        use_container_width=True,
    )
    archivo = st.file_uploader("Subí el Excel completo", type=["xlsx"])
    if archivo:
        df = pd.read_excel(archivo)
        st.dataframe(df, use_container_width=True)
        if st.button("Cargar materiales", type="primary", use_container_width=True):
            for resultado in cargar_materiales_bulk(df):
                finalizar(resultado)
