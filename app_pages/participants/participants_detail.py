import streamlit as st
import pandas as pd
import sql

def highlight_max(styler, columns=None):
            for column in columns:
                styler.highlight_max(color='green', axis=0, subset=[column])
            return styler

class ParticipantDetails():
    obj = None
    df_sql = None
    df = None
    parent_page = None
           
    def __init__(self, df=None):
        self.obj = st.expander(label='Details', expanded=True)
        self.df_sql = sql.participants()
        self.df = df
        df_id = df['id'].tolist()[0]
        
        self.parent_page = "app_pages/participants/participants_overview.py"
        if self.df is not None:
            with self.obj:
                st_name = st.text_input('Name', key=f'course_details_{df_id}_name', value=f'{self.df['name'].tolist()[0]}')
                st_description = st.text_area('Description', key=f'course_details_{df_id}_description', value=f'{self.df['description'].tolist()[0]}')
                st_active = st.toggle(label='Active', value=df['active'].tolist()[0], key=f'course_details_{df_id}_active')
                buttons_area = st.container(horizontal=True)
                if st.user.email in st.secrets["superusers"]["emails"]:
                    with buttons_area:
                        if st.button(label='', icon=':material/check:', key='participant_details_update'):
                            self.update(name=st_name, description=st_description, active=st_active)
                        if st.button(label='', icon=':material/delete:', key='participant_details_delete', disabled=True):
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
            
            if st.button(label='', icon=':material/check:'):
                fields = ['name', 'description', 'active']
                values = [name, description, active]
                self.df_sql.update(id=self.df['id'].tolist()[0], fields=fields, values=values)
                st.session_state.participant = self.df_sql.read(filter=f"WHERE table.id={self.df['id'].tolist()[0]}")
                
                if st_update_all == 'All':
                    self.update_downstream()
                    
                st.rerun()
    
    def update_downstream(self):
        if st.session_state.participant is None:
            return
        df = st.session_state.participant
        df_id = df['id'].tolist()[0]
        df_name = df['name'].tolist()[0]
        df_description = df['description'].tolist()[0]
        df_active = df['active'].tolist()[0]
        
        # Update each campaign participant
        campaign_participants_sql = sql.campaign_participants()
        campaign_participants_df = pd.DataFrame(campaign_participants_sql.read(filter=f"WHERE table.participant_id = {df_id}"))
        if not campaign_participants_df.empty:
            for campaign_participant_id in campaign_participants_df['id'].tolist():
                fields = ['name', 'description', 'active']
                values = [df_name, df_description, df_active]
                campaign_participants_sql.update(id=campaign_participant_id, fields=fields, values=values)
                
                # Update each competition participant
                competition_participants_sql = sql.competition_participants()
                competition_participants_df = pd.DataFrame(competition_participants_sql.read(filter=f"WHERE table.campaign_participant_id = {campaign_participant_id}"))
                if not competition_participants_df.empty:
                    for competition_participant_id in competition_participants_df['id'].tolist():
                        competition_participants_sql.update(id=competition_participant_id, fields=fields, values=values)
                
                        # Update each event participant
                        event_participants_sql = sql.event_participants()
                        event_participants_df = pd.DataFrame(event_participants_sql.read(filter=f"WHERE table.competition_participant_id = {competition_participant_id}"))
                        if not event_participants_df.empty:
                            for event_participant_id in  event_participants_df['id'].tolist():
                                event_participants_sql.update(id=event_participant_id, fields=fields, values=values)
                                
                                # Update each scoring card participant
                                scoring_participants_sql = sql.scoring_card_participants()
                                scoring_participants_df = pd.DataFrame(scoring_participants_sql.read(filter=f"WHERE table.event_participant_id = {event_participant_id}"))
                                if not scoring_participants_df.empty:
                                    for scoring_participant_id in scoring_participants_df['id'].tolist():
                                        scoring_participants_sql.update(id=scoring_participant_id, fields=fields, values=values)
                    
                                # Update each match participant
                                match_participants_sql = sql.match_participants()
                                match_participants_df = pd.DataFrame(match_participants_sql.read(filter=f"WHERE table.event_participant_id = {event_participant_id}"))
                                if not match_participants_df.empty:
                                    for match_participant_id in match_participants_df['id'].tolist():
                                        match_participants_sql.update(id=match_participant_id, fields=fields, values=values)
     
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


