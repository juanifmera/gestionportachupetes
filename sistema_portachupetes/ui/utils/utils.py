import streamlit as st
import time

def mostrar_exito_y_reiniciar(mensaje: str, delay: float = 1.5):
    """
    Muestra un mensaje de éxito, lanza la animación de globos,
    espera un poco, limpia la caché y recarga la app.
    
    Args:
        mensaje (str): Mensaje a mostrar en el st.success()
        delay (float): Tiempo en segundos para esperar antes del rerun
    """
    st.success(mensaje)
    st.balloons()
    time.sleep(delay)
    st.cache_data.clear()
    st.rerun()

def proteger_pagina():
    if "authentication_status" not in st.session_state or st.session_state["authentication_status"] != True:
        st.warning("🔐 Debés iniciar sesión para acceder a esta página.")
        st.stop()
