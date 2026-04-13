import streamlit as st
import pandas as pd
import sql


class CourseDetails():
    obj = None
    df_sql = None
    df = None
    parent_page = None
           
    def __init__(self, df=None):
        self.obj = st.expander(label='Details')
        self.df_sql = sql.courses()
        self.df = df
        df_id = df['id'].tolist()[0]
        
        self.parent_page = "app_pages/courses/courses_overview.py"
        if self.df is not None:
            with self.obj:
                st_name = st.text_input('Name', key=f'course_details_{df_id}_name', value=f'{self.df['name'].tolist()[0]}')
                st_description = st.text_area('Description', key=f'course_details_{df_id}_description', value=f'{self.df['description'].tolist()[0]}')
                st_active = st.toggle(label='Active', value=df['active'].tolist()[0], key=f'course_details_{df_id}_active')
                buttons_area = st.container(horizontal=True)
                if st.user.email == 'barendkruger@gmail.com':
                    with buttons_area:
                        if st.button(label='', icon=':material/check:', key='course_details_update'):
                            self.update(name=st_name, description=st_description, active=st_active)
                        if st.button(label='', icon=':material/delete:', key='course_details_delete'):
                            self.delete()                        
    
    def update(self, name=None, description=None, active=None):
        if self.df is not None:
            fields = ['name', 'description', 'active']
            values = [name, description, active]
            self.df_sql.update(id=self.df['id'].tolist()[0], fields=fields, values=values)
            st.session_state.course = self.df_sql.read(filter=f"WHERE table.id={self.df['id'].tolist()[0]}")
            st.rerun()
            
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


class CourseCourseTees():
    obj = None
    course_sql = None
    course_df = None
    course_tees_sql = None
    course_tees_df = None
    child_page = None    
    
    def __init__(self, course_df=None):
        self.child_page = "app_pages/course_tees/course_tees_detail.py"
        
        self.course_df = course_df
        self.course_tees_sql = sql.course_tees()
        self.course_tees_df = pd.DataFrame(self.course_tees_sql.read(filter=f"WHERE course_id={course_df['id'].tolist()[0]}"))
        if not self.course_tees_df.empty: self.course_tees_df = self.course_tees_df.sort_values(by='name')
        
        exp_course_tees = st.expander("Tees", expanded=True)
        with exp_course_tees:   
            col = st.container(horizontal=True, width='stretch')

            with col:
                if st.button(label='', icon=':material/add_2:', disabled=not st.user.email == 'barendkruger@gmail.com'): self.add(course_df['id'].tolist()[0])

            column_config = {key: None for key in self.course_tees_df.columns.to_list()}
            column_config['name'] = 'Name'
            column_config['description'] = 'Description'
            column_config['t_par'] = 'Par'
            column_config['t_rating'] = 'Rating'
            column_config['t_slope'] = 'Slope'
            column_config['t_distance'] = 'Distance'
            event = st.dataframe(
                self.course_tees_df,
                on_select='rerun',
                selection_mode='single-row',
                hide_index=True,
                column_config=column_config
            )
            #print(self.course_tees_df)
            if len(event.selection['rows']):
                selected_row = event.selection['rows'][0]
                id = self.course_tees_df.iloc[selected_row]['id']
                sel = self.course_tees_df[self.course_tees_df['id'] == id]
                if col.button(label='', icon=':material/jump_to_element:'):
                    self.open(sel, self.child_page)
            else:
                col.button(label='', icon=':material/jump_to_element:', disabled=True)
                
    # Add dialog
    @st.dialog("Add")
    def add(self, course_id=None):
        name = st.text_input("Name")
        description = st.text_input("Description")
        if st.button("Submit"):
            fields = ["name", "description", "course_id"]
            values = [name, description, course_id]
            self.course_tees_sql.add(fields=fields, values=values)
            st.rerun()
            
    # Open detail page            
    def open(self, sel, page):
        st.session_state.course_tee = sel
        
        st.session_state.page = page    
        st.rerun()



# Populate page 
con = st.container(horizontal=True, vertical_alignment='center')

st_details = CourseDetails(df=st.session_state.course)

st_course_tees = CourseCourseTees(course_df=st.session_state.course)

with con:
    if st.button(label='', icon=':material/arrow_back:'):
        st.session_state.course = None
        st.session_state.page = st_details.parent_page
        st.rerun()
    st.subheader(f"Course: {st.session_state.course['name'].tolist()[0]}")