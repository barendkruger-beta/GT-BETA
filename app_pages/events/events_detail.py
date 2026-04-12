import streamlit as st
import pandas as pd
import sql

class st_MatchInfo():
    sql = None
    match_df = None
    groups_df = None
    title = None
    players = None
    status = None
    
    def __init__(self, match_df=None):
        self.sql = sql.matches()
        self.match_df = match_df
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
 

class EventDetails():
    obj = None
    df = None
    parent_page = None
           
    def __init__(self, df=None):
        self.obj = st.expander(label='Details')
        self.df = df
        df_id = df['id'].tolist()[0]
        self.parent_page = "app_pages/competitions/competitions_detail.py"
        if self.df is not None:
            with self.obj:
                st_name = st.text_input('Name', key=f'event_details_{df_id}_name', value=f'{self.df['name'].tolist()[0]}')
                st_description = st.text_area('Description', key=f'event_details_{df_id}_description', value=f'{self.df['description'].tolist()[0]}')
                st_active = st.toggle(label='Active', value=df['active'].tolist()[0], key=f'event_details_{df_id}_active')
                buttons_area = st.container(horizontal=True)
                with buttons_area:
                    if st.session_state.global_admin:
                        if st.button(label='', icon=':material/check:', key='event_details_update'):
                            self.update(name=st_name, description=st_description, active=st_active)
                        if st.button(label='', icon=':material/delete:', key='event_details_delete'):
                            self.delete()                        
        
    def update(self, name=None, description=None, active=None):
        if self.df is not None:
            sql_event = sql.events()
            fields = ['name', 'description', 'active']
            values = [name, description, active]
            sql_event.update(id=self.df['id'].tolist()[0], fields=fields, values=values)
            st.session_state.event = sql_event.read(filter=f"WHERE table.id={self.df['id'].tolist()[0]}")
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


