import streamlit as st
import sql
import session_states
import pages
from datetime import datetime
from supabase import create_client, Client


def login_screen():
    st.header("Please log in")
    if st.button("Log in with Google"):
        st.login()
    if st.button("Refresh"):
        st.rerun()

def load_app():
    supabase_db = sql.get_supabase_admin()

    if 'user_participant_id' not in st.session_state:
        # Load user participant_id from database
        if st.user.is_logged_in:
            user_email = st.user.email.lower()
            #user_sql = sql.users()
            #user_df = user_sql.read(filter=f"WHERE table.email = '{user_email}'")
            user_df = sql.read_db(conn=supabase_db, table='participants', filter=[['email', user_email]], legacy=False)
            if not user_df.empty:
                st.session_state.user_participant_id = user_df.at[user_df.index[0], 'id']
                print(f'Loaded user_participant_id: {st.session_state.user_participant_id}')
                if user_email in st.secrets.superusers.emails:
                    st.session_state.global_admin = True
                    print(f'Super User: {user_df['name'].tolist()[0]}')
                else:
                    st.session_state.global_admin  = False
            else:
                print(f'No user found for email: {user_email}')
        else:
            print('User is not logged in')
    
    # Initialize session states
    session_states.init()
    session_states.load_states()
    
    # Auto logout if session is older than x days
    max_days = 7
    #print(f'{st.user.to_dict()}\n\n')
    login_dt = datetime.fromtimestamp(st.user.iat)
    cur_dt = datetime.now()
    diff = cur_dt - login_dt
    if diff.days >= max_days:
        st.logout()
        st.rerun()
   
    # Page navigation
    app_pages = pages.Pages()
    app_pages.dyn_pages_refresh()
    pg = st.navigation(app_pages.dyn_pages | app_pages.stat_pages)
    if "page" in st.session_state:
        if st.session_state.page is not None:
            page = st.session_state.page
            #print(page)
            st.session_state.page = None
            st.switch_page(page)                
    pg.run()


if not st.user.is_logged_in:
    # Show login screen
    login_screen()
else:
    conn = load_app()