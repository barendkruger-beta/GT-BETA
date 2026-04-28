import streamlit as st
import pandas as pd
import sql

# Load page dataframe
df_sql = sql.courses()
df = pd.DataFrame(df_sql.read())

# Set next detail page
detail_page = "app_pages/courses/courses_detail.py"

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
    st.session_state.course = sel
    #st.session_state.campaign = sel
    #st.session_state.series = None
    #st.session_state.event = None
    #st.session_state.groups = None
    #st.session_state.participants = None
    #st.session_state.event = None 
    #st.session_state.scoring_card = None 
    #st.session_state.scoring_hole = None
    
    st.session_state.page = page    
    st.rerun()

# Populate page       
st.subheader("Courses")

col = st.container(horizontal=True, width='stretch')
with col:
    if st.button(label='', icon=':material/add_2:', disabled=not st.user.email.lower() in st.secrets["superusers"]["emails"]): add()

column_config = {key: None for key in df.columns.to_list()}
column_config['name'] = st.column_config.TextColumn(label='Name')
column_config['description'] = st.column_config.TextColumn(label='Description')
column_config['active'] = st.column_config.CheckboxColumn(label='Active')

df = df.sort_values(['active','name'], ascending=[False, True])
#print(column_config)
event = st.dataframe(
    df,
    on_select='rerun',
    selection_mode='multi-row',
    column_config = column_config,
    hide_index=True,
)

if len(event.selection['rows']):
    selected_row = event.selection['rows'][0]
    id = df.iloc[selected_row]['id']
    sel = df[df['id'] == id]
    if col.button(label='', icon=':material/jump_to_element:'):
        open(sel, detail_page)
        pass
else:
    col.button(label='', icon=':material/jump_to_element:', disabled=True)
    pass

st.session_state.course = None