import streamlit as st
import sql


states = [
    'group',
    'participant',
    'campaign',
    'competition',
    'event',
    'scoring_card',
    'hole_number',
    'course',
    'course_tee',
    ]

local_states = [
    'user_participant_id',
    'global_admin',
    ]

def save_states():
    print('Saving states')
    if 'user_participant_id' in st.session_state:
        participant_id = st.session_state.user_participant_id
        if participant_id is not None:
            session_states_sql = sql.participant_states()
            session_states_df = session_states_sql.read(filter=f"WHERE table.participant_id = {participant_id}")
            
            # Maintain saved states
            if session_states_df is not None:
                for state_id in session_states_df['id'].tolist():
                    state_name = session_states_df.at[state_id, 'name']
                    state_value = session_states_df.at[state_id, 'value']
                    
                    # Remove if state is None
                    if st.session_state[state_name] is None:
                        session_states_sql.delete(id=state_id)

                    # Else update the state if it changed
                    elif state_value != st.session_state[state_name]['id'].tolist()[0]:
                        fields = ['name', 'value']
                        values = [state, state_id]
                        session_states_sql.update(id=state_id, fields=fields, values=values)

            # Create new saved states if not None
            session_states_df = session_states_sql.read(filter=f"WHERE table.participant_id = {participant_id}")
            for state in states:
                if state in st.session_state:
                    if st.session_state[state] is not None:
                        # Do not create if already maintained
                        if session_states_df is not None:
                            if state in session_states_df['name'].tolist():
                                continue

                        fields = ['name', 'value', 'participant_id']
                        values = [state, st.session_state[state]['id'].tolist()[0], st.session_state['user_participant_id']]
                        session_states_sql.add(fields=fields, values=values)
   
def load_states():
    print('Loading states')
    if 'user_participant_id' in st.session_state:
        participant_id = st.session_state.user_participant_id

        if participant_id is not None:
            session_states_sql = sql.participant_states()
            session_states_df = session_states_sql.read(filter=f"WHERE table.participant_id = {participant_id}")
            #print(session_states_df)

            if session_states_df is not None:
                for state_id in session_states_df['id'].tolist():
                    if session_states_df.at[state_id, 'name'] not in st.session_state:
                        #print(f'{session_states_df.at[state_id, 'name']} saved state has value: {session_states_df.at[state_id, 'value']}')
                        table_sql = sql.SQLiteTable(table_name=session_states_df.at[state_id, 'name']+'s')
                        table_df = table_sql.read(filter=f"WHERE table.id = {session_states_df.at[state_id, 'value']}")
                        st.session_state[session_states_df.at[state_id, 'name']] = table_df
                        #print(st.session_state)
                    elif st.session_state[session_states_df.at[state_id, 'name']] is None:
                        #print(f'{session_states_df.at[state_id, 'name']} state has value: {session_states_df.at[state_id, 'value']}')
                        table_sql = sql.SQLiteTable(table_name=session_states_df.at[state_id, 'name']+'s')
                        table_df = table_sql.read(filter=f"WHERE table.id = {session_states_df.at[state_id, 'value']}")
                        st.session_state[session_states_df.at[state_id, 'name']] = table_df
                        #print(st.session_state)

def init():
    print('Initializing states')
    for state in local_states:
        if state not in st.session_state:
            st.session_state[state] = None
    for state in states:
        if state not in st.session_state:
            st.session_state[state] = None

