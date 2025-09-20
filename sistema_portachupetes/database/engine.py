from sqlalchemy import create_engine
import streamlit as st

#DB_PATH = os.path.join(os.path.dirname(__file__), 'stock.db')
engine = create_engine(st.secrets["DATABASE_URL"])