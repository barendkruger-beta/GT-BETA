import streamlit as st
import pandas as pd
import sql
from pathlib import Path
from datetime import datetime

class DBList():
    
    def __init__(self):
        is_superuser = st.user.email in st.secrets["superusers"]["emails"]
        if not is_superuser:
            st.write('Access restricted, contact your administrator.')
            return

        files = [f for f in Path('./db_backups').iterdir() if f.is_file()]
        ctimes = []
        df_data = []
        for f in files:
            df_name = str(f.name)
            #df_created = datetime.fromtimestamp(f.stat().st_birthtime).strftime("%Y-%m-%d %H:%M:%S")
            try:
                creation_time = f.stat().st_birthtime
            except AttributeError:
                # Fallback to ctime (Creation on Windows, Metadata change on Linux)
                creation_time = f.stat().st_ctime
            df_created = datetime.fromtimestamp(creation_time).strftime("%Y-%m-%d %H:%M:%S")
            df_path = str(f)
            df_data.append([df_name, df_created, df_path])   

        #print(files)
        df = pd.DataFrame(df_data, columns=['name', 'created', 'path'])
        if len(df_data) > 0:
            df = df.sort_values(by=['created','name'], ascending=False)

        con = st.container(horizontal=True, width='stretch')

        column_config = {key: None for key in df.columns.to_list()}
        column_config['name'] = st.column_config.TextColumn(label='Name')
        column_config['created'] = st.column_config.TextColumn(label='Created')
        column_config['path'] = st.column_config.TextColumn(label='Path')

        st_df = st.dataframe(
            df,
            on_select='rerun',
            selection_mode=['single-row','single-cell'],
            hide_index=True,
            column_config=column_config
        )

        name = None
        if len(st_df.selection['rows']):
            name = df.iloc[st_df.selection['rows'][0]]['name']
        elif len(st_df.selection['cells']):
            name = df.iloc[st_df.selection['cells'][0][0]]['name']
        if name is not None:
            #print('ID is not none')
            sel = df[df['name'] == name]
            #print(name)
        else: sel = None

        with con:
            if st.button(label='', icon=':material/add_2:', disabled=not is_superuser): self.add()
            if st.button(label='', icon=':material/database_upload:', disabled=not is_superuser): self.upload()
            if st.button(label='', icon=':material/settings_backup_restore:', disabled=not is_superuser or sel is None): self.restore(path=sel['path'].tolist()[0])
            if st.button(label='', icon=':material/download:', disabled=not is_superuser or sel is None): self.download(path=sel['path'].tolist()[0])
            if st.button(label='', icon=':material/delete:', disabled=not is_superuser or sel is None): self.delete(path=sel['path'].tolist()[0])

    @st.dialog("Create backup")
    def add(self):
        db_name = st.text_input(label='Name', placeholder='Enter name')
        if len(db_name) == 0:
            db_name = None
        st.write('Are you sure')
        con = st.container(horizontal=True)
        with con:
            if st.button(label='Yes'):
                filename = sql.export_sql(db_name=db_name)
                st.rerun()
            if st.button(label='No'):
                st.rerun()
    
    @st.dialog("Restore from backup")
    def restore(self, path=None):
        st.write('Current data will be replaced')
        st.write('Are you sure')
        con = st.container(horizontal=True)
        with con:
            if st.button(label='Yes'):
                # Disable DB access

                # Move and rename previous DB to working folder
                source = Path(path)
                destination = Path("GT.db")
                destination.write_bytes(source.read_bytes())

                # Enable DB access

                st.rerun()
            if st.button(label='No'):
                st.rerun()

    @st.dialog("Download backup")
    def download(self, path=None):
        #st.write(path[path.find('\\')+1:])
        f_name = path[path.find('\\')+1:]
        with open(path, "rb") as f:
            st.download_button(label='Download', data=f, file_name=f_name, icon=':material/download:')

    @st.dialog("Upload backup")
    def upload(self, path=None):
        st_file = st.file_uploader(label='Choose file to upload', type='db')
        if st_file is not None:
            f_name = st_file.name.replace('db_backups_','')
            print(f_name)
            with open(f'./db_backups/{f_name}', "wb") as f:
                f.write(st_file.getbuffer())
                f.close
            st.rerun()

    @st.dialog("Delete backup")
    def delete(self, path=None):
        if path is None:
            return
        elif '.db' not in path:
            return
        
        st.write('Are you sure')
        con = st.container(horizontal=True)
        with con:
            if st.button(label='Yes'):
                file = Path(path)
                #print(f'{path} will be deleted')
                file.unlink()
                st.rerun()
            if st.button(label='No'):
                st.rerun()

# Populate page       
st.subheader("Database - Backup and Recovery")

st_db_list = DBList()