class EventScoringCards():
    obj = None
    event_df = None
    scoring_cards_sql = None
    scoring_cards_df = None
    groups_sql = None
    groups_df = None
    participants_sql = None
    participants_df = None
    child_page = None 
    date = None
    
    def __init__(self, event_df=None):
        self.child_page = "app_pages/scoring_cards/scoring_cards_detail.py"
        
        self.event_df = event_df
        self.scoring_cards_sql = sql.scoring_cards()
        self.scoring_cards_df = pd.DataFrame(self.scoring_cards_sql.read(filter=f"WHERE table.event_id={self.event_df['id'].tolist()[0]}"))
        if not self.scoring_cards_df.empty: self.scoring_cards_df = self.scoring_cards_df.sort_values(by=['sequence','name'])
        
        self.groups_sql = sql.scoring_card_groups()        
        self.participants_sql = sql.scoring_card_participants()
        
        all_groups_sql = sql.event_groups()
        all_groups_df = pd.DataFrame(all_groups_sql.read(filter=f"WHERE table.event_id={self.event_df['id'].tolist()[0]}"))
        if not all_groups_df.empty: all_groups_df = all_groups_df.sort_values(by='name')
        else: return
        
        all_participants_sql = sql.event_participants()
        all_participants_df = pd.DataFrame(all_participants_sql.read(filter=f"WHERE table.event_id={self.event_df['id'].tolist()[0]}"))
        if not all_participants_df.empty: all_participants_df = all_participants_df.sort_values(by='name')
        else: return
        
        exp_scoring_cards = st.expander("Scoring Cards", expanded=True)
        with exp_scoring_cards:
            col = st.container(horizontal=True, width='stretch')
            
            scoring_card_df = self.scoring_cards_df
            if not scoring_card_df.empty:
                participants_info = []
                for scoring_card_id in scoring_card_df['id'].tolist():
                    groups_df = self.groups_sql.read(filter=f"WHERE table.scoring_card_id={scoring_card_id}").sort_values(by='name')
                    info = str()
                    for group_name, group_id in zip(groups_df['name'].tolist(), groups_df['id'].tolist()):                    
                        participants_df = self.participants_sql.read(filter=f"WHERE table.scoring_card_id={scoring_card_id} AND table.scoring_card_group_id={group_id}").sort_values(by='name')
                        info+=f"{group_name}[{", ".join(participants_df['name'].tolist())}] "
                    participants_info.append(info)
                scoring_card_df['participants'] = participants_info
                    
            column_config = {key: None for key in self.scoring_cards_df.columns.to_list()}
            column_config['name'] = 'Name'
            #column_config['description'] = 'Description'
            column_config['participants'] = 'Participants'
            #column_config['event_participants_name'] = 'Scorer'            
            scoring_card = st.dataframe(
                self.scoring_cards_df,
                on_select='rerun',
                selection_mode=['single-row', 'single-cell'],
                hide_index=True,
                column_config=column_config
            )

            event_id = self.event_df['id'].tolist()[0]
            id = None
            if len(scoring_card.selection['rows']):
                id = self.scoring_cards_df.iloc[scoring_card.selection['rows'][0]]['id']
            elif len(scoring_card.selection['cells']):
                id = self.scoring_cards_df.iloc[scoring_card.selection['cells'][0][0]]['id']
            if id is not None:
                sel = self.scoring_cards_df[self.scoring_cards_df['id'] == id]
                col.button(label='', icon=':material/add_2:', key=f"event[{event_id}]_add_scoring_card", disabled=True)
                if col.button(label='', icon=':material/book_4:', key=f"event[{event_id}]_open_scoring_card"): self.open(sel, self.child_page)
                if col.button(label='', icon=':material/edit:', key=f"event[{event_id}]_edit_scoring_card", disabled=not st.session_state.global_admin): self.edit(scoring_card_df=sel, all_groups_df=all_groups_df, all_participants_df=all_participants_df)
                if col.button(label='', icon=':material/arrow_upward:', disabled=not st.session_state.global_admin): self.move(sel=sel, up=True)
                if col.button(label='', icon=':material/arrow_downward:', disabled=not st.session_state.global_admin): self.move(sel=sel, down=True)
                if col.button(label='', icon=':material/delete:', key=f"event[{event_id}]_remove_scoring_card", disabled=not st.session_state.global_admin): self.remove(scoring_card_df=sel)
            else:
                if col.button(label='', icon=':material/add_2:', key=f"event[{event_id}]_add_scoring_card"): self.add(event_id=event_id, all_groups_df=all_groups_df, all_participants_df=all_participants_df)
                col.button(label='', icon=':material/book_4:', key=f"event[{event_id}]_open_scoring_card", disabled=True)
                col.button(label='', icon=':material/edit:', key=f"event[{event_id}]_edit_scoring_card", disabled=True)
                col.button(label='', icon=':material/arrow_upward:', disabled=True)
                col.button(label='', icon=':material/arrow_downward:', disabled=True)
                col.button(label='', icon=':material/delete:', key=f"event[{event_id}]_remove_scoring_card", disabled=True)
            
    def update_date(self):
            self.df_date = str(st.session_state.event_sc_date)
            
    # Add dialog
    @st.dialog("Add Scoring Card")
    def add(self, event_id=None, all_groups_df=None, all_participants_df=None):
        courses_df = sql.courses().read()
        
        st_name = st.text_input("Name")
        st_description = st.text_input("Description")
        st_date = st.date_input('Date', format='YYYY-MM-DD', value='today', on_change=self.update_date, key='event_sc_date')
        st_course = st.selectbox("Course", options=courses_df['name'].tolist(), index=None)
        st_participants = st.multiselect("Participants", all_participants_df['name'].tolist())
        st_scorer = st.selectbox("Scorer", options=all_participants_df['name'].tolist(), index=None)
        
        if st.button("Submit"):
            if st_participants is not None:
                event_participants_sel = all_participants_df.query(f"name in {st_participants}")
                print(f"Selected participants = {event_participants_sel['name'].tolist()}")

            if st_course is not None and st_participants is not None and st_scorer is not None:
                # Get sequence number
                if not self.scoring_cards_df.empty:
                    sequence = self.scoring_cards_df['sequence'].max() + 1
                else: sequence = 1

                # Prepare sql query parameters
                event_course_id = courses_df[courses_df['name']==st_course]['id'].tolist()[0]
                event_scorer_id = all_participants_df[all_participants_df['name']==st_scorer]['id'].tolist()[0]
                fields = ["name", "description", "event_id", "event_participant_id", "course_id", "sequence", "date"]
                values = [st_name, st_description, event_id, event_scorer_id, event_course_id, sequence, f"'{st.session_state.event_sc_date}'"]
                
                # Create scoring card
                scoring_card_id = self.scoring_cards_sql.add(fields=fields, values=values)
                self.scoring_cards_df = pd.DataFrame(self.scoring_cards_sql.read(filter=f"WHERE table.event_id={self.event_df['id'].tolist()[0]}"))
                
                # Create scoring card groups
                self.add_groups(scoring_card_id=scoring_card_id, participants=st_participants, all_groups_df=all_groups_df, all_participants_df=all_participants_df)
                
                # Create scoring card participants
                self.add_participants(scoring_card_id=scoring_card_id, participants=st_participants, all_participants_df=all_participants_df)
                
            st.rerun()
        
    # Open detail page            
    def open(self, sel, page):
        st.session_state.scoring_card = sel
        
        st.session_state.page = page    
        st.rerun()

    # Edit dialog
    @st.dialog("Edit Scoring Card")
    def edit(self, scoring_card_df, all_groups_df=None, all_participants_df=None):
        scoring_card_id = scoring_card_df['id'].tolist()[0]
        #print(f"scoring_card ID = {scoring_card_id}")
        scoring_card_groups_df = pd.DataFrame(self.groups_sql.read(filter=f"WHERE table.scoring_card_id={scoring_card_id}"))
        scoring_card_participants_df = pd.DataFrame(self.participants_sql.read(filter=f"WHERE table.scoring_card_id={scoring_card_id}"))
        scorer_id = scoring_card_df['event_participant_id'].tolist()[0]
        course_id = scoring_card_df['course_id'].tolist()[0]
        
        courses_df = sql.courses().read()

        #print(f"scoring_card groups = {scoring_card_groups_df['name'].tolist()}")
        #print(f"scoring_card participants = {scoring_card_participants_df['name'].tolist()}")
        
        #print(f"scoring_card DF = {scoring_card_df.columns.to_list()}")
        st_name = st.text_input("Name", value=scoring_card_df['name'].tolist()[0])
        st_description = st.text_input("Description", value=scoring_card_df['description'].tolist()[0])
        st_date = st.date_input('Date', format='YYYY-MM-DD', value=scoring_card_df['date'].tolist()[0], on_change=self.update_date, key='event_sc_date')
        st_course = st.selectbox("Course", options=courses_df['name'].tolist(), index=courses_df['id'].tolist().index(course_id))
        st_participants = st.multiselect("Participants", all_participants_df['name'].tolist(), default=scoring_card_participants_df['name'].tolist())
        st_scorer = st.selectbox("Scorer", options=all_participants_df['name'].tolist(), index=all_participants_df['id'].tolist().index(scorer_id))
        
        if st.button("Submit"):
            if st_course is not None and st_participants is not None and st_scorer is not None and st.session_state.event_sc_date is not None:
                course_id = courses_df[courses_df['name']==st_course]['id'].tolist()[0]
                scorer_id = all_participants_df[all_participants_df['name']==st_scorer]['id'].tolist()[0]
                fields = ["name", "description", "event_participant_id", "course_id", "date"]
                values = [st_name, st_description, scorer_id, course_id, f"'{st.session_state.event_sc_date}'"]
                self.scoring_cards_sql.update(id=scoring_card_id, fields=fields, values=values)
                           
                # Update groups to be added
                self.add_groups(scoring_card_id=scoring_card_id, participants=st_participants, all_groups_df=all_groups_df, all_participants_df=all_participants_df)
                
                # Update participants to be added
                self.add_participants(scoring_card_id=scoring_card_id, participants=st_participants, all_participants_df=all_participants_df)
                        
                # Identify and update participants to be removed
                scoring_card_participants_df = pd.DataFrame(self.participants_sql.read(filter=f"WHERE table.scoring_card_id={scoring_card_id}"))
                if not scoring_card_participants_df.empty:
                    for participant in scoring_card_participants_df['name'].tolist():
                        if participant not in st_participants:
                            participant_id = scoring_card_participants_df[scoring_card_participants_df['name']==participant]['id'].tolist()[0]
                            self.participants_sql.delete(id=participant_id)
                            continue
                
                # Identify and update groups to be removed
                scoring_card_groups_df = pd.DataFrame(self.groups_sql.read(filter=f"WHERE table.scoring_card_id={scoring_card_id}"))
                scoring_card_participants_df = pd.DataFrame(self.participants_sql.read(filter=f"WHERE table.scoring_card_id={scoring_card_id}"))
                if not scoring_card_groups_df.empty:
                    for group_id in scoring_card_groups_df['id'].tolist():
                        if scoring_card_participants_df.empty:
                            self.groups_sql.delete(id=group_id)
                            continue
                        
                        if group_id not in scoring_card_participants_df['scoring_card_group_id'].tolist():
                            self.groups_sql.delete(id=group_id)
                            continue               
            
            st.rerun()

    # Remove function
    @st.dialog("Delete Scoring Card")
    def remove(self, scoring_card_df=None):
        st.text('Are you sure you want to delete the score card?\nThis wall delete all scored holes and matches')
        if st.button('Yes'):
            self.scoring_cards_sql.delete(id=scoring_card_df['id'].tolist()[0])
            st.rerun()
        if st.button('No'):
            st.rerun()
    
    # Move item up or down
    def move(self, sel, up=None, down=None):
        df_sql = sql.scoring_cards()
        df = self.scoring_cards_df
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
          
    def add_groups(self, scoring_card_id=None, participants=None, all_groups_df=None, all_participants_df=None):
        # Create scoring card groups if it does not exist yet
        for participant_name in participants:              
            event_group_id = all_participants_df.query(f"name == '{participant_name}'")['event_group_id'].tolist()[0]
            event_group_name = all_groups_df.query(f"id == {event_group_id}")['name'].tolist()[0]
            event_group_description = all_groups_df.query(f"id == {event_group_id}")['description'].tolist()[0]
            
            scoring_card_groups_df = pd.DataFrame(self.groups_sql.read(filter=f"WHERE table.scoring_card_id={scoring_card_id}"))
            
            if scoring_card_groups_df.empty:
                #print(f"No groups for scoring card, creating group for {participant_name}")
                fields = ["name", "description", "scoring_card_id", "event_group_id"]
                values = [event_group_name, event_group_description, scoring_card_id, event_group_id]
                self.groups_sql.add(fields=fields, values=values)  
                continue
                        
            if not scoring_card_groups_df.empty:
                if event_group_id not in scoring_card_groups_df['event_group_id'].tolist():
                    #print(f"Group for {participant_name} does not exist, creating group")
                    fields = ["name", "description", "scoring_card_id", "event_group_id"]
                    values = [event_group_name, event_group_description, scoring_card_id, event_group_id]
                    self.groups_sql.add(fields=fields, values=values)  
                    continue
    
    def add_participants(self, scoring_card_id=None, participants=None, all_participants_df=None):
        # Create scoring card participants
        for participant_name in participants:
            event_group_id = all_participants_df.query(f"name == '{participant_name}'")['event_group_id'].tolist()[0]
            scoring_card_groups_df = pd.DataFrame(self.groups_sql.read(filter=f"WHERE table.scoring_card_id={scoring_card_id}"))
            scoring_card_group_id = scoring_card_groups_df.query(f"scoring_card_id == {scoring_card_id} & event_group_id == {event_group_id}")['id'].tolist()[0]
            event_participant_id = all_participants_df.query(f"name == '{participant_name}'")['id'].tolist()[0]
            event_participant_name = all_participants_df.query(f"name == '{participant_name}'")['name'].tolist()[0]
            event_participant_description = all_participants_df.query(f"name == '{participant_name}'")['description'].tolist()[0]
            
            scoring_card_participants_df = pd.DataFrame(self.participants_sql.read(filter=f"WHERE table.scoring_card_id={scoring_card_id}"))
            
            if scoring_card_participants_df.empty:
                #print(f"No participants for scoring card, creating participant for {participant_name}")
                fields = ["name", "description", "scoring_card_id", "scoring_card_group_id", "event_participant_id"]
                values = [event_participant_name, event_participant_description, scoring_card_id, scoring_card_group_id, event_participant_id]
                self.participants_sql.add(fields=fields, values=values) 
                continue
                
            if not scoring_card_participants_df.empty:
                if event_participant_id not in scoring_card_participants_df['event_participant_id'].tolist():
                    #print(f"Participant for {participant_name} does not exist, creating participant")
                    fields = ["name", "description", "scoring_card_id", "scoring_card_group_id", "event_participant_id"]
                    values = [event_participant_name, event_participant_description, scoring_card_id, scoring_card_group_id, event_participant_id]
                    self.participants_sql.add(fields=fields, values=values) 
                    continue


