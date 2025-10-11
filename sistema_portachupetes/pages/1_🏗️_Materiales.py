import streamlit as st
from crud.materiales import agregar_material, listar_todos_materiales, eliminar_material, actualizar_varios_campos, obtener_material
from datetime import datetime, timedelta
import pandas as pd
import io
from ui.utils.utils import mostrar_exito_y_reiniciar, proteger_pagina
import os
import time

#Genero una funcion para listar el material y quede cacheado para no perder tiempo cuando quiero mirar datos previamente cargados. Evito pegarle tanto a la base de datos
@st.cache_data
def cargar_materiales():
    return listar_todos_materiales()

proteger_pagina()

st.title('Materiales :crown:')
st.divider()

tabs_materiales = st.tabs(['Agregar Material :smile:', 'Eliminar Material :angry:', 'Actualizar Material :zipper_mouth_face:', 'Listar Materiales :alien:', 'Bulk Request :skull:','Proximamente ... :dizzy_face:'])

## AGREGAR MATERIAL ##
with tabs_materiales[0]:
    st.subheader('➕ Agregar Material', divider='rainbow')
    st.write('Para agregar un material deberas completar el forms que se encuentra debajo:')

    with st.form('agregar_material', True):

        col1, col2 = st.columns(2)

        with col1:
            codigo_material = st.text_input('Colocar el codigo del Material', placeholder='EJ: BBLA, LAZU, SBLA')

            color = st.text_input('Agregar el color del Material', placeholder='EJ: Rojo, Azul, Blanco')

            fecha_ingreso = st.date_input('Seleccion Fecha de Ingreso', value=datetime.today(), format='DD/MM/YYYY')

            comentarios = st.text_area('Colocar comentarios opcionales al Material')

        with col2:
            descripcion = st.text_input('Agregar breve descripcion del Material', placeholder='EJ: Broche de Oso de Silicona Blanco')

            categoria = st.selectbox('Agregar Categoria', ['Broche', 'Llavero', 'Identificador', 'Letra', 'Bolita', 'Lenteja', 'Dije', 'Dije Especial', 'Bolita Especial'])

            subcategoria = st.radio('Agregar una Subcategoria', ['Normal', 'Especial'], horizontal=True)

            costo_unitario = st.number_input('Agregar el costo Unitario Promedio del Material', min_value=1, value=500)


        submit = st.form_submit_button('Agregar Material', icon='🚨', type='primary', width='stretch')

        #Verifico que todos los campos hayan sido completados con exito
        if submit:
            if not codigo_material or not descripcion or not color or not categoria or not subcategoria or not fecha_ingreso:
                st.error("⚠️ Todos los campos son obligatorios, excepto los comentarios y el Costo Unitario Promedio.")
            else:
                resultado = agregar_material(
                    codigo_material=codigo_material,
                    descripcion=descripcion,
                    color=color,
                    categoria=categoria,
                    subcategoria=subcategoria,
                    comentarios=comentarios,
                    costo_unitario=costo_unitario,
                    fecha_ingreso=fecha_ingreso # type: ignore
                )

                #Si el resultado comienza con Cruz, significa que algo salio mal, por lo tanto, error
                if resultado.startswith("❌"):
                    st.error(resultado)

                elif resultado.startswith('⚠️'):
                    st.warning(resultado)
                #Caso contrario, successfull
                else:
                    mostrar_exito_y_reiniciar(resultado)
                    
