import streamlit as st
import pandas as pd
import sql
import math
from datetime import date

e_num = ['0️⃣', '1️⃣', '2️⃣', '3️⃣', '4️⃣', '5️⃣', '6️⃣', '7️⃣', '8️⃣', '9️⃣']

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
        
        print(f'Group points: {group_points}') 
        if holes < tot_holes:
            hole_str = f'through {holes} of {tot_holes}'
        else: hole_str = ' - match complete' 
        # Match might include more than 2 teams !?
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
            

class ScoringCardDetails():
    obj = None
    df = None
    parent_page = None
    df_date = None
          
    def __init__(self, df=None):
        self.obj = st.expander(label='Details')
        self.df = df
        df_id = df['id'].tolist()[0]
        #courses_df = sql.c
        self.parent_page = "app_pages/events/events_detail.py"
        if self.df is not None:
            with self.obj:
                st_name = st.text_input('Name', key=f'scoring_card_details_{df_id}_name', value=f'{self.df['name'].tolist()[0]}', disabled=not st.session_state.global_admin)
                st_description = st.text_area('Description', key=f'scoring_card_details_{df_id}_description', value=f'{self.df['description'].tolist()[0]}', disabled=not st.session_state.global_admin)
                st_active = st.toggle(label='Active', value=df['active'].tolist()[0], key=f'scoring_card_details_{df_id}_active', disabled=not st.session_state.global_admin)
                con = st.container(horizontal=True)
                df_date = self.df['date'].tolist()[0]
                #return
                #if df_date is not None: df_date = date.fromisoformat(df_date)
                #if df_date is None: df_date = 'today'
                st_date = con.date_input('Date', format='YYYY-MM-DD', value=df_date, on_change=self.update_date, key='sc_date', disabled=not st.session_state.global_admin)
                st_slot = con.segmented_control(label='Field', options=['AM', 'PM'], default=f'{self.df['slot'].tolist()[0]}', disabled=not st.session_state.global_admin)
                buttons_area = st.container(horizontal=True)
                if st.session_state.global_admin:
                    with buttons_area:
                        if st.button(label='', icon=':material/check:', key='scoring_card_details_update'):
                            if st.session_state.sc_date is not None:
                                self.update(name=st_name, description=st_description, active=st_active, date=f"'{st.session_state.sc_date}'", slot=st_slot)
                            else: st.rerun()
                        if st.button(label='', icon=':material/delete:', key='scoring_card_details_delete'):
                            self.delete()
                            
    def update_date(self):
        self.df_date = str(st.session_state.sc_date)
        
    def update(self, name=None, description=None, active=None, date=None, slot=None):
        if self.df is not None:
            df_sql = sql.scoring_cards()
            fields = ['name', 'description', 'active', 'date', 'slot']
            values = [name, description, active, date, slot]
            print(date)
            df_sql.update(id=self.df['id'].tolist()[0], fields=fields, values=values)
            st.session_state.scoring_card = df_sql.read(filter=f"WHERE table.id={self.df['id'].tolist()[0]}")
            st.rerun()
            
    @st.dialog(title='Delete confirmation')
    def delete(self):
        st.write("Are you sure you want to delete the entry?")
        area = st.container(horizontal=True, horizontal_alignment='center')
        with area:
            if st.button(label='Yes'):
                if self.df is not None:
                    df_sql = sql.scoring_cards()
                    df_sql.delete(id=self.df['id'].tolist()[0])
                    st.session_state.scoring_card = None
                    st.session_state.page = self.parent_page
                    st.rerun()
            if st.button(label='No'):
                st.rerun()                        


