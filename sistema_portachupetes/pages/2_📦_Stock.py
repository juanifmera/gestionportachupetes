import streamlit as st
from datetime import datetime, timedelta
from crud.stock import listar_stock, agregar_stock, eliminar_stock, actualizar_stock, obtener_stock
from crud.materiales import listar_todos_materiales
import pandas as pd

#Genero una funcion para listar el material y quede cacheado para no perder tiempo cuando quiero mirar datos previamente cargados. Evito pegarle tanto a la base de datos
@st.cache_data
def cargar_materiales():
    return listar_todos_materiales()

#Cacheo el listado de Stock
@st.cache_data
def cargar_stock():
    return listar_stock()

st.title('Stock :memo:')
st.divider()

tabs_stock = st.tabs(['Agregar Stock :smile:', 'Eliminar Stock :angry:', 'Actualizar Stock :zipper_mouth_face:', 'Listar Stock :alien:', 'Proximamente ... :dizzy_face:'])

## AGREGAR STOCK ##
with tabs_stock[0]:
    st.subheader('➕ Agregar Stock', divider='rainbow')
    st.write('Para agregar Stock de un material deberas completar el forms que se encuentra debajo. En caso de que ya exista el stock del material, este sera incrementado:')

    df_stock = cargar_stock()
    df_materiales = cargar_materiales()
    st.dataframe(df_stock)

    with st.form('agregar_stock', True):

        col1, col2, col3 = st.columns(3)

        with col1:
            codigo_material = st.selectbox('Colocar el Codigo del Material:' , sorted(df_materiales['Código'].unique())) # type: ignore

        with col2:
            cantidad = st.number_input('Colocar la Cantidad a Ingresar:', min_value=1, step=1)

        with col3:
            fecha_ingreso = st.date_input('Colocar la Fecha de Ingreso:', value=datetime.today(), format='DD/MM/YYYY')

        submit = st.form_submit_button('Agregar Stock', icon='🚨', type='primary', width='stretch')

        if submit:

            if not codigo_material or not cantidad:
                st.error('Debes colocar informacion en los Input para Agregar Material')
            
            result = agregar_stock(codigo_material, cantidad) #type:ignore

            if result.startswith('✅'): #type:ignore
                st.success(result)
                st.balloons()
                st.cache_data.clear()
                st.rerun()

            elif result.startswith('⚠️'): #type:ignore
                st.warning(result)

            else:
                st.error(result)

## ELIMINAR STOCK ##
with tabs_stock[1]:
    st.subheader('🗑️ Eliminar Stock', divider='rainbow')
    st.write('Revisá el Stock disponibles y seleccioná uno para eliminar.')

    col1, col2, col3, col4 = st.columns(4)

    df_original = cargar_stock()

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

            confirmar = st.checkbox('⚠️ Confirmo que deseo eliminar este Stock permanentemente', value=False)
            submit = st.form_submit_button("Eliminar Material", type="primary", width='stretch', icon="💣")

            if submit:
                if not confirmar:
                    st.warning("⚠️ Debes confirmar la eliminación marcando la casilla.")
                    st.stop()

                resultado = eliminar_stock(material_a_eliminar) #type:ignore
                st.success(resultado)
                st.balloons()
                st.cache_data.clear()
                st.rerun()

        else:
            submit = st.form_submit_button("Eliminar Material", type="primary", width='stretch', icon="💣")
            st.warning("❌ No hay materiales disponibles con los filtros seleccionados.")

## ACTUALIZAR STOCK ##
with tabs_stock[2]:
    st.subheader('✏️ Actualizar Stock', divider='rainbow')
    st.write('Seleccioná un stock y modificá los campos que desees.')

    df = cargar_stock()

    if df.empty: # type: ignore
        st.warning("❌ No hay materiales para editar.")
        st.stop()

    codigo_seleccionado = st.selectbox('Seleccionar material a editar', sorted(df['Código'].unique())) # type: ignore
    stock = obtener_stock(codigo_seleccionado) # type: ignore

    with st.form('form_actualizar_stock', border=True):

        nueva_cantidad = st.number_input('Colocar cantidad actualizada de Stock:', value=stock['Cantidad'], min_value=0) #type:ignore
        submit = st.form_submit_button('Actualizar Stock', icon='💎', type='primary', width='stretch')

        if submit:
            result = actualizar_stock(codigo_seleccionado, nueva_cantidad)#type:ignore
            
            if result.startswith('✅'):#type:ignore
                st.success(result)
                st.cache_data.clear()
                st.rerun()
            
            elif result.startswith('⚠️'): #type:ignore
                st.warning(result)

            else:
                st.error(result)

## LISTAR STOCK ##
with tabs_stock[3]:
    st.subheader('📰 Listar Stock', divider='rainbow')
    st.write('Revisá el Stock disponible.')

    col1, col2, col3, col4 = st.columns(4)

    df_original = cargar_stock()

    with col1:
        filtro_categoria = st.selectbox('Filtrar por Categoría', key='filtro_cat_stock', options=['Todas'] + sorted(df_original['Categoría'].unique())) # type: ignore

    with col2:
        filtro_subcategoria = st.selectbox('Filtrar por Subcategoría', key='filtro_sub_stock', options=['Todas'] + sorted(df_original['Subcategoría'].unique())) # type: ignore

    with col3:
        filtro_color = st.selectbox('Filtrar por Color', key='filtro_col_stock', options=['Todos'] + sorted(df_original['Color'].unique())) # type: ignore

    with col4:
        buscar_codigo = st.text_input('Buscar por código', key='filtro_cod_stock', placeholder='EJ: BAZU')

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
with tabs_stock[4]:
    st.info(':warning: Mas Acciones seran Incorporadas en breve!!! (Llevar Ideas a Juan Mera)')