import streamlit as st
import pandas as pd
import sql

# Load page dataframe
df_sql = sql.course_tees()
df = pd.DataFrame(df_sql.read())

# Set next detail page
detail_page = "app_pages/course_tees/course_tees_detail.py"

# Add dialog
@st.dialog("Add")
def add():
    name = st.text_input("Name")
    description = st.text_input("Description")
    if st.button("Submit"):
        fields = ["name", "description"]
        values = [name, description]
        df_sql.add(fields=fields, values=values)
        st.rerun()

# Open detail page                        
def open(sel, page):
    st.session_state.course_tee = sel
    
    st.session_state.page = page    
    st.rerun()

# Populate page       
st.subheader("Course Tees")

col = st.container(horizontal=True, width='stretch')
with col:
    if st.button("Add"): add()

column_config = {key: None for key in df.columns.to_list()}
column_config['name'] = 'Name'
column_config['description'] = 'Description'

#print(column_config)
event = st.dataframe(
    df,
    on_select='rerun',
    selection_mode='multi-row',
    column_config = column_config,
)

if len(event.selection['rows']):
    selected_row = event.selection['rows'][0]
    id = df.iloc[selected_row]['id']
    sel = df[df['id'] == id]
    if col.button("Open"):
        open(sel, detail_page)
        pass
else:
    col.button("Open", disabled=True)
    pass

st.session_state.course_tee = None