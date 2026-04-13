import streamlit as st
import pandas as pd
import sql
import matplotlib


class CompetitionDetails():
    obj = None
    df = None
    parent_page = None
           
    def __init__(self, df=None):
        self.obj = st.expander(label='Details')
        self.df = df
        df_id = df['id'].tolist()[0]
        self.parent_page = "app_pages/campaigns/campaigns_detail.py"
        if self.df is not None:
            with self.obj:
                st_name = st.text_input('Name', key=f'competition_details_{df_id}_name', value=f'{self.df['name'].tolist()[0]}')
                st_description = st.text_area('Description', key=f'competition_details_{df_id}_description', value=f'{self.df['description'].tolist()[0]}')
                st_active = st.toggle(label='Active', value=df['active'].tolist()[0], key=f'competition_details_{df_id}_active')
                buttons_area = st.container(horizontal=True)
                if st.session_state.global_admin:
                    with buttons_area:
                        if st.button(label='', icon=':material/check:', key='competition_details_update'):
                            self.update(name=st_name, description=st_description, active=st_active)
                        if st.button(label='', icon=':material/delete:', key='competition_details_delete'):
                            self.delete()                        
    
    def update(self, name=None, description=None, active=None):
        if self.df is not None:
            sql_competition = sql.competitions()
            fields = ['name', 'description', 'active']
            values = [name, description, active]
            sql_competition.update(id=self.df['id'].tolist()[0], fields=fields, values=values)
            st.session_state.competition = sql_competition.read(filter=f"WHERE table.id={self.df['id'].tolist()[0]}")
            
            # Propogate events 'active'
            competition_id = self.df['id'].tolist()[0]
            events_sql = sql.events()
            events_df = pd.DataFrame(events_sql.read(f"WHERE table.competition_id = {competition_id}"))
            for event_id in events_df['id'].tolist():
                fields = ['active']
                values = [active]
                events_sql.update(id=event_id, fields=fields, values=values)
                
                # Propogate event groups 'active'
                event_groups_sql = sql.event_groups()
                event_groups_df = pd.DataFrame(event_groups_sql.read(f"WHERE table.event_id = {event_id}"))
                for event_group_id in event_groups_df['id'].tolist():
                    fields = ['active']
                    values = [active]
                    event_groups_sql.update(id=event_group_id, fields=fields, values=values)

                # Propogate event participants 'active'
                event_participants_sql = sql.event_participants()
                event_participants_df = pd.DataFrame(event_participants_sql.read(f"WHERE table.event_id = {event_id}"))
                for event_participant_id in event_participants_df['id'].tolist():
                    fields = ['active']
                    values = [active]
                    event_participants_sql.update(id=event_participant_id, fields=fields, values=values)
                    
                # Propogate scoring cards 'active'
                scoring_cards_sql = sql.scoring_cards()
                scoring_cards_df = pd.DataFrame(scoring_cards_sql.read(f"WHERE table.event_id = {event_id}"))
                for scoring_card_id in scoring_cards_df['id'].tolist():
                    fields = ['active']
                    values = [active]
                    scoring_cards_sql.update(id=scoring_card_id, fields=fields, values=values)

                    # Propogate scoring card groups 'active'
                    scoring_card_groups_sql = sql.scoring_card_groups()
                    scoring_card_groups_df = pd.DataFrame(scoring_card_groups_sql.read(f"WHERE table.scoring_card_id = {scoring_card_id}"))
                    for scoring_card_group_id in scoring_card_groups_df['id'].tolist():
                        fields = ['active']
                        values = [active]
                        scoring_card_groups_sql.update(id=scoring_card_group_id, fields=fields, values=values)

                    # Propogate scoring card participants 'active'
                    scoring_card_participants_sql = sql.scoring_card_participants()
                    scoring_card_participants_df = pd.DataFrame(scoring_card_participants_sql.read(f"WHERE table.scoring_card_id = {scoring_card_id}"))
                    for scoring_card_participant_id in scoring_card_participants_df['id'].tolist():
                        fields = ['active']
                        values = [active]
                        scoring_card_participants_sql.update(id=scoring_card_participant_id, fields=fields, values=values)

                    # Propogate scoring rounds 'active'
                    rounds_sql = sql.scoring_rounds()
                    rounds_df = pd.DataFrame(rounds_sql.read(f"WHERE table.scoring_card_id = {scoring_card_id}"))
                    for round_id in rounds_df['id'].tolist():
                        fields = ['active']
                        values = [active]
                        rounds_sql.update(id=round_id, fields=fields, values=values)
            
            st.rerun()

    @st.dialog(title='Delete confirmation')        
    def delete(self):
        st.write("Are you sure you want to delete the entry?")
        area = st.container(horizontal=True, horizontal_alignment='center')
        with area:
            if st.button(label='Yes'):
                if self.df is not None:
                    sql_competition = sql.competitions()
                    sql_competition.delete(id=self.df['id'].tolist()[0])
                    st.session_state.competition = None
                    st.session_state.page = self.parent_page
                    st.rerun()
            if st.button(label='No'):
                st.rerun()


