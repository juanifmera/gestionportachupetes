import streamlit as st
from datetime import datetime, timedelta
from crud.pedidos import crear_pedido, listar_todos_pedidos, actualizar_varios_campos_pedido, cancelar_pedido, obtener_pedido, terminar_pedido, listar_materiales_pedido, calcular_costo_total_pedido
from crud.stock import listar_stock
from crud.materiales import listar_todos_materiales
import pandas as pd
from ui.utils.utils import mostrar_exito_y_reiniciar, proteger_pagina

#Cacheo la lista de Stock
@st.cache_data
def cargar_stock():
    return listar_stock()

#Cacheo la lista de pedidos
@st.cache_data
def cargar_pedidos():
    return listar_todos_pedidos()

@st.cache_data
def cargar_materiales():
    return listar_todos_materiales()

proteger_pagina()

st.title('Pedidos :money_with_wings:')
st.divider()

tabs_pedido = st.tabs(['Generar Pedido :smile:', 'Cancelar pedido :angry:', 'Terminar pedido ✅', 'Actualizar pedido :zipper_mouth_face:', 'Listar pedidos :alien:', 'Ver Materiales por Pedido :monocle:','Proximamente ... :dizzy_face:'])

## GENERAR PEDIDO ##
with tabs_pedido[0]:

    st.subheader("🧾 Generar un Nuevo Pedido", divider="rainbow")

    # ---------- Paso 1: Configuración dinámica ----------
    st.markdown("### 🔧 Paso 1: Configuración de materiales")
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        cantidad_bolitas = st.number_input("🔵 ¿Cuántas bolitas distintas vas a usar?", min_value=0, max_value=10, step=1, key="cantidad_bolitas")
    with col2:
        cantidad_lentejas = st.number_input("🟤 ¿Cuántas lentejas distintas vas a usar?", min_value=0, max_value=10, step=1, key="cantidad_lentejas")
    with col3:
        cantidad_dijes_normales = st.number_input("✨ ¿Cuántos dijes normales vas a usar?", min_value=0, max_value=5, step=1, key="cantidad_dijes_normales")
    with col4:
        cantidad_dijes_especiales = st.number_input("💎 ¿Cuántos dijes especiales vas a usar?", min_value=0, max_value=5, step=1, key="cantidad_dijes_especiales")


    # ---------- Paso 2: Formulario principal ----------
    with st.form("generar_pedido_form", clear_on_submit=False, border=True):

        st.markdown("### 📋 Paso 2: Detalles del pedido")

        col1, col2 = st.columns(2)
        with col1:
            cliente = st.text_input("🧑 Nombre del cliente *", placeholder="Ej: Maria González")
            telefono = st.text_input("📞 Teléfono", placeholder="Ej: 1122334455")

        with col2:
            nombre_bebe = st.text_input("👶 Nombre del bebé *", placeholder="Ej: JULIÁN")
            fecha = st.date_input("📅 Fecha del pedido", value=datetime.today(), format='DD/MM/YYYY')

        st.divider()

        stock_df = cargar_stock()

        # --- Broche (obligatorio) ---
        broches = stock_df[stock_df["Categoría"] == "Broche"]["Código"].tolist() #type:ignore
        broche = st.selectbox("📌 Seleccionar Broche *", broches)

        #--- Dijes Normales (dinámico) ---
        st.markdown("### ✨ Dijes Normales")
        dijes_normales_seleccionados = []
        dijes_normales = stock_df[stock_df["Categoría"] == "Dije"]["Código"].tolist()#type:ignore

        for i in range(cantidad_dijes_normales):
            codigo = st.selectbox(f"Dije Normal #{i + 1}", dijes_normales, key=f"dije_normal_{i}")
            dijes_normales_seleccionados.append({"codigo": codigo})

        # --- Dijes Especiales (dinámico) ---
        st.markdown("### 💎 Dijes Especiales")
        dijes_especiales_seleccionados = []
        dijes_especiales = stock_df[stock_df["Categoría"] == "Dije Especial"]["Código"].tolist()#type:ignore

        for i in range(cantidad_dijes_especiales):
            codigo = st.selectbox(f"Dije Especial #{i + 1}", dijes_especiales, key=f"dije_especial_{i}")
            dijes_especiales_seleccionados.append({"codigo": codigo})

        # --- Bolitas (dinámico) ---
        st.markdown("### 🔵 Bolitas")
        bolitas_seleccionadas = []
        bolitas_disponibles = stock_df[stock_df["Categoría"] == "Bolita"]["Código"].tolist()#type:ignore

        for i in range(cantidad_bolitas):
            col1, col2 = st.columns([2, 1])
            with col1:
                codigo = st.selectbox(f"Bolita #{i + 1}", bolitas_disponibles, key=f"bolita_codigo_{i}")
            with col2:
                cantidad = st.number_input(f"Cantidad", min_value=1, step=1, key=f"bolita_cantidad_{i}")
            bolitas_seleccionadas.append({"codigo": codigo, "cantidad": cantidad})

        # --- Lentejas (dinámico) ---
        st.markdown("### 🟤 Lentejas")
        lentejas_seleccionadas = []
        lentejas_disponibles = stock_df[stock_df["Categoría"] == "Lenteja"]["Código"].tolist()#type:ignore

        for i in range(cantidad_lentejas):
            col1, col2 = st.columns([2, 1])
            with col1:
                codigo = st.selectbox(f"Lenteja #{i + 1}", lentejas_disponibles, key=f"lenteja_codigo_{i}")
            with col2:
                cantidad = st.number_input(f"Cantidad", min_value=1, step=1, key=f"lenteja_cantidad_{i}")
            lentejas_seleccionadas.append({"codigo": codigo, "cantidad": cantidad})

        st.divider()

        # ---------- Botón de envío ----------
        submit = st.form_submit_button("🧾 Generar Pedido", width='stretch', type='primary')

        if submit:
            if not cliente or not nombre_bebe or not broche:
                st.error("❌ Debés completar los campos obligatorios: Cliente, Nombre del Bebé y Broche.")
                st.stop()

            datos_portachupetes = {
                "broche": broche,
                "nombre": nombre_bebe.upper(),
                "dijes_normales": dijes_normales_seleccionados,
                "dijes_especiales": dijes_especiales_seleccionados,
                "bolitas": bolitas_seleccionadas,
                "lentejas": lentejas_seleccionadas,
            }

            resultado = crear_pedido(cliente, datos_portachupetes, telefono=telefono, fecha_pedido=fecha) #type:ignore

            if "éxito" in resultado.lower():
                mostrar_exito_y_reiniciar(resultado)
            else:
                st.error(resultado)

