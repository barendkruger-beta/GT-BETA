import streamlit as st
import sql

st.subheader("Groups")

class GroupsOverview():
    child_page = None
    df_sql = None
    df = None
    
    def __init__(self):
        self.child_page = "app_pages/groups/groups_detail.py"
    
        conn = sql.connect()
        df_sql = self.df_sql = sql.groups()
        df = self.df = df_sql.read()
                
        st_con = st.container(border=False)
        with st_con:
            st_con_buttons = st.container(border=False, horizontal=True)
            if st_con_buttons.button(label='', icon=':material/add_2:', key='groups_overview_add', disabled=not st.user.email == 'barendkruger@gmail.com'): self.add()
            
            column_config = {key: None for key in df.columns.to_list()}
            column_config['name'] = st.column_config.TextColumn(label='Name')
            column_config['description'] = st.column_config.TextColumn(label='Description')
            column_config['active'] = st.column_config.CheckboxColumn(label='Active')
            st_df = st.dataframe(
                key='groups_data',
                data=df,
                on_select='rerun',
                selection_mode=['single-row','single-cell'],
                hide_index=True,
                column_config=column_config,
                )

            index = None
            if len(st_df.selection['rows']):
                index = st_df.selection['rows'][0]
            elif len(st_df.selection['cells']):
                index = st_df.selection['cells'][0][0]
            if index is not None:
                if st_con_buttons.button(label='', icon=':material/book_4:', key='groups_overview_open', disabled=not st.user.email == 'barendkruger@gmail.com'):
                    self.open(index=index, df=df)
            else:
                st_con_buttons.button(label='', icon=':material/book_4:', key='groups_overview_open', disabled=True)
                    
    # Add dialog
    @st.dialog("Add")
    def add(self):
        name = st.text_input("Name")
        description = st.text_input("Description")
        active = st.toggle(label='Active', value=True)
        if st.button("Submit"):
            fields = ["name", "description", "active"]
            values = [name, description, active]
            self.df_sql.add(fields=fields, values=values)
            st.rerun()
            
    def open(self, index=None, df=None):
        if index is not None:
            id = df.iloc[index]['id']
            df_sel = df[df['id'] == id]
            st.session_state.group = df_sel
            
            st.session_state.page = self.child_page
            st.rerun()

groups = GroupsOverview()