class ScoringCardScoring():
    obj = None
    df = None
    groups_sql = None
    groups_df = None
    participants_sql = None
    participants_df = None
    hole_number = None
    participants = None
    child_page = None

    def __init__(self, df=None, matches_df=None):
        self.df = df
        self.participants = []
        groups_sql = sql.scoring_card_groups()
        self.groups_df = groups_df = pd.DataFrame(groups_sql.read(filter=f"WHERE table.scoring_card_id={self.df['id'].tolist()[0]}").sort_values(['name']))

        participants_sql = sql.scoring_card_participants()
        self.participants_df = participants_df = pd.DataFrame(participants_sql.read(filter=f"WHERE table.scoring_card_id={self.df['id'].tolist()[0]}").sort_values(['scoring_card_groups_name', 'name']))                
        
        course_tees_sql = sql.course_tees()
        
        if st.session_state.hole_number is None:
            st.session_state.hole_number = 1
        self.hole_number = st.session_state.hole_number
        exp_scoring = st.expander(f'Scoring - Hole {self.hole_number}', expanded=True)
        with exp_scoring:
            
            self.st_header()
            
            con_hole_info = st.container(horizontal=False, width='stretch', vertical_alignment='center')
            with con_hole_info:
                self.st_hole_info()            
            
            # Removed Start
            hole_df = pd.DataFrame(columns=['Player', 'Shots', 'Points'])
            
            # Read players hole information
            for participant_id in participants_df['id'].tolist():
                participant_df = participants_df.query(f'id == {participant_id}')
                if participant_df['handicap'].tolist()[0] is not None and participant_df['course_tee_id'].tolist()[0]:
                    participant = self.Participant(participant_df)
                    self.participants.append(participant)
                #print(participant_df)
            
            #print(len(self.participants))
            for participant in self.participants:
                #print(participant.participant_df)
                participant_id = participant.participant_df['id'].tolist()[0]
                hole_df.loc[participant_id] = [participant.participant_df['name'].tolist()[0],
                                               participant.hole_shots,
                                               participant.hole_points]
                
            st_form = st.form(key='scoring_hole_form', border=False, enter_to_submit=False)
            
            def hole_data_update():
                changes = st.session_state.hole_data
                #print(changes)        
                edited_rows = changes.get("edited_rows", {})        
                for index, updates in edited_rows.items():
                    for column, value in updates.items():
                        participant = self.participants[index]
                        #print(participant.participant_df)
                        participant.update_shots(shots=value)
                        
                # Update matches if hole scored
                if not matches_df.empty:
                    for match_id in matches_df['id'].tolist():
                        match_df = matches_df.query(f"id=={match_id}")
                        
                        # Only update match if hole is in match holes
                        match_start_hole = match_df['start_hole'].tolist()[0]
                        match_holes = match_df['holes'].tolist()[0]
                        match_hole_range = range(match_start_hole, match_start_hole + match_holes)
                        #print(match_hole_range)
                        if st.session_state.hole_number in match_hole_range:
                            self.update_match_hole(match_df=match_df)
                            
                st.rerun()
                
            with st_form:
                column_config = {key: None for key in hole_df.columns.to_list()}
                column_config['Player'] = st.column_config.TextColumn(label='Name', disabled=True)
                column_config['Shots'] = st.column_config.NumberColumn(format="%d", min_value=1, max_value=10)
                column_config['Points'] = st.column_config.NumberColumn(format="%d", disabled=True)
                st.data_editor(key='hole_data',
                            data=hole_df,
                            hide_index=True,
                            column_config=column_config,
                            #on_change=hole_data_update
                            )
                if st.form_submit_button(label='', icon=':material/check:'):
                    hole_data_update()
            # Removed End
            
    def st_hole_info(self):
        con_buttons = st.container(horizontal=True, width='stretch', horizontal_alignment='distribute', vertical_alignment='center')
        con_details = st.container(horizontal=False, width='stretch', horizontal_alignment='left', vertical_alignment='center')
        course_tee_ids = list(dict.fromkeys(self.participants_df['course_tee_id'].tolist()))
        
        for course_tee_id in course_tee_ids:
            if course_tee_id is not None:
                if not math.isnan(course_tee_id):
                    course_tee_df = pd.DataFrame(sql.course_tees().read(filter=f"WHERE table.id={course_tee_id}"))
                    tee_name = course_tee_df['name'].tolist()[0]
                    hole_number = st.session_state.hole_number
                    hole_stroke = course_tee_df[f't{hole_number}_stroke'].tolist()[0]
                    hole_par = course_tee_df[f't{hole_number}_par'].tolist()[0]
                    hole_distance = course_tee_df[f't{hole_number}_distance'].tolist()[0]
                    con_details.badge(label=f"**{tee_name}** -> _Par **{hole_par}**, Stroke **{hole_stroke}**, {hole_distance}m_", width='stretch')
                    
        if con_buttons.button(label='', icon=':material/line_start_arrow_notch:', key='scoring_card_hole_previous', width='stretch'):
            if st.session_state.hole_number > 1: st.session_state.hole_number-=1
            st.session_state.pop('scoring_card_hole_slider')
            st.rerun()
        if con_buttons.button(label='', icon=':material/line_end_arrow_notch:', key='scoring_card_hole_next', width='stretch'):
            if st.session_state.hole_number < 18: st.session_state.hole_number+=1
            st.session_state.pop('scoring_card_hole_slider')
            st.rerun()

    def st_header(self):
        def set_hole():
                st.session_state.hole_number = st.session_state.scoring_card_hole_slider
                
        con = st.container(horizontal=False, horizontal_alignment='left')
        with con:
            if 'scoring_card_hole_slider' not in st.session_state:
                st.session_state['scoring_card_hole_slider'] = st.session_state.hole_number
            st.slider(label='Hole',
                      key='scoring_card_hole_slider',
                      #value=st.session_state.hole_number,
                      min_value=1, max_value=18,
                      step=1,
                      on_change=set_hole,
                      label_visibility='collapsed')
            #st.radio(label='Holes',options=range(1,19), horizontal=True)
                           
    def match_scores(self, match_df=None):
        #print(match_df)
        match_id = match_df['id'].tolist()[0]
        match_groups_df = sql.match_groups().read(filter=f"WHERE table.match_id={match_id}").sort_values(['id'])
        match_participants_df = sql.match_participants().read(filter=f"WHERE table.match_id={match_id}")
        
        m_event_participant_ids = ','.join([str(x) for x in match_participants_df['event_participant_id'].tolist()])
        m_scoring_card_participants_df = pd.DataFrame(sql.scoring_card_participants().read(filter=f"WHERE table.event_participant_id IN ({m_event_participant_ids})")).sort_values(['id'])
        
        m_scoring_card_group_ids = ','.join([str(x) for x in m_scoring_card_participants_df['scoring_card_group_id'].tolist()])
        m_scoring_card_groups_df = pd.DataFrame(sql.scoring_card_groups().read(filter=f"WHERE table.id IN ({m_scoring_card_group_ids})"))
        
        s_scoring_card_ids = ','.join([str(x) for x in list(dict.fromkeys(m_scoring_card_participants_df['scoring_card_id'].tolist()))])
        m_scoringcards_df = pd.DataFrame(sql.scoring_cards().read(filter=f"WHERE table.id IN ({s_scoring_card_ids})")).sort_values(['id'])
        #print(m_scoringcards_df)
        
        m_scoringcard_ids = ','.join([str(x) for x in list(dict.fromkeys(m_scoringcards_df['id'].tolist()))])
        m_scoring_card_participant_ids = ','.join([str(x) for x in m_scoring_card_participants_df['id'].tolist()])
        m_scoring_card_participant_event_participant_ids = [int(x) for x in m_scoring_card_participants_df['event_participant_id'].tolist()]
        m_scoring_rounds_df = pd.DataFrame(sql.scoring_rounds().read(filter=f"WHERE table.scoring_card_id IN ({m_scoringcard_ids}) AND table.scoring_card_participant_id IN ({m_scoring_card_participant_ids})"))
        #print(m_scoring_rounds_df)
        
        if m_scoring_rounds_df.empty:
            return None
        m_scoring_round_ids = ','.join([str(x) for x in m_scoring_rounds_df.sort_values(['id'])['id'].tolist()])
        hole_num = st.session_state.hole_number
        m_scoring_holes_df = pd.DataFrame(sql.scoring_holes().read(filter=f"WHERE table.scoring_round_id IN ({m_scoring_round_ids}) AND number={hole_num}")).sort_values(['scoring_round_id'])
        
        # Add group info to round
        scoring_card_groups  = []
        event_groups = []
        for id in m_scoring_card_participants_df.sort_values(['id'])['id'].tolist():
            scoring_card_group_id = m_scoring_card_participants_df.query(f'id=={id}')['scoring_card_group_id'].tolist()[0]
            event_group_id = m_scoring_card_groups_df.query(f'id=={scoring_card_group_id}')['event_group_id'].tolist()[0]
            scoring_card_groups.append(scoring_card_group_id)
            event_groups.append(event_group_id)
        new_columns = {'s_event_participant_id': m_scoring_card_participants_df['event_participant_id'].tolist(),
                       's_scoring_card_group_id': scoring_card_groups,
                       's_event_group_id': event_groups,
                       }
        m_scoring_rounds_df = m_scoring_rounds_df.sort_values(['scoring_card_participant_id']).assign(**new_columns)
        
        # Add scoring info to round
        new_columns = {'scoring_hole_id': m_scoring_holes_df['id'].tolist(),
                       'scoring_hole_shots': m_scoring_holes_df['shots'].tolist(),
                       'scoring_hole_points': m_scoring_holes_df['points'].tolist(),
                       }
        #print(new_columns)
        m_scoring_rounds_df = m_scoring_rounds_df.sort_values(['id']).assign(**new_columns)  
        #print(f"Scoring info\n{m_scoring_rounds_df}")
        
        # Add group info to match
        event_groups = []
        for id in match_participants_df.sort_values(['id'])['id'].tolist():
            match_group_id = match_participants_df.query(f'id=={id}')['match_group_id'].tolist()[0]
            event_group_id = match_groups_df.query(f'id=={match_group_id}')['event_group_id'].tolist()[0]
            event_groups.append(event_group_id)   
        new_columns = {'m_event_group_id': event_groups,
                       }
        match_scores_df = match_participants_df.sort_values(['id']).assign(**new_columns)
        
        # Add scoring info to match
        m_scoring_rounds_df = m_scoring_rounds_df.sort_values(['s_event_group_id', 's_event_participant_id'])
        new_columns = {'scoring_hole_id': m_scoring_rounds_df['scoring_hole_id'].tolist(),
                       'scoring_hole_shots': m_scoring_rounds_df['scoring_hole_shots'].tolist(),
                       'scoring_hole_points': m_scoring_rounds_df['scoring_hole_points'].tolist(),
                       }
        match_scores_df = match_scores_df.sort_values(['m_event_group_id','event_participant_id']).assign(**new_columns)
        return match_scores_df
        #print(f"Match scoring info\n{match_scores_df}")
        
    def update_match_hole(self, match_df=None):
        match_scores_df = self.match_scores(match_df=match_df)
        #print(match_scores_df)
        if match_scores_df is not None:
            done = True
            for shots in match_scores_df['scoring_hole_shots'].tolist():
                if math.isnan(shots): done = False
            if not done: return
            
            #print(match_df)
            match_holes = match_df['holes'].tolist()[0]
            match_start_hole = match_df['start_hole'].tolist()[0]
            if match_start_hole == 1: hole_num = st.session_state.hole_number
            elif match_start_hole == 10:
                if match_holes <= 9: hole_num = st.session_state.hole_number - 9
                else:
                    if st.session_state.hole_number <= 9: hole_num = st.session_state.hole_number - 9
                    else: hole_num = st.session_state.hole_number + 9
            else:
                print('Starting at random position not yet supported')
                return
                
            match_id = match_df['id'].tolist()[0]            
            
            match_hole_sql = sql.match_holes()
            #print('\nUpdating match hole')
            match match_df['format_id'].tolist()[0]:
                case 1: # IPS-4BBB 
                    group_ids = list(dict.fromkeys(match_scores_df['match_group_id'].tolist()))
                    for group_id in group_ids:
                        participant_ids = match_scores_df.query(f'match_group_id=={group_id}')['id'].tolist()
                        points = max(match_scores_df.query(f'match_group_id=={group_id}')['scoring_hole_points'].tolist())
                        #print(f'Group:{group_id} Points:{points}')
                        
                        match_hole_df = match_hole_sql.read(filter=f"WHERE table.match_group_id={group_id} AND table.number={hole_num}")
                        fields = ['name', 'number', 'points', 'match_id', 'match_group_id']
                        values = ['', hole_num, points, match_id, group_id]
                        #return None
                        if match_hole_df is None:
                            match_hole_id = match_hole_sql.add(fields=fields, values=values)
                        else:
                            match_hole_id = match_hole_df['id'].tolist()[0]
                            match_hole_sql.update(id=match_hole_id, fields=fields, values=values)
                            
                case 2: # MP-4BBB
                    group_ids = list(dict.fromkeys(match_scores_df['match_group_id'].tolist()))
                    for group_id in group_ids:
                        participant_ids = match_scores_df.query(f'match_group_id=={group_id}')['id'].tolist()
                        
                        this_team_points = max(match_scores_df.query(f'match_group_id=={group_id}')['scoring_hole_points'].tolist())
                        other_team_points = max(match_scores_df.query(f'match_group_id!={group_id}')['scoring_hole_points'].tolist())                    
                        points = int(this_team_points>other_team_points)
                        #print(f'points:{points}')
                        
                        match_hole_df = match_hole_sql.read(filter=f"WHERE table.match_group_id={group_id} AND table.number={hole_num}")
                        if len(participant_ids) == 1: 
                            fields = ['name', 'number', 'points', 'match_id', 'match_group_id', 'match_participant_id']
                            values = ['', hole_num, points, match_id, group_id, participant_ids[0]]
                        else:
                            fields = ['name', 'number', 'points', 'match_id', 'match_group_id']
                            values = ['', hole_num, points, match_id, group_id]
                        #return None
                        if match_hole_df is None:
                            match_hole_id = match_hole_sql.add(fields=fields, values=values)
                        else:
                            match_hole_id = match_hole_df['id'].tolist()[0]
                            match_hole_sql.update(id=match_hole_id, fields=fields, values=values)
                            
                case 3: # IPS
                    group_ids = list(dict.fromkeys(match_scores_df['match_group_id'].tolist()))
                    for group_id in group_ids:
                        participant_ids = match_scores_df.query(f'match_group_id=={group_id}')['id'].tolist()
                        points = sum(match_scores_df.query(f'match_group_id=={group_id}')['scoring_hole_points'].tolist())
                        #print(f'Group:{group_id} Points:{points}')
                        
                        match_hole_df = match_hole_sql.read(filter=f"WHERE table.match_group_id={group_id} AND table.number={hole_num}")
                        if len(participant_ids) == 1: 
                            fields = ['name', 'number', 'points', 'match_id', 'match_group_id', 'match_participant_id']
                            values = ['', hole_num, points, match_id, group_id, participant_ids[0]]
                        else:
                            fields = ['name', 'number', 'points', 'match_id', 'match_group_id']
                            values = ['', hole_num, points, match_id, group_id]
                        #print(fields)
                        #print(values)
                        #return None
                        if match_hole_df is None:
                            match_hole_id = match_hole_sql.add(fields=fields, values=values)
                        else:
                            match_hole_id = match_hole_df['id'].tolist()[0]
                            match_hole_sql.update(id=match_hole_id, fields=fields, values=values)
                                        
                case 4: # MP
                    group_ids = list(dict.fromkeys(match_scores_df['match_group_id'].tolist()))
                    for group_id in group_ids:
                        participant_ids = match_scores_df.query(f'match_group_id=={group_id}')['id'].tolist()
                        
                        this_team_points = sum(match_scores_df.query(f'match_group_id=={group_id}')['scoring_hole_points'].tolist())
                        other_team_points = sum(match_scores_df.query(f'match_group_id!={group_id}')['scoring_hole_points'].tolist())
                        points = int(this_team_points>other_team_points)
                        #print(f'points:{points}')
                        
                        match_hole_df = match_hole_sql.read(filter=f"WHERE table.match_group_id={group_id} AND table.number={hole_num}")
                        if len(participant_ids) == 1: 
                            fields = ['name', 'number', 'points', 'match_id', 'match_group_id', 'match_participant_id']
                            values = ['', hole_num, points, match_id, group_id, participant_ids[0]]
                        else:
                            fields = ['name', 'number', 'points', 'match_id', 'match_group_id']
                            values = ['', hole_num, points, match_id, group_id]
                        #print(fields)
                        #print(values)
                        #return None
                        if match_hole_df is None:
                            pass
                            match_hole_id = match_hole_sql.add(fields=fields, values=values)
                        else:
                            match_hole_id = match_hole_df['id'].tolist()[0]
                            match_hole_sql.update(id=match_hole_id, fields=fields, values=values)
                
                case _:
                    pass

            # Update match group if completed
            match_groups_df = sql.match_groups().read(filter=f"WHERE table.match_id={match_id}")
            match_participants_df = sql.match_participants().read(filter=f"WHERE table.match_id={match_id}")
            
            group_ids = list(dict.fromkeys(match_scores_df['match_group_id'].tolist()))
            group_ids_str = ','.join(str(item) for item in group_ids)
            match_holes_df = match_hole_sql.read(filter=f"WHERE table.match_id={match_id}")
            #print(f"WHERE table.match_group_id IN ({group_ids_str})")
            scored_holes = match_holes_df['id'].count()
            #print(f'Scored hole = {scored_holes}, Match holes = {len(group_ids) * match_holes}')
            if scored_holes == len(group_ids) * match_holes:
                print('Match complete')
                match_value = match_df['value'].tolist()[0]
                group_points = []
                for group_id in group_ids:
                    group_points.append(match_holes_df.query(f"match_group_id=={group_id}")['points'].sum())
                if group_points[0] > group_points[1]:
                    # Update winner
                    sql.match_groups().update(id=group_ids[0], fields=['value'], values=[match_value])
                    participant_ids = match_participants_df.query(f"match_group_id=={group_ids[0]}")['id'].tolist()
                    for participant_id in participant_ids:
                        sql.match_participants().update(id=participant_id, fields=['value'], values=[match_value/len(participant_ids)])
                    
                    # Update loser
                    sql.match_groups().update(id=group_ids[1], fields=['value'], values=[0])
                    participant_ids = match_participants_df.query(f"match_group_id=={group_ids[1]}")['id'].tolist()
                    for participant_id in participant_ids:
                        sql.match_participants().update(id=participant_id, fields=['value'], values=[0])
                        
                elif group_points[0] == group_points[1]:
                    # Update all
                    sql.match_groups().update(id=group_ids[0], fields=['value'], values=[match_value/2])
                    sql.match_groups().update(id=group_ids[1], fields=['value'], values=[match_value/2])
                    participant_ids = match_participants_df.query(f"match_id=={match_id}")['id'].tolist()
                    for participant_id in participant_ids:
                        sql.match_participants().update(id=participant_id, fields=['value'], values=[match_value/len(participant_ids)])
                        
                else:
                    # Update winner
                    sql.match_groups().update(id=group_ids[1], fields=['value'], values=[match_value])
                    participant_ids = match_participants_df.query(f"match_group_id=={group_ids[1]}")['id'].tolist()
                    for participant_id in participant_ids:
                        sql.match_participants().update(id=participant_id, fields=['value'], values=[match_value/len(participant_ids)])
                        
                    # Update loser
                    sql.match_groups().update(id=group_ids[0], fields=['value'], values=[0])
                    participant_ids = match_participants_df.query(f"match_group_id=={group_ids[0]}")['id'].tolist()
                    for participant_id in participant_ids:
                        sql.match_participants().update(id=participant_id, fields=['value'], values=[0])
                
            else:
                print('Match ongoing')
    
    class Participant():
        scoring_card_df = None
        scoring_round_df = None
        scoring_hole_df = None
        participant_df = None
        group_df = None
        course_tee_df = None
        hole_shots = None
        hole_points = None
        
        def __init__(self, participant_df=None):            
            self.participant_df = participant_df
            course_tee_id = participant_df['course_tee_id'].tolist()[0]
            self.course_tee_df = pd.DataFrame(sql.course_tees().read(filter=f"WHERE table.id={course_tee_id}"))
            
            scoring_card_id = participant_df['scoring_card_id'].tolist()[0]
            self.scoring_card_df = pd.DataFrame(sql.scoring_cards().read(filter=f"WHERE table.id={scoring_card_id}"))
            
            scoring_cards_participant_id = participant_df['id'].tolist()[0]
            self.scoring_round_df = pd.DataFrame(sql.scoring_rounds().read(filter=f"WHERE table.scoring_card_id={scoring_card_id} AND table.scoring_card_participant_id={scoring_cards_participant_id}"))
            
            if not self.scoring_round_df.empty:
                scoring_round_id = self.scoring_round_df['id'].tolist()[0]
                self.scoring_hole_df = pd.DataFrame(sql.scoring_holes().read(filter=f"WHERE table.scoring_round_id={scoring_round_id} AND table.number={st.session_state.hole_number}"))
                if not self.scoring_hole_df.empty:
                    self.hole_shots = self.scoring_hole_df['shots'].tolist()[0]
                    self.hole_points = self.scoring_hole_df['points'].tolist()[0]
            else: self.scoring_hole_df = pd.DataFrame()
            
            #self.st_player()
        
        def shots(self):
            participant_df = self.participant_df
            participant_id = participant_df['id'].tolist()[0]
            participant_name = participant_df['name'].tolist()[0]              
            shots_keyname = f'scoring_card_player_{participant_id}_{participant_name}_holescore'
            points_keyname = f'scoring_card_player_{participant_id}_{participant_name}_holepoints'
            
            handicap = participant_df['handicap'].tolist()[0] 
            hole_number = st.session_state.hole_number
            hole_stroke = self.course_tee_df[f't{hole_number}_stroke'].tolist()[0]
            hole_par = self.course_tee_df[f't{hole_number}_par'].tolist()[0]
            strokes = int(handicap/18) + int(hole_stroke<=(handicap-(int(handicap/18)*18)))          
            self.hole_shots = st.session_state[shots_keyname]
            if self.hole_shots is None:
                self.hole_points = None
            elif self.hole_shots == 0:
                self.hole_points = 0
            else:
                self.hole_points = hole_par + 2 + strokes - self.hole_shots
                if self.hole_points < 0: self.hole_points = 0
            
            # Update scoring round            
            fields = ['name', 'course_tee_id', 'scoring_card_id', 'scoring_card_participant_id']
            scoring_card_name = self.scoring_card_df['name'].tolist()[0]
            scoring_round_name = f'{scoring_card_name}-{participant_name}'
            values = [scoring_round_name, self.course_tee_df['id'].tolist()[0], self.scoring_card_df['id'].tolist()[0], self.participant_df['id'].tolist()[0]]
            scoring_rounds_sql = sql.scoring_rounds()
            if self.scoring_round_df.empty: scoring_rounds_id = scoring_rounds_sql.add(fields=fields, values=values)
            else:
                scoring_rounds_id = self.scoring_round_df['id'].tolist()[0]
            self.scoring_round_df = scoring_rounds_sql.read(filter=f"WHERE table.id={scoring_rounds_id}")
            
            # Update scoring hole
            fields = ['name', 'number', 'shots', 'points', 'scoring_round_id']
            scoring_hole_name = f'{scoring_round_name}-{st.session_state.hole_number}'
            values = [scoring_hole_name, st.session_state.hole_number, self.hole_shots, self.hole_points, scoring_rounds_id]
            scoring_hole_sql = sql.scoring_holes()
            if self.scoring_hole_df.empty: scoring_hole_id = scoring_hole_sql.add(fields=fields, values=values)                
            else:
                scoring_hole_id = self.scoring_hole_df['id'].tolist()[0]
                scoring_hole_sql.update(id=scoring_hole_id, fields=fields, values=values)
            self.scoring_hole_df = scoring_hole_sql.read(filter=f"WHERE table.id={scoring_hole_id}")
            
            # Update eclectic
            event_participant_id = participant_df['event_participant_id'].tolist()[0]
            event_participant_df = pd.DataFrame(sql.event_participants().read(filter=f"WHERE table.id={event_participant_id}"))
            competition_participant_id = event_participant_df['competition_participant_id'].tolist()[0]
            competition_participant_df = pd.DataFrame(sql.competition_participants().read(filter=f"WHERE table.id={competition_participant_id}"))
            competition_id = competition_participant_df['competition_id'].tolist()[0]
            eclectic_df = pd.DataFrame(sql.eclectics().read(filter=f"WHERE table.competition_id={competition_id} and table.competition_participant_id={competition_participant_id}"))                        
            
            if not eclectic_df.empty:
                eclectic_id = eclectic_df['id'].tolist()[0]
                #print(f'Eclectic df\n{eclectic_df}')
                
                event_participants_df = pd.DataFrame(sql.event_participants().read(filter=f"WHERE table.competition_participant_id={competition_participant_id}"))
                event_participant_ids = ','.join([str(x) for x in event_participants_df['id'].tolist()])
                scoring_cards_participants_df = pd.DataFrame(sql.scoring_card_participants().read(filter=f"WHERE table.event_participant_id IN ({event_participant_ids})"))
                scoring_cards_participant_ids = ','.join([str(x) for x in scoring_cards_participants_df['id'].tolist()])
                scoring_rounds_df = pd.DataFrame(sql.scoring_rounds().read(filter=f"WHERE table.scoring_card_participant_id IN ({scoring_cards_participant_ids})"))
                scoring_round_ids = ','.join([str(x) for x in scoring_rounds_df['id'].tolist()])
                scoring_holes_df = pd.DataFrame(sql.scoring_holes().read(filter=f"WHERE table.scoring_round_id IN ({scoring_round_ids}) AND number={hole_number}"))
                electic_hole_id = scoring_holes_df.loc[scoring_holes_df['points'].idxmax()]['id']                
                #print(scoring_holes_df.loc[scoring_holes_df['points'].idxmax()]['id'])
                
                fields = [f'hole{st.session_state.hole_number}']
                values = [electic_hole_id]
                sql.eclectics().update(id=eclectic_id, fields=fields, values=values)
                
                eclectic_df = pd.DataFrame(sql.eclectics().read(filter=f"WHERE table.competition_id={competition_id} and table.competition_participant_id={competition_participant_id}"))

                total = 0
                eclectic_hole_ids = []
                for hole in range(1,18):
                    hole_id = eclectic_df[f'hole{hole}'].tolist()[0]
                    if hole_id is not None:
                        eclectic_hole_ids.append(hole_id)

                hole_ids = ','.join([str(x) for x in eclectic_hole_ids])
                scoring_holes_df = pd.DataFrame(sql.scoring_holes().read(filter=f"WHERE table.id IN ({hole_ids})"))        
                total = scoring_holes_df['points'].sum()
                #print(f'Total: {total}')
                
                fields = ['total']
                values = [total]
                sql.eclectics().update(id=eclectic_id, fields=fields, values=values)
        
        def update_shots(self, shots):
            participant_df = self.participant_df
            participant_id = participant_df['id'].tolist()[0]
            participant_name = participant_df['name'].tolist()[0]              
            #shots_keyname = f'scoring_card_player_{participant_id}_{participant_name}_holescore'
            #points_keyname = f'scoring_card_player_{participant_id}_{participant_name}_holepoints'
            
            handicap = participant_df['handicap'].tolist()[0] 
            hole_number = st.session_state.hole_number
            hole_stroke = self.course_tee_df[f't{hole_number}_stroke'].tolist()[0]
            hole_par = self.course_tee_df[f't{hole_number}_par'].tolist()[0]
            strokes = int(handicap/18) + int(hole_stroke<=(handicap-(int(handicap/18)*18)))          
            #self.hole_shots = st.session_state[shots_keyname]
            self.hole_shots = shots
            if self.hole_shots is None:
                self.hole_points = None
            elif self.hole_shots == 0:
                self.hole_points = None
            else:
                self.hole_points = hole_par + 2 + strokes - self.hole_shots
                if self.hole_points <= 0:
                    self.hole_points = 0
                    #self.hole_shots = hole_par + 2 + strokes
            
            # Update scoring round            
            fields = ['name', 'course_tee_id', 'scoring_card_id', 'scoring_card_participant_id']
            scoring_card_name = self.scoring_card_df['name'].tolist()[0]
            scoring_round_name = f'{scoring_card_name}-{participant_name}'
            values = [scoring_round_name, self.course_tee_df['id'].tolist()[0], self.scoring_card_df['id'].tolist()[0], self.participant_df['id'].tolist()[0]]
            scoring_rounds_sql = sql.scoring_rounds()
            if self.scoring_round_df.empty: scoring_rounds_id = scoring_rounds_sql.add(fields=fields, values=values)
            else:
                scoring_rounds_id = self.scoring_round_df['id'].tolist()[0]
            self.scoring_round_df = scoring_rounds_sql.read(filter=f"WHERE table.id={scoring_rounds_id}")
            
            # Update scoring hole
            fields = ['name', 'number', 'shots', 'points', 'scoring_round_id']
            scoring_hole_name = f'{scoring_round_name}-{st.session_state.hole_number}'
            values = [scoring_hole_name, st.session_state.hole_number, self.hole_shots, self.hole_points, scoring_rounds_id]
            #print(values)
            scoring_hole_sql = sql.scoring_holes()
            if self.scoring_hole_df.empty: scoring_hole_id = scoring_hole_sql.add(fields=fields, values=values)                
            else:
                scoring_hole_id = self.scoring_hole_df['id'].tolist()[0]
                scoring_hole_sql.update(id=scoring_hole_id, fields=fields, values=values)
            self.scoring_hole_df = scoring_hole_sql.read(filter=f"WHERE table.id={scoring_hole_id}")
            
            # Update eclectic
            event_participant_id = participant_df['event_participant_id'].tolist()[0]
            event_participant_df = pd.DataFrame(sql.event_participants().read(filter=f"WHERE table.id={event_participant_id}"))
            competition_participant_id = event_participant_df['competition_participant_id'].tolist()[0]
            competition_participant_df = pd.DataFrame(sql.competition_participants().read(filter=f"WHERE table.id={competition_participant_id}"))
            competition_id = competition_participant_df['competition_id'].tolist()[0]
            eclectic_df = pd.DataFrame(sql.eclectics().read(filter=f"WHERE table.competition_id={competition_id} and table.competition_participant_id={competition_participant_id}"))                        
            
            if not eclectic_df.empty:
                eclectic_id = eclectic_df['id'].tolist()[0]
                #print(f'Eclectic df\n{eclectic_df}')
                
                event_participants_df = pd.DataFrame(sql.event_participants().read(filter=f"WHERE table.competition_participant_id={competition_participant_id}"))
                event_participant_ids = ','.join([str(x) for x in event_participants_df['id'].tolist()])
                scoring_cards_participants_df = pd.DataFrame(sql.scoring_card_participants().read(filter=f"WHERE table.event_participant_id IN ({event_participant_ids})"))
                scoring_cards_participant_ids = ','.join([str(x) for x in scoring_cards_participants_df['id'].tolist()])
                scoring_rounds_df = pd.DataFrame(sql.scoring_rounds().read(filter=f"WHERE table.scoring_card_participant_id IN ({scoring_cards_participant_ids})"))
                scoring_round_ids = ','.join([str(x) for x in scoring_rounds_df['id'].tolist()])
                scoring_holes_df = pd.DataFrame(sql.scoring_holes().read(filter=f"WHERE table.scoring_round_id IN ({scoring_round_ids}) AND number={hole_number}"))
                electic_hole_id = scoring_holes_df.loc[scoring_holes_df['points'].idxmax()]['id']                
                #print(scoring_holes_df.loc[scoring_holes_df['points'].idxmax()]['id'])
                
                fields = [f'hole{st.session_state.hole_number}']
                values = [electic_hole_id]
                sql.eclectics().update(id=eclectic_id, fields=fields, values=values)
                
                eclectic_df = pd.DataFrame(sql.eclectics().read(filter=f"WHERE table.competition_id={competition_id} and table.competition_participant_id={competition_participant_id}"))

                total = 0
                eclectic_hole_ids = []
                for hole in range(1,18):
                    hole_id = eclectic_df[f'hole{hole}'].tolist()[0]
                    if hole_id is not None:
                        eclectic_hole_ids.append(hole_id)

                hole_ids = ','.join([str(x) for x in eclectic_hole_ids])
                scoring_holes_df = pd.DataFrame(sql.scoring_holes().read(filter=f"WHERE table.id IN ({hole_ids})"))        
                total = scoring_holes_df['points'].sum()
                #print(f'Total: {total}')
                
                fields = ['total']
                values = [total]
                sql.eclectics().update(id=eclectic_id, fields=fields, values=values)
                                     
        def st_player(self):            
            hole_number = st.session_state.hole_number
            participant_df = self.participant_df
            participant_id = participant_df['id'].tolist()[0]
            participant_name = participant_df['name'].tolist()[0]
            handicap = participant_df['handicap'].tolist()[0]            
            
            hole_stroke = self.course_tee_df[f't{hole_number}_stroke'].tolist()[0]
            hole_par = self.course_tee_df[f't{hole_number}_par'].tolist()[0]
            hole_distance = self.course_tee_df[f't{hole_number}_distance'].tolist()[0]
            strokes = int(handicap/18) + int(hole_stroke<=(handicap-(int(handicap/18)*18)))
            
            exp = st.expander(label=f'{participant_name} _:blue[({strokes} HC stroke)]_', expanded=True)
            con = exp.container(horizontal=True, width='stretch', horizontal_alignment='distribute', vertical_alignment='bottom')            
            
            # dynamic widgets keys
            shots_keyname = f'scoring_card_player_{participant_id}_{participant_name}_holescore'
            points_keyname = f'scoring_card_player_{participant_id}_{participant_name}_holepoints'           
            
            st_shots = con.number_input(label='Shots', key=shots_keyname,
                                        value=self.hole_shots,                            
                                        on_change=self.shots,
                                        min_value=0, max_value=9, placeholder='Enter')
            
            if points_keyname in st.session_state:
                st.session_state[points_keyname] = self.hole_points
            st_points = con.number_input(label='Points', key=points_keyname, format="%d",
                                         value=self.hole_points,                                                                                         
                                         min_value=0, max_value=9, disabled=True)
           
        
