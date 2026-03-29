import streamlit as st
import sql

st.subheader("Scoring Cards")

conn = sql.connect()
data = sql.scoring_cards()
st.data_editor(data.read())