class CompetitionEvents():
    obj = None
    competition_df = None
    events_sql = None
    events_df = None
    groups_sql = None
    groups_df = None
    participants_sql = None
    participants_df = None    
    child_page = None 
    
    def __init__(self, competition_df=None):
        self.child_page = "app_pages/events/events_detail.py"
        
        self.competition_df = competition_df
        df_id = competition_df['id'].tolist()[0]
        
        self.events_sql = sql.events()
        self.events_df = pd.DataFrame(self.events_sql.read(filter=f"WHERE table.competition_id={df_id}"))
        if not self.events_df.empty: self.events_df = self.events_df.sort_values(by=['sequence', 'name'])

        self.groups_sql = sql.competition_groups()
        self.groups_df = pd.DataFrame(self.groups_sql.read(filter=f"WHERE table.competition_id={df_id}"))
        if not self.groups_df.empty: self.groups_df = self.groups_df.sort_values(by='name')
            
        self.participants_sql = sql.competition_participants()
        self.participants_df = pd.DataFrame(self.participants_sql.read(filter=f"WHERE table.competition_id={df_id}"))
        if not self.participants_df.empty: self.participants_df = self.participants_df.sort_values(by=['competition_groups_name','name'])
        else: return
        
        exp_events = st.expander("Events", expanded=True)
        with exp_events:
            col = st.container(horizontal=True, width='stretch')
            
            column_config = {key: None for key in self.events_df.columns.to_list()}
            column_config['name'] = 'Name'
            column_config['description'] = 'Description'
            event = st.dataframe(
                self.events_df,
                on_select='rerun',
                selection_mode=['single-row', 'single-cell'],
                hide_index=True,
                column_config=column_config
            )

            id = None
            if len(event.selection['rows']):
                id = self.events_df.iloc[event.selection['rows'][0]]['id']
            elif len(event.selection['cells']):
                id = self.events_df.iloc[event.selection['cells'][0][0]]['id']
            if id is not None:
                sel = self.events_df[self.events_df['id'] == id]
                col.button(label='', icon=':material/add_2:', disabled=True)
                if col.button(label='', icon=':material/jump_to_element:'): self.open(sel, self.child_page)                    
                if col.button(label='', icon=':material/arrow_upward:', disabled=not st.session_state.global_admin): self.move(sel=sel, up=True)
                if col.button(label='', icon=':material/arrow_downward:', disabled=not st.session_state.global_admin): self.move(sel=sel, down=True)
            else:
                if col.button(label='', icon=':material/add_2:'): self.add(self.competition_df['id'].tolist()[0])
                col.button(label='', icon=':material/jump_to_element:', disabled=True)
                col.button(label='', icon=':material/arrow_upward:', disabled=True)
                col.button(label='', icon=':material/arrow_downward:', disabled=True)
      
    # Add dialog
    @st.dialog("Add")
    def add(self, competition_id=None):
        st_name = st.text_input("Name")
        st_description = st.text_input("Description")
        st_auto_participants = st.toggle("Add all participants", value=True)
        if st.button("Submit"):
            # Get sequence number
            if not self.events_df.empty:
                sequence = self.events_df['sequence'].max() + 1
            else: sequence = 1
            
            # Prepare sql query parameters
            fields = ["name", "description", "competition_id", "sequence"]
            values = [st_name, st_description, competition_id, sequence]
            event_id = self.events_sql.add(fields=fields, values=values)
            
            if st_auto_participants:
                event_groups_sql = sql.event_groups()
                event_participants_sql = sql.event_participants()
                for competition_group_id in self.groups_df['id'].tolist():
                    group_name = self.groups_df.query(f"id=={competition_group_id}")['name'].tolist()[0]
                    group_description = self.groups_df.query(f"id=={competition_group_id}")['description'].tolist()[0]
                    group_active = self.groups_df.query(f"id=={competition_group_id}")['active'].tolist()[0]
                    
                    fields = ["name", "description", "active", "event_id", "competition_group_id"]
                    values = [group_name, group_description, group_active, event_id, competition_group_id]
                    event_group_id = event_groups_sql.add(fields=fields, values=values)
                    
                    group_participants_df = self.participants_df.query(f"competition_group_id=={competition_group_id}")
                    for participant_id in group_participants_df['id'].tolist():
                        participant_name = self.participants_df.query(f"id=={participant_id}")['name'].tolist()[0]
                        participant_description = self.participants_df.query(f"id=={participant_id}")['description'].tolist()[0]
                        participant_active = self.participants_df.query(f"id=={participant_id}")['active'].tolist()[0]
                        
                        fields = ["name", "description", "active", "event_id", "event_group_id", "competition_participant_id"]
                        values = [participant_name, participant_description, participant_active, event_id, event_group_id, participant_id]
                        event_participants_sql.add(fields=fields, values=values)
                        
            st.rerun()
        
    # Open detail page            
    def open(self, sel, page):
        st.session_state.event = sel
        st.session_state.scoring_card = None

        st.session_state.page = page    
        st.rerun()

    # Move item up or down
    def move(self, sel, up=None, down=None):
        df_sql = sql.events()
        df = self.events_df
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


