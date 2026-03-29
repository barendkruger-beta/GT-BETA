import streamlit as st
import sql

st.subheader("Overview")

conn = sql.connect()
data = sql.tests()
st.data_editor(data.read())