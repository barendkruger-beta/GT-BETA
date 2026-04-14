import streamlit as st
import pandas as pd
import sql

global_admin = False

class CampaignDetails():
    obj = None
    df_sql = None
    df = None
    parent_page = None
           
    def __init__(self, df=None):        
        global global_admin
        self.df_sql = sql.campaigns()
        self.df = df     
        df_id = df['id'].tolist()[0]
        self.parent_page = "app_pages/campaigns/campaigns_overview.py"
        self.obj = st.expander(label='Details')
        
        # Get user role
        user_email = st.user.email
        participants_sql = sql.participants()
        participants_df = pd.DataFrame(participants_sql.read(f"WHERE table.email = '{user_email}'"))
        if not participants_df.empty:
            participant_id = participants_df['id'].tolist()[0]
            campaign_participants_sql = sql.campaign_participants()
            campaign_participants_df = pd.DataFrame(campaign_participants_sql.read(f"WHERE table.campaign_id = {df_id} AND table.participant_id = {participant_id}"))
            if not campaign_participants_df.empty:
                is_admin = campaign_participants_df['is_admin'].tolist()[0]
            #print(f'User:{st.user.name} Admin:{is_admin}')
            global_admin = is_admin > 0
            st.session_state.global_admin = global_admin

        if self.df is not None:
            with self.obj:
                st_name = st.text_input('Name', key=f'campaign_details_{df_id}_name', value=f'{self.df['name'].tolist()[0]}')
                st_description = st.text_area('Description', key=f'campaign_details_{df_id}_description', value=f'{self.df['description'].tolist()[0]}')
                st_active = st.toggle(label='Active', value=df['active'].tolist()[0], key=f'campaign_details_{df_id}_active')
                buttons_area = st.container(horizontal=True)
                with buttons_area:
                    if global_admin:
                        if st.button(label='', icon=':material/check:', key='campaign_details_update'):
                            self.update(name=st_name, description=st_description, active=st_active)
                        if st.button(label='', icon=':material/delete:', key='campaign_details_delete'):
                            self.delete()                        
    
    def update(self, name=None, description=None, active=None):
        if self.df is not None:
            fields = ['name', 'description', 'active']
            values = [name, description, active]
            self.df_sql.update(id=self.df['id'].tolist()[0], fields=fields, values=values)
            st.session_state.campaign = self.df_sql.read(filter=f"WHERE table.id={self.df['id'].tolist()[0]}")
            st.rerun()
            
    @st.dialog(title='Delete confirmation')        
    def delete(self):
        st.write("Are you sure you want to delete the entry?")
        area = st.container(horizontal=True, horizontal_alignment='center')
        with area:
            if st.button(label='Yes'):
                if self.df is not None:
                    self.df_sql.delete(id=self.df['id'].tolist()[0])
                    st.session_state.campaign = None
                    st.session_state.page = self.parent_page
                    st.rerun()
            if st.button(label='No'):
                st.rerun()
    
                
