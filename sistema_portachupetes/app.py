import streamlit as st
from PIL import Image
from datetime import datetime, timedelta, date
from PIL import Image
from crud.materiales import agregar_material, eliminar_material, listar_todos_materiales, obtener_material
from crud.stock import agregar_stock, eliminar_stock, actualizar_stock, listar_stock, obtener_stock
from logic.verificador import verificar_confeccion_portachupetes
from crud.pedidos import crear_pedido, obtener_materiales_utilizados, cancelar_pedido, modificar_pedido, terminar_pedido, listar_todos_pedidos, listar_materiales_pedido, listar_pedidos_por_estado, obtener_pedido
import pandas as pd

st.set_page_config(layout='wide', page_title='Udibaby Gestion', page_icon=':baby_bottle:')

nav = st.sidebar.title('Menu de Navegacion')
eleccion = st.sidebar.radio(' Seleccionar Pagina:',['Home', 'Materiales', 'Stock', 'Pedidos', 'Metricas'])

### HOME ###
if eleccion == 'Home':

    st.title('Udibaby Sistema de Gestion 👶')
    st.divider()
    st.subheader('Bienvenido al Sistema de Control de Gestion. En este sistema vas a poder:')
    st.markdown(
        '''
        - Agregar, Eliminar, Listar y Modificar **MATERIALES**
        - Agregar, Incrementar, Disminuir, Actualizar y Listar todo el **STOCK**
        - Verificar la confeccion de **PEDIDOS**
        - Generar **PEDIDOS** y descontar Stock automaticamente
        - Y MUCHO MAS!
        '''
    )
    st.divider()

    st.caption('Para comenzar a utilziar el sistema porfavor dirigirse a la barra de menu a la izquiera y comenzar a navegar por el sistema.')

    col1, col2, col3 = st.columns(3)

    img1 = Image.open('ui/static/juan.png').resize((300,380))
    img2 = Image.open('ui/static/icon.png').resize((300,380))
    img3 = Image.open('ui/static/luli.png').resize((300,380))

    with col1:
        st.image(img1, width='stretch', caption='Juan Mera / Co-Founder')

    with col2:
        st.image(img2, caption='Udibaby Logo', width='stretch')

    with col3:
        st.image(img3, width='stretch', caption='Lucia Mera / Founder')

### MATERIALES ###
elif eleccion == 'Materiales':
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
                        st.balloons()
                        st.success(resultado)

    ## ELIMINAR MATERIAL ##
    with tabs_materiales[1]:

        st.subheader('🗑️ Eliminar Material', divider='rainbow')
        st.write('Revisá los materiales disponibles y seleccioná uno para eliminar.')

        col1, col2, col3, col4 = st.columns(4)

        df_original = listar_todos_materiales()

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
                    st.success(resultado)
                    st.balloons()
            else:
                submit = st.form_submit_button("Eliminar Material", type="primary", width='stretch', icon="💣")
                st.warning("❌ No hay materiales disponibles con los filtros seleccionados.")
                
    ## ACTUALIZAR MATERIAL ##
    with tabs_materiales[2]:
        st.subheader('✏️ Actualizar Material', divider='rainbow')
        st.write('Seleccioná un material y modificá los campos que desees.')

        df = listar_todos_materiales()

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
                    from crud.materiales import actualizar_varios_campos
                    resultado = actualizar_varios_campos(codigo_seleccionado, cambios) # type: ignore
                    st.balloons()
                    st.success(resultado)

    ## LISTAR MATERIAL ##
    with tabs_materiales[3]:
        st.subheader('📰 Listar Material', divider='rainbow')
        st.write('Revisá los materiales disponibles.')

        col1, col2, col3, col4 = st.columns(4)

        df_original = listar_todos_materiales()

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