class CompetitionGroupParticipants():
    obj = None
    competition_df = None
    groups_sql = None
    groups_df = None
    participants_sql = None
    participants_df = None
    child_page = None    
    
    def __init__(self, competition_df=None):
        self.competition_df = competition_df
        self.groups_sql = sql.competition_groups()
        self.groups_df = pd.DataFrame(self.groups_sql.read())
        if not self.groups_df.empty: self.groups_df = self.groups_df.sort_values(by='name')
            
        self.participants_sql = sql.competition_participants()
        self.participants_df = pd.DataFrame(self.participants_sql.read())
        if not self.participants_df.empty: self.participants_df = self.participants_df.sort_values(by=['competition_groups_name','name'])
        
        pos_assigned_groups_sql = sql.competition_groups()
        pos_assigned_groups_df = pd.DataFrame(pos_assigned_groups_sql.read(filter=f"WHERE table.competition_id={self.competition_df['id'].tolist()[0]}"))
        pos_all_groups_sql = sql.campaign_groups()
        if not pos_assigned_groups_df.empty:
            pos_all_groups_df = pd.DataFrame(pos_all_groups_sql.read(filter=f"WHERE table.campaign_id={self.competition_df['campaign_id'].tolist()[0]}"))
            if not pos_all_groups_df.empty: pos_all_groups_df = pos_all_groups_df.sort_values(by='name')
        else:
            pos_all_groups_df = pd.DataFrame(pos_all_groups_sql.read(filter=f"WHERE table.campaign_id={self.competition_df['campaign_id'].tolist()[0]}"))
            if not pos_all_groups_df.empty: pos_all_groups_df = pos_all_groups_df.sort_values(by='name')
            
        pos_assigned_participants_sql = sql.competition_participants()
        pos_assigned_participants_df = pd.DataFrame(pos_assigned_participants_sql.read(filter=f"WHERE table.competition_id={self.competition_df['id'].tolist()[0]}"))
        if not pos_assigned_participants_df.empty: pos_assigned_participants_df = pos_assigned_participants_df.sort_values(by=['competition_groups_name','name'])
        
        pos_unassigned_participants_sql = sql.campaign_participants()
        if not pos_assigned_participants_df.empty:
            pos_unassigned_participants_df = pd.DataFrame(pos_unassigned_participants_sql.read(filter=f"WHERE table.campaign_id={self.competition_df['campaign_id'].tolist()[0]}")).query(f'id not in {pos_assigned_participants_df['campaign_participant_id'].tolist()}')
            if not pos_unassigned_participants_df.empty: pos_unassigned_participants_df = pos_unassigned_participants_df.sort_values(by='name')
        else:
            pos_unassigned_participants_df = pd.DataFrame(pos_unassigned_participants_sql.read(filter=f"WHERE table.campaign_id={self.competition_df['campaign_id'].tolist()[0]}"))
            if not pos_unassigned_participants_df.empty: pos_unassigned_participants_df = pos_unassigned_participants_df.sort_values(by='name')
                
        exp_groups_participants = st.expander("Groups & Participants", expanded=False, width='stretch')
        #con_assigned = exp_groups_participants.container(horizontal=True, width='stretch')
        with exp_groups_participants:                                      
            if not pos_assigned_participants_df.empty:
                exp_assigned_participants = st.expander("Participants", expanded=True)
                            
                st_form = exp_assigned_participants.form(key='competition_participants_form', border=False, enter_to_submit=False)
                def participants_form_update():
                    changes = st.session_state.competition_participants_data
                    print(changes)        
                    edited_rows = changes.get("edited_rows", {})        
                    for index, updates in edited_rows.items():
                        for column, value in updates.items():
                            match column:
                                case 'hc_index':
                                    self.participants_sql.update(id=pos_assigned_participants_df.iloc[index]['id'],
                                                                fields=[column],
                                                                values=[round(value,1)])
                                case 'competition_groups_name':
                                    sel_id = self.groups_df.query(f"name == '{value}'")['id'].tolist()[0]
                                    self.participants_sql.update(id=pos_assigned_participants_df.iloc[index]['id'],
                                                                fields=['competition_group_id'],
                                                                values=[sel_id])
                                
                                case 'Remove':
                                    if value:
                                        self.participants_sql.delete(id=pos_assigned_participants_df.iloc[index]['id'])
                                        print('Participant will be removed')
                                    
                                case _: print(f'{column} = {value}')
                    st.rerun()
                with st_form:
                    dataframe_df = pos_assigned_participants_df
                    dataframe_df['Remove'] = False
                    
                    group_options = pos_assigned_groups_df['name'].tolist()
                    
                    #print(dataframe_df)
                    column_config = {key: None for key in dataframe_df.columns.to_list()}
                    column_config['name'] = st.column_config.TextColumn(label='Name', disabled=True)
                    column_config['competition_groups_name'] = st.column_config.SelectboxColumn(label='Group', options=group_options, required=True)
                    column_config['hc_index'] = st.column_config.NumberColumn(label='Handicap', format="%.1f", required=True)
                    column_config['Remove'] = st.column_config.CheckboxColumn()
                    
                    if not pos_assigned_participants_df.empty:
                        if True:
                            assigned_participants = st.data_editor(
                                key='competition_participants_data',
                                data=pos_assigned_participants_df,
                                hide_index=True,
                                column_config=column_config,
                            )
                            if st.form_submit_button('Update', disabled=not st.session_state.global_admin):
                                participants_form_update()
                            #print(self.participants_sql.columns)
                        #for entry in pos_assigned_participants_df.to_numpy().tolist():
                        #    #print(entry)
                        #    self.st_assigned_participant(df=pos_assigned_participants_df.query(f'id=={entry[0]}'))
                    else:
                        st.text(body='No players assigned')
                        st.form_submit_button('Update', disabled=True)
                
        exp_unassigned = exp_groups_participants.expander("Available", expanded=False, width='stretch')
        #con_unassigned = exp_unassigned.container(horizontal=True, width='stretch')  
        with exp_unassigned:
            column_config = {key: None for key in pos_unassigned_participants_df.columns.to_list()}
            column_config['name'] = 'Participant'
            if not pos_unassigned_participants_df.empty:
                unassigned_participants = st.dataframe(
                    pos_unassigned_participants_df,
                    on_select='rerun',
                    selection_mode='multi-row',
                    hide_index=True,
                    column_config=column_config
                )
            
            column_config = {key: None for key in pos_all_groups_df.columns.to_list()}
            column_config['name'] = 'Group'
            if not pos_all_groups_df.empty and not pos_unassigned_participants_df.empty:
                all_groups = st.dataframe(
                    pos_all_groups_df,
                    on_select='rerun',
                    selection_mode='single-row',
                    hide_index=True,
                    column_config= column_config,
                )
        
        if False:
            con_assigned_buttons = exp_assigned_participants.container(horizontal=True, width='stretch')
            if not pos_assigned_participants_df.empty:    
                if len(assigned_participants.selection['rows']):
                    participants_ids = pos_assigned_participants_df.iloc[assigned_participants.selection['rows']]['id'].tolist()
                    participants_sels = pos_assigned_participants_df.query(f'id in {participants_ids}')
                    if con_assigned_buttons.button("Remove", key="remove_participants", width='stretch'):
                        self.remove_participants(selection=participants_sels)
                        pass
                else:
                    con_assigned_buttons.button("Remove", key="remove_participants", disabled=True, width='stretch')
            else:
                con_assigned_buttons.button("Remove", key="remove_participants", disabled=True, width='stretch')
                
        if not pos_unassigned_participants_df.empty:
            if len(unassigned_participants.selection['rows']) and len(all_groups.selection['rows']):
                participants_ids = pos_unassigned_participants_df.iloc[unassigned_participants.selection['rows']]['id'].tolist()
                participants_sels = pos_unassigned_participants_df.query(f'id in {participants_ids}')
                groups_ids = pos_all_groups_df.iloc[all_groups.selection['rows']]['id'].tolist()
                groups_sels = pos_all_groups_df.query(f'id in {groups_ids}')

                if exp_unassigned.button("Add", key="add_participants", width='stretch', disabled=not st.session_state.global_admin):
                    # Create group if not already assigned
                    group_id = pos_all_groups_df.iloc[all_groups.selection['rows']]['id'].tolist()[0]
                    if pos_assigned_groups_df.empty:
                        self.add_groups(selection=groups_sels)
                    elif group_id not in pos_assigned_groups_df['campaign_group_id'].tolist():
                        self.add_groups(selection=groups_sels)
                    
                    pos_assigned_groups_df = pd.DataFrame(pos_assigned_groups_sql.read(filter=f"WHERE table.competition_id={self.competition_df['id'].tolist()[0]}"))    
                    assigned_group_id = pos_assigned_groups_df.query(f'campaign_group_id == {group_id}')['id'].tolist()[0] 
                    #Create participant
                    self.add_participants(selection=participants_sels, group_id=assigned_group_id)   
            else:
                exp_unassigned.button("Add", key="add_participants", disabled=True, width='stretch')
        else:
            exp_unassigned.button("Add", key="add_participants", disabled=True, width='stretch')
    
    def st_assigned_participant(self, df):
        name = df['name'].tolist()[0]
        hc_index = df['hc_index'].tolist()[0]
        group_name = df['competition_groups_name'].tolist()[0]
        group_id = df['competition_group_id'].tolist()[0]
        group_options = self.groups_df['name'].tolist()
        group_ids = self.groups_df['id'].tolist()
        
        #hc_index = df['hc_index'].tolist()[0]
        #if hc_index is not None: 
        con = st.container(horizontal=True, width='stretch', vertical_alignment='center')
        col1,col2,col3 = con.columns(width='stretch', vertical_alignment='center', spec=3)
        #with con_player:
        col1.text(body=df['name'].tolist()[0])
        st_hc_index = col2.number_input(label='Name', label_visibility='collapsed', value=hc_index, key=f'player_{name}_hc_index', )
        st_group = col3.selectbox(label='Team', label_visibility='collapsed', key=f'player_{name}_group', options=group_options, index=group_ids.index(group_id))
        if con.button(label='!', key=f'player_{name}_save'):
            group_id = self.groups_df[self.groups_df['name']==st_group]['id'].tolist()[0]
            self.update_participant(id=df['id'].tolist()[0], hc_index=st_hc_index, group_id=group_id)
        con.button(label='--', key=f'player_{name}_remove')
        
    def update_participant(self, id, hc_index, group_id):
        fields = ['hc_index', 'competition_group_id']
        values = [hc_index, group_id]
        self.participants_sql.update(id=id, fields=fields, values=values)
    
    #WIP
    def remove_participant(self):
        pass
    
    def add_groups(self, selection):
        fields = selection.columns.tolist()
        fields[fields.index('id')] = 'campaign_group_id'
        fields.append('competition_id')
        for entry in selection.to_numpy().tolist():
            entry.append(self.competition_df['id'].tolist()[0])
            self.groups_sql.add(fields=fields, values=entry)
    
    def remove_groups(self, id):
        self.groups_sql.delete(id=id)

    def add_participants(self, selection, group_id):
        fields = selection.columns.tolist()
        fields[fields.index('id')] = 'campaign_participant_id'
        fields.append('competition_id')
        fields.append('competition_group_id')
        for entry in selection.to_numpy().tolist():
            entry.append(self.competition_df['id'].tolist()[0])
            entry.append(group_id)
            self.participants_sql.add(fields=fields, values=entry)
        st.rerun()
    
    def remove_participants(self, selection):
        id_index = selection.columns.tolist().index('id')
        group_id_index = selection.columns.tolist().index('competition_group_id')
        for entry in selection.to_numpy().tolist():
            # Remove participant
            self.participants_sql.delete(entry[id_index])
            # Refresh participants
            self.participants_df = pd.DataFrame(self.participants_sql.read())
            # If no participants linked to assigned group, remove this group
            if entry[group_id_index] not in self.participants_df['competition_group_id'].tolist():
                self.remove_groups(id=entry[group_id_index])
        st.rerun()


