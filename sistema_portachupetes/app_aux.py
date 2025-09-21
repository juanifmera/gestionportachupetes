import streamlit as st
import pandas as pd
import io
from crud.materiales import agregar_material
from sqlalchemy.orm import Session
from sqlalchemy import create_engine
from database.models import Material
from database.engine import engine

st.subheader('🕵 Bulk Request', divider='rainbow')
st.write('Realiza una carga masiva de Materiales en una sola acción.')

st.markdown("### Primer paso: Descargar y Completar el Template")
df_template = pd.read_excel("ui/static/Template Materiales - Udibaby.xlsx")

def convert_to_download(df):
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        df.to_excel(writer, index=False, sheet_name='Materiales')
    return output.getvalue()

st.download_button(
    label='📥 Descargar Template para cargar materiales',
    data=convert_to_download(df_template),
    file_name='Template Materiales - Udibaby.xlsx',
    mime='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
    type='primary',
    use_container_width=True
)

st.divider()

st.markdown("### Segundo paso: Cargar el template y validar la información")
st.markdown("Colocá el Template aquí 👇")
file = st.file_uploader("📤 Subí tu archivo Excel", type=["xlsx"])

if file:
    try:
        df = pd.read_excel(file)
        st.success("✅ Archivo cargado correctamente")
        st.dataframe(df.head())
    except Exception as e:
        st.error(f"❌ Error al leer el archivo: {e}")

st.divider()

st.markdown("### Tercer paso: Intenta realizar el Bulk Request para Materiales")
st.markdown("En caso de que hayas colocado bien toda la informacion en el template, los materiales deberian cargarse a la base de datos. En caso de ser incorrecto, deberas revisar que todos los campos del template esten completos. RECORDA no modificar la estructura del archivo.")

submit = st.button('Subir Bulk Request!!!', type='primary', width='stretch')

def bulk_upload_materiales(df):
    try:

        df = pd.read_excel(file)

        for index, material in df.iterrows():

            resultado = agregar_material(codigo_material=material['codigo material'], descripcion=material['descripcion'], color=material['color'], categoria=material['categoria'], subcategoria=material['subcategoria'], fecha_ingreso=material['fecha ingreso'],comentarios=material['comentarios'])

            if resultado.startswith('✅'):
                st.success(resultado)

            elif resultado.startswith('⚠️'):
                st.warning(resultado)

            else:
                st.error(resultado)

        return "✔️ Carga masiva finalizada correctamente."

    except Exception as e:
        return f'Error a la hora de cargar un Bulk Request'

if submit:
    result = bulk_upload_materiales(df)
    st.success(result)