class ScoringCardGroupParticipants():
    obj = None
    df = None
    groups_sql = None
    groups_df = None
    participants_sql = None
    participants_df = None
    child_page = None
    configured = None    
    
    def __init__(self, df=None):
        self.df = df
        self.groups_sql = sql.scoring_card_groups()
        self.groups_df = pd.DataFrame(self.groups_sql.read(filter=f"WHERE table.scoring_card_id={self.df['id'].tolist()[0]}"))
        if not self.groups_df.empty: self.groups_df = self.groups_df.sort_values(by='name')
            
        self.participants_sql = sql.scoring_card_participants()
        self.participants_df = pd.DataFrame(self.participants_sql.read(filter=f"WHERE table.scoring_card_id={self.df['id'].tolist()[0]}"))
        if not self.participants_df.empty: self.participants_df = self.participants_df.sort_values(by=['scoring_card_groups_name','name'])
        
        pos_assigned_groups_sql = sql.scoring_card_groups()
        pos_assigned_groups_df = pd.DataFrame(pos_assigned_groups_sql.read(filter=f"WHERE table.scoring_card_id={self.df['id'].tolist()[0]}"))
        pos_all_groups_sql = sql.event_groups()
        if not pos_assigned_groups_df.empty:
            pos_all_groups_df = pd.DataFrame(pos_all_groups_sql.read(filter=f"WHERE table.event_id={self.df['event_id'].tolist()[0]}"))
            if not pos_all_groups_df.empty: pos_all_groups_df = pos_all_groups_df.sort_values(by='name')
        else:
            pos_all_groups_df = pd.DataFrame(pos_all_groups_sql.read(filter=f"WHERE table.event_id={self.df['event_id'].tolist()[0]}"))
            if not pos_all_groups_df.empty: pos_all_groups_df = pos_all_groups_df.sort_values(by='name')
            
        pos_assigned_participants_sql = sql.scoring_card_participants()
        pos_assigned_participants_df = pd.DataFrame(pos_assigned_participants_sql.read(filter=f"WHERE table.scoring_card_id={self.df['id'].tolist()[0]}"))
        if not pos_assigned_participants_df.empty: pos_assigned_participants_df = pos_assigned_participants_df.sort_values(by=['scoring_card_groups_name','name'])
        
        pos_unassigned_participants_sql = sql.event_participants()
        if not pos_assigned_participants_df.empty:
            pos_unassigned_participants_df = pd.DataFrame(pos_unassigned_participants_sql.read(filter=f"WHERE table.event_id={self.df['event_id'].tolist()[0]}")).query(f'id not in {pos_assigned_participants_df['event_participant_id'].tolist()}')
            if not pos_unassigned_participants_df.empty: pos_unassigned_participants_df = pos_unassigned_participants_df.sort_values(by='name')
        else:
            pos_unassigned_participants_df = pd.DataFrame(pos_unassigned_participants_sql.read(filter=f"WHERE table.event_id={self.df['event_id'].tolist()[0]}"))
            if not pos_unassigned_participants_df.empty: pos_unassigned_participants_df = pos_unassigned_participants_df.sort_values(by='name')
                
        exp_groups_participants = st.expander("Participants", expanded=True)
        con_assigned = exp_groups_participants.container(width='stretch')
        with con_assigned:                                      
        #    exp_assigned_participants = st.expander("Participants", expanded=True)
        #    with exp_assigned_participants:
            st_form = st.form(key='participants_form', border=False, enter_to_submit=False)
            def participants_form_update():
                changes = st.session_state.participants_data
                #print(changes)        
                edited_rows = changes.get("edited_rows", {})        
                for index, updates in edited_rows.items():
                    for column, value in updates.items():
                        match column:
                            case 'handicap':
                                self.participants_sql.update(id=pos_assigned_participants_df.iloc[index]['id'],
                                                            fields=[column],
                                                            values=[value])
                            case 'course_tees_name':
                                #self.sco
                                course_id = self.df['course_id'].tolist()[0]
                                course_tees_df = sql.course_tees().read(filter=f'WHERE table.course_id={course_id}')
                                course_tee_id = course_tees_df.query(f"name == '{value}'")['id'].tolist()[0]
                                self.participants_sql.update(id=pos_assigned_participants_df.iloc[index]['id'],
                                                            fields=['course_tee_id'],
                                                            values=[course_tee_id])
                            
                            case _: print(f'{column} = {value}')
                st.rerun()
            
            with st_form:
                # Load course tee names for selection box
                course_id = self.df['course_id'].tolist()[0]
                course_tees_df = sql.course_tees().read(filter=f'WHERE table.course_id={course_id}')
                course_tee_names = course_tees_df['name'].tolist()
                
                # Add scoring columns
                shots, points = self.participants_round_scoring(participants_df=pos_assigned_participants_df)
                #print(f'{shots}\n{points}')
                pos_assigned_participants_df['Shots'] = shots
                pos_assigned_participants_df['Points'] = points
                pos_assigned_participants_df['sel'] = False
                
                # Add select column
                pos_assigned_participants_df['sel'] = False
                
                column_config = {key: None for key in pos_assigned_participants_df.columns.to_list()}
                column_config['name'] = st.column_config.TextColumn(label='Name', disabled=True)
                column_config['handicap'] = st.column_config.NumberColumn(label='HC', format="%d", required=True)
                column_config['course_tees_name'] = st.column_config.SelectboxColumn(label='Tee', options=course_tee_names, required=True)
                column_config['Shots'] = st.column_config.NumberColumn(label='Shots', format="%d", disabled=True)
                column_config['Points'] = st.column_config.NumberColumn(label='Points', format="%d", disabled=True)
                column_config['sel'] = st.column_config.CheckboxColumn(label='')
                st.data_editor(key='participants_data',
                            data=pos_assigned_participants_df,
                            hide_index=True,
                            column_config=column_config,
                            #on_change=hole_data_update
                            )
                #print(pos_assigned_participants_df)
                if st.form_submit_button(label='', icon=':material/check:', disabled=not st.session_state.global_admin):
                    participants_form_update()
                
                #print(pos_assigned_participants_df['course_tee_id'])
                handicaps = pos_assigned_participants_df['handicap'].tolist()
                course_tees = pos_assigned_participants_df['course_tee_id'].tolist()
                if None in handicaps or len([x for x in handicaps if math.isnan(x)]) > 0:
                    self.configured = False
                if None in course_tees or len([x for x in course_tees if math.isnan(x)]) > 0:
                    self.configured = False
                else:
                #    print('Configured')
                    self.configured = True
                    
            #for row in pos_assigned_participants_df.itertuples():
            #    self.st_scoring_card_player(entry=row, scoring_card_df=self.df)
                
        exp_unassigned = exp_groups_participants.expander("Available", expanded=False)
        con_unassigned = exp_unassigned.container(horizontal=True, width='stretch')  
        with con_unassigned:
            column_config = {key: None for key in pos_unassigned_participants_df.columns.to_list()}
            column_config['name'] = 'Participant'
            column_config['event_groups_name'] = 'Group'
            if not pos_unassigned_participants_df.empty:
                unassigned_participants = st.dataframe(
                    pos_unassigned_participants_df,
                    on_select='rerun',
                    selection_mode='multi-row',
                    hide_index=True,
                    column_config=column_config
                )
                    
        # Add button        
        if not pos_unassigned_participants_df.empty and st.session_state.global_admin:
            if len(unassigned_participants.selection['rows']):# and len(all_groups.selection['rows']):
                participants_ids = pos_unassigned_participants_df.iloc[unassigned_participants.selection['rows']]['id'].tolist()
                participants_sels = pos_unassigned_participants_df.query(f'id in {participants_ids}')
                groups_ids = pos_unassigned_participants_df.iloc[unassigned_participants.selection['rows']]['event_group_id'].tolist()
        
                if exp_unassigned.button("Add", key="add_participants", width='stretch'):                    
                    self.add_participants(selection=participants_sels, groups_df=pos_assigned_groups_df)   
            else:
                exp_unassigned.button("Add", key="add_participants", disabled=True, width='stretch')
        else:
            exp_unassigned.button("Add", key="add_participants", disabled=True, width='stretch')
                               
    def add_groups(self, selection):
        fields = selection.columns.tolist()
        fields.pop(fields.index('id'))# = 'event_group_id'
        fields[fields.index('name')] = sql.event_groups().read(filter=f"WHERE table.id={fields[fields.index('event_group_id')]}")['name'].tolist()[0]
        fields.append('scoring_card_id')       
        
        for entry in selection.to_numpy().tolist():
            entry.append(self.df['id'].tolist()[0])
            self.groups_sql.add(fields=fields, values=entry)

    def remove_groups(self, id):
        self.groups_sql.delete(id=id)

    def add_participants(self, selection, groups_df):
        fields = selection.columns.tolist()
        fields[fields.index('id')] = 'event_participant_id'
        fields.append('scoring_card_id')
        
        # Create groups if required
        name_index = selection.columns.tolist().index('name')
        group_id_index = selection.columns.tolist().index('event_group_id')
        for entry in selection.to_numpy().tolist():
            scoring_card_id = self.df['id'].tolist()[0]
            entry.append(scoring_card_id)
            event_group_id = entry[group_id_index]
            entry[name_index] = sql.event_groups().read(filter=f"WHERE table.id={event_group_id}")['name'].tolist()[0]
            
            if not self.groups_df.empty:
                if entry[group_id_index] not in self.groups_df.query(f'scoring_card_id == {scoring_card_id}')['event_group_id'].tolist():
                    #print(f'Not in current groups - create group')
                    self.groups_sql.add(fields=fields, values=entry)
                    self.groups_df = pd.DataFrame(self.groups_sql.read())
                else:
                    #print('Group already exists')
                    self.groups_df.query(f'scoring_card_id == {scoring_card_id} & event_group_id == {entry[group_id_index]}')['id'].tolist()[0]
            else:
                #print('No groups exist - create group')
                self.groups_sql.add(fields=fields, values=entry)
                self.groups_df = pd.DataFrame(self.groups_sql.read())
                
        # Create participants   
        fields = selection.columns.tolist()
        fields[fields.index('id')] = 'event_participant_id'
        fields.append('scoring_card_id')
        fields.append('scoring_card_group_id')
             
        group_id_index = selection.columns.tolist().index('event_group_id')
        for entry in selection.to_numpy().tolist():
            scoring_card_id = self.df['id'].tolist()[0]
            entry.append(scoring_card_id)

            scoring_card_group_id = self.groups_df.query(f'scoring_card_id == {scoring_card_id} & event_group_id == {entry[group_id_index]}')['id'].tolist()[0]
            entry.append(scoring_card_group_id)
            
            #print(f'entry = {entry}')
            self.participants_sql.add(fields=fields, values=entry)
        st.rerun()
    
    def remove_participants(self, selection):
        id_index = selection.columns.tolist().index('id')
        group_id_index = selection.columns.tolist().index('scoring_card_group_id')
        for entry in selection.to_numpy().tolist():
            # Remove participant
            self.participants_sql.delete(entry[id_index])
            # Refresh participants
            self.participants_df = pd.DataFrame(self.participants_sql.read())
            # If no participants linked to assigned group, remove this group
            if not self.participants_df.empty:
                if entry[group_id_index] not in self.participants_df['scoring_card_group_id'].tolist():
                    self.remove_groups(id=entry[group_id_index])
            else: self.remove_groups(id=entry[group_id_index])
        st.rerun()

    def update_participant(self, id, handicap, course_tee_id):
        if handicap is not None and course_tee_id is not None:
            fields = ['handicap', 'course_tee_id']
            values = [handicap, course_tee_id]
            self.participants_sql.update(id=id, fields=fields, values=values)

    def st_scoring_card_player(self, entry=None, scoring_card_df=None):       
        #print(f'Entry = {entry}')
        con = st.container(horizontal=True, width='stretch', vertical_alignment='center')
        with con:            
            if entry.handicap is None: handicap = None
            elif math.isnan(entry.handicap): handicap = None
            else: handicap = int(entry.handicap)
            
            course_id = scoring_card_df['course_id'].tolist()[0]
            course_tees_df = sql.course_tees().read(filter=f'WHERE table.course_id={course_id}')
            if entry.course_tee_id is None: course_tee_index = None
            elif math.isnan(entry.course_tee_id): course_tee_index = None
            else: course_tee_index = course_tees_df['name'].tolist().index(entry.course_tees_name)
            
            st.selectbox(label='Player', options=entry.name, label_visibility='collapsed')
            #st.text(body=f'{entry.name}')
            #st_handicap = st.number_input(label='HC Index', value=handicap, key=f'scoring_card_hc_index_{entry.id}', label_visibility='collapsed', placeholder='Enter', format="%d")
            st_handicap = st.text_input(label='HC Index', value=f'{handicap}', key=f'scoring_card_hc_index_{entry.id}', label_visibility='collapsed', placeholder='Enter')
            st_course_tee = st.selectbox(label='Tee', options=course_tees_df['name'].tolist(), index=course_tee_index, key=f'scoring_card_course_tee_{entry.id}', label_visibility='collapsed')
            btn_enable = st_handicap.isdigit() and st_course_tee is not None
            if btn_enable:
                if st.button(label='✅', key=f'scoring_card_player_{entry.name}_update', width='content', disabled=False):
                    course_tee_id = course_tees_df[course_tees_df['name']==st_course_tee]['id'].tolist()[0]
                    self.update_participant(id=entry.id, handicap=st_handicap, course_tee_id=course_tee_id)
            else: st.button(label='✅', key=f'scoring_card_player_{entry.name}_update', width='content', disabled=True)
            if st.button(label='❌', key=f'scoring_card_player_{entry.name}_remove', width='content'):
                self.delete_player(participant_df=self.participants_df.query(f"id == {entry.id}"))
    
    def participants_round_scoring(self, participants_df=None):
        scoring_card_id = self.df['id'].tolist()[0]
        participant_ids_str = ','.join(map(str, participants_df['id'].tolist()))
        scoring_rounds_df = pd.DataFrame(sql.scoring_rounds().read(f"WHERE table.scoring_card_id={scoring_card_id} AND table.scoring_card_participant_id IN ({participant_ids_str})"))
        if scoring_rounds_df.empty: return [None, None]
        scoring_round_ids_str = ','.join(map(str, scoring_rounds_df['id'].tolist()))
        scoring_holes_df = pd.DataFrame(sql.scoring_holes().read(f"WHERE table.scoring_round_id IN ({scoring_round_ids_str})"))

        scoring_card_id = self.df['id'].tolist()[0]
        
        shots_list = []
        points_list = []        
        for participant_id in participants_df['id'].tolist():
            if not scoring_rounds_df.query(f"scoring_card_participant_id == {participant_id}").empty:
                round_id = scoring_rounds_df.query(f"scoring_card_participant_id == {participant_id}")['id'].tolist()[0]
                shots = scoring_holes_df.query(f"scoring_round_id == {round_id}")['shots'].sum()
                shots_list.append(shots)
                points = scoring_holes_df.query(f"scoring_round_id == {round_id}")['points'].sum()            
                points_list.append(points)
            else:
                shots_list.append(0)
                points_list.append(0)
        
        return [shots_list, points_list]    
        
    
    @st.dialog("Delete player")
    def delete_player(self, participant_df):
        st.text('Are you sure you want to delete the player and their round data?')
        if st.button(label='Yes'):
            participant_id = participant_df['id'].tolist()[0]
            group_id = participant_df['scoring_card_group_id'].tolist()[0]
            self.participants_sql.delete(id=participant_id)
            self.participants_df = pd.DataFrame(self.participants_sql.read(filter=f"WHERE table.scoring_card_id={self.df['id'].tolist()[0]}"))
            
            if group_id not in self.participants_df['scoring_card_group_id'].tolist():
                #print('Group can be removed')
                self.groups_sql.delete(id=group_id)
            
            st.rerun()
    