## CANCELAR PEDIDO ##
with tabs_pedido[1]:
    st.subheader('🗑️ Cancelar Pedido', divider='rainbow')
    st.write('Revisá los pedidos en proceso y seleccioná uno para cancelarlo.')

    col1, col2, col3, col4 = st.columns(4)

    df_pedidos = cargar_pedidos()
    df_pedidos_filtrado = df_pedidos[df_pedidos['Estado'] == 'En proceso'] #type:ignore

    st.dataframe(df_pedidos_filtrado, width='stretch')

    with st.form('form_cancelar_pedido', border=False):
        if not df_pedidos.empty: #type:ignore
            pedido_a_cancelar = st.selectbox('Seleccionar el pedido a cancelar', sorted(df_pedidos_filtrado['ID'].unique(), reverse=True)) #type:ignore

            confirmar = st.checkbox('⚠️ Confirmo que deseo cancelar este pedido. Cancelar el pedido hara que los materiales sean reingresados al Stock', value=False)
            submit = st.form_submit_button("Cancelar Pedido", type="primary", width='stretch', icon="💣")

            if submit:
                if not confirmar:
                    st.warning("⚠️ Debes confirmar la eliminación marcando la casilla.")
                    st.stop()

                resultado = cancelar_pedido(int(pedido_a_cancelar)) #type:ignore
                mostrar_exito_y_reiniciar(resultado)

## TERMINAR PEDIDO ##
with tabs_pedido[2]:
    st.subheader('📦 Terminar Pedido', divider='rainbow')
    st.write('Seleccioná un pedido en proceso para marcarlo como terminado.')

    df_pedidos = cargar_pedidos()
    df_pedidos_filtrado = df_pedidos[df_pedidos['Estado'] == 'En proceso']  #type:ignore

    st.dataframe(df_pedidos_filtrado, width='stretch')

    with st.form('form_terminar_pedido', border=False):
        if not df_pedidos_filtrado.empty:  # type: ignore
            pedido_a_terminar = st.selectbox(
                'Seleccionar el pedido a terminar',
                sorted(df_pedidos_filtrado['ID'].unique(), reverse=True) #type:ignore
            )

            confirmar = st.checkbox(
                '✅ Confirmo que deseo terminar este pedido. Esto marcará el pedido como "Terminado".',
                value=False
            )
            submit = st.form_submit_button("Terminar Pedido", type="primary", width='stretch', icon="📦")

            if submit:
                if not confirmar:
                    st.warning("⚠️ Debes confirmar marcando la casilla.")
                    st.stop()

                resultado = terminar_pedido(int(pedido_a_terminar))  # type: ignore
                mostrar_exito_y_reiniciar(resultado)
            