class EventMatches():
    obj = None
    event_df = None
    matches_sql = None
    matches_df = None
    groups_sql = None
    groups_df = None
    participants_sql = None
    participants_df = None
    child_page = None

    def __init__(self, event_df=None):
        self.event_df = event_df
        self.matches_sql = sql.matches()
        self.matches_df = pd.DataFrame(self.matches_sql.read(filter=f"WHERE table.event_id={self.event_df['id'].tolist()[0]}"))
        if not self.matches_df.empty:
            self.matches_df = self.matches_df.sort_values(by=['sequence','name'])
            matches_ids_str = ','.join(map(str, self.matches_df['id'].tolist()))
        else:
            matches_ids_str = ''
            
        self.groups_sql = sql.match_groups()
        self.groups_df = pd.DataFrame(self.groups_sql.read(filter=f"WHERE table.match_id IN ({matches_ids_str})"))
        if not self.groups_df.empty: self.groups_df = self.groups_df.sort_values(by=['name'])
        self.participants_sql = sql.match_participants()
        
        all_groups_sql = sql.event_groups()
        all_groups_df = pd.DataFrame(all_groups_sql.read(filter=f"WHERE table.event_id={self.event_df['id'].tolist()[0]}"))
        if not all_groups_df.empty: all_groups_df = all_groups_df.sort_values(by='name')
        else: return
        
        all_participants_sql = sql.event_participants()
        all_participants_df = pd.DataFrame(all_participants_sql.read(filter=f"WHERE table.event_id={self.event_df['id'].tolist()[0]}"))
        if not all_participants_df.empty: all_participants_df = all_participants_df.sort_values(by='name')
        else: return
        
        exp_matches = st.expander("Matches", expanded=False)
        with exp_matches:
            col = st.container(horizontal=True, width='stretch')
            with col:
                if st.button(label='', icon=':material/add_2:', key="add_match", disabled=not st.session_state.global_admin): self.add(event_id=self.event_df['id'].tolist()[0],
                                                               all_groups_df=all_groups_df,
                                                               all_participants_df=all_participants_df)
                #if st.button(label="Refresh", key='event_matches_refresh_button'): st.rerun()
                    
            matches_df = self.matches_df
            if not matches_df.empty:
                participants_info = []
                for match_id in matches_df['id'].tolist():
                    groups_df = self.groups_sql.read(filter=f"WHERE table.match_id={match_id}").sort_values(by='name')
                    info = str()
                    for group_name, group_id in zip(groups_df['name'].tolist(), groups_df['id'].tolist()):                    
                        participants_df = self.participants_sql.read(filter=f"WHERE table.match_id={match_id} AND table.match_group_id={group_id}").sort_values(by='name')
                        info+=f"{group_name}[{", ".join(participants_df['name'].tolist())}] "
                    participants_info.append(info)
                matches_df['participants'] = participants_info
            
                # Show overview
                #print(self.groups_df)
                matches_overview_df = pd.DataFrame(columns=['group_id', 'Group', 'Points'])
                group_ids = list(dict.fromkeys(self.groups_df['event_group_id'].tolist()))
                group_names = list(dict.fromkeys(self.groups_df['event_groups_name'].tolist()))
                group_points = list()
                for group_id in group_ids:
                    group_points.append(self.groups_df.query(f"event_group_id=={group_id}")['value'].sum())
                
                matches_overview_df['group_id'] = group_ids
                matches_overview_df['Group'] = group_names
                matches_overview_df['Points'] = group_points
                
                column_config = {key: None for key in matches_overview_df.columns.to_list()}
                column_config['Group'] = st.column_config.TextColumn(label='Name', disabled=True)
                column_config['Points'] = st.column_config.NumberColumn(label='Points', disabled=True)
                st.data_editor(data=matches_overview_df, column_config=column_config, hide_index=True)
                
                # Show matches   
                #print(self.matches_df)
                for match_id in self.matches_df['id'].tolist():
                    #print(match_id)
                    match_df = self.matches_df.query(f"id == {match_id}")
                    #print(match_df)
                    match = st_MatchInfo(match_df=match_df)
                    match.st_obj()
    
    @st.dialog("Add match")
    def add(self, event_id=None, all_groups_df=None, all_participants_df=None):
        formats_sql = sql.formats()
        formats_df = formats_sql.read()
        
        st_name = st.text_input("Name")
        st_description = st.text_input("Description")
        st_con_format = st.container(horizontal=True, horizontal_alignment='distribute')
        with st_con_format:
            st_format = st.selectbox("Format", formats_df['name'].tolist(), index=None)
            st_value = st.text_input("Value", value="1")
        st_con_holes = st.container(horizontal=True)
        with st_con_holes:
            st_holes = st.segmented_control("Holes", options=[9,18], default=18)
            st_start_hole = st.segmented_control("Start", options=[1,10], default=1)
        st_participants = st.multiselect("Participants", all_participants_df['name'].tolist())
          
        if st.button("Submit"):
            if st_format is None or len(st_participants) < 2: 
                return
            
            format_id = formats_df.query(f"name == '{st_format}'")['id'].tolist()[0]
            fields = ["name", "description", "value", "holes", "start_hole", "event_id", "format_id"]
            values = [st_name, st_description, float(st_value), int(st_holes), int(st_start_hole), event_id, format_id]
            # Create match
            match_id = self.matches_sql.add(fields=fields, values=values)
            self.matches_df = pd.DataFrame(self.matches_sql.read(filter=f"WHERE table.event_id={self.event_df['id'].tolist()[0]}"))
            
            # Create match groups
            self.add_groups(match_id=match_id, participants=st_participants, all_groups_df=all_groups_df, all_participants_df=all_participants_df)
                    
            # Create match participants
            self.add_participants(match_id=match_id, participants=st_participants, all_participants_df=all_participants_df)
            
            st.rerun()
    
    @st.dialog("Edit match")
    def edit(self, match_df, all_groups_df=None, all_participants_df=None):
        
        formats_sql = sql.formats()
        formats_df = formats_sql.read()
        
        match_id = match_df['id'].tolist()[0]
        #print(f"Match ID = {match_id}")
        match_groups_df = pd.DataFrame(self.groups_sql.read(filter=f"WHERE table.match_id={match_id}"))
        match_participants_df = pd.DataFrame(self.participants_sql.read(filter=f"WHERE table.match_id={match_id}"))
        #print(f"Match groups = {match_groups_df['name'].tolist()}")
        #print(f"Match participants = {match_participants_df['name'].tolist()}")
        
        #print(f"Match DF = {match_df.columns.to_list()}")
        st_name = st.text_input("Name", value=match_df['name'].tolist()[0])
        st_description = st.text_input("Description", value=match_df['description'].tolist()[0])
        st_format = st.selectbox("Format", formats_df['name'].tolist(), index=match_df['format_id'].tolist()[0]-1)
        st_value = st.text_input("Value", value=match_df['value'].tolist()[0])
        st_participants = st.multiselect("Participants", all_participants_df['name'].tolist(), default=match_participants_df['name'].tolist())
        
        if st.button("Submit"):
            if st_format is None or len(st_participants) < 2: 
                return
            
            # Update match
            format_id = formats_df.query(f"name == '{st_format}'")['id'].tolist()[0]
            fields = ["name", "description", "format_id", "value"]
            values = [st_name, st_description, format_id, float(st_value)]
            self.matches_sql.update(id=match_id, fields=fields, values=values)
            
            # Update groups to be added
            self.add_groups(match_id=match_id, participants=st_participants, all_groups_df=all_groups_df, all_participants_df=all_participants_df)
            
            # Update participants to be added
            self.add_participants(match_id=match_id, participants=st_participants, all_participants_df=all_participants_df)
                    
            # Identify and update participants to be removed
            match_participants_df = pd.DataFrame(self.participants_sql.read(filter=f"WHERE table.match_id={match_id}"))
            if not match_participants_df.empty:
                for participant in match_participants_df['name'].tolist():
                    if participant not in st_participants:
                        participant_id = match_participants_df[match_participants_df['name']==participant]['id'].tolist()[0]
                        self.participants_sql.delete(id=participant_id)
                        continue
            
            # Identify and update groups to be removed
            match_groups_df = pd.DataFrame(self.groups_sql.read(filter=f"WHERE table.match_id={match_id}"))
            match_participants_df = pd.DataFrame(self.participants_sql.read(filter=f"WHERE table.match_id={match_id}"))
            if not match_groups_df.empty:
                for group_id in match_groups_df['id'].tolist():
                    if match_participants_df.empty:
                        self.groups_sql.delete(id=group_id)
                        continue
                    
                    if group_id not in match_participants_df['match_group_id'].tolist():
                        self.groups_sql.delete(id=group_id)
                        continue               
            
            st.rerun()
    
    def add_groups(self, match_id=None, participants=None, all_groups_df=None, all_participants_df=None):
        # Create match groups if it does not exist yet
        for participant_name in participants:              
            event_group_id = all_participants_df.query(f"name == '{participant_name}'")['event_group_id'].tolist()[0]
            event_group_name = all_groups_df.query(f"id == {event_group_id}")['name'].tolist()[0]
            event_group_description = all_groups_df.query(f"id == {event_group_id}")['description'].tolist()[0]
            
            match_groups_df = pd.DataFrame(self.groups_sql.read(filter=f"WHERE table.match_id={match_id}"))
            
            if match_groups_df.empty:
                #print(f"No groups for match, creating group for {participant_name}")
                fields = ["name", "description", "match_id", "event_group_id"]
                values = [event_group_name, event_group_description, match_id, event_group_id]
                self.groups_sql.add(fields=fields, values=values)  
                continue
                        
            if not match_groups_df.empty:
                if event_group_id not in match_groups_df['event_group_id'].tolist():
                    #print(f"Group for {participant_name} does not exist, creating group")
                    fields = ["name", "description", "match_id", "event_group_id"]
                    values = [event_group_name, event_group_description, match_id, event_group_id]
                    self.groups_sql.add(fields=fields, values=values)  
                    continue
            
    def add_participants(self, match_id=None, participants=None, all_participants_df=None):
        # Create match participants
        for participant_name in participants:
            event_group_id = all_participants_df.query(f"name == '{participant_name}'")['event_group_id'].tolist()[0]
            match_groups_df = pd.DataFrame(self.groups_sql.read(filter=f"WHERE table.match_id={match_id}"))
            match_group_id = match_groups_df.query(f"match_id == {match_id} & event_group_id == {event_group_id}")['id'].tolist()[0]
            event_participant_id = all_participants_df.query(f"name == '{participant_name}'")['id'].tolist()[0]
            event_participant_name = all_participants_df.query(f"name == '{participant_name}'")['name'].tolist()[0]
            event_participant_description = all_participants_df.query(f"name == '{participant_name}'")['description'].tolist()[0]
            
            match_participants_df = pd.DataFrame(self.participants_sql.read(filter=f"WHERE table.match_id={match_id}"))
            
            if match_participants_df.empty:
                #print(f"No participants for match, creating participant for {participant_name}")
                fields = ["name", "description", "match_id", "match_group_id", "event_participant_id"]
                values = [event_participant_name, event_participant_description, match_id, match_group_id, event_participant_id]
                self.participants_sql.add(fields=fields, values=values) 
                continue
                
            if not match_participants_df.empty:
                if event_participant_id not in match_participants_df['event_participant_id'].tolist():
                    #print(f"Participant for {participant_name} does not exist, creating participant")
                    fields = ["name", "description", "match_id", "match_group_id", "event_participant_id"]
                    values = [event_participant_name, event_participant_description, match_id, match_group_id, event_participant_id]
                    self.participants_sql.add(fields=fields, values=values) 
                    continue
    
    def remove(self, match_df=None):
        self.matches_sql.delete(id=match_df['id'].tolist()[0])
        st.rerun()
      
        
