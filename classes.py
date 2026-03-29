import streamlit as st
import pandas as pd
import sql

# region st Classes

class st_EventDetails():
    obj = None
    df = None
    parent_page = None
    df = None
           
    def __init__(self, df=None):
        self.obj = st.expander(label='Details')
        self.df = df
        self.parent_page = "app_pages/series/series_details.py"
        if self.df is not None:
            self.df = self.df
            with self.obj:
                st.text_input('Name', key=f'event_details_name', value=f'{self.df['name'].tolist()[0]}')
                st.text_area('Description', key=f'event_details_description', value=f'{self.df['description'].tolist()[0]}')
                buttons_area = st.container(horizontal=True)
                with buttons_area:
                    if st.button(label='Update', key='event_details_update'):
                        self.update()
                    if st.button(label='Delete', key='event_details_delete'):
                        self.delete()                        
    
    def update(self):
        if self.df is not None:
            sql_event = sql.events()
            sql_event.update(id=self.df['id'].tolist()[0],
                                 name=st.session_state.event_details_name,
                                 description=st.session_state.event_details_description)
            st.session_state.event = sql_event.read(filter=f"WHERE id={self.df['id'].tolist()[0]}")
            st.rerun()
            
    @st.dialog(title='Delete confirmation')        
    def delete(self):
        st.write("Are you sure you want to delete the entry?")
        area = st.container(horizontal=True, horizontal_alignment='center')
        with area:
            if st.button(label='Yes'):
                if self.df is not None:
                    sql_event = sql.events()
                    sql_event.delete(id=self.df['id'].tolist()[0])
                    st.session_state.event = None
                    st.session_state.page = self.parent_page
                    st.rerun()
            if st.button(label='No'):
                st.rerun()


class st_SequenceGroupDetails():
    obj = None
    df = None
    parent_page = None
    df = None
           
    def __init__(self, df=None):
        self.obj = st.expander(label='Details')
        self.df = df
        self.parent_page = "app_pages/events/events_details.py"
        if self.df is not None:
            self.df = self.df
            with self.obj:
                st.text_input('Name', key=f'sequence_group_details_name', value=f'{self.df['name'].tolist()[0]}')
                st.text_area('Description', key=f'sequence_group_details_description', value=f'{self.df['description'].tolist()[0]}')
                buttons_area = st.container(horizontal=True)
                with buttons_area:
                    if st.button(label='Update', key='sequence_group_details_update'):
                        self.update()
                    if st.button(label='Delete', key='sequence_group_details_delete'):
                        self.delete()                        
    
    def update(self):
        if self.df is not None:            
            sql_sequence_group = sql.sequence_groups()
            sql_sequence_group.update(id=self.df['id'].tolist()[0],
                                 name=st.session_state.sequence_group_details_name,
                                 description=st.session_state.sequence_group_details_description)
            st.session_state.sequence_group = sql_sequence_group.read(filter=f"WHERE id={self.df['id'].tolist()[0]}")
            st.rerun()
            
    @st.dialog(title='Delete confirmation')        
    def delete(self):
        st.write("Are you sure you want to delete the entry?")
        area = st.container(horizontal=True, horizontal_alignment='center')
        with area:
            if st.button(label='Yes'):
                if self.df is not None:
                    sql_sequence_group = sql.sequence_groups()
                    sql_sequence_group.delete(id=self.df['id'].tolist()[0])
                    st.session_state.sequence_group = None
                    st.session_state.page = self.parent_page
                    st.rerun()
            if st.button(label='No'):
                st.rerun()                


class st_SequenceGroupParticipants():
    sequences_df = None
    participants_df = None
    
    def __init__(self):
        pass
    
    def add(self):
        pass
    
    def update(self):
        pass
    
    def remove(self):
        pass  
    
# endregion