class IndividualStats():
    campaigns_df = None
    competitions_df = None
    events_df = None
    cards_df = None
    rounds_df = None
    tees_df = None
    courses_df = None
    holes_df = None
    
    def __init__(self, df=None):
        df_id = df['id'].tolist()[0]
        
        # Campaigns
        campaign_participants_sql = sql.campaign_participants()
        campaign_participants_df = pd.DataFrame(campaign_participants_sql.read(filter=f"WHERE table.participant_id = {df_id}"))
        if not campaign_participants_df.empty: campaign_participants_ids_str = ','.join([str(x) for x in campaign_participants_df['id'].tolist()])
        else: return
        campaigns_ids_str = ','.join([str(x) for x in campaign_participants_df['campaign_id'].tolist()])
        campaigns_sql = sql.campaigns()
        self.campaigns_df = campaigns_df = pd.DataFrame(campaigns_sql.read(filter=f"WHERE table.id IN ({campaigns_ids_str})"))
        
        # Competitions
        competition_participants_sql = sql.competition_participants()
        competition_participants_df = pd.DataFrame(competition_participants_sql.read(filter=f"WHERE table.campaign_participant_id IN ({campaign_participants_ids_str})"))
        if not competition_participants_df.empty: competition_participants_ids_str = ','.join([str(x) for x in competition_participants_df['id'].tolist()])
        else: return
        competitions_ids_str = ','.join([str(x) for x in competition_participants_df['competition_id'].tolist()])
        competitions_sql = sql.competitions()
        self.competitions_df = competitions_df = pd.DataFrame(competitions_sql.read(filter=f"WHERE table.id IN ({competitions_ids_str}) AND table.active = 0"))
        
        # Events
        event_participants_sql = sql.event_participants()
        event_participants_df = pd.DataFrame(event_participants_sql.read(filter=f"WHERE table.competition_participant_id IN ({competition_participants_ids_str}) AND table.active = 0"))
        if not event_participants_df.empty: event_participants_ids_str = ','.join([str(x) for x in event_participants_df['id'].tolist()])
        else: return
        event_ids_str = ','.join([str(x) for x in event_participants_df['event_id'].tolist()])
        events_sql = sql.events()
        self.events_df = events_df = pd.DataFrame(events_sql.read(filter=f"WHERE table.id IN ({event_ids_str}) AND table.active = 0"))
        
        # Scoring Cards.
        scoring_card_participants_sql = sql.scoring_card_participants()
        scoring_card_participants_df = pd.DataFrame(scoring_card_participants_sql.read(filter=f"WHERE table.event_participant_id IN ({event_participants_ids_str}) AND table.active = 0"))
        if not scoring_card_participants_df.empty: scoring_card_participants_ids_str = ','.join([str(x) for x in scoring_card_participants_df['id'].tolist()])
        else: return
        cards_ids_str = ','.join([str(x) for x in scoring_card_participants_df['scoring_card_id'].tolist()])
        cards_sql = sql.scoring_cards()
        self.cards_df = cards_df = pd.DataFrame(cards_sql.read(filter=f"WHERE table.id IN ({cards_ids_str}) AND table.active = 0"))
        
        # Scoring Rounds
        rounds_sql = sql.scoring_rounds()
        self.rounds_df = rounds_df = pd.DataFrame(rounds_sql.read(filter=f"WHERE table.scoring_card_participant_id in ({scoring_card_participants_ids_str}) AND table.active = 0"))
        if not rounds_df.empty: rounds_ids_str = ','.join([str(x) for x in rounds_df['id'].tolist()])
        else: return
        course_tees_ids_str = ','.join([str(x) for x in rounds_df['course_tee_id'].tolist()])
        
        # Course Tees
        course_tees_sql = sql.course_tees()
        self.tees_df = course_tees_df = pd.DataFrame(course_tees_sql.read(filter=f"WHERE table.id IN ({course_tees_ids_str})"))
        courses_ids_str = ','.join([str(x) for x in course_tees_df['course_id'].tolist()])
        
        # Courses
        courses_sql = sql.courses()
        self.courses_df = courses_df = pd.DataFrame(courses_sql.read(filter=f"WHERE table.id IN ({courses_ids_str})"))
        
        # Scoring Holes
        holes_sql = sql.scoring_holes()
        self.holes_df = holes_df = pd.DataFrame(holes_sql.read(filter=f"WHERE table.scoring_round_id IN ({rounds_ids_str})"))
        if not holes_df.empty: holes_ids_str = ','.join([str(x) for x in holes_df['id'].tolist()])
        
        # Combine parent data
        holes_df['HC'] = None
        holes_df['Par'] = None
        holes_df['Stroke'] = None
        holes_df['course_tee_id'] = None
        holes_df['card_id'] = None
        holes_df['course_id'] = None
        holes_df['event_id'] = None
        holes_df['event_sequence'] = None
        holes_df['competition_id'] = None
        holes_df['competition_sequence'] = None
        holes_df['campaign_id'] = None
        for index, hole_id in enumerate(holes_df['id'].tolist()):
            hole_df = holes_df.query(f'id=={hole_id}')
            hole_num = int(hole_df['number'].tolist()[0])
            round_id = hole_df['scoring_round_id'].tolist()[0]
            round_df = rounds_df.query(f'id=={round_id}')
            
            card_id = round_df['scoring_card_id'].tolist()[0]
            card_participant_id = round_df['scoring_card_participant_id'].tolist()[0]
            course_tee_id = round_df['course_tee_id'].tolist()[0]
            card_df = cards_df.query(f'id=={card_id}')
            course_tee_df = course_tees_df.query(f'id=={course_tee_id}')
            
            event_id = card_df['event_id'].tolist()[0]
            course_id = card_df['course_id'].tolist()[0]
            card_participant_df = scoring_card_participants_df.query(f'id=={card_participant_id}')
            event_df = events_df.query(f'id=={event_id}')
            #course_df = course
            
            event_sequence = event_df['sequence'].tolist()[0]
            competition_id = event_df['competition_id'].tolist()[0]
            competition_df = competitions_df.query(f'id=={competition_id}')
            
            competition_sequence = competition_df['sequence'].tolist()[0]
            campaign_id = competition_df['campaign_id'].tolist()[0]
            
            holes_df.at[hole_id, 'HC'] = card_participant_df['handicap'].tolist()[0]
            holes_df.at[hole_id, 'Par'] = course_tee_df[f't{hole_num}_par'].tolist()[0]
            holes_df.at[hole_id, 'Stroke'] = course_tee_df[f't{hole_num}_stroke'].tolist()[0]
            holes_df.at[hole_id, 'course_tee_id'] = course_tee_id
            holes_df.at[hole_id, 'card_id'] = card_id
            holes_df.at[hole_id, 'course_id'] = course_id
            holes_df.at[hole_id, 'event_id'] = event_id
            holes_df.at[hole_id, 'event_sequence'] = event_sequence
            holes_df.at[hole_id, 'competition_id'] = competition_id
            holes_df.at[hole_id, 'competition_sequence'] = competition_sequence
            holes_df.at[hole_id, 'campaign_id'] = campaign_id
        
        #print(holes_df)

        exp_main = st.expander("Individual stats", expanded=True)
        
        with exp_main:
            self.st_campaigns(holes_df=holes_df)
            self.st_competitions(holes_df=holes_df)
            self.st_rounds(holes_df=holes_df)
    
    def st_campaigns(self, holes_df=None):
        exp = st.expander(label='Campaigns')
        df = pd.DataFrame()#columns=['date', 'shots', 'points'])
        indexes = holes_df.groupby(['campaign_id']).sum().index.tolist()
        #print(indexes)
        
        campaigns_ids = indexes
        
        df['campaign'] = [self.campaigns_df.query(f'id=={x}')['name'].tolist()[0] for x in campaigns_ids]
        
        df['shots'] = holes_df.groupby(['campaign_id']).sum()['shots'].tolist()
        df['points'] = holes_df.groupby(['campaign_id']).sum()['points'].tolist()
        
        rounds_list = holes_df.groupby(['campaign_id', 'scoring_round_id']).count().groupby(level=0).count()['points'].tolist()
        df['rounds_count'] = rounds_list
        df['average'] = [a / b for a, b in zip(holes_df.groupby(['campaign_id']).sum()['points'].tolist(), rounds_list)]
                    
        df['Par 3'] = holes_df.query('Par==3').groupby(['campaign_id'])['points'].mean().tolist()
        df['Par 4'] = holes_df.query('Par==4').groupby(['campaign_id'])['points'].mean().tolist()
        df['Par 5'] = holes_df.query('Par==5').groupby(['campaign_id'])['points'].mean().tolist()
        
        df['OUT'] = holes_df.query('number<=9').groupby(['campaign_id']).sum()['points'].tolist() / df['rounds_count']
        df['IN'] = holes_df.query('number>9').groupby(['campaign_id']).sum()['points'].tolist() / df['rounds_count']
        
        df = df.sort_values(['campaign'], ascending=False)
        
        column_config = {key: None for key in df.columns.to_list()}
        column_config['campaign'] = st.column_config.TextColumn(label='Campaign')
        column_config['shots'] = st.column_config.NumberColumn(label='Shots', format="%d")
        column_config['points'] = st.column_config.NumberColumn(label='Points', format="%d")
        column_config['average'] = st.column_config.NumberColumn(label='Points  µ', format="%.2f")
        column_config['Par 3'] = st.column_config.NumberColumn(label='Par 3 µ', format="%.2f")
        column_config['Par 4'] = st.column_config.NumberColumn(label='Par 4 µ', format="%.2f")
        column_config['Par 5'] = st.column_config.NumberColumn(label='Par 5 µ', format="%.2f")
        column_config['OUT'] = st.column_config.NumberColumn(label='Out µ', format="%.2f")
        column_config['IN'] = st.column_config.NumberColumn(label='In µ', format="%.2f")
        
        exp.dataframe(data=df, hide_index=True, column_config=column_config)
    
    def st_competitions(self, holes_df=None):
        exp = st.expander(label='Competitions')
        df = pd.DataFrame()#columns=['date', 'shots', 'points'])
        indexes = holes_df.groupby(['competition_id']).sum().index.tolist()
        #print(indexes)
        
        campaigns_ids = holes_df.groupby(['competition_id'])['campaign_id'].mean().tolist()
        
        df['campaign'] = [self.campaigns_df.query(f'id=={x}')['name'].tolist()[0] for x in campaigns_ids]
        df['competition'] = [self.competitions_df.query(f'id=={x}')['name'].tolist()[0] for x in indexes]
        
        df['shots'] = holes_df.groupby(['competition_id']).sum()['shots'].tolist()
        df['points'] = holes_df.groupby(['competition_id']).sum()['points'].tolist()
        
        rounds_list = self.events_df.groupby(['competition_id']).count()['id'].tolist()
        df['rounds_count'] = rounds_list
        df['average'] = [a / b for a, b in zip(holes_df.groupby(['competition_id']).sum()['points'].tolist(), rounds_list)]
        
        #test = holes_df.groupby(['competition_id', 'scoring_round_id']).count().groupby(level=0).count()['points'].tolist()
        #print(test)
        
        df['Par 3'] = holes_df.query('Par==3').groupby(['competition_id'])['points'].mean().tolist()
        df['Par 4'] = holes_df.query('Par==4').groupby(['competition_id'])['points'].mean().tolist()
        df['Par 5'] = holes_df.query('Par==5').groupby(['competition_id'])['points'].mean().tolist()
        
        df['OUT'] = holes_df.query('number<=9').groupby(['competition_id'])['points'].sum().tolist() / df['rounds_count']
        df['IN'] = holes_df.query('number>9').groupby(['competition_id'])['points'].sum().tolist() / df['rounds_count']
        
        df = df.sort_values(['competition'], ascending=False)
        
        columns = ['points', 'average', 'Par 3', 'Par 4', 'Par 5', 'OUT', 'IN']
        df = df.style.pipe(highlight_max, columns=columns)
        
        column_config = {key: None for key in df.columns.to_list()}
        column_config['campaign'] = st.column_config.TextColumn(label='Campaign')
        column_config['competition'] = st.column_config.TextColumn(label='Comp')
        column_config['shots'] = st.column_config.NumberColumn(label='Shots', format="%d")
        column_config['points'] = st.column_config.NumberColumn(label='Points', format="%d")
        column_config['average'] = st.column_config.NumberColumn(label='Points µ', format="%.2f")
        column_config['Par 3'] = st.column_config.NumberColumn(label='Par 3 µ', format="%.2f")
        column_config['Par 4'] = st.column_config.NumberColumn(label='Par 4 µ', format="%.2f")
        column_config['Par 5'] = st.column_config.NumberColumn(label='Par 5 µ', format="%.2f")
        column_config['OUT'] = st.column_config.NumberColumn(label='Out µ', format="%.2f")
        column_config['IN'] = st.column_config.NumberColumn(label='In µ', format="%.2f")
        
        exp.dataframe(data=df, hide_index=True, column_config=column_config)
        
    def st_rounds(self, holes_df=None):
        exp = st.expander(label='Rounds')
        df = pd.DataFrame()#columns=['date', 'shots', 'points'])
        indexes = holes_df.groupby(['scoring_round_id']).sum().index.tolist()
        #print(indexes)

        campaigns_ids = holes_df.groupby(['scoring_round_id'])['campaign_id'].mean().tolist()
        competitions_ids = holes_df.groupby(['scoring_round_id'])['competition_id'].mean().tolist()
        course_tees_ids = holes_df.groupby(['scoring_round_id'])['course_tee_id'].mean().tolist()
        courses_ids = holes_df.groupby(['scoring_round_id'])['course_id'].mean().tolist()

        df['date'] = self.cards_df['date'].tolist()
        
        df['campaign'] = [self.campaigns_df.query(f'id=={x}')['name'].tolist()[0] for x in campaigns_ids]
        df['competition'] = [self.competitions_df.query(f'id=={x}')['name'].tolist()[0] for x in competitions_ids]
        df['Course'] = [self.courses_df.query(f'id=={x}')['name'].tolist()[0] for x in courses_ids]
        df['Tee'] = [self.tees_df.query(f'id=={x}')['name'].tolist()[0] for x in course_tees_ids]

        df['hc_index'] = holes_df.groupby(['scoring_round_id'])['HC'].mean().tolist()
        df['shots'] = holes_df.groupby(['scoring_round_id']).sum()['shots'].tolist()
        df['points'] = holes_df.groupby(['scoring_round_id']).sum()['points'].tolist()
        
        df['Par 3'] = holes_df.query('Par==3').groupby(['scoring_round_id'])['points'].mean().tolist()
        df['Par 4'] = holes_df.query('Par==4').groupby(['scoring_round_id'])['points'].mean().tolist()
        df['Par 5'] = holes_df.query('Par==5').groupby(['scoring_round_id'])['points'].mean().tolist()
        
        df['OUT'] = holes_df.query('number<=9').groupby(['scoring_round_id']).sum()['points'].tolist()
        df['IN'] = holes_df.query('number>9').groupby(['scoring_round_id']).sum()['points'].tolist()
        
        df = df.sort_values(['date'], ascending=False)
        
        columns = ['points', 'Par 3', 'Par 4', 'Par 5', 'OUT', 'IN']
        df = df.style.pipe(highlight_max, columns=columns)
        
        column_config = {key: None for key in df.columns.to_list()}
        column_config['date'] = st.column_config.TextColumn(label='Date')
        column_config['campaign'] = st.column_config.TextColumn(label='Campaign')
        column_config['competition'] = st.column_config.TextColumn(label='Comp')
        column_config['Course'] = st.column_config.TextColumn(label='Course')
        column_config['Tee'] = st.column_config.TextColumn(label='Tee')
        column_config['hc_index'] = st.column_config.NumberColumn(label='HC', format="%d")
        column_config['shots'] = st.column_config.NumberColumn(label='TOT', format="%d")
        column_config['points'] = st.column_config.NumberColumn(label='PTS', format="%d")
        column_config['Par 3'] = st.column_config.NumberColumn(format="%.2f")
        column_config['Par 4'] = st.column_config.NumberColumn(format="%.2f")
        column_config['Par 5'] = st.column_config.NumberColumn(format="%.2f")
        column_config['OUT'] = st.column_config.NumberColumn(format="%d")
        column_config['IN'] = st.column_config.NumberColumn(format="%d")
        
        exp.dataframe(data=df, hide_index=True, column_config=column_config)


class MatchStats():
    
    def __init__(self, df=None):
        pass
        # Campaigns
        
        # Competitions
        
        # Events
        
        # Match Rounds
        
        exp_main = st.expander("Match stats", expanded=True)
        with exp_main:
            st.text(body='Coming soon')


class EclecticStats():
    
    def __init__(self, df=None):
        pass
        # Campaigns
        
        # Competitions
        
        exp_main = st.expander("Eclectic stats", expanded=True)
        with exp_main:
            st.text(body='Coming soon')


# Populate page 
con = st.container(horizontal=True, vertical_alignment='center')

st_details = ParticipantDetails(df=st.session_state.participant)

st_individual_stats = IndividualStats(df=st.session_state.participant)

st_match_stats = MatchStats(df=st.session_state.participant)

st_eclectic_stats = EclecticStats(df=st.session_state.participant)

with con:
    if st.button(label='', icon=':material/arrow_back:'):
        st.session_state.participant = None
        st.session_state.page = st_details.parent_page
        st.rerun()
    st.subheader(f"Participant: {st.session_state.participant['name'].tolist()[0]}")