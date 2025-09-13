import streamlit as st
from datetime import datetime
import pandas as pd
import json

st.title('Hello')

with st.sidebar:
    st.title('Hola Mundo')
    st.button('Apretame', icon=':material/arrow_drop_down:', use_container_width=True, )
    add_radio = st.radio('Choose an option', ['1-5 Days',2,3], captions=['Primero', 'Segundo', 'Tercero'], label_visibility='visible')

    upload_file = st.file_uploader('Please upload your file')

    if upload_file is not None:
        content = upload_file.read().decode('utf-8')
        st.write('File Content:', content, height=200)

time = st.date_input('Select a date pls', value=datetime.today(), format='DD/MM/YYYY')
if time:
    st.write(time.strftime('%d/%m/%Y'))
else:
    st.write('pick a time pls')

st.divider()
st.subheader('DataFrames')

data= {
    'Name':['Juan', 'Male', 'Diego'],
    'Age':[24, 25, 43],
    'Hobbie':['Cantar', 'Bailar', 'Ser Feliz'],
}

df = pd.DataFrame(data)

st.write('Static Table')
st.table(df,)

st.write('Interactive Table')
st.data_editor(df)

st.write('Dataframe')
st.dataframe(df)

st.divider()
st.subheader('JSON')
person = {'name':'Alice',
          'age':24,
          'skills':['Python', 'StreamLit', 'DataScience']}

juan = st.json(person)

st.download_button('clickme', data='Tricks', type='primary', use_container_width=True)

st.divider()
st.subheader('Editable Tables')

editable_table = st.data_editor(df, hide_index=True, num_rows='dynamic')
tabla_editada = editable_table
st.write(tabla_editada)

st.divider()
st.subheader('Containers')

with st.container():
    st.write('This is inside a container')
    st.write('This is also inside a Container 2')

col1, col2 = st.columns(2)

with col1:
    st.write('Im on Column 1!')
    input = st.text_input('Colocar tu Nombre Aca', placeholder='Ej, Marta')
    
    if input:
        st.write(f'Tu nombre es {input}!')

def ball():
    st.balloons()
    st.warning('Advertencia')

with col2:
    st.write('Im on Column 2!')
    boton_sorpresa = st.download_button(type='primary', label='Boton Sorpresa', data='SORPRESA!', on_click=ball)

with st.expander('More Info :question:'):
    st.write('Hidden Content Reveal when expanded')
    st.bar_chart({"data": [1, 5, 2, 6, 2, 1]})

st.warning('Hola')
st.error('Hola')
st.success('Hola')

st.divider()

st.slider('Age', 1, 10, 5, 1)

st.divider()

options = st.sidebar.selectbox('Select Page:', ['HOME', 'Settings', 'About'])
st.sidebar.write(f'Sidebar Content Here: {options}')

st.write(f'ACTUAL PAGE {options}')

st.divider()
st.caption('This is a small caption text')

from PIL import Image
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

st.subheader('Images', divider='rainbow')
st.image('primera.png', caption='Confirmacion de Derivacion de Aportes', width=150)

st.video('https://www.youtube.com/watch?v=eAgONwZ_dKM&t=5907s', start_time=3600)

st.divider()
st.subheader('Session State Demo')

if "counter" not in st.session_state:
    st.session_state.counter = 0

if st.button('Increment'):
    st.session_state.counter += 1

st.write(f'Counter Value:', st.session_state.counter)

#############

#Si no coloco ningun nombre, por defecto el nombre en la sesion va a ser Guest
if 'name' not in st.session_state:
    st.session_state.name = 'Guest'

name_input = st.text_input('Place your name', placeholder='EJ Juan Mera')

# Si entro un nombre en el text input que sea diferente a Guest, se cambiara el nombre de Guest por el ingresado dentro de la sesion
if name_input != st.session_state.name:
    st.session_state.name = name_input

st.write(f'Hello {st.session_state.name}')

st.divider()
st.header('Logging')

if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False

if not st.session_state.logged_in:
    if st.button('Login'):
        st.session_state.logged_in = True
        st.success(f'You are Now Logged In!')

else:
    st.write('Welcome Back')
    if st.button('Logout'):
        st.session_state.logged_in = False

st.divider()
st.subheader('Data')

uploded_file = st.file_uploader('Upload a CSV, Excel, or JSON', type=['csv', 'xlsx', 'json'])

if uploded_file:

    if uploded_file.name.endswith('csv'):
        df = pd.read_csv(uploded_file)
        st.write("CSV Preview")
        st.dataframe(df.head())

    elif uploded_file.name.endswith('xlsx'):
        df = pd.read_excel(uploded_file)
        st.write("Excel Preview")
        st.dataframe(df.head())

    elif uploded_file.name.endswith('json'):
        data = json.load(uploded_file)
        st.write("Json Preview")
        st.json(data)

if uploded_file:
    file_size = uploded_file.size / 1024
    st.write(f'File name {uploded_file.name}, Size: {file_size:.2f} KB')
    if file_size > 500:
        st.warning('File is large preview may be limeted')