class st_MatchInfo():
    sql = None
    match_df = None
    groups_df = None
    title = None
    players = None
    status = None
    
    def __init__(self, match_df=None):
        self.sql = sql.matches()
        self.df = match_df
        groups_sql = sql.match_groups()
        participants_sql = sql.match_participants()
        scoring_holes_sql = sql.scoring_holes()
        match_holes_sql = sql.match_holes()
        
        match_id = match_df['id'].tolist()[0]
        match_name = match_df['name'].tolist()[0]
        format_id = match_df['format_id'].tolist()[0]
        format_name = match_df['formats_name'].tolist()[0]
        value = match_df['value'].tolist()[0]
        tot_holes = match_df['holes'].tolist()[0]
        participants_df = participants_sql.read(filter=f"WHERE table.match_id={match_id}").sort_values(by=['match_groups_name', 'name'])
        groups_df = groups_sql.read(filter=f"WHERE table.match_id={match_id}").sort_values(by=['name'])
        self.groups_df = groups_df
        
        participants_ids = participants_df['id'].tolist()
        groups_ids = groups_df['id'].tolist()
        
        group_names = list()
        group_participant_names = list()
        group_points = list()
        #group_participant_ids = ','.join([str(x) for x in self.groups_df['match_id'].tolist()])
        for group_id in groups_ids:
            # Names
            group_names.append(groups_df.query(f'id=={group_id}')['name'].tolist()[0])
            group_participant_names.append(participants_df.query(f'match_group_id=={group_id}')['name'].tolist())
            
            # Points & Holes completed
            match_holes_df = match_holes_sql.read(filter=f"WHERE table.match_id={match_id} AND table.match_group_id={group_id}")
            if match_holes_df is not None:
                if not match_holes_df.empty:
                    points = sum(match_holes_df['points'].tolist())
                    group_points.append(points)
                    holes = len(match_holes_df['id'].tolist())
                else:
                    group_points.append(0)
                    holes = 0
            else:
                group_points.append(0)
                holes = 0
        
        if holes < tot_holes:
            hole_str = f'through {holes} of {tot_holes}'
        else: hole_str = ' - match complete' 
        if group_points[0] > group_points[1]:
            delta_value = f'**:green[{group_names[0]} up {group_points[0]-group_points[1]}]** :gray[{hole_str}]'
        elif group_points[1] > group_points[0]:
            delta_value = f'**:green[{group_names[1]} up {group_points[1]-group_points[0]}]** :gray[{hole_str}]'
        else: delta_value = f'**All Square** :gray[{hole_str}]'

        self.title = f':primary[**{match_name}** ({format_name})] {group_names[0]} :gray[vs] {group_names[1]} :blue[[{value}]]'
        self.players = f'{' / '.join(group_participant_names[0])} :gray[vs] {' / '.join(group_participant_names[1])}'
        self.status = delta_value
        
        #self.st_obj(match_df=match_df, title=title, players=players, status=status)
        return          
            
    def st_obj(self):
        con = st.container(border=True, gap=None)
        with con:
            st.markdown(body=f'{self.title}', )
            st.markdown(body=f':small[{self.players}]')
            st.markdown(body=f'_:small[{self.status}]_')
        return con
    
    @st.dialog(title='Delete confirmation')
    def delete(self):
        st.write("Are you sure you want to delete the entry?")
        area = st.container(horizontal=True, horizontal_alignment='center')
        with area:
            if st.button(label='Yes'):
                if self.df is not None:
                    self.sql.delete(id=self.df['id'].tolist()[0])
                    st.rerun()
            if st.button(label='No'):
                st.rerun() 


