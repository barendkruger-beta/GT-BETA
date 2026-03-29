import streamlit as st
import sql

sequence_templates = sql.sequence_templates()
data = sql.sequence_templates()

@st.dialog("Add")
def add():
    name = st.text_input("Name")
    description = st.text_input("Description")
    pars = [4,5,3,6,5,4,3,4,4, 4,4,5,3,5,3,4,4,4]
    strokes = [1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18]
    distances = [201,202,203,204,205,206,207,208,209,210,211,212,213,214,215,216,217,218]
    if st.button("Submit"):
        sequence_templates.add(name=name, description=description, pars=pars, strokes=strokes, distances=distances)
        st.rerun()
        
st.subheader("Overview")
if st.button("Add"): add()

st.data_editor(data.read())