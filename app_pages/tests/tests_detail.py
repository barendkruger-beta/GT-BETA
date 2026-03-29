import streamlit as st
import sql

campaign = st.session_state.campaign
series = st.session_state.series
event = st.session_state.event
sequence_group = st.session_state.sequence_group
sequence = st.session_state.sequence
test = st.session_state.test
tests = sql.tests()
data = test

st.subheader("Test")

for entry in data:
    col1, col2, col3 = st.columns([1,1,1])
    col1.text(entry[1])
    col2.text(entry[2])
    btnkey = str(entry[0])+entry[1]+entry[2]
    #if col3.button('open', key=btnkey):
    #    open(entry=entry)