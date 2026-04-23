import streamlit as st
import pandas as pd
import sql

# Load page dataframe
df_sql = sql.campaigns()
df = pd.DataFrame(df_sql.read())

# Set next detail page
detail_page = "app_pages/campaigns/campaigns_detail.py"

# Add dialog
@st.dialog("Add")
def add():
    name = st.text_input("Name")
    description = st.text_input("Description")
    active = st.toggle(label='Active', value=True)
    if st.button("Submit"):
        fields = ["name", "description", "active"]
        values = [name, description, active]
        df_sql.add(fields=fields, values=values)
        st.rerun()

# Open detail page                        
def navigate(sel, page):
    st.session_state.campaign = sel
    st.session_state.group = None
    st.session_state.participant = None
    st.session_state.competition = None
    st.session_state.event = None 
    st.session_state.scoring_card = None 
    st.session_state.scoring_hole = None
    st.session_state.course = None
    st.session_state.course_tee = None
    
    st.session_state.page = page    
    st.rerun()


# Populate page       
st.subheader("Campaigns")

col = st.container(horizontal=True, width='stretch')
with col:
    if st.button(label='', icon=':material/add_2:', disabled=True): add()

column_config = {key: None for key in df.columns.to_list()}
column_config['name'] = st.column_config.TextColumn(label='Name')
column_config['description'] = st.column_config.TextColumn(label='Description')
column_config['active'] = st.column_config.CheckboxColumn(label='Active')

#print(column_config)
event = st.dataframe(
    df,
    on_select='rerun',
    selection_mode=['single-row','single-cell'],
    hide_index=True,
    column_config=column_config
)

id = None
if len(event.selection['rows']):
    id = df.iloc[event.selection['rows'][0]]['id']
elif len(event.selection['cells']):
    id = df.iloc[event.selection['cells'][0][0]]['id']
if id is not None:
    #print('ID is not none')
    sel = df[df['id'] == id]
    if col.button(label='', icon=':material/jump_to_element:'):
        navigate(sel, detail_page)
else:
    col.button(label='', icon=':material/jump_to_element:', disabled=True)
