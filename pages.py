import streamlit as st

class Pages():
    stat_pages = {}
    dyn_pages = {}
    
    def __init__(self):
        # Static Pages
        campaigns_page = st.Page('app_pages/campaigns/campaigns_overview.py', title='Campaigns', default=True)
        courses_page = st.Page('app_pages/courses/courses_overview.py', title='Courses')
        course_tees_page = st.Page('app_pages/course_tees/course_tees_overview.py', title='Course Tees')
        groups_page = st.Page('app_pages/groups/groups_overview.py', title='Groups')
        participants_page = st.Page('app_pages/participants/participants_overview.py', title='Participants')
                                    
        competitions_page = st.Page('app_pages/competitions/competitions_overview.py', title='Competitions')
        events_page = st.Page('app_pages/events/events_overview.py', title='Events')
        scoring_cards_page = st.Page('app_pages/scoring_cards/scoring_cards_overview.py', title='Scoring Cards')

        db_page = st.Page('app_pages/db/db_overview.py', title='Database')

        self.stat_pages = { 
                'General': [
                    campaigns_page,
                    courses_page,
                    groups_page,
                    participants_page,
                    db_page,
                ],
                #'Tables': [
                    #competitions_page,
                    #events_page,
                    #scoring_cards_page,
                    #course_tees_page,
                #    ],
                }

    def dyn_pages_refresh(self):
        # Dynamic Pages
        dyn_pages = {}
        pages = list()
        title = str()
        if st.session_state.group is not None:
            groups_detail_page = st.Page('app_pages/groups/groups_detail.py', title=st.session_state.group['name'].tolist()[0])
            pages.append(groups_detail_page)
        if st.session_state.participant is not None:
            participants_detail_page = st.Page('app_pages/participants/participants_detail.py', title=st.session_state.participant['name'].tolist()[0])
            pages.append(participants_detail_page)
        if st.session_state.course is not None:
            course_detail_page = st.Page('app_pages/courses/courses_detail.py', title=st.session_state.course['name'].tolist()[0])
            pages.append(course_detail_page)
        if st.session_state.course_tee is not None:
            course_tee_detail_page = st.Page('app_pages/course_tees/course_tees_detail.py', title=st.session_state.course_tee['name'].tolist()[0])
            pages.append(course_tee_detail_page)
        if st.session_state.campaign is not None:
            campaign_detail_page = st.Page('app_pages/campaigns/campaigns_detail.py', title=st.session_state.campaign['name'].tolist()[0])
            pages.append(campaign_detail_page)
        if st.session_state.competition is not None:
            competitions_detail_page = st.Page('app_pages/competitions/competitions_detail.py', title=st.session_state.competition['name'].tolist()[0])
            pages.append(competitions_detail_page)
        if st.session_state.event is not None:
            events_detail_page = st.Page('app_pages/events/events_detail.py', title=st.session_state.event['name'].tolist()[0])
            pages.append(events_detail_page)
        if st.session_state.scoring_card is not None:
            scoring_cards_detail_page = st.Page('app_pages/scoring_cards/scoring_cards_detail.py', title=st.session_state.scoring_card['name'].tolist()[0])
            pages.append(scoring_cards_detail_page)
        #if st.session_state.sequence is not None:
        #    sequences_detail_page = st.Page('app_pages/sequences/sequences_detail.py', title=st.session_state.sequence[1])
        #    pages.append(sequences_detail_page)

        self.dyn_pages = {
            'Active': pages,
        }