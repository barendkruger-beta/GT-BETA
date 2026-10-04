import streamlit as st
import sql

supabase_db = sql.get_supabase_admin()

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
    #print('Saving states')
    if 'user_participant_id' in st.session_state:
        participant_id = st.session_state.user_participant_id
        #print(f'participant_id: {participant_id}')
        if participant_id is not None:
            #session_states_sql = sql.participant_states()
            #session_states_df = session_states_sql.read(filter=f"WHERE table.participant_id = {participant_id}")
            session_states_df = sql.read_db(conn=supabase_db, table='participant_states', filter=[['participant_id', participant_id]], legacy=False)
            
            # Maintain saved states
            if not session_states_df.empty:
                for state_id in session_states_df['id'].tolist():
                    state_name = session_states_df.at[state_id, 'name']
                    state_value = session_states_df.at[state_id, 'value']
                    print(f"Saving {state_name} with value {state_value}")
                    
                    # Remove if state is None
                    if st.session_state[state_name] is None:
                        #session_states_sql.delete(id=state_id)
                        filter = [['id', state_id]]
                        sql.remove_db(conn=supabase_db, table='participant_states', filter=filter, legacy=False)

                    # Else update the state if it changed
                    else:
                        print(f"Type: {type(state_value)} Value: {state_value}")
                        if 'hole_number' in state_name:
                            cur_state_value = st.session_state[state_name]
                        else:
                            cur_state_value = st.session_state[state_name]['id'].tolist()[0]
                        if state_value != cur_state_value:
                            fields = ['name', 'value']
                            values = [state_name, cur_state_value]
                            #session_states_sql.update(id=state_id, fields=fields, values=values)
                            sql.write_db(conn=supabase_db, table='participant_states', entry_id=state_id, fields=fields, values=values)

            # Create new saved states if not None
            #session_states_df = session_states_sql.read(filter=f"WHERE table.participant_id = {participant_id}")
            session_states_df = sql.read_db(conn=supabase_db, table='participant_states', filter=[['participant_id', participant_id]], legacy=False)
            for state in states:
                #print(f'Checking state [{state}]')
                if state in st.session_state:
                    if st.session_state[state] is not None:
                        # Do not create if already maintained
                        if not session_states_df.empty:
                            if state in session_states_df['name'].tolist():
                                continue

                        if isinstance(st.session_state[state], int):
                            state_value = st.session_state[state]
                        else:
                            state_value = st.session_state[state]['id'].tolist()[0]
                            
                        fields = ['name', 'value', 'participant_id']
                        values = [state, state_value, st.session_state['user_participant_id'].item()]
                        #session_states_sql.add(fields=fields, values=values)
                        sql.write_db(conn=supabase_db, table='participant_states', fields=fields, values=values)
    else:
        print('No user_participant_id in session state')
   
def load_states():
    #print('Loading states')
    if 'user_participant_id' in st.session_state:
        participant_id = st.session_state.user_participant_id

        if participant_id is not None:
            #session_states_sql = sql.participant_states()
            #session_states_df = session_states_sql.read(filter=f"WHERE table.participant_id = {participant_id}")
            session_states_df = sql.read_db(conn=supabase_db, table='participant_states', filter=[['participant_id', participant_id]], legacy=False)
            #print(session_states_df)

            if not session_states_df.empty:
                for state_id in session_states_df['id'].tolist():
                    if session_states_df.at[state_id, 'name'] not in st.session_state:
                        #print(f'{session_states_df.at[state_id, 'name']} saved state has value: {session_states_df.at[state_id, 'value']}')
                        #table_sql = sql.SQLiteTable(table_name=session_states_df.at[state_id, 'name']+'s')
                        #table_df = table_sql.read(filter=f"WHERE table.id = {session_states_df.at[state_id, 'value']}")
                        if 'hole_number' in session_states_df.at[state_id, 'name']:
                            st.session_state[session_states_df.at[state_id, 'name']] = session_states_df.at[state_id, 'value']
                        else:
                            table_df = sql.read_db(conn=supabase_db, table=session_states_df.at[state_id, 'name']+'s', filter=[['id', session_states_df.at[state_id, 'value']]], legacy=False)
                            st.session_state[session_states_df.at[state_id, 'name']] = table_df
                        #print(st.session_state)
                    elif st.session_state[session_states_df.at[state_id, 'name']] is None:
                        #print(f'{session_states_df.at[state_id, 'name']} state has value: {session_states_df.at[state_id, 'value']}')
                        #table_sql = sql.SQLiteTable(table_name=session_states_df.at[state_id, 'name']+'s')
                        #table_df = table_sql.read(filter=f"WHERE table.id = {session_states_df.at[state_id, 'value']}")
                        if 'hole_number' in session_states_df.at[state_id, 'name']:
                            st.session_state[session_states_df.at[state_id, 'name']] = session_states_df.at[state_id, 'value']
                        else:
                            table_df = sql.read_db(conn=supabase_db, table=session_states_df.at[state_id, 'name']+'s', filter=[['id', session_states_df.at[state_id, 'value']]], legacy=False)
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

