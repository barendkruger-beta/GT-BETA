import streamlit as st
import pandas as pd
import sql


class GroupDetails():
    obj = None
    df_sql = None
    df = None
    parent_page = None
           
    def __init__(self, df=None):
        self.obj = st.expander(label='Details', expanded=True)
        self.df_sql = sql.groups()
        self.df = df
        df_id = df['id'].tolist()[0]
        
        self.parent_page = "app_pages/groups/groups_overview.py"
        if self.df is not None:
            with self.obj:
                st_name = st.text_input('Name', key=f'course_details_{df_id}_name', value=f'{self.df['name'].tolist()[0]}')
                st_description = st.text_area('Description', key=f'course_details_{df_id}_description', value=f'{self.df['description'].tolist()[0]}')
                st_active = st.toggle(label='Active', value=df['active'].tolist()[0], key=f'course_details_{df_id}_active')
                buttons_area = st.container(horizontal=True)
                if st.user.email.lower() in st.secrets["superusers"]["emails"]:
                    with buttons_area:
                        if st.button(label='', icon=':material/check:', key='group_details_update'):
                            self.update(name=st_name, description=st_description, active=st_active)
                        if st.button(label='WIP', icon=':material/delete:', key='group_details_delete', disabled=True):
                            self.delete()                        
    
    @st.dialog(title='Update confirmation')
    def update(self, name=None, description=None, active=None):
        if self.df is not None:
            st.write('Do you want to update all linked instances?')
            st_update_all = st.segmented_control(
                label='Do you want to update all linked instances?',
                options=['All', 'Only this item'],
                default='All',
                )
            
            if st.button('Update'):
                fields = ['name', 'description', 'active']
                values = [name, description, active]
                self.df_sql.update(id=self.df['id'].tolist()[0], fields=fields, values=values)
                st.session_state.group = self.df_sql.read(filter=f"WHERE table.id={self.df['id'].tolist()[0]}")
                
                if st_update_all == 'All':
                    self.update_downstream()
                    
                st.rerun()
    
    def update_downstream(self):
        if st.session_state.group is None:
            return
        df = st.session_state.group
        df_id = df['id'].tolist()[0]
        df_name = df['name'].tolist()[0]
        df_description = df['description'].tolist()[0]
        df_active = df['active'].tolist()[0]
        
        # Update each campaign group
        campaign_groups_sql = sql.campaign_groups()
        campaign_groups_df = pd.DataFrame(campaign_groups_sql.read(filter=f"WHERE table.group_id = {df_id}"))
        if not campaign_groups_df.empty:
            for campaign_group_id in campaign_groups_df['id'].tolist():
                fields = ['name', 'description', 'active']
                values = [df_name, df_description, df_active]
                campaign_groups_sql.update(id=campaign_group_id, fields=fields, values=values)
                
                # Update each competition group
                competition_groups_sql = sql.competition_groups()
                competition_groups_df = pd.DataFrame(competition_groups_sql.read(filter=f"WHERE table.campaign_group_id = {campaign_group_id}"))
                if not competition_groups_df.empty:
                    for competition_group_id in competition_groups_df['id'].tolist():
                        competition_groups_sql.update(id=competition_group_id, fields=fields, values=values)
                
                        # Update each event group
                        event_groups_sql = sql.event_groups()
                        event_groups_df = pd.DataFrame(event_groups_sql.read(filter=f"WHERE table.competition_group_id = {competition_group_id}"))
                        if not event_groups_df.empty:
                            for event_group_id in  event_groups_df['id'].tolist():
                                event_groups_sql.update(id=event_group_id, fields=fields, values=values)
                                
                                # Update each scoring card group
                                scoring_groups_sql = sql.scoring_card_groups()
                                scoring_groups_df = pd.DataFrame(scoring_groups_sql.read(filter=f"WHERE table.event_group_id = {event_group_id}"))
                                if not scoring_groups_df.empty:
                                    for scoring_group_id in scoring_groups_df['id'].tolist():
                                        scoring_groups_sql.update(id=scoring_group_id, fields=fields, values=values)
                    
                                # Update each match group
                                match_groups_sql = sql.match_groups()
                                match_groups_df = pd.DataFrame(match_groups_sql.read(filter=f"WHERE table.event_group_id = {event_group_id}"))
                                if not match_groups_df.empty:
                                    for match_group_id in match_groups_df['id'].tolist():
                                        match_groups_sql.update(id=match_group_id, fields=fields, values=values)
    
    
    @st.dialog(title='Delete confirmation')        
    def delete(self):
        st.write("Are you sure you want to delete the entry?")
        area = st.container(horizontal=True, horizontal_alignment='center')
        with area:
            if st.button(label='Yes'):
                if self.df is not None:
                    self.df_sql.delete(id=self.df['id'].tolist()[0])
                    st.session_state.course = None
                    st.session_state.page = self.parent_page
                    st.rerun()
            if st.button(label='No'):
                st.rerun()

# Populate page
with st.spinner('Loading data'):
    con = st.container(horizontal=True, vertical_alignment='center')

    st_details = GroupDetails(df=st.session_state.group)

    with con:
        if st.button(label='', icon=':material/arrow_back:'):
            st.session_state.group = None
            st.session_state.page = st_details.parent_page
            st.rerun()
        st.subheader(f"Group: {st.session_state.group['name'].tolist()[0]}")
        