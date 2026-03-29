import streamlit as st
import sql

st.subheader("Competitions")

competitions = sql.competitions()

st.data_editor(competitions.read())