## ELIMINAR MATERIAL ##
with tabs_materiales[1]:

    st.subheader('🗑️ Eliminar Material', divider='rainbow')
    st.write('Revisá los materiales disponibles y seleccioná uno para eliminar.')

    col1, col2, col3, col4 = st.columns(4)

    df_original = cargar_materiales()

    with col1:
        filtro_categoria = st.selectbox('Filtrar por Categoría', ['Todas'] + sorted(df_original['Categoría'].unique())) # type: ignore

    with col2:
        filtro_subcategoria = st.selectbox('Filtrar por Subcategoría', ['Todas'] + sorted(df_original['Subcategoría'].unique())) # type: ignore

    with col3:
        filtro_color = st.selectbox('Filtrar por Color', ['Todos'] + sorted(df_original['Color'].unique())) # type: ignore

    with col4:
        buscar_codigo = st.text_input('Buscar por código', placeholder='EJ: BAZU')

    df_filtrado = df_original.copy() # type: ignore

    if filtro_categoria != 'Todas':
        df_filtrado = df_filtrado[df_filtrado['Categoría'] == filtro_categoria]

    if filtro_subcategoria != 'Todas':
        df_filtrado = df_filtrado[df_filtrado['Subcategoría'] == filtro_subcategoria]

    if filtro_color != 'Todos':
        df_filtrado = df_filtrado[df_filtrado['Color'] == filtro_color]

    if buscar_codigo:
        df_filtrado = df_filtrado[df_filtrado['Código'].str.contains(buscar_codigo.upper(), case=False)]

    st.dataframe(df_filtrado, width='stretch')

    with st.form('form_eliminar_material', border=False):
        if not df_filtrado.empty:
            material_a_eliminar = st.selectbox('Seleccionar el material a eliminar', sorted(df_filtrado['Código'].unique()))

            confirmar = st.checkbox('⚠️ Confirmo que deseo eliminar este material permanentemente', value=False)
            submit = st.form_submit_button("Eliminar Material", type="primary", width='stretch', icon="💣")

            if submit:
                if not confirmar:
                    st.warning("⚠️ Debes confirmar la eliminación marcando la casilla.")
                    st.stop()

                resultado = eliminar_material(material_a_eliminar) #type:ignore
                mostrar_exito_y_reiniciar(resultado)
        else:
            submit = st.form_submit_button("Eliminar Material", type="primary", width='stretch', icon="💣")
            st.warning("❌ No hay materiales disponibles con los filtros seleccionados.")
            
## ACTUALIZAR MATERIAL ##
with tabs_materiales[2]:
    st.subheader('✏️ Actualizar Material', divider='rainbow')
    st.write('Seleccioná un material y modificá los campos que desees.')

    with st.spinner('Cargando Registros ...'):
        df = cargar_materiales()

    if df.empty: # type: ignore
        st.warning("❌ No hay materiales para editar.")
        st.stop()

    codigo_seleccionado = st.selectbox('Seleccionar material a editar', sorted(df['Código'].unique())) # type: ignore

    material = obtener_material(codigo_seleccionado) # type: ignore

    with st.form('form_actualizar_material', border=True):

        col1, col2 = st.columns(2)

        with col1:
            descripcion = st.text_input("Descripción", value=material["Descripción"]) # type: ignore
            color = st.text_input("Color", value=material["Color"])# type: ignore
            categoria = st.selectbox("Categoría", ["Broche", 'Llavero', 'Identificador', "Letra", "Bolita", "Lenteja", "Dije", "Dije Especial", "Bolita Especial"], index=["Broche", "Letra", "Bolita", "Lenteja", "Dije", "Dije Especial", "Bolita Especial"].index(material["Categoría"])) # type: ignore
        
        with col2:
            subcategoria = st.radio("Subcategoría", ["Normal", "Especial"], horizontal=True, index=["Normal", "Especial"].index(material["Subcategoría"]))# type: ignore
            comentarios = st.text_area("Comentarios", value=material["Comentarios"])# type: ignore
            costo_unitario = st.number_input('Costo Unitario', value=material['Costo Unitario'] or 0)# type: ignore

        submit = st.form_submit_button(":zap: Actualizar Material", type="primary", width='stretch')

        if submit:
            cambios = {}
            if descripcion != material["Descripción"]:# type: ignore
                cambios["descripcion"] = descripcion
            if color != material["Color"]:# type: ignore
                cambios["color"] = color
            if categoria != material["Categoría"]:# type: ignore
                cambios["categoria"] = categoria
            if subcategoria != material["Subcategoría"]:# type: ignore
                cambios["subcategoria"] = subcategoria
            if costo_unitario != material['Costo Unitario']:# type: ignore
                cambios['costo_unitario'] = costo_unitario
            if comentarios != material["Comentarios"]:# type: ignore
                cambios["comentarios"] = comentarios
            if not cambios:
                st.info("No se detectaron cambios. Nada que actualizar.")
            else:
                resultado = actualizar_varios_campos(codigo_seleccionado, cambios) # type: ignore
                mostrar_exito_y_reiniciar(resultado)

