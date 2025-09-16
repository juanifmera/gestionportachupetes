import streamlit as st
from PIL import Image
from datetime import datetime
from crud.materiales import agregar_material, actualizar_material, eliminar_material, listar_todos_materiales,listo_con_filtro, validar_material
from crud.stock import agregar_stock, eliminar_stock, actualizar_stock, reducir_stock, listar_stock
from logic.verificador import verificar_confeccion_portachupetes
from crud.pedidos import crear_pedido, obtener_materiales_utilizados, cancelar_pedido, modificar_pedido, terminar_pedido, listar_todos_pedidos, listar_materiales_pedido, listar_pedidos_por_estado

st.set_page_config(layout='wide', page_title='Udibaby Gestion', page_icon=':baby_bottle:')

nav = st.sidebar.title('Menu de Navegacion')
eleccion = st.sidebar.radio(' Seleccionar Pagina:',['Home', 'Materiales', 'Stock', 'Pedidos', 'Metricas'])

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
        st.image(img1, use_container_width=True, caption='Juan Mera / Co-Founder')

    with col2:
        st.image(img2, caption='Udibaby Logo', use_container_width=True)

    with col3:
        st.image(img3, use_container_width=True, caption='Lucia Mera / Founder')

elif eleccion == 'Materiales':
    st.title('Materiales :crown:')
    st.divider()

    tabs_materiales = st.tabs(['Agregar Material :smile:', 'Eliminar Material :angry:', 'Actualizar Material :zipper_mouth_face:', 'Listar Materiales :alien:', 'Proximamente ...:dizzy_face:'])

    with tabs_materiales[0]:
        st.write('Para agregar un material deberas completar el forms que se encuentra debajo:')

        with st.form('agregar_material', True):

            st.subheader('Agregar un Material', divider='rainbow')

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

            submit = st.form_submit_button('Agregar Material', icon='🚨', type='secondary', use_container_width=True)

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
                        fecha_ingreso
                    )

                    #Si el resultado comienza con Cruz, significa que algo salio mal, por lo tanto, error
                    if resultado.startswith("❌"):
                        st.error(resultado)
                    #Caso contrario, successfull
                    else:
                        st.balloons()
                        st.success(resultado)

    with tabs_materiales[1]:
        st.write('chau')

    with tabs_materiales[2]:
        st.write(3)

    with tabs_materiales[3]:
        st.write(4)

    with tabs_materiales[4]:
        st.info(':warning: Mas Acciones seran Incorporadas en breve!!! (Llevar Ideas a Juan Mera)')

elif eleccion == 'Stock':
    st.title('Stock')
    st.divider()

elif eleccion == 'Pedidos':
    st.title('Pedidos')
    st.divider()

elif eleccion == 'Metricas':
    st.title('Metricas')
    st.divider()

else:
    st.warning('No seleccionaste ninguna opcion del Menu de Navegacion')