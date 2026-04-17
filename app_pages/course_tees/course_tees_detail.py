import streamlit as st
import pandas as pd
import sql
import math

class CourseTeeDetails():
    obj = None
    df_sql = None
    df = None
    parent_page = None
           
    def __init__(self, df=None):
        self.obj = st.expander(label='Details')
        self.df_sql = sql.course_tees()
        self.df = df
        df_id = df['id'].tolist()[0]
        self.parent_page = "app_pages/courses/courses_detail.py"
        if self.df is not None:
            with self.obj:
                st_name = st.text_input('Name', key=f'course_tee_details_name', value=f'{self.df['name'].tolist()[0]}')
                st_description = st.text_area('Description', key=f'course_tee_details_description', value=f'{self.df['description'].tolist()[0]}')
                st_par = st.number_input(label='Par', value=self.df['t_par'].tolist()[0], disabled=False)
                st_rating = st.number_input(label='Rating', value=self.df['t_rating'].tolist()[0])
                st_slope = st.number_input(label='Slope', value=self.df['t_slope'].tolist()[0])
                st_active = st.toggle(label='Active', value=df['active'].tolist()[0], key=f'course_tee_details_{df_id}_active')
                
                buttons_area = st.container(horizontal=True)
                if st.user.email == 'barendkruger@gmail.com':
                    with buttons_area:
                        if st.button(label='', icon=':material/check:', key='course_tee_details_update'):
                            self.update(name=st_name, description=st_description, par=st_par, rating=st_rating, slope=st_slope, active=st_active)
                        if st.button(label='', icon=':material/delete:', key='course_tee_details_delete'):
                            self.delete()                        
        
    def update(self, name=None, description=None, par=None, rating=None, slope=None, active=None):
        if self.df is not None:
            fields = ['name', 'description', 't_par', 't_rating', 't_slope', 'active']
            values = [name, description, par, rating, slope, active]
            self.df_sql.update(id=self.df['id'].tolist()[0], fields=fields, values=values)
            st.session_state.course_tee = self.df_sql.read(filter=f"WHERE table.id={self.df['id'].tolist()[0]}")
            st.rerun()
            
    @st.dialog(title='Delete confirmation')        
    def delete(self):
        st.write("Are you sure you want to delete the entry?")
        area = st.container(horizontal=True, horizontal_alignment='center')
        with area:
            if st.button(label='Yes'):
                if self.df is not None:
                    self.df_sql.delete(id=self.df['id'].tolist()[0])
                    st.session_state.course_tee = None
                    st.session_state.page = self.parent_page
                    st.rerun()
            if st.button(label='No'):
                st.rerun()


class CourseTeeHoles():
    obj = None
    df_sql = None
    df = None
    card_df = None
    
    def __init__(self, df=None):
        self.obj = st.expander(label='Holes', expanded=True)
        
        self.df_sql = sql.course_tees()
        df_id = df['id'].tolist()[0]
        self.df = self.df_sql.read(f"WHERE table.id={df_id}")
        df_id = df['id'].tolist()[0]        

        self.card_df = self.load(df=self.df)
        
        with self.obj:
            st_form = st.form(key='course_tee_form', enter_to_submit=False, border=False)
            with st_form:
                st.data_editor(key='course_tee_data',
                            data=self.card_df,
                            hide_index=True,
                            #on_change=self.update,
                            column_config={"Number":st.column_config.TextColumn(disabled=True),
                                           "Par":st.column_config.NumberColumn(format="%d"),
                                           "Stroke":st.column_config.NumberColumn(format="%d"),
                                           "Distance":st.column_config.NumberColumn(format="%d"),
                                           #"Active":st.column_config.CheckboxColumn(),
                                           }
                            )
                if st.form_submit_button(label='', icon=':material/check:', disabled=not st.user.email == 'barendkruger@gmail.com'):
                    self.update()
                    st.rerun()
      
    def load(self, df):
        card_df = pd.DataFrame(columns=['Number', 'Par', 'Stroke', 'Distance'])        
        #card_df['Stroke'] = pd.to_numeric(card_df['Stroke'], errors='coerce').astype('Int64')
        par_out = par_in = par_tot = None
        dist_out = dist_in = dist_tot = None

        # OUT
        for hole in range(1,10):
            index = hole            
            par = df[f't{hole}_par'].tolist()[0]
            stroke = df[f't{hole}_stroke'].tolist()[0]
            distance = df[f't{hole}_distance'].tolist()[0]
            card_df.loc[index] = [str(hole), par, stroke, distance]
        card_df.loc[10] = ['OUT', None, None, None]

        # IN
        for hole in range(10,19):
            index = hole + 1            
            par = df[f't{hole}_par'].tolist()[0]
            stroke = df[f't{hole}_stroke'].tolist()[0]
            distance = df[f't{hole}_distance'].tolist()[0]
            card_df.loc[index] = [str(hole), par, stroke, distance]
        card_df.loc[20] = ['IN', None, None, None]

        if not card_df['Par'].hasnans:
            par_out = sum(card_df['Par'].tolist()[:9])
            par_in = sum(card_df['Par'].tolist()[9:])
            par_tot = card_df['Par'].sum()

        if not card_df['Distance'].hasnans:
            dist_out = sum(card_df['Distance'].tolist()[:9])
            dist_in = sum(card_df['Distance'].tolist()[9:])
            dist_tot = card_df['Distance'].sum()
        
        card_df.loc[10] = ['OUT', par_out, None, dist_out]      
        card_df.loc[20] = ['IN', par_in, None, dist_in]
        card_df.loc[21] = ['TOT', par_tot, None, dist_tot]
        #print(card_df)
        return card_df
                
    def update(self):
        changes = st.session_state.course_tee_data
        #print(self.card_df)
        #print(changes)        
        edited_rows = changes.get("edited_rows", {})        
        for index, updates in edited_rows.items():
            for column, value in updates.items():
                #print(f'index:{index} column:{column} value:{value}')
                self.card_df.at[str(index+1), column] = str(value)
                
                if (index+1) not in [10,20,21]:
                    #print(f'index={index+1} column={column.lower()}')
                    if (index+1) <= 9: hole = index + 1
                    else:                        
                        hole = index
                    self.df_sql.update(id=self.df['id'].tolist()[0], fields=[f't{hole}_{column.lower()}'], values=[value])
                else:
                    #print(edited_rows)
                    pass
        df_id = self.df['id'].tolist()[0]
        self.df = self.df_sql.read(f"WHERE table.id={df_id}") 
        self.card_df = self.load(df=self.df)
                        
        #print(self.card_df)
        
        
# Populate page 
con = st.container(horizontal=True, vertical_alignment='center')

st_details = CourseTeeDetails(df=st.session_state.course_tee)

st_course_tee_holes = CourseTeeHoles(df=st.session_state.course_tee)

with con:
    if st.button(label='', icon=':material/arrow_back:'):
        st.session_state.course_tee = None
        st.session_state.page = st_details.parent_page
        st.rerun()
    st.subheader(f"Tee: {st.session_state.course_tee['name'].tolist()[0]}")