class CompetitionMatches():
    obj = None
    competition_df = None
    events_sql = None
    events_df = None
    matches_sql = None
    matches_df = None
    groups_sql = None
    groups_df = None
    participants_sql = None
    participants_df = None
    child_page = None

    def __init__(self, competition_df=None):
        self.competition_df = competition_df
        competition_id = self.competition_df['id'].tolist()[0]
        competition_name = self.competition_df['name'].tolist()[0]
        
        self.events_sql = sql.events()
        self.events_df = pd.DataFrame(self.events_sql.read(filter=f"WHERE table.competition_id={self.competition_df['id'].tolist()[0]}"))
        if not self.events_df.empty:
            self.events_df = self.events_df.sort_values(by=['sequence','name'])
            events_ids_str = ','.join(map(str, self.events_df['id'].tolist()))
        else: return
        
        self.matches_sql = sql.matches()
        self.matches_df = pd.DataFrame(self.matches_sql.read(filter=f"WHERE table.event_id IN ({events_ids_str})"))
        if not self.matches_df.empty: self.matches_df = self.matches_df.sort_values(by=['sequence','name'])
        else: return
        matches_ids_str = ','.join(map(str, self.matches_df['id'].tolist()))
        #print(self.matches_df)
        
        self.groups_sql = sql.match_groups()
        self.groups_df = pd.DataFrame(self.groups_sql.read(filter=f"WHERE table.match_id IN ({matches_ids_str})"))
        
        self.participants_sql = sql.match_participants()
        
        comp_groups_sql = sql.competition_groups()
        comp_groups_df = pd.DataFrame(comp_groups_sql.read(filter=f"WHERE table.competition_id={self.competition_df['id'].tolist()[0]}"))
        if not comp_groups_df.empty: comp_groups_df = comp_groups_df.sort_values(by='name')
        
        all_participants_sql = sql.competition_participants()
        all_participants_df = pd.DataFrame(all_participants_sql.read(filter=f"WHERE table.competition_id={self.competition_df['id'].tolist()[0]}"))
        if not all_participants_df.empty: all_participants_df = all_participants_df.sort_values(by='name')
    
        exp_matches = st.expander("Matches", expanded=False)
        with exp_matches:           
            if not self.matches_df.empty:
                # Show overview
                #print(self.groups_df)
                matches_overview_df = pd.DataFrame(columns=['comp_group_id', 'event_group_id', 'match_group_id', 'Group', 'Points'])
                event_group_ids = list(dict.fromkeys(self.groups_df['event_group_id'].tolist()))
                event_group_names = list(dict.fromkeys(self.groups_df['event_groups_name'].tolist()))
                group_points = list()
                for group_id in comp_groups_df['id'].tolist():
                    comp_event_group_df = pd.DataFrame(sql.event_groups().read(f"WHERE table.competition_group_id={group_id}"))
                    comp_event_group_ids = comp_event_group_df['id'].tolist()
                    comp_event_group_names = comp_event_group_df['name'].tolist()
                    points = 0
                    for event_group_id in event_group_ids:
                        if event_group_id in comp_event_group_ids:
                            points += self.groups_df.query(f"event_group_id=={event_group_id}")['value'].sum()
                    group_points.append(points)
                
                #print(f'comp_groups_ids = {comp_groups_df['id'].tolist()}')
                #print(f'event_group_names = {event_group_names}')
                #print(f'group_points = {group_points}')
                matches_overview_df['group_id'] = comp_groups_df['id'].tolist()
                matches_overview_df['Group'] = comp_groups_df['name'].tolist()
                matches_overview_df['Points'] = group_points
                matches_overview_df = matches_overview_df.sort_values(by='Group', ascending=True)
                
                column_config = {key: None for key in matches_overview_df.columns.to_list()}
                column_config['Group'] = st.column_config.TextColumn(label='Name', disabled=True)
                column_config['Points'] = st.column_config.NumberColumn(label='Points', disabled=True)
                st.data_editor(
                    key=f'competition_matches_overview_{competition_id}_{competition_name}',
                    data=matches_overview_df,
                    column_config=column_config,
                    hide_index=True
                    )
                
                # Show event matches
                for event_id in list(dict.fromkeys(self.matches_df['event_id'].tolist())):
                    event_name = self.events_df.query(f"id == {event_id}")['name'].tolist()[0]
                    exp_event = st.expander(label=event_name, expanded=False)
                    with exp_event:
                        # Show event overview
                        matches_overview_df = pd.DataFrame(columns=['group_id', 'Group', 'Points'])
                        event_match_ids = self.matches_df.query(f"event_id=={event_id}")['id'].tolist()
                        event_match_ids_str = ','.join(str(x) for x in event_match_ids)
                        if len(event_match_ids) > 1:
                            group_ids = list(dict.fromkeys(self.groups_df.query(f"match_id in ({event_match_ids_str})")['event_group_id'].tolist()))
                            group_names = list(dict.fromkeys(self.groups_df.query(f"match_id in ({event_match_ids_str})")['event_groups_name'].tolist()))
                        else:
                            group_ids = list(dict.fromkeys(self.groups_df.query(f"match_id == {event_match_ids_str}")['event_group_id'].tolist()))
                            group_names = list(dict.fromkeys(self.groups_df.query(f"match_id == {event_match_ids_str}")['event_groups_name'].tolist()))
                        group_points = list()
                        for group_id in group_ids:
                            group_points.append(self.groups_df.query(f"event_group_id=={group_id}")['value'].sum())
                        
                        matches_overview_df['group_id'] = group_ids
                        matches_overview_df['Group'] = group_names
                        matches_overview_df['Points'] = group_points
                        matches_overview_df = matches_overview_df.sort_values(by='Group', ascending=True)
                        
                        column_config = {key: None for key in matches_overview_df.columns.to_list()}
                        column_config['Group'] = st.column_config.TextColumn(label='Name', disabled=True)
                        column_config['Points'] = st.column_config.NumberColumn(label='Points', disabled=True)
                        st.data_editor(
                            key=f'competition_event_matches_overview_{competition_id}_{competition_name}_{event_id}_{event_name}',
                            data=matches_overview_df,
                            column_config=column_config,
                            hide_index=True
                            )
                        
                        # Show matches
                        for match_id in self.matches_df.query(f"event_id == {event_id}")['id'].tolist():
                                match_df = self.matches_df.query(f"id == {match_id}")
                                match = st_MatchInfo(match_df=match_df)
                                match.st_obj()


