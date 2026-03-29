import streamlit as st
import sql

st.subheader("Overview")

conn = sql.connect()
data = sql.sequences()
st.data_editor(data.read())