### STOCK ###
elif eleccion == 'Stock':
    st.title('Stock :memo:')
    st.divider()

    tabs_stock = st.tabs(['Agregar Stock :smile:', 'Eliminar Stock :angry:', 'Actualizar Stock :zipper_mouth_face:', 'Listar Stock :alien:', 'Proximamente ... :dizzy_face:'])

    ## AGREGAR STOCK ##
    with tabs_stock[0]:
        st.subheader('➕ Agregar Stock', divider='rainbow')
        st.write('Para agregar Stock de un material deberas completar el forms que se encuentra debajo. En caso de que ya exista el stock del material, este sera incrementado:')

        df_stock = listar_stock()
        df_materiales = listar_todos_materiales()
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

                elif result.startswith('⚠️'): #type:ignore
                    st.warning(result)

                else:
                    st.error(result)

    ## ELIMINAR STOCK ##
    with tabs_stock[1]:
        st.subheader('🗑️ Eliminar Stock', divider='rainbow')
        st.write('Revisá el Stock disponibles y seleccioná uno para eliminar.')

        col1, col2, col3, col4 = st.columns(4)

        df_original = listar_stock()

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
            else:
                submit = st.form_submit_button("Eliminar Material", type="primary", width='stretch', icon="💣")
                st.warning("❌ No hay materiales disponibles con los filtros seleccionados.")

    ## ACTUALIZAR STOCK ##
    with tabs_stock[2]:
        st.subheader('✏️ Actualizar Stock', divider='rainbow')
        st.write('Seleccioná un stock y modificá los campos que desees.')

        df = listar_stock()

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
                
                elif result.startswith('⚠️'): #type:ignore
                    st.warning(result)

                else:
                    st.error(result)

    ## LISTAR STOCK ##
    with tabs_stock[3]:
        st.subheader('📰 Listar Stock', divider='rainbow')
        st.write('Revisá el Stock disponible.')

        col1, col2, col3, col4 = st.columns(4)

        df_original = listar_stock()

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