class ScoringCardsDisplay():
    obj = None
    df = None
    groups_sql = None
    groups_df = None
    participants_sql = None
    participants_df = None
    course_tee_sql = None
    course_tee_df = None
    participants = None
    
    def __init__(self, df=None, matches_df=None):
        self.df = df
        scoring_card_id = df['id'].tolist()[0]
        self.participants = []
        groups_sql = sql.scoring_card_groups()
        self.groups_df = groups_df = pd.DataFrame(groups_sql.read(filter=f"WHERE table.scoring_card_id={self.df['id'].tolist()[0]}").sort_values(['name']))

        participants_sql = sql.scoring_card_participants()
        self.participants_df = participants_df = pd.DataFrame(participants_sql.read(filter=f"WHERE table.scoring_card_id={self.df['id'].tolist()[0]}").sort_values(['scoring_card_groups_name', 'name']))                
        
        scorecard_df = pd.DataFrame(
            columns=['Hole', 'S1', 'P1', 'S2', 'P2', 'S3', 'P3', 'S4', 'P4']
            )
        
        col_hole = list()
        front_9 = [str(x) for x in range(1,10)]
        back_9 = [str(x) for x in range(10,19)]
        col_hole = front_9
        col_hole.append("OUT")
        col_hole = col_hole + back_9
        col_hole.append("IN")
        col_hole.append("TOT")
        scorecard_df['Hole'] = col_hole
        
        participant_index = 1
        for participant_id in participants_df['id'].tolist():
            participant_df = participants_df.query(f'id == {participant_id}')
            if participant_df['handicap'].tolist()[0] is not None and participant_df['course_tee_id'].tolist()[0]:
                participant = self.Participant(participant_df)
                self.participants.append(participant)
                out_shots = 0
                out_points = 0
                in_shots = 0
                in_points = 0
                for hole in range(1,19):
                    if hole <= 9: df_index = hole - 1
                    else: df_index = hole
                    if participant.round_shots is not None:
                        if len(participant.round_shots) > 0:
                            scorecard_df.at[df_index, f'S{participant_index}'] = participant.round_shots[hole-1]
                            scorecard_df.at[df_index, f'P{participant_index}'] = participant.round_points[hole-1]
                            if hole <= 9:
                                out_shots += participant.round_shots[hole-1]
                                out_points += participant.round_points[hole-1]
                            else:
                                in_shots += participant.round_shots[hole-1]
                                in_points += participant.round_points[hole-1]
                scorecard_df.at[9, f'S{participant_index}'] = out_shots
                scorecard_df.at[9, f'P{participant_index}'] = out_points
                scorecard_df.at[19, f'S{participant_index}'] = in_shots
                scorecard_df.at[19, f'P{participant_index}'] = in_points
                scorecard_df.at[20, f'S{participant_index}'] = out_shots + in_shots
                scorecard_df.at[20, f'P{participant_index}'] = out_points + in_points
            participant_index += 1
        
        exp = st.expander(label='Scorecard')
        form = exp.form(key=f'scoring_card_{scoring_card_id}_bulk_form', border=False)
                    
        def form_update():
            changes = st.session_state[f'scoring_card_bulk_update']
            print(changes)        
            edited_rows = changes.get("edited_rows", {})        
            for index, updates in edited_rows.items():
                if index in range(0,9) or index in range(10,20):
                    for column, value in updates.items():
                        p_index = int(column[1:])-1
                        if index < 9: hole = index + 1
                        else: hole = index
                        participant = self.participants[p_index]
                        participant.update_shots(hole_number=hole, shots=value)
                        #print(f'Participant={participant.participant_df['name'].tolist()[0]} Hole={hole} Val={value}')
            
            for index, updates in edited_rows.items():
                if index in range(0,9) or index in range(10,20):
                    for column, value in updates.items():
                    # Update matches if hole scored
                        p_index = int(column[1:])-1
                        if index < 9: hole = index + 1
                        else: hole = index
                        
                        if not matches_df.empty:
                            for match_id in matches_df['id'].tolist():
                                match_df = matches_df.query(f"id=={match_id}")
                                
                                # Only update match if hole is in match holes
                                match_start_hole = match_df['start_hole'].tolist()[0]
                                match_holes = match_df['holes'].tolist()[0]
                                match_hole_range = range(match_start_hole, match_start_hole + match_holes)
                                #print(match_hole_range)
                                if hole in match_hole_range:
                                    self.update_match_hole(match_df=match_df, hole_number=hole)
                            
            st.rerun()
        
        with form:
            column_config = {
                "Hole": st.column_config.TextColumn(label='Hole', disabled=True),
                'S1': st.column_config.NumberColumn(label=self.participants[0].participant_df['name'].tolist()[0], format='%d'),
                'P1': st.column_config.NumberColumn(label='Pts', format='%d', disabled=True),
                'S2': st.column_config.NumberColumn(label=self.participants[1].participant_df['name'].tolist()[0], format='%d'),
                'P2': st.column_config.NumberColumn(label='Pts', format='%d', disabled=True),
                'S3': st.column_config.NumberColumn(label=self.participants[2].participant_df['name'].tolist()[0], format='%d'),
                'P3': st.column_config.NumberColumn(label='Pts', format='%d', disabled=True),
                'S4': st.column_config.NumberColumn(label=self.participants[3].participant_df['name'].tolist()[0], format='%d'),
                'P4': st.column_config.NumberColumn(label='Pts', format='%d', disabled=True),
            }
            st.data_editor(
                key=f'scoring_card_bulk_update',
                data=scorecard_df,
                column_config=column_config,
                hide_index=True,)
            
            if st.form_submit_button(label='', icon=':material/check:', disabled=not st.session_state.global_admin):
                form_update()

    def match_scores(self, match_df=None, hole_number=None):
        #print(match_df)
        if hole_number is None: hole_num = st.session_state.hole_number
        else: hole_num = hole_number
        match_id = match_df['id'].tolist()[0]
        match_groups_df = sql.match_groups().read(filter=f"WHERE table.match_id={match_id}").sort_values(['id'])
        match_participants_df = sql.match_participants().read(filter=f"WHERE table.match_id={match_id}")
        
        m_event_participant_ids = ','.join([str(x) for x in match_participants_df['event_participant_id'].tolist()])
        m_scoring_card_participants_df = pd.DataFrame(sql.scoring_card_participants().read(filter=f"WHERE table.event_participant_id IN ({m_event_participant_ids})")).sort_values(['id'])
        
        m_scoring_card_group_ids = ','.join([str(x) for x in m_scoring_card_participants_df['scoring_card_group_id'].tolist()])
        m_scoring_card_groups_df = pd.DataFrame(sql.scoring_card_groups().read(filter=f"WHERE table.id IN ({m_scoring_card_group_ids})"))
        
        s_scoring_card_ids = ','.join([str(x) for x in list(dict.fromkeys(m_scoring_card_participants_df['scoring_card_id'].tolist()))])
        m_scoringcards_df = pd.DataFrame(sql.scoring_cards().read(filter=f"WHERE table.id IN ({s_scoring_card_ids})")).sort_values(['id'])
        #print(m_scoringcards_df)
        
        m_scoringcard_ids = ','.join([str(x) for x in list(dict.fromkeys(m_scoringcards_df['id'].tolist()))])
        m_scoring_card_participant_ids = ','.join([str(x) for x in m_scoring_card_participants_df['id'].tolist()])
        m_scoring_card_participant_event_participant_ids = [int(x) for x in m_scoring_card_participants_df['event_participant_id'].tolist()]
        m_scoring_rounds_df = pd.DataFrame(sql.scoring_rounds().read(filter=f"WHERE table.scoring_card_id IN ({m_scoringcard_ids}) AND table.scoring_card_participant_id IN ({m_scoring_card_participant_ids})"))
        #print(m_scoring_rounds_df)
        
        if m_scoring_rounds_df.empty:
            return None
        m_scoring_round_ids = ','.join([str(x) for x in m_scoring_rounds_df.sort_values(['id'])['id'].tolist()])
        
        m_scoring_holes_df = pd.DataFrame(sql.scoring_holes().read(filter=f"WHERE table.scoring_round_id IN ({m_scoring_round_ids}) AND number={hole_num}")).sort_values(['scoring_round_id'])
        
        # Add group info to round
        scoring_card_groups  = []
        event_groups = []
        for id in m_scoring_card_participants_df.sort_values(['id'])['id'].tolist():
            scoring_card_group_id = m_scoring_card_participants_df.query(f'id=={id}')['scoring_card_group_id'].tolist()[0]
            event_group_id = m_scoring_card_groups_df.query(f'id=={scoring_card_group_id}')['event_group_id'].tolist()[0]
            scoring_card_groups.append(scoring_card_group_id)
            event_groups.append(event_group_id)
        new_columns = {'s_event_participant_id': m_scoring_card_participants_df['event_participant_id'].tolist(),
                       's_scoring_card_group_id': scoring_card_groups,
                       's_event_group_id': event_groups,
                       }
        m_scoring_rounds_df = m_scoring_rounds_df.sort_values(['scoring_card_participant_id']).assign(**new_columns)
        
        # Add scoring info to round
        new_columns = {'scoring_hole_id': m_scoring_holes_df['id'].tolist(),
                       'scoring_hole_shots': m_scoring_holes_df['shots'].tolist(),
                       'scoring_hole_points': m_scoring_holes_df['points'].tolist(),
                       }
        #print(new_columns)
        m_scoring_rounds_df = m_scoring_rounds_df.sort_values(['id']).assign(**new_columns)  
        #print(f"Scoring info\n{m_scoring_rounds_df}")
        
        # Add group info to match
        event_groups = []
        for id in match_participants_df.sort_values(['id'])['id'].tolist():
            match_group_id = match_participants_df.query(f'id=={id}')['match_group_id'].tolist()[0]
            event_group_id = match_groups_df.query(f'id=={match_group_id}')['event_group_id'].tolist()[0]
            event_groups.append(event_group_id)   
        new_columns = {'m_event_group_id': event_groups,
                       }
        match_scores_df = match_participants_df.sort_values(['id']).assign(**new_columns)
        
        # Add scoring info to match
        m_scoring_rounds_df = m_scoring_rounds_df.sort_values(['s_event_group_id', 's_event_participant_id'])
        new_columns = {'scoring_hole_id': m_scoring_rounds_df['scoring_hole_id'].tolist(),
                       'scoring_hole_shots': m_scoring_rounds_df['scoring_hole_shots'].tolist(),
                       'scoring_hole_points': m_scoring_rounds_df['scoring_hole_points'].tolist(),
                       }
        match_scores_df = match_scores_df.sort_values(['m_event_group_id','event_participant_id']).assign(**new_columns)
        return match_scores_df
        #print(f"Match scoring info\n{match_scores_df}")
        
    def update_match_hole(self, match_df=None, hole_number=None):
        if hole_number is None: hole_number = st.session_state.hole_number
        match_scores_df = self.match_scores(match_df=match_df, hole_number=hole_number)
        
        #print(match_scores_df)
        if match_scores_df is not None:
            done = True
            for shots in match_scores_df['scoring_hole_shots'].tolist():
                if math.isnan(shots): done = False
            if not done: return
            
            #print(match_df)
            match_holes = match_df['holes'].tolist()[0]
            match_start_hole = match_df['start_hole'].tolist()[0]
            if match_start_hole == 1: hole_num = hole_number
            elif match_start_hole == 10:
                if match_holes <= 9: hole_num = hole_number - 9
                else:
                    if hole_number <= 9: hole_num = hole_number - 9
                    else: hole_num = hole_number + 9
            else:
                print('Starting at random position not yet supported')
                return
            #print(f'Hole number = {hole_num}')
                
            match_id = match_df['id'].tolist()[0]            
            
            match_hole_sql = sql.match_holes()
            #print('\nUpdating match hole')
            match match_df['format_id'].tolist()[0]:
                case 1: # IPS-4BBB 
                    group_ids = list(dict.fromkeys(match_scores_df['match_group_id'].tolist()))
                    for group_id in group_ids:
                        participant_ids = match_scores_df.query(f'match_group_id=={group_id}')['id'].tolist()
                        points = max(match_scores_df.query(f'match_group_id=={group_id}')['scoring_hole_points'].tolist())
                        #print(f'Group:{group_id} Points:{points}')
                        
                        match_hole_df = match_hole_sql.read(filter=f"WHERE table.match_group_id={group_id} AND table.number={hole_num}")
                        fields = ['name', 'number', 'points', 'match_id', 'match_group_id']
                        values = ['', hole_num, points, match_id, group_id]
                        #return None
                        if match_hole_df is None:
                            match_hole_id = match_hole_sql.add(fields=fields, values=values)
                        else:
                            match_hole_id = match_hole_df['id'].tolist()[0]
                            match_hole_sql.update(id=match_hole_id, fields=fields, values=values)
                            
                case 2: # MP-4BBB
                    group_ids = list(dict.fromkeys(match_scores_df['match_group_id'].tolist()))
                    for group_id in group_ids:
                        participant_ids = match_scores_df.query(f'match_group_id=={group_id}')['id'].tolist()
                        
                        this_team_points = max(match_scores_df.query(f'match_group_id=={group_id}')['scoring_hole_points'].tolist())
                        other_team_points = max(match_scores_df.query(f'match_group_id!={group_id}')['scoring_hole_points'].tolist())                    
                        points = int(this_team_points>other_team_points)
                        #print(f'points:{points}')
                        
                        match_hole_df = match_hole_sql.read(filter=f"WHERE table.match_group_id={group_id} AND table.number={hole_num}")
                        if len(participant_ids) == 1: 
                            fields = ['name', 'number', 'points', 'match_id', 'match_group_id', 'match_participant_id']
                            values = ['', hole_num, points, match_id, group_id, participant_ids[0]]
                        else:
                            fields = ['name', 'number', 'points', 'match_id', 'match_group_id']
                            values = ['', hole_num, points, match_id, group_id]
                        #return None
                        if match_hole_df is None:
                            match_hole_id = match_hole_sql.add(fields=fields, values=values)
                        else:
                            match_hole_id = match_hole_df['id'].tolist()[0]
                            match_hole_sql.update(id=match_hole_id, fields=fields, values=values)
                            
                case 3: # IPS
                    group_ids = list(dict.fromkeys(match_scores_df['match_group_id'].tolist()))
                    for group_id in group_ids:
                        participant_ids = match_scores_df.query(f'match_group_id=={group_id}')['id'].tolist()
                        points = sum(match_scores_df.query(f'match_group_id=={group_id}')['scoring_hole_points'].tolist())
                        #print(f'Group:{group_id} Points:{points}')
                        
                        match_hole_df = match_hole_sql.read(filter=f"WHERE table.match_group_id={group_id} AND table.number={hole_num}")
                        if len(participant_ids) == 1: 
                            fields = ['name', 'number', 'points', 'match_id', 'match_group_id', 'match_participant_id']
                            values = ['', hole_num, points, match_id, group_id, participant_ids[0]]
                        else:
                            fields = ['name', 'number', 'points', 'match_id', 'match_group_id']
                            values = ['', hole_num, points, match_id, group_id]
                        #print(fields)
                        #print(values)
                        #return None
                        if match_hole_df is None:
                            match_hole_id = match_hole_sql.add(fields=fields, values=values)
                        else:
                            match_hole_id = match_hole_df['id'].tolist()[0]
                            match_hole_sql.update(id=match_hole_id, fields=fields, values=values)
                                        
                case 4: # MP
                    group_ids = list(dict.fromkeys(match_scores_df['match_group_id'].tolist()))
                    for group_id in group_ids:
                        participant_ids = match_scores_df.query(f'match_group_id=={group_id}')['id'].tolist()
                        
                        this_team_points = sum(match_scores_df.query(f'match_group_id=={group_id}')['scoring_hole_points'].tolist())
                        other_team_points = sum(match_scores_df.query(f'match_group_id!={group_id}')['scoring_hole_points'].tolist())
                        points = int(this_team_points>other_team_points)
                        #print(f'points:{points}')
                        
                        match_hole_df = match_hole_sql.read(filter=f"WHERE table.match_group_id={group_id} AND table.number={hole_num}")
                        if len(participant_ids) == 1: 
                            fields = ['name', 'number', 'points', 'match_id', 'match_group_id', 'match_participant_id']
                            values = ['', hole_num, points, match_id, group_id, participant_ids[0]]
                        else:
                            fields = ['name', 'number', 'points', 'match_id', 'match_group_id']
                            values = ['', hole_num, points, match_id, group_id]
                        #print(fields)
                        #print(values)
                        #return None
                        if match_hole_df is None:
                            pass
                            match_hole_id = match_hole_sql.add(fields=fields, values=values)
                        else:
                            match_hole_id = match_hole_df['id'].tolist()[0]
                            match_hole_sql.update(id=match_hole_id, fields=fields, values=values)
                
                case _:
                    pass

            # Update match group if completed
            match_groups_df = sql.match_groups().read(filter=f"WHERE table.match_id={match_id}")
            match_participants_df = sql.match_participants().read(filter=f"WHERE table.match_id={match_id}")
            
            group_ids = list(dict.fromkeys(match_scores_df['match_group_id'].tolist()))
            group_ids_str = ','.join(str(item) for item in group_ids)
            match_holes_df = match_hole_sql.read(filter=f"WHERE table.match_id={match_id}")
            #print(f"WHERE table.match_group_id IN ({group_ids_str})")
            scored_holes = match_holes_df['id'].count()
            #print(f'Scored hole = {scored_holes}, Match holes = {len(group_ids) * match_holes}')
            if scored_holes == len(group_ids) * match_holes:
                print('Match complete')
                match_value = match_df['value'].tolist()[0]
                group_points = []
                for group_id in group_ids:
                    group_points.append(match_holes_df.query(f"match_group_id=={group_id}")['points'].sum())
                if group_points[0] > group_points[1]:
                    # Update winner
                    sql.match_groups().update(id=group_ids[0], fields=['value'], values=[match_value])
                    participant_ids = match_participants_df.query(f"match_group_id=={group_ids[0]}")['id'].tolist()
                    for participant_id in participant_ids:
                        sql.match_participants().update(id=participant_id, fields=['value'], values=[match_value/len(participant_ids)])
                    
                    # Update loser
                    sql.match_groups().update(id=group_ids[1], fields=['value'], values=[0])
                    participant_ids = match_participants_df.query(f"match_group_id=={group_ids[1]}")['id'].tolist()
                    for participant_id in participant_ids:
                        sql.match_participants().update(id=participant_id, fields=['value'], values=[0])
                        
                elif group_points[0] == group_points[1]:
                    # Update all
                    sql.match_groups().update(id=group_ids[0], fields=['value'], values=[match_value/2])
                    sql.match_groups().update(id=group_ids[1], fields=['value'], values=[match_value/2])
                    participant_ids = match_participants_df.query(f"match_id=={match_id}")['id'].tolist()
                    for participant_id in participant_ids:
                        sql.match_participants().update(id=participant_id, fields=['value'], values=[match_value/len(participant_ids)])
                        
                else:
                    # Update winner
                    sql.match_groups().update(id=group_ids[1], fields=['value'], values=[match_value])
                    participant_ids = match_participants_df.query(f"match_group_id=={group_ids[1]}")['id'].tolist()
                    for participant_id in participant_ids:
                        sql.match_participants().update(id=participant_id, fields=['value'], values=[match_value/len(participant_ids)])
                        
                    # Update loser
                    sql.match_groups().update(id=group_ids[0], fields=['value'], values=[0])
                    participant_ids = match_participants_df.query(f"match_group_id=={group_ids[0]}")['id'].tolist()
                    for participant_id in participant_ids:
                        sql.match_participants().update(id=participant_id, fields=['value'], values=[0])
                
            else:
                print('Match ongoing')
                
    class Participant():
        scoring_card_df = None
        scoring_round_df = None
        scoring_hole_df = None
        scoring_holes_df = None
        participant_df = None
        group_df = None
        course_tee_df = None
        hole_shots = None
        round_shots = None
        hole_points = None
        round_points = None
        
        def __init__(self, participant_df=None):            
            self.participant_df = participant_df
            course_tee_id = participant_df['course_tee_id'].tolist()[0]
            self.course_tee_df = pd.DataFrame(sql.course_tees().read(filter=f"WHERE table.id={course_tee_id}"))
            
            scoring_card_id = participant_df['scoring_card_id'].tolist()[0]
            self.scoring_card_df = pd.DataFrame(sql.scoring_cards().read(filter=f"WHERE table.id={scoring_card_id}"))
            
            scoring_cards_participant_id = participant_df['id'].tolist()[0]
            self.scoring_round_df = pd.DataFrame(sql.scoring_rounds().read(filter=f"WHERE table.scoring_card_id={scoring_card_id} AND table.scoring_card_participant_id={scoring_cards_participant_id}"))
            
            if not self.scoring_round_df.empty:
                scoring_round_id = self.scoring_round_df['id'].tolist()[0]
                self.scoring_hole_df = pd.DataFrame(sql.scoring_holes().read(filter=f"WHERE table.scoring_round_id={scoring_round_id} AND table.number={st.session_state.hole_number}"))
                if not self.scoring_hole_df.empty:
                    self.hole_shots = self.scoring_hole_df['shots'].tolist()[0]
                    self.hole_points = self.scoring_hole_df['points'].tolist()[0]
                scoring_holes_df = pd.DataFrame(sql.scoring_holes().read(filter=f"WHERE table.scoring_round_id={scoring_round_id}"))
                self.scoring_holes_df = scoring_holes_df
                self.round_shots = list()
                self.round_points = list()
                if not scoring_holes_df.empty:
                    for hole in range(1,19):
                        if not scoring_holes_df.query(f'number=={hole}').empty:
                            self.round_shots.append(scoring_holes_df.query(f'number=={hole}')['shots'].tolist()[0])
                            self.round_points.append(scoring_holes_df.query(f'number=={hole}')['points'].tolist()[0])
                        else:
                            self.round_shots.append(None)
                            self.round_points.append(None)
            else: self.scoring_hole_df = pd.DataFrame()
        
        def shots(self, hole_number=None):
            participant_df = self.participant_df
            participant_id = participant_df['id'].tolist()[0]
            participant_name = participant_df['name'].tolist()[0]              
            shots_keyname = f'scoring_card_player_{participant_id}_{participant_name}_holescore'
            points_keyname = f'scoring_card_player_{participant_id}_{participant_name}_holepoints'
            
            handicap = participant_df['handicap'].tolist()[0] 
            if hole_number is None:
                hole_number = st.session_state.hole_number
            hole_stroke = self.course_tee_df[f't{hole_number}_stroke'].tolist()[0]
            hole_par = self.course_tee_df[f't{hole_number}_par'].tolist()[0]
            strokes = int(handicap/18) + int(hole_stroke<=(handicap-(int(handicap/18)*18)))          
            self.hole_shots = st.session_state[shots_keyname]
            if self.hole_shots is None:
                self.hole_points = None
            elif self.hole_shots == 0:
                self.hole_points = 0
            else:
                self.hole_points = hole_par + 2 + strokes - self.hole_shots
                if self.hole_points < 0: self.hole_points = 0
            
            # Update scoring round            
            fields = ['name', 'course_tee_id', 'scoring_card_id', 'scoring_card_participant_id']
            scoring_card_name = self.scoring_card_df['name'].tolist()[0]
            scoring_round_name = f'{scoring_card_name}-{participant_name}'
            values = [scoring_round_name, self.course_tee_df['id'].tolist()[0], self.scoring_card_df['id'].tolist()[0], self.participant_df['id'].tolist()[0]]
            scoring_rounds_sql = sql.scoring_rounds()
            if self.scoring_round_df.empty: scoring_rounds_id = scoring_rounds_sql.add(fields=fields, values=values)
            else:
                scoring_rounds_id = self.scoring_round_df['id'].tolist()[0]
            self.scoring_round_df = scoring_rounds_sql.read(filter=f"WHERE table.id={scoring_rounds_id}")
            
            # Update scoring hole
            fields = ['name', 'number', 'shots', 'points', 'scoring_round_id']
            scoring_hole_name = f'{scoring_round_name}-{hole_number}'
            values = [scoring_hole_name, hole_number, self.hole_shots, self.hole_points, scoring_rounds_id]
            scoring_hole_sql = sql.scoring_holes()
            if self.scoring_hole_df.empty: scoring_hole_id = scoring_hole_sql.add(fields=fields, values=values)                
            else:
                scoring_hole_id = self.scoring_hole_df['id'].tolist()[0]
                scoring_hole_sql.update(id=scoring_hole_id, fields=fields, values=values)
            self.scoring_hole_df = scoring_hole_sql.read(filter=f"WHERE table.id={scoring_hole_id}")
            
            # Update eclectic
            event_participant_id = participant_df['event_participant_id'].tolist()[0]
            event_participant_df = pd.DataFrame(sql.event_participants().read(filter=f"WHERE table.id={event_participant_id}"))
            competition_participant_id = event_participant_df['competition_participant_id'].tolist()[0]
            competition_participant_df = pd.DataFrame(sql.competition_participants().read(filter=f"WHERE table.id={competition_participant_id}"))
            competition_id = competition_participant_df['competition_id'].tolist()[0]
            eclectic_df = pd.DataFrame(sql.eclectics().read(filter=f"WHERE table.competition_id={competition_id} and table.competition_participant_id={competition_participant_id}"))                        
            
            if not eclectic_df.empty:
                eclectic_id = eclectic_df['id'].tolist()[0]
                #print(f'Eclectic df\n{eclectic_df}')
                
                event_participants_df = pd.DataFrame(sql.event_participants().read(filter=f"WHERE table.competition_participant_id={competition_participant_id}"))
                event_participant_ids = ','.join([str(x) for x in event_participants_df['id'].tolist()])
                scoring_cards_participants_df = pd.DataFrame(sql.scoring_card_participants().read(filter=f"WHERE table.event_participant_id IN ({event_participant_ids})"))
                scoring_cards_participant_ids = ','.join([str(x) for x in scoring_cards_participants_df['id'].tolist()])
                scoring_rounds_df = pd.DataFrame(sql.scoring_rounds().read(filter=f"WHERE table.scoring_card_participant_id IN ({scoring_cards_participant_ids})"))
                scoring_round_ids = ','.join([str(x) for x in scoring_rounds_df['id'].tolist()])
                scoring_holes_df = pd.DataFrame(sql.scoring_holes().read(filter=f"WHERE table.scoring_round_id IN ({scoring_round_ids}) AND number={hole_number}"))
                electic_hole_id = scoring_holes_df.loc[scoring_holes_df['points'].idxmax()]['id']                
                #print(scoring_holes_df.loc[scoring_holes_df['points'].idxmax()]['id'])
                
                fields = [f'hole{hole_number}']
                values = [electic_hole_id]
                sql.eclectics().update(id=eclectic_id, fields=fields, values=values)
                
                eclectic_df = pd.DataFrame(sql.eclectics().read(filter=f"WHERE table.competition_id={competition_id} and table.competition_participant_id={competition_participant_id}"))

                total = 0
                eclectic_hole_ids = []
                for hole in range(1,18):
                    hole_id = eclectic_df[f'hole{hole}'].tolist()[0]
                    if hole_id is not None:
                        eclectic_hole_ids.append(hole_id)

                hole_ids = ','.join([str(x) for x in eclectic_hole_ids])
                scoring_holes_df = pd.DataFrame(sql.scoring_holes().read(filter=f"WHERE table.id IN ({hole_ids})"))        
                total = scoring_holes_df['points'].sum()
                #print(f'Total: {total}')
                
                fields = ['total']
                values = [total]
                sql.eclectics().update(id=eclectic_id, fields=fields, values=values)
        
        def update_shots(self, hole_number=None, shots=None):
            participant_df = self.participant_df
            participant_id = participant_df['id'].tolist()[0]
            participant_name = participant_df['name'].tolist()[0]              
            #shots_keyname = f'scoring_card_player_{participant_id}_{participant_name}_holescore'
            #points_keyname = f'scoring_card_player_{participant_id}_{participant_name}_holepoints'
            
            handicap = participant_df['handicap'].tolist()[0] 
            if hole_number is None:
                hole_number = st.session_state.hole_number
            hole_stroke = self.course_tee_df[f't{hole_number}_stroke'].tolist()[0]
            hole_par = self.course_tee_df[f't{hole_number}_par'].tolist()[0]
            strokes = int(handicap/18) + int(hole_stroke<=(handicap-(int(handicap/18)*18)))          
            #self.hole_shots = st.session_state[shots_keyname]
            self.hole_shots = shots
            if self.hole_shots is None:
                self.hole_points = None
            elif self.hole_shots == 0:
                self.hole_points = None
            else:
                self.hole_points = hole_par + 2 + strokes - self.hole_shots
                if self.hole_points <= 0:
                    self.hole_points = 0
                    #self.hole_shots = hole_par + 2 + strokes
            
            # Update scoring round            
            fields = ['name', 'course_tee_id', 'scoring_card_id', 'scoring_card_participant_id']
            scoring_card_name = self.scoring_card_df['name'].tolist()[0]
            scoring_round_name = f'{scoring_card_name}-{participant_name}'
            values = [scoring_round_name, self.course_tee_df['id'].tolist()[0], self.scoring_card_df['id'].tolist()[0], self.participant_df['id'].tolist()[0]]
            scoring_rounds_sql = sql.scoring_rounds()
            if self.scoring_round_df.empty: scoring_rounds_id = scoring_rounds_sql.add(fields=fields, values=values)
            else:
                scoring_rounds_id = self.scoring_round_df['id'].tolist()[0]
            self.scoring_round_df = scoring_rounds_sql.read(filter=f"WHERE table.id={scoring_rounds_id}")
            
            # Update scoring hole
            fields = ['name', 'number', 'shots', 'points', 'scoring_round_id']
            scoring_hole_name = f'{scoring_round_name}-{hole_number}'
            values = [scoring_hole_name, hole_number, self.hole_shots, self.hole_points, scoring_rounds_id]
            #print(values)
            scoring_hole_sql = sql.scoring_holes()
            
            #print(self.scoring_holes_df)
            if self.scoring_holes_df is None: scoring_hole_sql.add(fields=fields, values=values)
            elif self.scoring_holes_df.empty: scoring_hole_sql.add(fields=fields, values=values)
            else:
                hole_df = self.scoring_holes_df.query(f'number=={hole_number}')
                if hole_df.empty: scoring_hole_id = scoring_hole_sql.add(fields=fields, values=values)                
                else:
                    scoring_hole_id = hole_df['id'].tolist()[0]
                    scoring_hole_sql.update(id=scoring_hole_id, fields=fields, values=values)
                self.scoring_hole_df = scoring_hole_sql.read(filter=f"WHERE table.id={scoring_hole_id}")
                scoring_round_id = self.scoring_round_df['id'].tolist()[0]
                scoring_holes_df = pd.DataFrame(sql.scoring_holes().read(filter=f"WHERE table.scoring_round_id={scoring_round_id}"))
                self.scoring_holes_df = scoring_holes_df
            
            # Update eclectic
            event_participant_id = participant_df['event_participant_id'].tolist()[0]
            event_participant_df = pd.DataFrame(sql.event_participants().read(filter=f"WHERE table.id={event_participant_id}"))
            competition_participant_id = event_participant_df['competition_participant_id'].tolist()[0]
            competition_participant_df = pd.DataFrame(sql.competition_participants().read(filter=f"WHERE table.id={competition_participant_id}"))
            competition_id = competition_participant_df['competition_id'].tolist()[0]
            eclectic_df = pd.DataFrame(sql.eclectics().read(filter=f"WHERE table.competition_id={competition_id} and table.competition_participant_id={competition_participant_id}"))                        
            
            if not eclectic_df.empty:
                eclectic_id = eclectic_df['id'].tolist()[0]
                #print(f'Eclectic df\n{eclectic_df}')
                
                event_participants_df = pd.DataFrame(sql.event_participants().read(filter=f"WHERE table.competition_participant_id={competition_participant_id}"))
                event_participant_ids = ','.join([str(x) for x in event_participants_df['id'].tolist()])
                scoring_cards_participants_df = pd.DataFrame(sql.scoring_card_participants().read(filter=f"WHERE table.event_participant_id IN ({event_participant_ids})"))
                scoring_cards_participant_ids = ','.join([str(x) for x in scoring_cards_participants_df['id'].tolist()])
                scoring_rounds_df = pd.DataFrame(sql.scoring_rounds().read(filter=f"WHERE table.scoring_card_participant_id IN ({scoring_cards_participant_ids})"))
                scoring_round_ids = ','.join([str(x) for x in scoring_rounds_df['id'].tolist()])
                scoring_holes_df = pd.DataFrame(sql.scoring_holes().read(filter=f"WHERE table.scoring_round_id IN ({scoring_round_ids}) AND number={hole_number}"))
                electic_hole_id = scoring_holes_df.loc[scoring_holes_df['points'].idxmax()]['id']                
                #print(scoring_holes_df.loc[scoring_holes_df['points'].idxmax()]['id'])
                
                fields = [f'hole{hole_number}']
                values = [electic_hole_id]
                sql.eclectics().update(id=eclectic_id, fields=fields, values=values)
                
                eclectic_df = pd.DataFrame(sql.eclectics().read(filter=f"WHERE table.competition_id={competition_id} and table.competition_participant_id={competition_participant_id}"))

                total = 0
                eclectic_hole_ids = []
                for hole in range(1,18):
                    hole_id = eclectic_df[f'hole{hole}'].tolist()[0]
                    if hole_id is not None:
                        eclectic_hole_ids.append(hole_id)

                hole_ids = ','.join([str(x) for x in eclectic_hole_ids])
                scoring_holes_df = pd.DataFrame(sql.scoring_holes().read(filter=f"WHERE table.id IN ({hole_ids})"))        
                total = scoring_holes_df['points'].sum()
                #print(f'Total: {total}')
                
                fields = ['total']
                values = [total]
                sql.eclectics().update(id=eclectic_id, fields=fields, values=values)
                                     
        def st_player(self, hole_number=None):            
            if hole_number is None:
                hole_number = st.session_state.hole_number
            participant_df = self.participant_df
            participant_id = participant_df['id'].tolist()[0]
            participant_name = participant_df['name'].tolist()[0]
            handicap = participant_df['handicap'].tolist()[0]            
            
            hole_stroke = self.course_tee_df[f't{hole_number}_stroke'].tolist()[0]
            hole_par = self.course_tee_df[f't{hole_number}_par'].tolist()[0]
            hole_distance = self.course_tee_df[f't{hole_number}_distance'].tolist()[0]
            strokes = int(handicap/18) + int(hole_stroke<=(handicap-(int(handicap/18)*18)))
            
            exp = st.expander(label=f'{participant_name} _:blue[({strokes} HC stroke)]_', expanded=True)
            con = exp.container(horizontal=True, width='stretch', horizontal_alignment='distribute', vertical_alignment='bottom')            
            
            # dynamic widgets keys
            shots_keyname = f'scoring_card_player_{participant_id}_{participant_name}_holescore'
            points_keyname = f'scoring_card_player_{participant_id}_{participant_name}_holepoints'           
            
            st_shots = con.number_input(label='Shots', key=shots_keyname,
                                        value=self.hole_shots,                            
                                        on_change=self.shots,
                                        min_value=0, max_value=9, placeholder='Enter')
            
            if points_keyname in st.session_state:
                st.session_state[points_keyname] = self.hole_points
            st_points = con.number_input(label='Points', key=points_keyname, format="%d",
                                         value=self.hole_points,                                                                                         
                                         min_value=0, max_value=9, disabled=True)
  
  
