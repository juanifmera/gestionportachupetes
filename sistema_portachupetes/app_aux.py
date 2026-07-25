"""Pantalla auxiliar para probar la carga masiva de materiales."""

import io

import pandas as pd
import streamlit as st

from crud.materiales import cargar_materiales_bulk

st.subheader("🕵 Carga masiva de materiales", divider="rainbow")
archivo = st.file_uploader("📤 Subí tu archivo Excel", type=["xlsx"])

if archivo:
    df = pd.read_excel(archivo)
    st.dataframe(df, use_container_width=True)
    if st.button("Subir materiales", type="primary", use_container_width=True):
        for resultado in cargar_materiales_bulk(df):
            if resultado.startswith("✅"):
                st.success(resultado)
            elif resultado.startswith("⚠️"):
                st.warning(resultado)
            else:
                st.error(resultado)
