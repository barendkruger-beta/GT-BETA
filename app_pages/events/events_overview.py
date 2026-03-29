import streamlit as st
import sql

st.subheader("Events")

conn = sql.connect()
data = sql.events()
st.data_editor(data.read())