## ACTUALIZAR PEDIDO ##
with tabs_pedido[3]:
    st.subheader('✏️ Actualizar Pedido', divider='rainbow')
    st.write('Seleccioná un pedido activo y modificá los campos que desees.')

    df_pedidos = cargar_pedidos()
    df_pedidos_activos = df_pedidos[~df_pedidos['Estado'].isin(['Cancelado', 'Terminado'])]  # type: ignore

    if df_pedidos_activos.empty:# type: ignore
        st.warning("❌ No hay pedidos activos para actualizar.")
        st.stop()

    id_pedido = st.selectbox("Seleccionar Pedido a Actualizar (ID)", sorted(df_pedidos_activos['ID'].unique(), reverse=True))# type: ignore
    datos_pedido = obtener_pedido(int(id_pedido))  # type: ignore

    with st.form("form_actualizar_pedido", border=True):

        nuevo_cliente = st.text_input("Nombre del Cliente", value=datos_pedido['Cliente'])  # type: ignore
        nuevo_telefono = st.text_input("Teléfono", value=datos_pedido['Teléfono'])  # type: ignore
        nueva_fecha = st.date_input("Fecha del Pedido", value=datos_pedido['Fecha Pedido'], format='DD/MM/YYYY')  # type: ignore
        nuevo_costo = st.number_input('Costo Total', value=datos_pedido['Costo Total'])# type: ignore

        st.caption("No se permite modificar el estado del pedido desde este formulario.")
        submit = st.form_submit_button(":dart: Actualizar Pedido", type="primary", width="stretch")

        if submit:
            cambios = {}

            if nuevo_cliente != datos_pedido['Cliente']:  # type: ignore
                cambios['cliente'] = nuevo_cliente
            if nuevo_telefono != datos_pedido['Teléfono']:  # type: ignore
                cambios['telefono'] = nuevo_telefono
            if nueva_fecha != datos_pedido['Fecha Pedido']:  # type: ignore
                cambios['fecha_pedido'] = nueva_fecha
            if nuevo_costo != datos_pedido['Costo Total']: # type: ignore
                cambios['costo_total'] = nuevo_costo

            if not cambios:
                st.info("No se detectaron cambios para actualizar.")
                st.stop()

            resultado = actualizar_varios_campos_pedido(int(id_pedido), cambios)  #type:ignore

            if resultado.startswith("✅"):
                mostrar_exito_y_reiniciar(resultado)
            else:
                st.error(resultado)

## LISTAR PEDIDOS ##
with tabs_pedido[4]:
    st.subheader('📰 Listar Pedidos', divider='rainbow')
    st.write('Revisá los Pedidos confeccionados.')

    col1, col2, col3 = st.columns(3)

    df_original = cargar_pedidos()

    with col1:
        filtro_estado = st.selectbox('Filtrar por Estado', key='filtro_estado_pedido', options=['Todas'] + sorted(df_original['Estado'].unique()), width='stretch')  # type: ignore

    with col2:
        buscar_codigo = st.text_input('Buscar por ID', key='filtro_cod_pedido', placeholder='EJ: 1', width='stretch')

    with col3:
        buscar_cliente = st.text_input('Buscar por Cliente', key='filtro_cliente_pedido', placeholder='EJ: Maria Luz', width='stretch')

    df_filtrado = df_original.copy()  # type: ignore

    # Asegurar que la columna es datetime.date
    df_filtrado['Fecha Creación'] = pd.to_datetime(df_filtrado['Fecha Creación']).dt.date

    # Aplicar filtros
    if filtro_estado != 'Todas':
        df_filtrado = df_filtrado[df_filtrado['Estado'] == filtro_estado]

    if buscar_codigo:
        df_filtrado = df_filtrado[df_filtrado['ID'] == int(buscar_codigo)]

    if buscar_cliente:
        df_filtrado = df_filtrado[df_filtrado['Cliente'].str.contains(buscar_cliente, case=False)]

    # Mostrar resultados
    if df_filtrado.empty:
        st.dataframe(df_filtrado, width='stretch')
        st.warning("❌ No hay Pedidos disponibles con los filtros seleccionados.")
    else:
        st.dataframe(df_filtrado[["ID", "Cliente", "Telefono", "Fecha Creación", "Estado", "Costo Total"]], width='stretch')
        st.info(f'Se encontraron {df_filtrado.shape[0]} registros para su búsqueda')