class Individuals():
    obj = None
    competition_df = None
    competition_participant_sql = None
    competition_participant_df = None
    events_sql = None
    events_df = None
    event_participants_sql = None
    event_participants_df = None
    scoring_cards_sql = None
    scoring_cards_df = None
    scoring_card_participants_sql = None
    scoring_card_participants_df = None
    scoring_rounds_sql = None
    scoring_rounds_df = None
    scoring_holes_sql = None
    scoring_holes_df = None
    child_page = None
    
    def __init__(self, competition_df=None):
        self.competition_df = competition_df
        competition_id = competition_df['id'].tolist()[0]
        
        # Competition participants
        self.competition_participants_sql = sql.competition_participants()
        self.competition_participants_df = pd.DataFrame(self.competition_participants_sql.read(filter=f"WHERE table.competition_id={competition_id}"))
        if not self.competition_participants_df.empty: self.competition_participants_df = self.competition_participants_df.sort_values(by=['competition_groups_name','name'])
        
        # Events
        self.events_sql = sql.events()
        self.events_df = pd.DataFrame(self.events_sql.read(filter=f"WHERE table.competition_id={competition_id}"))
        if not self.events_df.empty: self.events_df = self.events_df.sort_values(by=['sequence', 'name'])
        else: return
        events_ids = ','.join([str(x) for x in list(dict.fromkeys(self.events_df['id'].tolist()))])
        
        # Event participants
        self.event_participants_sql = sql.event_participants()
        self.event_participants_df = pd.DataFrame(self.event_participants_sql.read(filter=f"WHERE table.event_id IN ({events_ids})"))
        if not self.event_participants_df.empty: self.event_participants_df = self.event_participants_df.sort_values(by=['event_groups_name','name'])
        else: return
        
        # Scoring cards
        self.scoring_cards_sql = sql.scoring_cards()
        self.scoring_cards_df = pd.DataFrame(self.scoring_cards_sql.read(filter=f"WHERE table.event_id IN ({events_ids})"))
        if not self.scoring_cards_df.empty: self.scoring_cards_df = self.scoring_cards_df.sort_values(by=['sequence', 'name'])
        else: return
        scoring_cards_ids = ','.join([str(x) for x in list(dict.fromkeys(self.scoring_cards_df['id'].tolist()))])        
        
        # Scoring card participants
        self.scoring_card_participants_sql = sql.scoring_card_participants()
        self.scoring_card_participants_df = pd.DataFrame(self.scoring_card_participants_sql.read(filter=f"WHERE table.scoring_card_id IN ({scoring_cards_ids})"))
        if not self.scoring_card_participants_df.empty: self.scoring_card_participants_df = self.scoring_card_participants_df.sort_values(by=['scoring_card_groups_name','name'])
        else: return
        scoring_card_participants_ids = ','.join([str(x) for x in list(dict.fromkeys(self.scoring_card_participants_df['id'].tolist()))])
        
        # Scoring rounds
        self.scoring_rounds_sql = sql.scoring_rounds()
        self.scoring_rounds_df = pd.DataFrame(self.scoring_rounds_sql.read(filter=f"WHERE table.scoring_card_participant_id IN ({scoring_card_participants_ids})"))
        if self.scoring_rounds_df.empty: return
        scoring_rounds_ids = ','.join([str(x) for x in list(dict.fromkeys(self.scoring_rounds_df['id'].tolist()))])
        
        # Scoring holes
        self.scoring_holes_sql = sql.scoring_holes()
        self.scoring_holes_df = pd.DataFrame(self.scoring_holes_sql.read(filter=f"WHERE table.scoring_round_id IN ({scoring_rounds_ids})"))
        if self.scoring_holes_df.empty: return
        
        # Course tees
        course_tees_sql = sql.course_tees()
        
        
        # Calculate participant info
        board_df = pd.DataFrame(columns=['Rank', 'Participant ID', 'Name', 'Shots', 'Points', 'round_id', 'pts_list', 'rank', 'Hole'])
        for competition_participant_id in self.competition_participants_df['id'].tolist():
            competition_participant_name = self.competition_participants_df.query(f"id == {competition_participant_id}")['name'].tolist()[0]
            event_participant_df = self.event_participants_df.query(f"competition_participant_id == {competition_participant_id}")
            event_participant_ids = event_participant_df['id'].tolist()
            if not event_participant_df.empty:
                scoring_card_participant_df = self.scoring_card_participants_df.query(f"event_participant_id in @event_participant_ids")
                if not scoring_card_participant_df.empty:
                    scoring_card_participant_ids = scoring_card_participant_df['id'].tolist()
                    rounds_df = self.scoring_rounds_df.query(f"scoring_card_participant_id in @scoring_card_participant_ids")
                    if not rounds_df.empty:
                        round_ids = rounds_df['id'].tolist()
                        holes_df = self.scoring_holes_df.query(f"scoring_round_id in @round_ids")
                                                          
                        if not holes_df.empty:
                            shots = holes_df['shots'].sum()
                            points = holes_df['points'].sum()
                            hole = holes_df['points'].count()
                            board_df.loc[competition_participant_id] = [
                                0,
                                competition_participant_id,
                                competition_participant_name,
                                shots,
                                points,
                                None,
                                None,
                                0,
                                hole]
        all_stroke_points = []
        for competition_participant_id in self.competition_participants_df['id'].tolist():
            competition_participant_name = self.competition_participants_df.query(f"id == {competition_participant_id}")['name'].tolist()[0]
            event_participant_df = self.event_participants_df.query(f"competition_participant_id == {competition_participant_id}")
            event_participant_ids = event_participant_df['id'].tolist()
            #print(f'Participant: {competition_participant_name}')
            if not event_participant_df.empty:        
                scoring_card_participant_df = self.scoring_card_participants_df.query(f"event_participant_id in @event_participant_ids")
                if not scoring_card_participant_df.empty:
                    scoring_card_participant_ids = scoring_card_participant_df['id'].tolist()
                    rounds_df = self.scoring_rounds_df.query(f"scoring_card_participant_id in @scoring_card_participant_ids")
                #print(f'Round IDs: {rounds_df['id'].tolist()}')
                stroke_holes = []

                for round_id in rounds_df['id'].tolist():
                    round_df = rounds_df.query(f"id == {round_id}")
                    course_tee_id = round_df['course_tee_id'].tolist()[0]
                    course_tee_df = pd.DataFrame(course_tees_sql.read(filter=f"WHERE table.id={course_tee_id}"))
                    #course_tee_df = self.course_tees_df.query(f"id == {course_tee_id}")
                    strokes_df = course_tee_df.filter(regex='stroke$', axis=1)
                    strokes_df.columns = range(1,19)
                    index = strokes_df.index.tolist()[0]

                    strokes_df = strokes_df.transpose().sort_values(by=[index])
                    strokes_df.columns = [index]
                    strokes_df = strokes_df.transpose()
                    stroke_holes.append(strokes_df.columns.tolist())            
                
                #print(f'Stroke Holes: {stroke_holes}')
                        
                stroke_points = []
                #if rounds_df.empty:
                #    stroke_points.append([0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0])
                for index, round_id in enumerate(rounds_df['id'].tolist()):
                    round_df = rounds_df.query(f"id == {round_id}")
                    holes_df = self.scoring_holes_df.query(f"scoring_round_id == {round_id}")
                    points = []
                    cntr = 0
                    for hole in stroke_holes[index]:
                        points_df = holes_df.query(f"number == {hole}")
                        if not points_df.empty:
                            points.append(points_df['points'].tolist()[0])
                        else: points.append(None)
                    stroke_points.append(points)
                #print(f'Stroke Points: {stroke_points}')
                #print(f'Stroke Points: {stroke_points}')    
                stroke_points_t = [list(i) for i in zip(*stroke_points)]
                #print(f'Stroke Points T: {stroke_points_t}')
                for index, points in enumerate(stroke_points_t):
                    stroke_points_t[index] = sum(points)
                #print(f'Stroke Points Summed: {stroke_points_t}')
                all_stroke_points.append(stroke_points_t)
                #print(stroke_points_t)
        
        
        all_stroke_points = [x for x in all_stroke_points if x != []]
        #print(f'All Stroke Points:\n{all_stroke_points}')
        all_stroke_points = [list(row) for row in zip(*all_stroke_points)]
        #print(f'All Stroke Points:\n{all_stroke_points}')
        for hole in range(0,len(all_stroke_points)):
            board_df[f'S{hole+1}p'] = all_stroke_points[hole]

        filter_str = ['Points']
        for hole in range(1,19):
            filter_str.append(f'S{hole}p')
            #print(filter_str)
        #board_df = board_df.sort_values(by=filter_str, ascending=False)                
        #board_df['Rank'] = pd.Series(board_df['Points']).rank(method='min', ascending=False).astype(int).tolist()

        #print(filter_str)
        #print(board_df)    
        board_df = board_df.sort_values(by=filter_str, ascending=False)
        board_df['Rank'] = pd.Series(board_df['Points']).rank(method='min', ascending=False).astype(int).tolist()
        #board_df['Rank'] = range(1,board_df['Participant ID'].count()+1)
        #for participant_id in board_df['id'].tolist():
            
        #column_config['rank'] = st.column_config.NumberColumn(format="%d", disabled=True)
        exp = st.expander(label='Individual Leaderboard')
        with exp:
            header_con = st.container(horizontal=True, width='stretch')
            st_extended = header_con.toggle(label='Extended', key='event_card_extended_toggle', width='content')
            
            # Show winner if rounds completed
            rounds_completed = True
            #print(self.scoring_rounds_df)
            for active in self.scoring_rounds_df['active'].tolist():
                if active is True or active == 1: rounds_completed = False
            
            if rounds_completed:
                #print(board_df)
                winning_points = board_df['Points'].max()
                winners_df = board_df.query(f"Points == {winning_points}")
                winner_found = False
                if len(winners_df['Points'].tolist()) == 1:
                    winner_name = winners_df['Name'].tolist()[0]
                    winner_points = winners_df['Points'].tolist()[0]
                    winner_txt = f'{winner_name} wins with {winner_points} points'
                    countout_txt = ''
                else: # Calculate count out info if tied winners
                    points_lists = winners_df['pts_list'].tolist()
                    print(points_lists)
                    for hole in []:#range(0,18):
                        hole_pts_list = []                                        
                        max_pts = -1
                        for pts in points_lists:
                            points = pts[hole]
                            hole_pts_list.append(points)
                            if points > max_pts: max_pts = points
                        
                        count = 0
                        max_index = 0
                        for index, pts in enumerate(points_lists):
                            points = pts[hole]
                            if points == max_pts:
                                count += 1
                                max_index = index
                                
                        
                        if count == 1:
                            winner_found = True
                            winner_id = winners_df['Participant ID'].tolist()[max_index]
                            winner_name = winners_df['Name'].tolist()[max_index]
                            winner_points = winners_df['Points'].tolist()[max_index]
                            board_df.loc[board_df['Participant ID']==winner_id, 'rank'] = 1
                            board_df = board_df.sort_values(by=['rank', 'Points'], ascending=False)
                            countout_txt = f' - count out on stroke hole {hole+1} with {max_pts} points'
                            break    
                        
                #winner_txt = f'{winner_name} wins with a total of {winner_points} points {countout_txt}'
                #st.text(body=winner_txt)
            
            column_config = {key: None for key in board_df.columns.to_list()}
            column_config['Rank'] = st.column_config.NumberColumn(format="%d", disabled=True)
            column_config['Name'] = st.column_config.TextColumn(disabled=True)
            #column_config['Shots'] = st.column_config.NumberColumn(format="%d", disabled=True)
            column_config['Points'] = st.column_config.NumberColumn(format="%d", disabled=True)
            if not rounds_completed:
                column_config['Hole'] = st.column_config.NumberColumn(format="%d", disabled=True)
            if st_extended:
                #print('Showing extended info')
                for hole in range(1,19):
                    column_config[f'S{hole}p'] = st.column_config.NumberColumn(label=f'S{hole}', format="%d", disabled=True)
                    
            st.dataframe(key='individuals_competition_data',
                        data=board_df,
                        hide_index=True,
                        column_config=column_config,
                        )