class EventGroupParticipants():
    obj = None
    event_df = None
    groups_sql = None
    groups_df = None
    participants_sql = None
    participants_df = None
    child_page = None    
    
    def __init__(self, event_df=None):
        self.event_df = event_df
        self.groups_sql = sql.event_groups()
        self.groups_df = pd.DataFrame(self.groups_sql.read())
        if not self.groups_df.empty: self.groups_df = self.groups_df.sort_values(by='name')
            
        self.participants_sql = sql.event_participants()
        self.participants_df = pd.DataFrame(self.participants_sql.read())
        if not self.participants_df.empty: self.participants_df = self.participants_df.sort_values(by=['event_groups_name','name'])
        
        pos_assigned_groups_sql = sql.event_groups()
        pos_assigned_groups_df = pd.DataFrame(pos_assigned_groups_sql.read(filter=f"WHERE table.event_id={self.event_df['id'].tolist()[0]}"))
        pos_all_groups_sql = sql.competition_groups()
        if not pos_assigned_groups_df.empty:
            pos_all_groups_df = pd.DataFrame(pos_all_groups_sql.read(filter=f"WHERE table.competition_id={self.event_df['competition_id'].tolist()[0]}"))
            if not pos_all_groups_df.empty: pos_all_groups_df = pos_all_groups_df.sort_values(by='name')
        else:
            pos_all_groups_df = pd.DataFrame(pos_all_groups_sql.read(filter=f"WHERE table.competition_id={self.event_df['competition_id'].tolist()[0]}"))
            if not pos_all_groups_df.empty: pos_all_groups_df = pos_all_groups_df.sort_values(by='name')
            
        pos_assigned_participants_sql = sql.event_participants()
        pos_assigned_participants_df = pd.DataFrame(pos_assigned_participants_sql.read(filter=f"WHERE table.event_id={self.event_df['id'].tolist()[0]}"))
        if not pos_assigned_participants_df.empty: pos_assigned_participants_df = pos_assigned_participants_df.sort_values(by=['event_groups_name','name'])
        
        pos_unassigned_participants_sql = sql.competition_participants()
        if not pos_assigned_participants_df.empty:
            pos_unassigned_participants_df = pd.DataFrame(pos_unassigned_participants_sql.read(filter=f"WHERE table.competition_id={self.event_df['competition_id'].tolist()[0]}")).query(f'id not in {pos_assigned_participants_df['competition_participant_id'].tolist()}')
            if not pos_unassigned_participants_df.empty: pos_unassigned_participants_df = pos_unassigned_participants_df.sort_values(by='name')
        else:
            pos_unassigned_participants_df = pd.DataFrame(pos_unassigned_participants_sql.read(filter=f"WHERE table.competition_id={self.event_df['competition_id'].tolist()[0]}"))
            if not pos_unassigned_participants_df.empty: pos_unassigned_participants_df = pos_unassigned_participants_df.sort_values(by='name')
                
        exp_groups_participants = st.expander("Groups & Participants", expanded=False)
        con_assigned = exp_groups_participants.container(horizontal=True, width='stretch')
        with con_assigned:                                      
            exp_assigned_participants = st.expander("Participants", expanded=True)
            with exp_assigned_participants:
                column_config = {key: None for key in pos_assigned_participants_df.columns.to_list()}
                column_config['name'] = 'Name'
                column_config['event_groups_name'] = 'Group'
                column_config['hc_index'] = 'HC Index'

                if not pos_assigned_participants_df.empty:
                    assigned_participants = st.dataframe(
                        pos_assigned_participants_df,
                        on_select='rerun',
                        selection_mode='multi-row',
                        hide_index=True,
                        column_config=column_config
                    )
        
        exp_unassigned = exp_groups_participants.expander("Available", expanded=False)
        con_unassigned = exp_unassigned.container(horizontal=True, width='stretch')  
        with con_unassigned:
            column_config = {key: None for key in pos_unassigned_participants_df.columns.to_list()}
            column_config['name'] = 'Participant'
            column_config['competition_groups_name'] = 'Group'
            column_config['hc_index'] = 'HC Index'
            if not pos_unassigned_participants_df.empty:
                unassigned_participants = st.dataframe(
                    pos_unassigned_participants_df,
                    on_select='rerun',
                    selection_mode='multi-row',
                    hide_index=True,
                    column_config=column_config
                )
        
        # Remove button
        if not pos_assigned_participants_df.empty and st.session_state.global_admin:    
            if len(assigned_participants.selection['rows']):
                participants_ids = pos_assigned_participants_df.iloc[assigned_participants.selection['rows']]['id'].tolist()
                participants_sels = pos_assigned_participants_df.query(f'id in {participants_ids}')
                if exp_assigned_participants.button("Remove", key="remove_participants", width='stretch'):
                    self.remove_participants(selection=participants_sels)
                    pass
            else:
                exp_assigned_participants.button("Remove", key="remove_participants", disabled=True, width='stretch')
        else:
            exp_assigned_participants.button("Remove", key="remove_participants", disabled=True, width='stretch')
        
        # Add button        
        if not pos_unassigned_participants_df.empty and st.session_state.global_admin:
            if len(unassigned_participants.selection['rows']):# and len(all_groups.selection['rows']):
                participants_ids = pos_unassigned_participants_df.iloc[unassigned_participants.selection['rows']]['id'].tolist()
                participants_sels = pos_unassigned_participants_df.query(f'id in {participants_ids}')
                groups_ids = pos_unassigned_participants_df.iloc[unassigned_participants.selection['rows']]['competition_group_id'].tolist()

                if exp_unassigned.button("Add", key="add_participants", width='stretch'):                    
                    self.add_participants(selection=participants_sels, groups_df=pos_assigned_groups_df)   
            else:
                exp_unassigned.button("Add", key="add_participants", disabled=True, width='stretch')
        else:
            exp_unassigned.button("Add", key="add_participants", disabled=True, width='stretch')
                               
    def add_groups(self, selection):
        fields = selection.columns.tolist()
        fields.pop(fields.index('id'))# = 'competition_group_id'
        fields[fields.index('name')] = sql.competition_groups().read(filter=f"WHERE table.id={fields[fields.index('competition_group_id')]}")['name'].tolist()[0]
        fields.append('event_id')       
        
        for entry in selection.to_numpy().tolist():
            entry.append(self.event_df['id'].tolist()[0])
            self.groups_sql.add(fields=fields, values=entry)
    
    def remove_groups(self, id):
        self.groups_sql.delete(id=id)

    def add_participants(self, selection, groups_df):
        fields = selection.columns.tolist()
        fields[fields.index('id')] = 'competition_participant_id'
        fields.append('event_id')
        
        # Create groups if required
        name_index = selection.columns.tolist().index('name')
        group_id_index = selection.columns.tolist().index('competition_group_id')
        for entry in selection.to_numpy().tolist():
            event_id = self.event_df['id'].tolist()[0]
            entry.append(event_id)
            competition_group_id = entry[group_id_index]
            entry[name_index] = sql.competition_groups().read(filter=f"WHERE table.id={competition_group_id}")['name'].tolist()[0]
            
            if not self.groups_df.empty:
                if entry[group_id_index] not in self.groups_df.query(f'event_id == {event_id}')['competition_group_id'].tolist():
                    #print(f'Not in current groups - create group')
                    self.groups_sql.add(fields=fields, values=entry)
                    self.groups_df = pd.DataFrame(self.groups_sql.read())
                else:
                    #print('Group already exists')
                    self.groups_df.query(f'event_id == {event_id} & competition_group_id == {entry[group_id_index]}')['id'].tolist()[0]
            else:
                #print('No groups exist - create group')
                self.groups_sql.add(fields=fields, values=entry)
                self.groups_df = pd.DataFrame(self.groups_sql.read())
                
        # Create participants   
        fields = selection.columns.tolist()
        fields[fields.index('id')] = 'competition_participant_id'
        fields.append('event_id')
        fields.append('event_group_id')
             
        group_id_index = selection.columns.tolist().index('competition_group_id')
        for entry in selection.to_numpy().tolist():
            event_id = self.event_df['id'].tolist()[0]
            entry.append(event_id)

            event_group_id = self.groups_df.query(f'event_id == {event_id} & competition_group_id == {entry[group_id_index]}')['id'].tolist()[0]
            entry.append(event_group_id)
            
            #print(f'entry = {entry}')
            self.participants_sql.add(fields=fields, values=entry)
        st.rerun()
    
    def remove_participants(self, selection):
        id_index = selection.columns.tolist().index('id')
        group_id_index = selection.columns.tolist().index('event_group_id')
        for entry in selection.to_numpy().tolist():
            # Remove participant
            self.participants_sql.delete(entry[id_index])
            # Refresh participants
            self.participants_df = pd.DataFrame(self.participants_sql.read())
            # If no participants linked to assigned group, remove this group
            if not self.participants_df.empty:
                if entry[group_id_index] not in self.participants_df['event_group_id'].tolist():
                    self.remove_groups(id=entry[group_id_index])
            else: self.remove_groups(id=entry[group_id_index])
        st.rerun()


