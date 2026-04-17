import streamlit as st
import sql
import session_states
import pages
from datetime import datetime

def login_screen():
    st.header("Please log in")
    if st.button("Log in with Google"):
        st.login()

if not st.user.is_logged_in:
    # Show login screen
    login_screen()
else:
    # Initialize session states
    session_states.init()
    
    # Auto logout if session is older than x days
    max_days = 7
    #print(f'{st.user.to_dict()}\n\n')
    login_dt = datetime.fromtimestamp(st.user.iat)
    cur_dt = datetime.now()
    diff = cur_dt - login_dt
    if diff.days >= max_days:
        st.logout()
        st.rerun()

    # Initialize SQL database
    init = sql.init()
    
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