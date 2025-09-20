import streamlit as st
import streamlit_authenticator as stauth
import yaml
from yaml.loader import SafeLoader
import base64

st.set_page_config(layout='wide', page_title='Udibaby Gestion', page_icon=':baby_bottle:')

config = dict(st.secrets)

authenticator = stauth.Authenticate(
    config['credentials'],
    config['cookie']['name'],
    config['cookie']['key'],
    config['cookie']['expiry_days']
)

# Mostrar login
authenticator.login(
    location="main",
    fields={
        "Form name": "🔐 Iniciar sesión",
        "Username": "Usuario",
        "Password": "Contraseña",
        "Login": "Ingresar"
    },
    key="login"
)

authentication_status = st.session_state.get("authentication_status")
name = st.session_state.get("name")
username = st.session_state.get("username")

# Control de acceso
if authentication_status:
    
    st.sidebar.title(f'Udiybaby - {username}')
    st.sidebar.success(f"Bienvenido, {name} 👋")
    st.sidebar.info("Navegá entre las páginas desde la barra lateral")
    authenticator.logout("Cerrar sesión", "sidebar")

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

    with open("ui/static/juan.png", "rb") as file:
        juan_image = file.read()

    with open("ui/static/icon.png", "rb") as file:
        icon_image = file.read()

    with open("ui/static/luli.png", "rb") as file:
        luli_image = file.read()
        
    juan_image = base64.b64encode(juan_image).decode()
    icon_image = base64.b64encode(icon_image).decode()
    luli_image = base64.b64encode(luli_image).decode()

    with col1:
        st.markdown(
            f"""
            <div style='text-align: center; margin-bottom: 20px;'>
                <img src="data:image/jpeg;base64,{juan_image}" 
                    style="width: 350px; height: 350px; object-fit: cover; border-radius: 50%; border: 3px solid #ddd;" 
                    alt="Foto de perfil" />
            </div>
            """, unsafe_allow_html=True
            )
        st.markdown(f"<p style='text-align: center;'>Juan Mera / Co-Founder</p>", unsafe_allow_html=True)

    with col2:
        st.markdown(
            f"""
            <div style='text-align: center; margin-bottom: 20px;'>
                <img src="data:image/jpeg;base64,{icon_image}" 
                    style="width: 350px; height: 350px; object-fit: cover; border-radius: 50%; border: 3px solid #ddd;" 
                    alt="Foto de perfil" />
            </div>
            """, unsafe_allow_html=True
            )
        st.markdown(f"<p style='text-align: center;'>Udibaby Logo</p>", unsafe_allow_html=True)

    with col3:
            st.markdown(
            f"""
            <div style='text-align: center; margin-bottom: 20px;'>
                <img src="data:image/jpeg;base64,{luli_image}" 
                    style="width: 350px; height: 350px; object-fit: cover; border-radius: 50%; border: 3px solid #ddd;" 
                    alt="Foto de perfil" />
            </div>
            """, unsafe_allow_html=True
            )
            st.markdown(f"<p style='text-align: center;'>Lucia Mera / Founder</p>", unsafe_allow_html=True)

    st.markdown(f"<p style='text-align: center;'>© Todos los derechos reservados | Juan Ignacio Francisco Mera</p>", unsafe_allow_html=True)

    st.stop()

elif authentication_status is False:
    st.error("❌ Usuario o contraseña incorrectos")

elif authentication_status is None:
    st.warning("👀 Por favor ingresá tus credenciales")