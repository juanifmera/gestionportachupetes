from sqlalchemy import create_engine
import streamlit as st

#DB_PATH = os.path.join(os.path.dirname(__file__), 'stock.db')
engine = create_engine("postgresql://juanifmera:8SJD1tajd64ZkOKmFns55LDsQ0eycJ6e@dpg-d36vj3ggjchc73br6he0-a.oregon-postgres.render.com/udibaby")