## LISTAR MATERIAL ##
with tabs_materiales[3]:
    st.subheader('📰 Listar Material', divider='rainbow')
    st.write('Revisá los materiales disponibles.')

    col1, col2, col3, col4 = st.columns(4)

    df_original = cargar_materiales()

    with col1:
        filtro_categoria = st.selectbox('Filtrar por Categoría', key='filtro_cat', options=['Todas'] + sorted(df_original['Categoría'].unique())) # type: ignore

    with col2:
        filtro_subcategoria = st.selectbox('Filtrar por Subcategoría', key='filtro_sub', options=['Todas'] + sorted(df_original['Subcategoría'].unique())) # type: ignore

    with col3:
        filtro_color = st.selectbox('Filtrar por Color', key='filtro_col', options=['Todos'] + sorted(df_original['Color'].unique())) # type: ignore

    with col4:
        buscar_codigo = st.text_input('Buscar por código', key='filtro_cod', placeholder='EJ: BAZU')

    df_filtrado = df_original.copy() # type: ignore

    if filtro_categoria != 'Todas':
        df_filtrado = df_filtrado[df_filtrado['Categoría'] == filtro_categoria]

    if filtro_subcategoria != 'Todas':
        df_filtrado = df_filtrado[df_filtrado['Subcategoría'] == filtro_subcategoria]

    if filtro_color != 'Todos':
        df_filtrado = df_filtrado[df_filtrado['Color'] == filtro_color]

    if buscar_codigo:
        df_filtrado = df_filtrado[df_filtrado['Código'].str.contains(buscar_codigo.upper(), case=False)]

    # Si el df esta vacio
    if df_filtrado.empty:
        st.dataframe(df_filtrado, width='stretch')
        st.warning("❌ No hay materiales disponibles con los filtros seleccionados.")
    
    # Si el df tiene valores
    if not df_filtrado.empty: # type: ignore
        st.dataframe(df_filtrado, width='stretch')
        st.info(f'Se encontraron {df_filtrado.shape[0]} registros para su busqueda')

## BULK REQUEST ##
with tabs_materiales[4]:
    st.subheader('🕵 Bulk Request', divider='rainbow')
    st.write('Realiza una carga masiva de Materiales en una sola acción.')

    st.markdown("### Primer paso: Descargar y Completar el Template")
    ruta_base = os.path.dirname(__file__)
    ruta_tempate_materiales = os.path.join(ruta_base,'..', "ui", "static", "Template Materiales - Udibaby.xlsx")
    df_template = pd.read_excel(ruta_tempate_materiales)

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
            st.dataframe(df)
        except Exception as e:
            st.error(f"❌ Error al leer el archivo: {e}")

    st.divider()

    st.markdown("### Tercer paso: Intenta realizar el Bulk Request para Materiales")
    st.markdown("En caso de que hayas colocado bien toda la informacion en el template, los materiales deberian cargarse a la base de datos. En caso de ser incorrecto, deberas revisar que todos los campos del template esten completos. RECORDA no modificar la estructura del archivo.")

    submit = st.button('Subir Bulk Request!!!', type='primary', width='stretch')

    # Funcion para cargar Varios Materiales #
    def bulk_upload_materiales(df):
        try:
            df = pd.read_excel(
                file,
                dtype={'codigo material': str},  # fuerza texto
                converters={'codigo material': lambda v: (str(int(v)) if isinstance(v, float) and v.is_integer() else str(v)).strip().upper()})
            
            for index, material in df.iterrows():
                resultado = agregar_material(codigo_material=material['codigo material'], descripcion=material['descripcion'], color=material['color'], categoria=material['categoria'], subcategoria=material['subcategoria'], fecha_ingreso=material['fecha ingreso'], comentarios=material['comentarios'], costo_unitario=material['costo unitario'])
                
                with st.spinner('Agregando Materiales a la Base de Datos ..'):
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
        with st.spinner('Porfavor verificar la carga de datos ..'):
            time.sleep(10)
        st.cache_data.clear()
        st.rerun()

## PROXIMAS FEATURES ##
with tabs_materiales[5]:
    st.info(':warning: Mas Acciones seran Incorporadas en breve!!! (Llevar Ideas a Juan Mera)')