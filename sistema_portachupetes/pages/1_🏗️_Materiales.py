import streamlit as st
from crud.materiales import agregar_material, listar_todos_materiales, eliminar_material, actualizar_varios_campos, obtener_material
from datetime import datetime, timedelta
import pandas as pd
from ui.utils.utils import mostrar_exito_y_reiniciar, proteger_pagina

#Genero una funcion para listar el material y quede cacheado para no perder tiempo cuando quiero mirar datos previamente cargados. Evito pegarle tanto a la base de datos
@st.cache_data
def cargar_materiales():
    return listar_todos_materiales()

proteger_pagina()

st.title('Materiales :crown:')
st.divider()

tabs_materiales = st.tabs(['Agregar Material :smile:', 'Eliminar Material :angry:', 'Actualizar Material :zipper_mouth_face:', 'Listar Materiales :alien:', 'Proximamente ... :dizzy_face:'])

## AGREGAR MATERIAL ##
with tabs_materiales[0]:
    st.subheader('➕ Agregar Material', divider='rainbow')
    st.write('Para agregar un material deberas completar el forms que se encuentra debajo:')

    with st.form('agregar_material', True):

        col1, col2 = st.columns(2)

        with col1:
            codigo_material = st.text_input('Colocar el codigo del Material', placeholder='EJ: BBLA, LAZU, SBLA')

            color = st.text_input('Agregar el color del Material', placeholder='EJ: Rojo, Azul, Blanco')

            fecha_ingreso = st.date_input('Seleccion Fecha de Ingreso', value=datetime.now(), format='DD/MM/YYYY')

        with col2:
            descripcion = st.text_input('Agregar breve descripcion del Material', placeholder='EJ: Broche de Oso de Silicona Blanco')

            categoria = st.selectbox('Agregar Categoria', ['Broche', 'Letra', 'Bolita', 'Lenteja', 'Dije', 'Dije Especial', 'Bolita Especial'])

            subcategoria = st.radio('Agregar una Subcategoria', ['Normal', 'Especial'], horizontal=True)

        comentarios = st.text_area('Colocar comentarios opcionales al Material')

        submit = st.form_submit_button('Agregar Material', icon='🚨', type='primary', width='stretch')

        #Verifico que todos los campos hayan sifo completados con exito
        if submit:
            if not codigo_material or not descripcion or not color or not categoria or not subcategoria or not fecha_ingreso:
                st.error("⚠️ Todos los campos son obligatorios, excepto los comentarios.")
            else:
                resultado = agregar_material(
                    codigo_material,
                    descripcion,
                    color,
                    categoria,
                    subcategoria,
                    comentarios,
                    fecha_ingreso # type: ignore
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
            categoria = st.selectbox("Categoría", ["Broche", "Letra", "Bolita", "Lenteja", "Dije", "Dije Especial", "Bolita Especial"], index=["Broche", "Letra", "Bolita", "Lenteja", "Dije", "Dije Especial", "Bolita Especial"].index(material["Categoría"])) # type: ignore
        
        with col2:
            subcategoria = st.radio("Subcategoría", ["Normal", "Especial"], horizontal=True, index=["Normal", "Especial"].index(material["Subcategoría"]))# type: ignore
            comentarios = st.text_area("Comentarios", value=material["Comentarios"])# type: ignore

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

## PROXIMAS FEATURES ##
with tabs_materiales[4]:
    st.info(':warning: Mas Acciones seran Incorporadas en breve!!! (Llevar Ideas a Juan Mera)')