class ScoringCardsMatches():
    obj = None
    df = None
    groups_sql = None
    groups_df = None
    participants_sql = None
    participants_df = None
    matches_sql = None
    matches_df = None
    child_page = None
    
    def __init__(self, df=None):
        self.df = df
        self.groups_sql = sql.match_groups()
        self.participants_sql = sql.match_participants()
        self.matches_sql = sql.matches()
        
        scoring_card_groups_sql = sql.scoring_card_groups()
        scoring_card_groups_df = pd.DataFrame(scoring_card_groups_sql.read(filter=f"WHERE table.scoring_card_id={self.df['id'].tolist()[0]}"))
        if not scoring_card_groups_df.empty: scoring_card_groups_df = scoring_card_groups_df.sort_values(by='name')
            
        scoring_card_participants_sql = sql.scoring_card_participants()
        scoring_card_participants_df = pd.DataFrame(scoring_card_participants_sql.read(filter=f"WHERE table.scoring_card_id={self.df['id'].tolist()[0]}"))
        if not scoring_card_participants_df.empty: scoring_card_participants_df = scoring_card_participants_df.sort_values(by=['scoring_card_groups_name','name'])
        
        sc_event_id = df['event_id'].tolist()[0]
        #sc_event_participants_df = scoring_card_participants_df['event_participant_id'].tolist()
        sc_event_participants_ids = ','.join([str(x) for x in scoring_card_participants_df['event_participant_id'].tolist()])
        #print(sc_event_participants_ids)
        
        self.participants_df = pd.DataFrame(self.participants_sql.read(filter=f"WHERE table.event_participant_id IN ({sc_event_participants_ids})"))
        if not self.participants_df.empty:
            sc_match_ids = ','.join([str(x) for x in self.participants_df['match_id'].tolist()])
            self.matches_df = pd.DataFrame(self.matches_sql.read(filter=f"WHERE table.id IN ({sc_match_ids})"))
            if not self.matches_df.empty: self.matches_df = self.matches_df.sort_values(by=['sequence', 'name'])
        else: self.matches_df = pd.DataFrame()
        
    def st(self):
        if not self.matches_df.empty:
            exp = st.expander(label='Matches', expanded=True)
            for match_id in self.matches_df['id'].tolist():
                with exp:
                    match_df = self.matches_df.query(f"id == {match_id}")
                    match = st_MatchInfo(match_df=match_df)
                    match.st_obj()
        
    #def st_match(self, match_df=None):        
    #    st_matchinfo = st_MatchInfo(match_df=match_df)


# Populate page 
st.subheader(f"Scoring Card: {st.session_state.scoring_card['name'].tolist()[0]}")

st_details = ScoringCardDetails(df=st.session_state.scoring_card)

st_groups_participants = ScoringCardGroupParticipants(df=st.session_state.scoring_card)

if st_groups_participants.configured:
    st_matches = ScoringCardsMatches(df=st.session_state.scoring_card)

    st_scoring = ScoringCardScoring(df=st.session_state.scoring_card, matches_df=st_matches.matches_df)

    st_matches.st()
    
    st_scorecard = ScoringCardsDisplay(df=st.session_state.scoring_card, matches_df=st_matches.matches_df)
