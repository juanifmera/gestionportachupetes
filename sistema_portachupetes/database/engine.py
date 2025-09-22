from sqlalchemy import create_engine
import streamlit as st

engine = create_engine(st.secrets["DATABASE_URL"])
#engine = create_engine('postgresql://juanifmera:8SJD1tajd64ZkOKmFns55LDsQ0eycJ6e@dpg-d36vj3ggjchc73br6he0-a.oregon-postgres.render.com/udibaby')