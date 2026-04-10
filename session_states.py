import streamlit as st

def init():
    if "group" not in st.session_state:
        st.session_state.group = None    
    group = st.session_state.group
    
    if "participant" not in st.session_state:
        st.session_state.participant = None    
    participant = st.session_state.participant

    if "global_admin" not in st.session_state:
        st.session_state.global_admin = None    
    global_admin = st.session_state.global_admin
            
    if "campaign" not in st.session_state:
        st.session_state.campaign = None
    campaign = st.session_state.campaign

    if "competition" not in st.session_state:
        st.session_state.competition = None    
    competition = st.session_state.competition
        
    if "event" not in st.session_state:
        st.session_state.event = None    
    event = st.session_state.event

    if "scoring_card" not in st.session_state:
        st.session_state.scoring_card = None    
    scoring_card = st.session_state.scoring_card

    if "hole_number" not in st.session_state:
        st.session_state.hole_number = None
    hole_number = st.session_state.hole_number
    
    if "course" not in st.session_state:
        course = st.session_state.course = None
    
    if "course_tee" not in st.session_state:
        course_tee = st.session_state.course_tee = None