### PEDIDOS ###
elif eleccion == 'Pedidos':
    st.title('Pedidos :money_with_wings:')
    st.divider()

    tabs_pedido = st.tabs(['Generar Pedido :smile:', 'Cancelar pedido :angry:', 'Actualizar pedido :zipper_mouth_face:', 'Listar pedidos :alien:', 'Proximamente ... :dizzy_face:'])
    
    ## GENERAR PEDIDO ##
    with tabs_pedido[0]:

        st.subheader("🧾 Generar un Nuevo Pedido", divider="rainbow")

        # ---------- Paso 1: Configuración dinámica ----------
        st.markdown("### 🔧 Paso 1: Configuración de materiales")
        col1, col2 = st.columns(2)
        with col1:
            cantidad_bolitas = st.number_input("¿Cuántas bolitas distintas vas a usar?", min_value=0, max_value=10, step=1, key="cantidad_bolitas")
        with col2:
            cantidad_lentejas = st.number_input("¿Cuántas lentejas distintas vas a usar?", min_value=0, max_value=10, step=1, key="cantidad_lentejas")

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

            stock_df = listar_stock()

            # --- Broche (obligatorio) ---
            broches = stock_df[stock_df["Categoría"] == "Broche"]["Código"].tolist() #type:ignore
            broche = st.selectbox("📌 Seleccionar Broche *", broches)

            # --- Dijes ---
            dijes_normales = stock_df[stock_df["Categoría"] == "Dije"]["Código"].tolist()#type:ignore
            dije_normal = st.selectbox("✨ Dije Normal (opcional)", [""] + dijes_normales)

            dijes_especiales = stock_df[stock_df["Categoría"] == "Dije Especial"]["Código"].tolist()#type:ignore
            dije_especial = st.selectbox("💎 Dije Especial (opcional)", [""] + dijes_especiales)

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
                    "dije_normal": dije_normal if dije_normal else None,
                    "dije_especial": dije_especial if dije_especial else None,
                    "bolitas": bolitas_seleccionadas,
                    "lentejas": lentejas_seleccionadas,
                }

                resultado = crear_pedido(cliente, datos_portachupetes, telefono=telefono, fecha_pedido=fecha)#type:ignore

                if "éxito" in resultado.lower():
                    st.success(resultado)
                    st.balloons()
                else:
                    st.error(resultado)

    ## CANCELAR PEDIDO ##
    with tabs_pedido[1]:
        st.subheader('🗑️ Cancelar Pedido', divider='rainbow')
        st.write('Revisá los pedidos en proceso y seleccioná uno para cancelarlo.')

        col1, col2, col3, col4 = st.columns(4)

        df_pedidos = listar_todos_pedidos()
        df_pedidos_filtrado = df_pedidos[df_pedidos['Estado'] == 'En proceso'] #type:ignore

        st.dataframe(df_pedidos_filtrado, width='stretch')

        with st.form('form_cancelar_pedido', border=False):
            if not df_pedidos.empty: #type:ignore
                pedido_a_cancelar = st.selectbox('Seleccionar el pedido a cancelar', sorted(df_pedidos_filtrado['ID'].unique())) #type:ignore

                confirmar = st.checkbox('⚠️ Confirmo que deseo cancelar este pedido. Cancelar el pedido hara que los materiales sean reingresados al Stock', value=False)
                submit = st.form_submit_button("Cancelar Pedido", type="primary", width='stretch', icon="💣")

                if submit:
                    if not confirmar:
                        st.warning("⚠️ Debes confirmar la eliminación marcando la casilla.")
                        st.stop()

                    resultado = cancelar_pedido(int(pedido_a_cancelar)) #type:ignore
                    st.success(resultado)
                    st.balloons()
                
    ## ACTUALIZAR PEDIDO ##
    with tabs_pedido[2]:
        st.subheader('✏️ Actualizar Pedido', divider='rainbow')
        st.write('Seleccioná un pedido activo y modificá los campos que desees.')

        df_pedidos = listar_todos_pedidos()
        df_pedidos_activos = df_pedidos[~df_pedidos['Estado'].isin(['Cancelado', 'Terminado'])]  # type: ignore

        if df_pedidos_activos.empty:# type: ignore
            st.warning("❌ No hay pedidos activos para actualizar.")
            st.stop()

        id_pedido = st.selectbox("Seleccionar Pedido a Actualizar (ID)", sorted(df_pedidos_activos['ID'].unique()))# type: ignore
        datos_pedido = obtener_pedido(int(id_pedido))  # type: ignore

        with st.form("form_actualizar_pedido", border=True):

            nuevo_cliente = st.text_input("Nombre del Cliente", value=datos_pedido['Cliente'])  # type: ignore
            nuevo_telefono = st.text_input("Teléfono", value=datos_pedido['Teléfono'])  # type: ignore
            nueva_fecha = st.date_input("Fecha del Pedido", value=datos_pedido['Fecha Pedido'], format='DD/MM/YYYY')  # type: ignore

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

                if not cambios:
                    st.info("No se detectaron cambios para actualizar.")
                    st.stop()

                errores = []
                for campo, valor in cambios.items():
                    resultado = modificar_pedido(int(id_pedido), campo, valor)  # type: ignore
                    if resultado.startswith("Pedido con ID"):
                        st.success(resultado)
                    else:
                        errores.append(resultado)

                if errores:
                    st.error("\n".join(errores))
                else:
                    st.balloons()

    ## LISTAR PEDIDOS ##
    with tabs_pedido[3]:
        st.subheader('📰 Listar Pedidos', divider='rainbow')
        st.write('Revisá los Pedidos confeccionados.')

        col1, col2, col3 = st.columns(3)

        df_original = listar_todos_pedidos()

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
            st.dataframe(df_filtrado, width='stretch')
            st.info(f'Se encontraron {df_filtrado.shape[0]} registros para su búsqueda')

    ## PROXIMAS FEATURES ##    
    with tabs_pedido[4]:
        st.info(':warning: Mas Acciones seran Incorporadas en breve!!! (Llevar Ideas a Juan Mera)')
        
### METRICAS ###
elif eleccion == 'Metricas':
    st.title('Metricas')
    st.divider()

else:
    st.warning('No seleccionaste ninguna opcion del Menu de Navegacion')