class CampaignCompetitions():
    obj = None
    campaign_sql = None
    campaign_df = None
    competitions_sql = None
    competitions_df = None
    participants_sql = None
    participants_df = None
    child_page = None    
    
    def __init__(self, campaign_df=None):
        self.child_page = "app_pages/competitions/competitions_detail.py"
        
        self.campaign_df = campaign_df
        self.competitions_sql = sql.competitions()
        self.competitions_df = pd.DataFrame(self.competitions_sql.read(filter=f"WHERE campaign_id={campaign_df['id'].tolist()[0]}"))
        if not self.competitions_df.empty: self.competitions_df = self.competitions_df.sort_values(by=['sequence', 'name'], ascending=True)
        
        self.participants_sql = sql.campaign_participants()
        self.participants_df = pd.DataFrame(self.participants_sql.read())
        if not self.participants_df.empty: self.participants_df = self.participants_df.sort_values(by='name')
        else: return
        
        pos_assigned_groups_sql = sql.campaign_groups()
        pos_assigned_groups_df = pd.DataFrame(pos_assigned_groups_sql.read(filter=f"WHERE campaign_id={self.campaign_df['id'].tolist()[0]}"))
        if not pos_assigned_groups_df.empty: pos_assigned_groups_df = pos_assigned_groups_df.sort_values(by='name')
        else: return
        
        exp_competitions = st.expander("Competitions", expanded=True)
        with exp_competitions:   
            col = st.container(horizontal=True, width='stretch')

            column_config = {key: None for key in self.competitions_df.columns.to_list()}
            column_config['name'] = 'Name'
            column_config['description'] = 'Description'
            event = st.dataframe(
                self.competitions_df,
                on_select='rerun',
                selection_mode=['single-row','single-cell'],
                hide_index=True,
                column_config=column_config
            )
            
            id = None
            if len(event.selection['rows']):
                id = self.competitions_df.iloc[event.selection['rows'][0]]['id']
            elif len(event.selection['cells']):
                id = self.competitions_df.iloc[event.selection['cells'][0][0]]['id']
            if id is not None:
                sel = self.competitions_df[self.competitions_df['id'] == id]
                col.button(label='', icon=':material/add_2:', disabled=True)
                if col.button(label='', icon=':material/jump_to_element:'): self.open(sel, self.child_page)
                if col.button(label='', icon=':material/arrow_upward:', disabled=not st.session_state.global_admin): self.move(sel=sel, up=True)
                if col.button(label='', icon=':material/arrow_downward:', disabled=not st.session_state.global_admin): self.move(sel=sel, down=True)                    
            else:
                if col.button(label='', icon=':material/add_2:'): self.add(campaign_df['id'].tolist()[0])
                col.button(label='', icon=':material/jump_to_element:', disabled=True)
                col.button(label='', icon=':material/arrow_upward:', disabled=True)
                col.button(label='', icon=':material/arrow_downward:', disabled=True)                
                
    # Add dialog
    @st.dialog("Add")
    def add(self, campaign_id=None):
        st_name = st.text_input("Name")
        st_description = st.text_input("Description")
        if st.button("Submit"):
            # Get sequence number
            if not self.competitions_df.empty:
                sequence = self.competitions_df['sequence'].max() + 1
            else: sequence = 1
            
            # Prepare sql query parameters
            fields = ["name", "description", "campaign_id", "sequence"]
            values = [st_name, st_description, campaign_id, sequence]
            
            # Create competition
            self.competitions_sql.add(fields=fields, values=values)
            st.rerun()
            
    # Open detail page            
    def open(self, sel, page):
        st.session_state.competition = sel
        st.session_state.event = None
        st.session_state.group = None
        st.session_state.participant = None
        st.session_state.event = None 
        
        st.session_state.page = page    
        st.rerun()

    # Move item up or down
    def move(self, sel, up=None, down=None):
        df_sql = sql.competitions()
        df = self.competitions_df
        this_id = sel['id'].tolist()[0]
        this_sequence = sel['sequence'].tolist()[0]
        min_sequence = df['sequence'].min()
        max_sequence = df['sequence'].max()

        if this_sequence == min_sequence and up is True: return
        if this_sequence == max_sequence and down is True: return
        if up is not None and down is not None: return
        
        ids = df['id'].tolist()
        this_index = ids.index(this_id)
        
        if up is not None: other_id = ids[this_index-1]
        elif down is not None: other_id = ids[this_index+1]
        
        other_df = df.query(f'id=={other_id}')
        other_sequence = other_df['sequence'].tolist()[0]
        
        # Update this event
        fields = ['sequence']
        values = [other_sequence]
        df_sql.update(id=this_id, fields=fields, values=values)
        
        # Update other event
        fields = ['sequence']
        values = [this_sequence]
        df_sql.update(id=other_id, fields=fields, values=values)
        
        st.rerun()
    
        