class Eclectic():
     individuals = None
     
     def __init__(self, individuals):
        self.individuals = individuals

        if self.individuals.scoring_holes_df is None: return
        elif self.individuals.scoring_holes_df.empty: return
        
        # Calculate participant info
        board_df = pd.DataFrame(columns=['Rank', 'Participant ID', 'Name', 'Points', 'scoring_hole_ids', 'pts_list', 'rank', '1', '2', '3', '4', '5', '6', '7', '8', '9', '10', '11', '12', '13', '14', '15', '16', '17', '18'])
        for competition_participant_id in self.individuals.competition_participants_df['id'].tolist():
            competition_participant_name = self.individuals.competition_participants_df.query(f"id == {competition_participant_id}")['name'].tolist()[0]
            event_participant_df = self.individuals.event_participants_df.query(f"competition_participant_id == {competition_participant_id}")
            event_participant_ids = event_participant_df['id'].tolist()
            
            board_df_detail_cols = [0,
                                        competition_participant_id,
                                        competition_participant_name,
                                        0, None, 0, 0
            ]
            if not event_participant_df.empty:                
                scoring_card_participant_df = self.individuals.scoring_card_participants_df.query(f"event_participant_id in @event_participant_ids")
                if not scoring_card_participant_df.empty:
                    scoring_card_participant_ids = scoring_card_participant_df['id'].tolist()
                    rounds_df = self.individuals.scoring_rounds_df.query(f"scoring_card_participant_id in @scoring_card_participant_ids")
                    if not rounds_df.empty:
                        round_ids = rounds_df['id'].tolist()
                        holes_df = self.individuals.scoring_holes_df.query(f"scoring_round_id in @round_ids")                                                                 
                        if not holes_df.empty: 
                            board_df_hole_cols = list()                           
                            for hole in range(1,19):
                                holes_pts = holes_df.query(f"number == {hole}")['points']
                                if not holes_pts.empty:
                                    board_df_hole_cols.append(max(holes_pts))
                                else: board_df_hole_cols.append(0)
                        else:
                            board_df_hole_cols = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
                    else:
                        board_df_hole_cols = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
                else:
                    board_df_hole_cols = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
            else:
                board_df_hole_cols = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
            
            board_df_detail_cols[3] = sum(board_df_hole_cols)
            board_df_row = board_df_detail_cols + board_df_hole_cols
            board_df.loc[competition_participant_id] = board_df_row
                        
        board_df = board_df.sort_values(by=['Points'], ascending=False)
        board_df['Rank'] = pd.Series(board_df['Points']).rank(method='min', ascending=False).astype(int).tolist()   
        
        def df_holes_format(v, props=''):
            if v == 0:
                return 'background-color:darkyellow;'
            elif v == 1:
                return 'background-color:lightyellow;'
            elif v == 2:
                return 'background-color:black;'
            elif v == 3:
                return 'background-color:lightgreen;'
            else:
                return 'background-color:green;'
        #    styler.background_gradient(axis=None, vmin=0, vmax=6, cmap='BuYlGn')
        #    return styler
        
        hole_cols = [str(x) for x in range(1,19)]
        board_df = board_df.style.background_gradient(axis=0, subset=hole_cols, vmin=-1, vmax=5, cmap='RdYlGn').set_properties(**{'text-align': 'center', 'font-size': '50px'})#.set_properties(**{'font-size': '20px'})
        
        #board_df = board_df.style.map(df_holes_format, props='', subset=['1', '2'])
        #print(board_df.iloc[:,7:])
        #styler = pd.io.formats.style.Styler(df=board_df.iloc[:,7:], formatter=
        #board_df.loc['1':'18'] = board_df.loc['1':'18'].style.pipe(df_holes_format)
        exp = st.expander(label='Eclectic')
        with exp:
            column_config = {key: None for key in board_df.columns.to_list()}
            column_config['Rank'] = st.column_config.NumberColumn(label='#', format='%d', disabled=True, width=25)
            column_config['Name'] = st.column_config.TextColumn(disabled=True)
            column_config['Points'] = st.column_config.NumberColumn(label='Pts', format='%d', disabled=True, width=40)
            for hole in range(1,19):
                column_config[f'{hole}'] = st.column_config.NumberColumn(format="%d", disabled=True, width=25)
            st.dataframe(key='eclectic_competition_data',
                        data=board_df,
                        hide_index=True,
                        column_config=column_config,
                        )


# Populate page 
con = st.container(horizontal=True, vertical_alignment='center')

st_details = CompetitionDetails(df=st.session_state.competition)

st_events = CompetitionEvents(competition_df=st.session_state.competition)

st_individuals = Individuals(competition_df=st.session_state.competition) 

st_matches = CompetitionMatches(competition_df=st.session_state.competition)

st_eclectic = Eclectic(st_individuals)
st_groups_participants = CompetitionGroupParticipants(competition_df=st.session_state.competition)

with con:
    if st.button(label='', icon=':material/arrow_back:'):
        st.session_state.competition = None
        st.session_state.page = st_details.parent_page
        st.rerun()
    st.subheader(f"Competitions: {st.session_state.competition['name'].tolist()[0]}")