class Individuals():
    obj = None
    event_df = None
    event_participants_sql = None
    event_participants_df = None
    scoring_cards_sql = None
    scoring_cards_df = None
    scoring_card_participants_sql = None
    scoring_card_participants_df = None
    scoring_rounds_sql = None
    scoring_rounds_df = None
    course_tees_sql = None
    course_tees_df = None
    scoring_holes_sql = None
    scoring_holes_df = None
    child_page = None
    
    def __init__(self, event_df=None):
        self.event_df = event_df
        event_id = event_df['id'].tolist()[0]
        
        # Event participants
        self.event_participants_sql = sql.event_participants()
        self.event_participants_df = pd.DataFrame(self.event_participants_sql.read(filter=f"WHERE table.event_id={event_id}"))
        if not self.event_participants_df.empty: self.event_participants_df = self.event_participants_df.sort_values(by=['event_groups_name','name'])
        
        # Scoring cards
        self.scoring_cards_sql = sql.scoring_cards()
        self.scoring_cards_df = pd.DataFrame(self.scoring_cards_sql.read(filter=f"WHERE table.event_id={event_id}"))
        if not self.scoring_cards_df.empty: self.scoring_cards_df = self.scoring_cards_df.sort_values(by='name')
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
        course_tees_ids = ','.join([str(x) for x in list(dict.fromkeys(self.scoring_rounds_df['course_tee_id'].tolist()))])
        scoring_rounds_ids = ','.join([str(x) for x in list(dict.fromkeys(self.scoring_rounds_df['id'].tolist()))])
        
        # Course tees
        self.course_tees_sql = sql.course_tees()
        self.course_tees_df = pd.DataFrame(self.course_tees_sql.read(filter=f"WHERE table.id IN ({course_tees_ids})"))
        if self.course_tees_df.empty: return        
        
        # Scoring holes
        self.scoring_holes_sql = sql.scoring_holes()
        self.scoring_holes_df = pd.DataFrame(self.scoring_holes_sql.read(filter=f"WHERE table.scoring_round_id IN ({scoring_rounds_ids})"))
        if self.scoring_holes_df.empty: return
        
        # Points card
        if not self.scoring_holes_df.empty:
            columns = ['Rank', 'Participant ID', 'Name', 'Points', 'Shots', 'round_id']               
            points_card = pd.DataFrame(columns=columns)
            
            participants = []        
            for round_id in self.scoring_rounds_df['id'].tolist():
                round_df = self.scoring_rounds_df.query(f"id == {round_id}")
                scoring_card_participant_id = round_df['scoring_card_participant_id'].tolist()[0]
                event_participant_id = self.scoring_card_participants_df.query(f"id == {scoring_card_participant_id}")['event_participant_id'].tolist()[0]
                event_participant_name = self.event_participants_df.query(f"id == {event_participant_id}")['name'].tolist()[0]
                holes_df = self.scoring_holes_df.query(f"scoring_round_id == {round_id}")
                points = holes_df['points'].sum()
                holes = holes_df['points'].count()
                shots = holes_df['shots'].sum()
                participants.append([None, event_participant_id, event_participant_name, points, shots, holes, round_id])
            participants = [list(i) for i in zip(*participants)]
            #print(transposed_list)
            points_card['Rank'] = participants[0]
            points_card['Participant ID'] = participants[1]
            points_card['Name'] = participants[2]
            points_card['Points'] = participants[3]
            points_card['Shots'] = participants[4]
            points_card['Hole'] = participants[5]
            points_card['round_id'] = participants[6]
                        
            stroke_holes = []
            for round_id in self.scoring_rounds_df['id'].tolist():
                round_df = self.scoring_rounds_df.query(f"id == {round_id}")
                course_tee_id = round_df['course_tee_id'].tolist()[0]
                course_tee_df = self.course_tees_df.query(f"id == {course_tee_id}")
                strokes_df = course_tee_df.filter(regex='stroke$', axis=1)
                strokes_df.columns = range(1,19)
                index = strokes_df.index.tolist()[0]

                strokes_df = strokes_df.transpose().sort_values(by=[index])
                strokes_df.columns = [index]
                strokes_df = strokes_df.transpose()
                stroke_holes.append(strokes_df.columns.tolist())            
                        
            stroke_points = []
            for round_id in self.scoring_rounds_df['id'].tolist():
                holes_df = self.scoring_holes_df.query(f"scoring_round_id == {round_id}")
                points = []
                cntr = 0
                for hole in stroke_holes[cntr]:
                    points_df = holes_df.query(f"number == {hole}")
                    if not points_df.empty:
                        points.append(points_df['points'].tolist()[0])
                    else: points.append(None)
                stroke_points.append(points)
            stroke_points_t = [list(i) for i in zip(*stroke_points)]
            
            #print(stroke_points_t)
            for hole in range(0,len(stroke_points_t)):
                points_card[f'S{hole+1}p'] = stroke_points_t[hole]

            filter_str = ['Points']
            for hole in range(1,19):
                filter_str.append(f'S{hole}p')
            #print(filter_str)
            points_card = points_card.sort_values(by=filter_str, ascending=False)                
            points_card['Rank'] = pd.Series(points_card['Points']).rank(method='min', ascending=False).astype(int).tolist()
            #print(points_card)
        
        exp = st.expander(label='Individual Leaderboard')
        with exp:
            header_con = st.container(horizontal=True, width='stretch')
            st_extended = header_con.toggle(label='Extended', key='event_card_extended_toggle', width='content')
            
            dataframe_df = points_card
            column_config = {key: None for key in dataframe_df.columns.to_list()}
            column_config['Rank'] = st.column_config.NumberColumn(format="%d", disabled=True)
            column_config['Name'] = st.column_config.TextColumn(disabled=True)
            column_config['Shots'] = st.column_config.NumberColumn(format="%d", disabled=True)
            column_config['Points'] = st.column_config.NumberColumn(format="%d", disabled=True)
            if st_extended:
                #print('Showing extended info')
                for hole in range(1,19):
                    column_config[f'S{hole}p'] = st.column_config.NumberColumn(label=f'S{hole}', format="%d", disabled=True)
                        
            rounds_completed = True            
            for active in self.scoring_rounds_df['active'].tolist():
                if active:
                    rounds_completed = False
                    break
                
            if not rounds_completed:
                column_config['Hole'] = st.column_config.NumberColumn(format="%d", disabled=True)
            else:
                #winner
                pass
            
            st.dataframe(key='individuals_data',
                        data=dataframe_df,
                        hide_index=True,
                        column_config=column_config,
                        )
            
 
# Populate page 
con = st.container(horizontal=True, vertical_alignment='center')

st_details = EventDetails(df=st.session_state.event)
                      
st_scoring_cards = EventScoringCards(event_df=st.session_state.event)

st_individuals = Individuals(event_df=st.session_state.event)     
                             
st_matches = EventMatches(event_df=st.session_state.event)

st_groups_participants = EventGroupParticipants(event_df=st.session_state.event)

with con:
    if st.button(label='', icon=':material/arrow_back:'):
        st.session_state.event = None
        st.session_state.page = st_details.parent_page
        st.rerun()
    st.subheader(f"Event: {st.session_state.event['name'].tolist()[0]}")