class CampaignGroupParticipants():
    obj = None
    campaign_df = None
    groups_sql = None
    groups_df = None
    participants_sql = None
    participants_df = None
    child_page = None    
    
    def __init__(self, campaign_df=None):
        self.campaign_df = campaign_df
        self.groups_sql = sql.campaign_groups()
        self.groups_df = pd.DataFrame(self.groups_sql.read())
        if not self.groups_df.empty: self.groups_df = self.groups_df.sort_values(by='name')
        
        self.participants_sql = sql.campaign_participants()
        self.participants_df = pd.DataFrame(self.participants_sql.read())
        if not self.participants_df.empty: self.participants_df = self.participants_df.sort_values(by='name')
        
        pos_assigned_groups_sql = sql.campaign_groups()
        pos_assigned_groups_df = pd.DataFrame(pos_assigned_groups_sql.read(filter=f"WHERE campaign_id={self.campaign_df['id'].tolist()[0]}"))
        if not pos_assigned_groups_df.empty: pos_assigned_groups_df = pos_assigned_groups_df.sort_values(by='name')
        
        pos_unassigned_groups_sql = sql.groups()
        if not pos_assigned_groups_df.empty:
            pos_unassigned_groups_df = pd.DataFrame(pos_unassigned_groups_sql.read()).query(f'id not in {pos_assigned_groups_df['group_id'].tolist()}')
            if not pos_unassigned_groups_df.empty: pos_unassigned_groups_df = pos_unassigned_groups_df.sort_values(by='name')
        else:
            pos_unassigned_groups_df = pd.DataFrame(pos_unassigned_groups_sql.read())
            if not pos_unassigned_groups_df.empty: pos_unassigned_groups_df = pos_unassigned_groups_df.sort_values(by='name')
            
        pos_assigned_participants_sql = sql.campaign_participants()
        pos_assigned_participants_df = pd.DataFrame(pos_assigned_participants_sql.read(filter=f"WHERE campaign_id={self.campaign_df['id'].tolist()[0]}"))
        if not pos_assigned_participants_df.empty: pos_assigned_participants_df = pos_assigned_participants_df.sort_values(by='name')
        
        pos_unassigned_participants_sql = sql.participants()
        if not pos_assigned_participants_df.empty:
            pos_unassigned_participants_df = pd.DataFrame(pos_unassigned_participants_sql.read()).query(f'id not in {pos_assigned_participants_df['participant_id'].tolist()}')
            if not pos_unassigned_participants_df.empty: pos_unassigned_participants_df = pos_unassigned_participants_df.sort_values(by='name')
        else:
            pos_unassigned_participants_df = pd.DataFrame(pos_unassigned_participants_sql.read())
            if not pos_unassigned_participants_df.empty: pos_unassigned_participants_df = pos_unassigned_participants_df.sort_values(by='name')
                
        exp_groups = st.expander("Groups & Participants", expanded=False)
        with exp_groups:
            exp_assigned_groups = st.expander("Groups", expanded=True)
            with exp_assigned_groups:
                column_config = {key: None for key in pos_assigned_groups_df.columns.to_list()}
                column_config['name'] = 'Name'
                column_config['description'] = 'Description'
                if not pos_assigned_groups_df.empty:
                    assigned_groups = st.dataframe(
                        pos_assigned_groups_df,
                        on_select='rerun',
                        selection_mode='multi-row',
                        hide_index=True,
                        column_config=column_config
                    )
                            
            exp_assigned_participants = st.expander("Participants", expanded=True)
            with exp_assigned_participants:
                column_config = {key: None for key in pos_assigned_participants_df.columns.to_list()}
                column_config['name'] = 'Name'
                column_config['description'] = 'Description'
                column_config['is_admin'] = st.column_config.CheckboxColumn('Campaign Admin')
                if not pos_assigned_participants_df.empty:
                    assigned_participants = st.dataframe(
                        pos_assigned_participants_df,
                        on_select='rerun',
                        selection_mode='multi-row',
                        hide_index=True,
                        column_config=column_config
                    )
                                
            exp_unassigned_groups = st.expander("Available groups", expanded=False)
            with exp_unassigned_groups:
                column_config = {key: None for key in pos_unassigned_groups_df.columns.to_list()}
                column_config['name'] = 'Name'
                column_config['description'] = 'Description'
                if not pos_unassigned_groups_df.empty:
                    unassigned_groups = st.dataframe(
                        pos_unassigned_groups_df,
                        on_select='rerun',
                        selection_mode='multi-row',
                        hide_index=True,
                        column_config=column_config
                    )
            
            exp_unassigned_participants = st.expander("Available participants", expanded=False)
            with exp_unassigned_participants:
                column_config = {key: None for key in pos_unassigned_participants_df.columns.to_list()}
                column_config['name'] = 'Name'
                column_config['description'] = 'Description'
                if not pos_unassigned_participants_df.empty:
                    unassigned_participants = st.dataframe(
                        pos_unassigned_participants_df,
                        on_select='rerun',
                        selection_mode='multi-row',
                        hide_index=True,
                        column_config=column_config
                    )
                      
            if not pos_unassigned_groups_df.empty and global_admin:
                if len(unassigned_groups.selection['rows']):
                    ids = pos_unassigned_groups_df.iloc[unassigned_groups.selection['rows']]['id'].tolist()
                    sels = pos_unassigned_groups_df.query(f'id in {ids}')
                    if exp_unassigned_groups.button(label='', icon=':material/add_2:', key="add_groups"):
                        self.add_groups(selection=sels)
                else:
                    exp_unassigned_groups.button(label='', icon=':material/add_2:', key="add_groups", disabled=True)
            #else: 
            #    exp_unassigned_groups.button("Add", key="add_groups", disabled=True, width='stretch')
            
            if not pos_assigned_groups_df.empty and global_admin:    
                if len(assigned_groups.selection['rows']):
                    ids = pos_assigned_groups_df.iloc[assigned_groups.selection['rows']]['id'].tolist()
                    sels = pos_assigned_groups_df.query(f'id in {ids}')
                    if exp_assigned_groups.button(label='', icon=':material/delete:', key="remove_groups"):
                        self.remove_groups(selection=sels)
                else:
                    exp_assigned_groups.button(label='', icon=':material/delete:', key="remove_groups", disabled=True)
            #else:
            #    exp_assigned_groups.button("Remove", key="remove_groups", disabled=True, width='stretch')
            
            if not pos_unassigned_participants_df.empty and global_admin:               
                if len(unassigned_participants.selection['rows']):
                    ids = pos_unassigned_participants_df.iloc[unassigned_participants.selection['rows']]['id'].tolist()
                    sels = pos_unassigned_participants_df.query(f'id in {ids}')
                    if exp_unassigned_participants.button(label='', icon=':material/add_2:', key="add_participants"):
                        self.add_participants(selection=sels)
                else:
                    exp_unassigned_participants.button(label='', icon=':material/add_2:', key="add_participants", disabled=True)
            #else:
            #    exp_unassigned_participants.button("Add", key="add_participants", disabled=True, width='stretch')
            
            con = exp_assigned_participants.container(horizontal=True) 
            if not pos_assigned_participants_df.empty and global_admin:
                if len(assigned_participants.selection['rows']):
                    ids = pos_assigned_participants_df.iloc[assigned_participants.selection['rows']]['id'].tolist()
                    sels = pos_assigned_participants_df.query(f'id in {ids}')
                    if con.button(label='', icon=':material/edit:', key="edit_participant"):
                        self.edit_participant(selection=sels)
                    if con.button(label='', icon=':material/delete:', key="remove_participants"):
                        self.remove_participants(selection=sels)
                else:
                    con.button(label='', icon=':material/edit:', key="edit_participant", disabled=True)
                    con.button(label='', icon=':material/delete:', key="remove_participants", disabled=True)
            #else:
            #    con.button("Remove", key="remove_participants", disabled=True, width='stretch')
          
    def add_groups(self, selection):
        fields = selection.columns.tolist()
        fields[fields.index('id')] = 'group_id'
        fields[fields.index('name')] = 'name'
        fields.append('campaign_id')
        for entry in selection.to_numpy().tolist():
            entry.append(self.campaign_df['id'].tolist()[0])
            self.groups_sql.add(fields=fields, values=entry)
        st.rerun()
    
    def remove_groups(self, selection):
        id_index = selection.columns.tolist().index('id')
        for entry in selection.to_numpy().tolist():
            self.groups_sql.delete(entry[id_index])
        st.rerun()
        
    def add_participants(self, selection):
        fields = selection.columns.tolist()
        fields[fields.index('id')] = 'participant_id'
        fields[fields.index('name')] = 'name'
        fields.append('campaign_id')
        fields.append('is_admin')
        #print(fields)
        for entry in selection.to_numpy().tolist():
            entry.append(self.campaign_df['id'].tolist()[0])
            entry.append(True)
            #print(entry)            
            self.participants_sql.add(fields=fields, values=entry)
        st.rerun()
    
    def remove_participants(self, selection):
        id_index = selection.columns.tolist().index('id')
        for entry in selection.to_numpy().tolist():
            self.participants_sql.delete(entry[id_index])
        st.rerun()

    @st.dialog(title='Edit campaign participant')
    def edit_participant(self, selection):
        #print(selection)
        participant_id = selection['id'].tolist()[0]
        st_description = st.text_input(label='Description', value=selection['description'].tolist()[0])
        st_is_admin = st.toggle(label='Administrator', value=selection['is_admin'].tolist()[0])

        if st.button("Update"):
            fields = ["description", "is_admin"]
            values = [st_description, st_is_admin]
            self.participants_sql.update(id=participant_id, fields=fields, values=values)
            #print(f'ID to update: {participant_id}\nValues:{values}')
            st.rerun()

# Populate page 
con = st.container(horizontal=True, vertical_alignment='center')

st_details = CampaignDetails(df=st.session_state.campaign)

st_competitions = CampaignCompetitions(campaign_df=st.session_state.campaign)

st_groups_participants = CampaignGroupParticipants(campaign_df=st.session_state.campaign)

with con:
    if st.button(label='', icon=':material/arrow_back:'):
        st.session_state.campaign = None
        st.session_state.page = st_details.parent_page
        st.rerun()
    if st.button(label='', icon=':material/refresh:'):
        st.rerun()
    st.subheader(f"Campaign: {st.session_state.campaign['name'].tolist()[0]}")