## VISUALIZAR MATERIALES POR PEDIDO ##
with tabs_pedido[5]:
    st.subheader("🔍 Detalle de un Pedido", divider="rainbow")
    st.write("Seleccioná un pedido *Terminado* o *En proceso* para ver los materiales utilizados en su confección.")

    # Obtener todos los pedidos
    df_pedidos = cargar_pedidos()

    # Filtrar solo los pedidos válidos
    if isinstance(df_pedidos, pd.DataFrame) and not df_pedidos.empty:
        df_filtrado = df_pedidos[df_pedidos["Estado"].isin(["En proceso", "Terminado"])]
        
        if not df_filtrado.empty:
            pedido_ids = sorted(df_filtrado["ID"].unique(), reverse=True)
            pedido_seleccionado = st.selectbox("Seleccioná el ID del Pedido", pedido_ids)

            # Mostrar información general del pedido
            datos = obtener_pedido(int(pedido_seleccionado)) #type:ignore
            if isinstance(datos, dict):
                st.markdown(f"""
                **👤 Cliente:** {datos['Cliente'].capitalize()}  
                **📞 Teléfono:** {datos['Teléfono'] if datos['Teléfono'] else ':red[Falta Dato]'}  
                **📅 Fecha del Pedido:** {datos['Fecha Pedido'].strftime('%d/%m/%Y')}  
                **📦 Estado:** {datos['Estado']}  
                **💵 Costo:** ${int(datos['Costo Total'])}
                """)

                st.divider()
                st.markdown("### 🧱 Materiales utilizados")

                # Obtener materiales
                with st.spinner(f'Cargando Materiales del Pedido {pedido_seleccionado}'):
                    df_materiales = listar_materiales_pedido(int(pedido_seleccionado)) #type:ignore

                # Enriquecer con categoría (si hay datos)
                if not df_materiales.empty : #type:ignore
                    # Traer info de materiales (para obtener categoría)
                    df_info = cargar_materiales()

                    # Hacemos merge con los materiales usados
                    df_final = pd.merge(df_materiales, df_info, on="Código", how="left") #type:ignore

                    # Ordenar columnas
                    df_final.rename(columns={'Costo Unitario_x':'Costo Unitario'}, inplace=True)
                    df_final['Costo Total'] = df_final['Cantidad'] * df_final['Costo Unitario']
                    df_final = df_final[["Código", "Categoría", 'Descripción', 'Color', "Cantidad", "Costo Unitario", 'Costo Total']]
                    st.dataframe(df_final, width='stretch')

                    st.info(f"Se utilizaron {df_final.shape[0]} materiales en este pedido. "
                            f"Costo total del Portachupetes: **${int(datos['Costo Total'])}**")

                    # 🔑 Validar letras extra
                    cantidad_letras = len(df_final[df_final['Categoría'] == 'Letra'])
                    if cantidad_letras > 5:
                        extras = cantidad_letras - 5
                        cargo_extra = extras * 500
                        st.warning(f'Este pedido contiene **{extras}** letra(s) adicionales. '
                                f'El cargo extra es de **${cargo_extra}**.')

                    st.success(f'Precio Estimado de Venta teniendo en cuenta un margen del 275%: '
                            f'**${int(datos["Costo Total"] * 2.75)}**')

                else:
                    st.warning("⚠️ No se encontraron materiales asociados a este pedido.")
            else:
                st.error(f"❌ Error al obtener detalles del pedido: {datos}")
        else:
            st.warning("❌ No hay pedidos en estado 'En proceso' o 'Terminado' para mostrar.")
    else:
        st.warning("❌ No hay pedidos registrados en el sistema.")

## PROXIMAS FEATURES ##    
with tabs_pedido[6]:
    st.info(':warning: Mas Acciones seran Incorporadas en breve!!! (Llevar Ideas a Juan Mera)')