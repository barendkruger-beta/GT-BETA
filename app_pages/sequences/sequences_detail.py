import streamlit as st
import sql

campaign = st.session_state.campaign
series = st.session_state.series
event = st.session_state.event
sequence_group = st.session_state.sequence_group
sequence = st.session_state.sequence
tests = sql.tests()
data = tests.read(filter=f'WHERE sequence_id = {sequence[0]}')

@st.dialog("Add")
def add():
    name = st.text_input("Name")
    description = st.text_input("Description")
    if st.button("Submit"):
        tests.add(name=name, description=description, sequence_id=sequence[0])
        st.rerun()
            
def open(entry):
    st.session_state.test = entry
    st.rerun()
    
st.subheader("Tests")
st.badge(f"{campaign[1]} {series[1]} {event[1]} {sequence_group[1]} {sequence[1]}")
if st.button("Add"): add()

for entry in data:
    col1, col2, col3 = st.columns([1,1,1])
    col1.text(entry[1])
    col2.text(entry[2])
    btnkey = str(entry[0])+entry[1]+entry[2]
    #if col3.button('open', key=btnkey):
    #    open(entry=entry)