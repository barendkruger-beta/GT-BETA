import streamlit as st
import sqlite3
from sqlalchemy import text, types
import pandas as pd

tables = []

def connect():
    conn = sqlite3.connect('GT.db')
    return conn

def init():
    conn = connect()    
    cursor = conn.cursor()
    cursor.execute('PRAGMA foreign_keys = ON;')   
    
    # Create Tables
    #print('Creating Tables')
    cursor.execute('''CREATE TABLE IF NOT EXISTS formats (
        id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT, description TEXT, active BOOLEAN DEFAULT TRUE, sequence INTEGER DEFAULT 0
        );''')
    tables.append('formats') 
       
    cursor.execute('''CREATE TABLE IF NOT EXISTS groups (
        id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT, description TEXT, active BOOLEAN DEFAULT TRUE, sequence INTEGER DEFAULT 0
        );''')
    tables.append('groups') 
    
    cursor.execute('''CREATE TABLE IF NOT EXISTS participants (
        id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT, full_name TEXT, description TEXT, active BOOLEAN DEFAULT TRUE, sequence INTEGER DEFAULT 0
        );''')
    tables.append('participants') 

    cursor.execute('''CREATE TABLE IF NOT EXISTS courses (
        id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT, description TEXT, active BOOLEAN DEFAULT TRUE, sequence INTEGER DEFAULT 0
        );''')
    tables.append('courses') 
        
    cursor.execute('''CREATE TABLE IF NOT EXISTS course_tees (
        id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT, description TEXT, active BOOLEAN DEFAULT TRUE, sequence INTEGER DEFAULT 0, t_par INTEGER, t_distance INTEGER, t_rating REAL, t_slope REAL,
        t1_par INTEGER, t1_stroke INTEGER, t1_distance INTEGER, t2_par INTEGER, t2_stroke INTEGER, t2_distance INTEGER, t3_par INTEGER, t3_stroke INTEGER, t3_distance INTEGER,
        t4_par INTEGER, t4_stroke INTEGER, t4_distance INTEGER, t5_par INTEGER, t5_stroke INTEGER, t5_distance INTEGER, t6_par INTEGER, t6_stroke INTEGER, t6_distance INTEGER,
        t7_par INTEGER, t7_stroke INTEGER, t7_distance INTEGER, t8_par INTEGER, t8_stroke INTEGER, t8_distance INTEGER, t9_par INTEGER, t9_stroke INTEGER, t9_distance INTEGER,
        t10_par INTEGER, t10_stroke INTEGER, t10_distance INTEGER, t11_par INTEGER, t11_stroke INTEGER, t11_distance INTEGER, t12_par INTEGER, t12_stroke INTEGER, t12_distance INTEGER,
        t13_par INTEGER, t13_stroke INTEGER, t13_distance INTEGER, t14_par INTEGER, t14_stroke INTEGER, t14_distance INTEGER, t15_par INTEGER, t15_stroke INTEGER, t15_distance INTEGER,
        t16_par INTEGER, t16_stroke INTEGER, t16_distance INTEGER, t17_par INTEGER, t17_stroke INTEGER, t17_distance INTEGER, t18_par INTEGER, t18_stroke INTEGER, t18_distance INTEGER,
        course_id INTEGER,
        FOREIGN KEY (course_id) REFERENCES courses(id)
        );''')
    tables.append('course_tees')
    
    cursor.execute('''CREATE TABLE IF NOT EXISTS campaigns (
        id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT, description TEXT, active BOOLEAN DEFAULT TRUE, sequence INTEGER DEFAULT 0
        );''')
    tables.append('campaigns')
    
    cursor.execute('''CREATE TABLE IF NOT EXISTS campaign_groups (
        id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT, description TEXT, active BOOLEAN DEFAULT TRUE, sequence INTEGER DEFAULT 0,
        group_id INTEGER, campaign_id INTEGER,
        FOREIGN KEY (group_id) REFERENCES groups(id),
        FOREIGN KEY (campaign_id) REFERENCES campaigns(id) ON UPDATE CASCADE ON DELETE CASCADE
        );''')
    tables.append('campaign_groups')
    
    cursor.execute('''CREATE TABLE IF NOT EXISTS campaign_participants (
        id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT, description TEXT, active BOOLEAN DEFAULT TRUE, sequence INTEGER DEFAULT 0,
        participant_id INTEGER, campaign_group_id INTEGER, campaign_id INTEGER, 
        FOREIGN KEY (participant_id) REFERENCES participants(id),
        FOREIGN KEY (campaign_id) REFERENCES campaigns(id) ON UPDATE CASCADE ON DELETE CASCADE
        );''')
    tables.append('campaign_participants')
    
    cursor.execute('''CREATE TABLE IF NOT EXISTS competitions (
        id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT, description TEXT, active BOOLEAN DEFAULT TRUE, sequence INTEGER DEFAULT 0,
        campaign_id INTEGER,
        FOREIGN KEY (campaign_id) REFERENCES campaigns(id) ON UPDATE CASCADE ON DELETE CASCADE
        );''')
    tables.append('competitions')
    
    cursor.execute('''CREATE TABLE IF NOT EXISTS competition_groups (
        id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT, description TEXT, active BOOLEAN DEFAULT TRUE, sequence INTEGER DEFAULT 0,
        competition_id INTEGER, campaign_group_id INTEGER,
        FOREIGN KEY (competition_id) REFERENCES competitions(id) ON UPDATE CASCADE ON DELETE CASCADE,
        FOREIGN KEY (campaign_group_id) REFERENCES campaign_groups(id) ON UPDATE CASCADE ON DELETE CASCADE
        );''')
    tables.append('competition_groups')
    
    cursor.execute('''CREATE TABLE IF NOT EXISTS competition_participants (
        id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT, description TEXT, active BOOLEAN DEFAULT TRUE, sequence INTEGER DEFAULT 0, hc_index REAL,
        competition_id INTEGER, competition_group_id INTEGER, campaign_participant_id INTEGER,
        FOREIGN KEY (competition_id) REFERENCES competitions(id) ON UPDATE CASCADE ON DELETE CASCADE,
        FOREIGN KEY (competition_group_id) REFERENCES competition_groups(id) ON UPDATE CASCADE ON DELETE CASCADE,
        FOREIGN KEY (campaign_participant_id) REFERENCES campaign_participants(id) ON UPDATE CASCADE ON DELETE CASCADE
        );''')
    tables.append('competition_participants')
    
    cursor.execute('''CREATE TABLE IF NOT EXISTS eclectics (
        id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT, description TEXT, active BOOLEAN DEFAULT TRUE, sequence INTEGER DEFAULT 0, total INTEGER,
        hole1 INTEGER, hole2 INTEGER, hole3 INTEGER, hole4 INTEGER, hole5 INTEGER, hole6 INTEGER,
        hole7 INTEGER, hole8 INTEGER, hole9 INTEGER, hole10 INTEGER, hole11 INTEGER, hole12 INTEGER,
        hole13 INTEGER, hole14 INTEGER, hole15 INTEGER, hole16 INTEGER, hole17 INTEGER, hole18 INTEGER,
        competition_id INTEGER, competition_participant_id,
        FOREIGN KEY (competition_id) REFERENCES competitions(id) ON UPDATE CASCADE ON DELETE CASCADE,
        FOREIGN KEY (competition_participant_id) REFERENCES competition_participants(id) ON UPDATE CASCADE ON DELETE CASCADE
        );''')
    tables.append('eclectics')
    
    cursor.execute('''CREATE TABLE IF NOT EXISTS events (
        id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT, description TEXT, active BOOLEAN DEFAULT TRUE, sequence INTEGER DEFAULT 0,
        competition_id INTEGER,
        FOREIGN KEY (competition_id) REFERENCES competitions(id) ON UPDATE CASCADE ON DELETE CASCADE
        );''')
    tables.append('events')
    
    cursor.execute('''CREATE TABLE IF NOT EXISTS event_groups (
        id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT, description TEXT, active BOOLEAN DEFAULT TRUE, sequence INTEGER DEFAULT 0,
        event_id INTEGER, competition_group_id INTEGER,
        FOREIGN KEY (event_id) REFERENCES events(id) ON UPDATE CASCADE ON DELETE CASCADE,
        FOREIGN KEY (competition_group_id) REFERENCES competition_groups(id) ON UPDATE CASCADE ON DELETE CASCADE
        );''')
    tables.append('event_groups')
    
    cursor.execute('''CREATE TABLE IF NOT EXISTS event_participants (
        id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT, description TEXT, active BOOLEAN DEFAULT TRUE, sequence INTEGER DEFAULT 0, hc_index REAL,
        event_id INTEGER, event_group_id INTEGER, competition_participant_id INTEGER,
        FOREIGN KEY (event_id) REFERENCES events(id) ON UPDATE CASCADE ON DELETE CASCADE,
        FOREIGN KEY (event_group_id) REFERENCES event_groups(id) ON UPDATE CASCADE ON DELETE CASCADE,
        FOREIGN KEY (competition_participant_id) REFERENCES competition_participants(id) ON UPDATE CASCADE ON DELETE CASCADE
        );''')
    tables.append('event_participants')
    
    cursor.execute('''CREATE TABLE IF NOT EXISTS matchs (
        id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT, description TEXT, active BOOLEAN DEFAULT TRUE, sequence INTEGER DEFAULT 0, value REAL, holes INTEGER DEFAULT 18, start_hole INTEGER DEFAULT 1,
        event_id INTEGER, format_id INTEGER,
        FOREIGN KEY (event_id) REFERENCES events(id) ON UPDATE CASCADE ON DELETE CASCADE,
        FOREIGN KEY (format_id) REFERENCES formats(id) ON UPDATE CASCADE ON DELETE CASCADE
        );''')
    tables.append('matchs')
    
    cursor.execute('''CREATE TABLE IF NOT EXISTS match_groups (
        id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT, description TEXT, active BOOLEAN DEFAULT TRUE, sequence INTEGER DEFAULT 0, value REAL,
        match_id INTEGER, event_group_id INTEGER,
        FOREIGN KEY (match_id) REFERENCES matchs(id) ON UPDATE CASCADE ON DELETE CASCADE,
        FOREIGN KEY (event_group_id) REFERENCES event_groups(id) ON UPDATE CASCADE ON DELETE CASCADE
        );''')
    tables.append('match_groups')
    
    cursor.execute('''CREATE TABLE IF NOT EXISTS match_participants (
        id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT, description TEXT, active BOOLEAN DEFAULT TRUE, sequence INTEGER DEFAULT 0, value REAL, handicap INTEGER,
        match_id INTEGER, match_group_id, event_participant_id INTEGER,
        FOREIGN KEY (match_id) REFERENCES matchs(id) ON UPDATE CASCADE ON DELETE CASCADE,
        FOREIGN KEY (match_group_id) REFERENCES match_groups(id) ON UPDATE CASCADE ON DELETE CASCADE,
        FOREIGN KEY (event_participant_id) REFERENCES event_participants(id) ON UPDATE CASCADE ON DELETE CASCADE
        );''')
    tables.append('match_participants')
    
    cursor.execute('''CREATE TABLE IF NOT EXISTS match_holes (
        id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT, description TEXT, sequence INTEGER DEFAULT 0, number INTEGER, points INTEGER,
        match_id INTEGER, match_group_id INTEGER, match_participant_id INTEGER, scoring_hole_id INTEGER,
        FOREIGN KEY(match_id) REFERENCES matchs(id) ON UPDATE CASCADE ON DELETE CASCADE,
        FOREIGN KEY (match_group_id) REFERENCES match_groups(id) ON UPDATE CASCADE ON DELETE CASCADE,
        FOREIGN KEY (match_participant_id) REFERENCES match_participants(id) ON UPDATE CASCADE ON DELETE CASCADE,
        FOREIGN KEY (scoring_hole_id) REFERENCES scoring_holes(id) ON UPDATE CASCADE ON DELETE CASCADE
        );''')
    tables.append('match_holes')
    
    cursor.execute('''CREATE TABLE IF NOT EXISTS scoring_cards (
        id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT, description TEXT, active BOOLEAN DEFAULT TRUE, sequence INTEGER DEFAULT 0, validated BOOLEAN, hole INTEGER DEFAULT 0, date DATE, slot TEXT DEFAULT 'AM',
        event_id INTEGER, event_participant_id INTEGER, course_id INTEGER,
        FOREIGN KEY (event_id) REFERENCES events(id) ON UPDATE CASCADE ON DELETE CASCADE,
        FOREIGN KEY (event_participant_id) REFERENCES event_participants(id) ON UPDATE CASCADE ON DELETE CASCADE,
        FOREIGN KEY (course_id) REFERENCES courses(id) ON UPDATE CASCADE ON DELETE SET NULL
        );''')
    tables.append('scoring_cards')
    
    cursor.execute('''CREATE TABLE IF NOT EXISTS scoring_card_groups (
        id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT, description TEXT, active BOOLEAN DEFAULT TRUE, sequence INTEGER DEFAULT 0,
        scoring_card_id INTEGER, event_group_id INTEGER,
        FOREIGN KEY (scoring_card_id) REFERENCES scoring_cards(id) ON UPDATE CASCADE ON DELETE CASCADE,
        FOREIGN KEY (event_group_id) REFERENCES event_groups(id) ON UPDATE CASCADE ON DELETE CASCADE
        );''')
    tables.append('scoring_card_groups')
    
    cursor.execute('''CREATE TABLE IF NOT EXISTS scoring_card_participants (
        id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT, description TEXT, active BOOLEAN DEFAULT TRUE, sequence INTEGER DEFAULT 0, handicap INTEGER,
        scoring_card_id INTEGER, scoring_card_group_id INTEGER, event_participant_id INTEGER, course_tee_id INTEGER,
        FOREIGN KEY (scoring_card_id) REFERENCES scoring_cards(id) ON UPDATE CASCADE ON DELETE CASCADE,
        FOREIGN KEY (scoring_card_group_id) REFERENCES scoring_card_groups(id) ON UPDATE CASCADE ON DELETE CASCADE,
        FOREIGN KEY (event_participant_id) REFERENCES event_participants(id) ON UPDATE CASCADE ON DELETE CASCADE,
        FOREIGN KEY (course_tee_id) REFERENCES course_tees(id) ON UPDATE CASCADE ON DELETE CASCADE
        );''')
    tables.append('scoring_card_participants')
       
    cursor.execute('''CREATE TABLE IF NOT EXISTS scoring_rounds (
        id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT, description TEXT, active BOOLEAN DEFAULT TRUE, sequence INTEGER DEFAULT 0, rating INTEGER, validated BOOLEAN,
        course_tee_id INTEGER, scoring_card_id INTEGER, scoring_card_participant_id INTEGER,
        FOREIGN KEY (course_tee_id) REFERENCES course_tees(id) ON UPDATE CASCADE ON DELETE SET NULL,
        FOREIGN KEY (scoring_card_id) REFERENCES scoring_cards(id) ON UPDATE CASCADE ON DELETE CASCADE, 
        FOREIGN KEY (scoring_card_participant_id) REFERENCES scoring_card_participants(id) ON UPDATE CASCADE ON DELETE CASCADE
        );''')    
    tables.append('scoring_rounds')
    
    cursor.execute('''CREATE TABLE IF NOT EXISTS scoring_holes (
        id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT, description TEXT, sequence INTEGER DEFAULT 0, number INTEGER, shots INTEGER, points INTEGER,
        scoring_round_id INTEGER,
        FOREIGN KEY(scoring_round_id) REFERENCES scoring_rounds(id) ON UPDATE CASCADE ON DELETE CASCADE
        );''')
    tables.append('scoring_holes')
    
    cursor.execute('''CREATE TABLE IF NOT EXISTS event_validated_rounds (
        id INTEGER PRIMARY KEY AUTOINCREMENT, event_name TEXT, participant_name TEXT, round TEXT, description TEXT, active BOOLEAN DEFAULT TRUE, sequence INTEGER DEFAULT 0,
        event_id INTEGER, event_participant_id INTEGER, course_tees_id INTEGER,
        FOREIGN KEY (event_id) REFERENCES events(id) ON UPDATE CASCADE ON DELETE CASCADE,
        FOREIGN KEY (event_participant_id) REFERENCES event_participants(id) ON UPDATE CASCADE ON DELETE CASCADE,
        FOREIGN KEY (course_tees_id) REFERENCES course_tees(id)
        );''')
    tables.append('event_validated_rounds')
    
    cursor.execute('''CREATE TABLE IF NOT EXISTS event_validated_holes (
        id INTEGER PRIMARY KEY AUTOINCREMENT, event_name TEXT, participant_name TEXT, round TEXT, hole TEXT, description TEXT, active BOOLEAN DEFAULT TRUE, sequence INTEGER DEFAULT 0,
        event_validated_round_id INTEGER,
        FOREIGN KEY(event_validated_round_id) REFERENCES event_validated_rounds(id) ON UPDATE CASCADE ON DELETE CASCADE
        );''')
    tables.append('event_validated_holes')
        
    conn.commit()
    #print(f'Tables created\n{tables}')
    
    # Check if FirstCreated and LastModified columns have been created, else create them
    cursor.execute(f"SELECT * FROM {tables[0]} LIMIT 0") # Limit 0 to get structure without data
    column_names = [description[0] for description in cursor.description]
    if 'created' in column_names:
        conn.close()
        return None
    
    # Create FirstCreated and LastModified columns
    print('Creating FirstCreated and LastModified columns')
    for table in tables:
        #print(f'\t{table}')
        cursor.execute(f'''ALTER TABLE {table} ADD COLUMN created TEXT DEFAULT CURRENT_TIMESTAMP;''')
        cursor.execute(f'''ALTER TABLE {table} ADD COLUMN last_modified TEXT DEFAULT CURRENT_TIMESTAMP;''')
    conn.commit()
    
    # Create LastModified Triggers
    print('Creating Trigger for LastModified columns')
    for table in tables:
        #print(f'\t{table}')
        cursor.execute(f'''CREATE TRIGGER update_last_modified_{table}
                       AFTER UPDATE ON {table}
                       FOR EACH ROW
                       BEGIN
                       UPDATE {table}
                       SET last_modified = CURRENT_TIMESTAMP
                       WHERE rowid = NEW.rowid;
                       END;''')
    conn.commit()
    
    conn.close()
    return None
    
def testdata():
    conn = connect()    
    cursor = conn.cursor()
    # Purge Tables
    #tables = ['event_validated_holes', 'campaigns']#, 'series', 'events', 'groups', 'participants', 'sequence_groups', 'sequences', 'tests']
    for table in reversed(tables):
        cursor.execute(f"DELETE FROM {table};")
    cursor.execute(f"DELETE FROM sqlite_sequence;")# WHERE NAME IN [{str_tables}];")
    conn.commit()
    
    # Create Courses
    cursor.execute("""INSERT INTO courses (
        name, description        
        ) 
        VALUES ('Silver Lakes Country Club', 'Pretoria, South Africa'
        );""")
    cursor.execute("""INSERT INTO courses (
        name, description        
        ) 
        VALUES ('Woodhill Country Club', 'Pretoria, South Africa'
        );""")
    
    # Create Course Tees
    cursor.execute("""INSERT INTO course_tees (
        name, description, t_par, t_distance, t_rating, t_slope,       
        t1_par, t1_stroke, t1_distance, t2_par, t2_stroke, t2_distance, t3_par, t3_stroke, t3_distance,
        t4_par, t4_stroke, t4_distance, t5_par, t5_stroke, t5_distance, t6_par, t6_stroke, t6_distance,
        t7_par, t7_stroke, t7_distance, t8_par, t8_stroke, t8_distance, t9_par, t9_stroke, t9_distance,
        t10_par, t10_stroke, t10_distance, t11_par, t11_stroke, t11_distance, t12_par, t12_stroke, t12_distance,
        t13_par, t13_stroke, t13_distance, t14_par, t14_stroke, t14_distance, t15_par, t15_stroke, t15_distance,
        t16_par, t16_stroke, t16_distance, t17_par, t17_stroke, t17_distance, t18_par, t18_stroke, t18_distance,
        course_id
        ) 
        VALUES ('Red', 'Silver Lakes Country Club', 72, 6640, 75.2, 150,
        4, 8, 395, 5, 14, 553, 3, 16, 180,
        4, 12, 375, 4, 4, 371, 4, 6, 378,
        5, 18, 474, 4, 2, 404, 3, 10, 167,
        4, 9, 375, 4, 7, 401, 4, 1, 465,
        3, 5, 179, 5, 11, 492, 4, 17, 328,
        3, 15, 182, 4, 3, 445, 5, 13, 476,
        1
        );""")
    cursor.execute("""INSERT INTO course_tees (
        name, description, t_par, t_distance, t_rating, t_slope,       
        t1_par, t1_stroke, t1_distance, t2_par, t2_stroke, t2_distance, t3_par, t3_stroke, t3_distance,
        t4_par, t4_stroke, t4_distance, t5_par, t5_stroke, t5_distance, t6_par, t6_stroke, t6_distance,
        t7_par, t7_stroke, t7_distance, t8_par, t8_stroke, t8_distance, t9_par, t9_stroke, t9_distance,
        t10_par, t10_stroke, t10_distance, t11_par, t11_stroke, t11_distance, t12_par, t12_stroke, t12_distance,
        t13_par, t13_stroke, t13_distance, t14_par, t14_stroke, t14_distance, t15_par, t15_stroke, t15_distance,
        t16_par, t16_stroke, t16_distance, t17_par, t17_stroke, t17_distance, t18_par, t18_stroke, t18_distance,
        course_id
        ) 
        VALUES ('White', 'Silver Lakes Country Club', 72, 6214, 73.1, 145,
        4, 8, 381, 5, 14, 534, 3, 16, 157,
        4, 12, 346, 4, 4, 343, 4, 6, 357,
        5, 18, 462, 4, 2, 387, 3, 10, 151,
        4, 9, 334, 4, 7, 384, 4, 1, 410,
        3, 5, 164, 5, 11, 446, 4, 17, 320,
        3, 15, 140, 4, 3, 436, 5, 13, 462,
        1
        );""")
    
    # Create Formats
    cursor.execute("INSERT INTO formats (name, description) VALUES ('IPS-4BBB', 'Stableford Four-Ball Better Ball');")
    cursor.execute("INSERT INTO formats (name, description) VALUES ('MP-4BBB', 'Match Play Four-Ball Better Ball');")
    cursor.execute("INSERT INTO formats (name, description) VALUES ('IPS', 'Stableford');")
    cursor.execute("INSERT INTO formats (name, description) VALUES ('MP', 'Match Play');")
    
    # Create Groups and Participants
    cursor.execute("INSERT INTO groups (name, description) VALUES ('Swingers', 'group 1');")
    cursor.execute("INSERT INTO groups (name, description) VALUES ('Hackers', 'group 2');")
    cursor.execute("INSERT INTO groups (name, description) VALUES ('Tossers', 'group 3');")
    cursor.execute("INSERT INTO participants (name, description) VALUES ('Barend', 'Golf Club A');")
    cursor.execute("INSERT INTO participants (name, description) VALUES ('Fred', 'Golf Club A');")
    cursor.execute("INSERT INTO participants (name, description) VALUES ('Gerrit', 'Golf Club A');")    
    cursor.execute("INSERT INTO participants (name, description) VALUES ('Reon', 'Golf Club B');")
    cursor.execute("INSERT INTO participants (name, description) VALUES ('Frikkie', 'Golf Club D');")
    cursor.execute("INSERT INTO participants (name, description) VALUES ('Dwerg', 'Golf Club F');")
    cursor.execute("INSERT INTO participants (name, description) VALUES ('Theunis', 'Golf Club F');")
    cursor.execute("INSERT INTO participants (name, description) VALUES ('Ryno', 'Golf Club F');")
    cursor.execute("INSERT INTO participants (name, description) VALUES ('Gideon', 'Golf Club F');")
    cursor.execute("INSERT INTO participants (name, description) VALUES ('Lambert', 'Golf Club F');")
    cursor.execute("INSERT INTO participants (name, description) VALUES ('Gerhard', 'Golf Club F');")
    cursor.execute("INSERT INTO participants (name, description) VALUES ('Morne', 'Golf Club F');")
    cursor.execute("INSERT INTO participants (name, description) VALUES ('Wesley', 'Golf Club F');")
    cursor.execute("INSERT INTO participants (name, description) VALUES ('Crusty', 'Golf Club F');")
    
    # Create Campaigns
    cursor.execute("INSERT INTO campaigns (name, description) VALUES ('GT', 'Feeling Dangerous');")
    cursor.execute("INSERT INTO campaigns (name, description) VALUES ('Other campaign', 'bla');")
    cursor.execute("INSERT INTO campaigns (name, description) VALUES ('Empty campaign', 'Keep Empty');")
    
    # Assign groups to Campaign
    cursor.execute("INSERT INTO campaign_groups (name, description, group_id, campaign_id) VALUES ('Swingers', 'campaign_group 1', 1, 1);")
    cursor.execute("INSERT INTO campaign_groups (name, description, group_id, campaign_id) VALUES ('Hackers', 'campaign_group 2', 2, 1);")
    
    if False:
        # Assign participants to Campaign
        cursor.execute("INSERT INTO campaign_participants (name, description, participant_id, campaign_id) VALUES ('Barend', 'campaign_participant 1', 1, 1);")
        cursor.execute("INSERT INTO campaign_participants (name, description, participant_id, campaign_id) VALUES ('Gerrit', 'campaign_participant 2', 3, 1);")
        
        #Create Competitions
        cursor.execute("INSERT INTO competitions (name, description, campaign_id) VALUES ('GT2025', 'Vuil-Bijl', 1);")
        cursor.execute("INSERT INTO competitions (name, description, campaign_id) VALUES ('GT2024', 'Wes-Kaap', 1);")
        cursor.execute("INSERT INTO competitions (name, description, campaign_id) VALUES ('Boendoes2025', 'Kathu', 2);")
        
        # Assign groups to Competition
        cursor.execute("INSERT INTO competition_groups (name, description, competition_id, campaign_group_id) VALUES ('Swingers', 'competition_group 1', 1, 1);")
        cursor.execute("INSERT INTO competition_groups (name, description, competition_id, campaign_group_id) VALUES ('Hackers', 'competition_group 2', 1, 2);")
        
        # Assign participants to Competition
        cursor.execute("INSERT INTO competition_participants (name, description, competition_id, competition_group_id, campaign_participant_id, hc_index) VALUES ('Barend', 'competition_participant 1', 1, 1, 1, 12.5);")
        cursor.execute("INSERT INTO competition_participants (name, description, competition_id, competition_group_id, campaign_participant_id, hc_index) VALUES ('Gerrit', 'competition_participant 2', 1, 2, 2, 19.5);")
        
        #Create Events
        cursor.execute("INSERT INTO events (name, description, competition_id) VALUES ('Day 1', 'Golf Course ABC', 1);")
        cursor.execute("INSERT INTO events (name, description, competition_id) VALUES ('Day 2', 'Golf Course XYZ', 1);")
        cursor.execute("INSERT INTO events (name, description, competition_id) VALUES ('Day 1', 'Golf Course BLA', 2);")
    
    #Create Matches
    
    conn.commit()
    conn.close()    

def read_table_columns(table):
    conn = connect()
    cursor = conn.cursor()
    cursor.execute(f"SELECT * FROM {table} LIMIT 0") # Limit 0 to get structure without data
    column_names = [description[0] for description in cursor.description]
    conn.close()
    return column_names

def read_table_columns_full(table):
    conn = connect()
    cursor = conn.cursor()
    cursor.execute(f"SELECT * FROM pragma_table_info('{table}') as {table};")
    sql_columns = cursor.fetchall()
    columns = [[column[1], column[2]] for column in sql_columns]
    conn.close()
    return columns    
      
def read_table_foreign_keys(table):
    conn = connect()
    cursor = conn.cursor()
    cursor.execute(f"SELECT * FROM pragma_foreign_key_list('{table}') as {table};")
    sql_foreign_keys = cursor.fetchall()
    foreign_columns = [f'{column[2]}.{column[4]}' for column in sql_foreign_keys]
    conn.close()
    #print(f'Foreign keys = {foreign_columns}')
    return foreign_columns 
     
def convert_sqlite_python(columns, fields, values):
    formatted_values = []
    for field, value in zip(fields, values):
        sql_type = None
        #print()
        #print(f'Start conversion check for field = {field}')
        for c in columns:
            if c[0] == field:
                sql_type = c[1]
                #print(f'column found with type {sql_type}')
                break
                
        match value:
            case None:
                value = 'NULL'
                       
        match sql_type:    
            case 'TEXT':
                #print(f'Original str = {value}')
                #if value[0] != "'":
                formatted_values.append(f"'{value}'")
                #print(f'New str = {value}')
            case None:
                #print(f'Column not found')
                formatted_values.append('None')
            case _:
                #print(f'No formatting required, value = {value}')
                formatted_values.append(str(value))
    return formatted_values
         
def read_table(qry):
    #print(qry)
    conn = connect()
    cursor = conn.cursor()
    cursor.execute("PRAGMA foreign_keys = ON;")
    cursor.execute(qry)
    data = cursor.fetchall()
    conn.close()
    #print(data)
    return data

def write_table(qry):
    print(qry)
    conn = connect()
    cursor = conn.cursor()
    cursor.execute("PRAGMA foreign_keys = ON;")
    cursor.execute(qry)
    data = None
    if 'INSERT' in qry:
        cursor.execute("SELECT last_insert_rowid();")
        data = cursor.fetchall()[0][0]
        print(f'New entry with ID={data} created')        
    conn.commit()
    conn.close()
    return data

     
class campaigns():
    table = 'campaigns'   
    columns = None
    foreign_columns = None
    
    def __init__(self):
        self.columns = read_table_columns_full(self.table)
        self.foreign_columns = read_table_foreign_keys(self.table)

    def read(self, filter=None):
        qry = f"SELECT {self.table}.* "
        if len(self.foreign_columns):            
            for column in self.foreign_columns:
                qry += f", {column.replace(".id", ".name")} {column.replace(".id", "_name")} "
        qry += f"FROM {self.table} "
        if len(self.foreign_columns):
            for column in self.foreign_columns:
                qry += f"LEFT JOIN {column[:column.find(".")-1]}s ON {self.table}.{column.replace("s.", "_")} = {column} "
        if filter is not None: qry+=' '+filter.replace("table.", f"{self.table}.")
        qry += ";"
        
        data = read_table(qry)
        df = None
        column_names = [list(row) for row in zip(*self.columns)][0]
        if len(self.foreign_columns):            
            for column in self.foreign_columns:
                column_names.append(f"{column.replace(".id", "_name")}")
                
        if data:
            indexes = [list(i) for i in zip(*data)][0]
            df = pd.DataFrame(data=data, columns=column_names, index=indexes)
        return df 
    
    def add(self, fields, values):
        f = []
        for field in fields: f.append(field)
        v = []
        for value in values: v.append(value)
        
        columns = list(map(list, zip(*self.columns)))[0]
        for field, value in zip(fields, values):
            if field not in columns:
                v.pop(f.index(field))
                f.pop(f.index(field))
            else:
                pass
                #print(f'field in columns = {field}')
                               
        formatted_values = convert_sqlite_python(columns=self.columns, fields=f, values=v)
        #print(f'formatted values = {formatted_values}')
        qry = f"INSERT INTO {self.table} ({','.join(f)}) VALUES ({','.join(formatted_values)});"
        return write_table(qry)  

    def update(self, id, fields, values):
        formatted_values = convert_sqlite_python(columns=self.columns, fields=fields, values=values)
        cols = []
        for field, value in zip(fields, formatted_values):
            cols.append(f"{field}={value}")

        qry = f"UPDATE {self.table} SET {','.join(cols)} WHERE id={id};"
        return write_table(qry)
    
    def delete(self, id):
        qry = f'DELETE FROM {self.table} WHERE id={id}'
        return write_table(qry) 

    
class campaign_groups():
    table = 'campaign_groups'   
    columns = None
    foreign_columns = None
    
    def __init__(self):
        self.columns = read_table_columns_full(self.table)
        self.foreign_columns = read_table_foreign_keys(self.table)

    def read(self, filter=None):
        qry = f"SELECT {self.table}.* "
        if len(self.foreign_columns):            
            for column in self.foreign_columns:
                qry += f", {column.replace(".id", ".name")} {column.replace(".id", "_name")} "
        qry += f"FROM {self.table} "
        if len(self.foreign_columns):
            for column in self.foreign_columns:
                qry += f"LEFT JOIN {column[:column.find(".")-1]}s ON {self.table}.{column.replace("s.", "_")} = {column} "
        if filter is not None: qry+=' '+filter.replace("table.", f"{self.table}.")
        qry += ";"
        
        data = read_table(qry)
        df = None
        column_names = [list(row) for row in zip(*self.columns)][0]
        if len(self.foreign_columns):            
            for column in self.foreign_columns:
                column_names.append(f"{column.replace(".id", "_name")}")
                
        if data:
            indexes = [list(i) for i in zip(*data)][0]
            df = pd.DataFrame(data=data, columns=column_names, index=indexes)
        return df 
    
    def add(self, fields, values):
        f = []
        for field in fields: f.append(field)
        v = []
        for value in values: v.append(value)
        
        columns = list(map(list, zip(*self.columns)))[0]
        for field, value in zip(fields, values):
            if field not in columns:
                v.pop(f.index(field))
                f.pop(f.index(field))
            else:
                pass
                #print(f'field in columns = {field}')
                               
        formatted_values = convert_sqlite_python(columns=self.columns, fields=f, values=v)
        #print(f'formatted values = {formatted_values}')
        qry = f"INSERT INTO {self.table} ({','.join(f)}) VALUES ({','.join(formatted_values)});"
        return write_table(qry)  

    def update(self, id, fields, values):
        formatted_values = convert_sqlite_python(columns=self.columns, fields=fields, values=values)
        cols = []
        for field, value in zip(fields, formatted_values):
            cols.append(f"{field}={value}")

        qry = f"UPDATE {self.table} SET {','.join(cols)} WHERE id={id};"
        return write_table(qry)
    
    def delete(self, id):
        qry = f'DELETE FROM {self.table} WHERE id={id}'
        return write_table(qry) 

    
class campaign_participants():
    table = 'campaign_participants'   
    columns = None
    foreign_columns = None
    
    def __init__(self):
        self.columns = read_table_columns_full(self.table)
        self.foreign_columns = read_table_foreign_keys(self.table)

    def read(self, filter=None):
        qry = f"SELECT {self.table}.* "
        if len(self.foreign_columns):            
            for column in self.foreign_columns:
                qry += f", {column.replace(".id", ".name")} {column.replace(".id", "_name")} "
        qry += f"FROM {self.table} "
        if len(self.foreign_columns):
            for column in self.foreign_columns:
                qry += f"LEFT JOIN {column[:column.find(".")-1]}s ON {self.table}.{column.replace("s.", "_")} = {column} "
        if filter is not None: qry+=' '+filter.replace("table.", f"{self.table}.")
        qry += ";"
        
        data = read_table(qry)
        df = None
        column_names = [list(row) for row in zip(*self.columns)][0]
        if len(self.foreign_columns):            
            for column in self.foreign_columns:
                column_names.append(f"{column.replace(".id", "_name")}")
                
        if data:
            indexes = [list(i) for i in zip(*data)][0]
            df = pd.DataFrame(data=data, columns=column_names, index=indexes)
        return df 
    
    def add(self, fields, values):
        f = []
        for field in fields: f.append(field)
        v = []
        for value in values: v.append(value)
        
        columns = list(map(list, zip(*self.columns)))[0]
        for field, value in zip(fields, values):
            if field not in columns:
                v.pop(f.index(field))
                f.pop(f.index(field))
            else:
                pass
                #print(f'field in columns = {field}')
                               
        formatted_values = convert_sqlite_python(columns=self.columns, fields=f, values=v)
        #print(f'formatted values = {formatted_values}')
        qry = f"INSERT INTO {self.table} ({','.join(f)}) VALUES ({','.join(formatted_values)});"
        return write_table(qry)  

    def update(self, id, fields, values):
        formatted_values = convert_sqlite_python(columns=self.columns, fields=fields, values=values)
        cols = []
        for field, value in zip(fields, formatted_values):
            cols.append(f"{field}={value}")

        qry = f"UPDATE {self.table} SET {','.join(cols)} WHERE id={id};"
        return write_table(qry)
    
    def delete(self, id):
        qry = f'DELETE FROM {self.table} WHERE id={id}'
        return write_table(qry) 
   
    
class competitions():
    table = 'competitions'
    columns = None
    foreign_columns = None
    
    def __init__(self):
        self.columns = read_table_columns_full(self.table)
        self.foreign_columns = read_table_foreign_keys(self.table)

    def read(self, filter=None):
        qry = f"SELECT {self.table}.* "
        if len(self.foreign_columns):            
            for column in self.foreign_columns:
                qry += f", {column.replace(".id", ".name")} {column.replace(".id", "_name")} "
        qry += f"FROM {self.table} "
        if len(self.foreign_columns):
            for column in self.foreign_columns:
                qry += f"LEFT JOIN {column[:column.find(".")-1]}s ON {self.table}.{column.replace("s.", "_")} = {column} "
        if filter is not None: qry+=' '+filter.replace("table.", f"{self.table}.")
        qry += ";"
        
        data = read_table(qry)
        df = None
        column_names = [list(row) for row in zip(*self.columns)][0]
        if len(self.foreign_columns):            
            for column in self.foreign_columns:
                column_names.append(f"{column.replace(".id", "_name")}")
                
        if data:
            indexes = [list(i) for i in zip(*data)][0]
            df = pd.DataFrame(data=data, columns=column_names, index=indexes)
        return df 
    
    def add(self, fields, values):
        f = []
        for field in fields: f.append(field)
        v = []
        for value in values: v.append(value)
        
        columns = list(map(list, zip(*self.columns)))[0]
        for field, value in zip(fields, values):
            if field not in columns:
                v.pop(f.index(field))
                f.pop(f.index(field))
            else:
                pass
                #print(f'field in columns = {field}')
                               
        formatted_values = convert_sqlite_python(columns=self.columns, fields=f, values=v)
        #print(f'formatted values = {formatted_values}')
        qry = f"INSERT INTO {self.table} ({','.join(f)}) VALUES ({','.join(formatted_values)});"
        return write_table(qry)  

    def update(self, id, fields, values):
        formatted_values = convert_sqlite_python(columns=self.columns, fields=fields, values=values)
        cols = []
        for field, value in zip(fields, formatted_values):
            cols.append(f"{field}={value}")

        qry = f"UPDATE {self.table} SET {','.join(cols)} WHERE id={id};"
        return write_table(qry)
    
    def delete(self, id):
        qry = f'DELETE FROM {self.table} WHERE id={id}'
        return write_table(qry) 
   

class competition_groups():
    table = 'competition_groups'   
    columns = None
    foreign_columns = None
    
    def __init__(self):
        self.columns = read_table_columns_full(self.table)
        self.foreign_columns = read_table_foreign_keys(self.table)

    def read(self, filter=None):
        qry = f"SELECT {self.table}.* "
        if len(self.foreign_columns):            
            for column in self.foreign_columns:
                qry += f", {column.replace(".id", ".name")} {column.replace(".id", "_name")} "
        qry += f"FROM {self.table} "
        if len(self.foreign_columns):
            for column in self.foreign_columns:
                qry += f"LEFT JOIN {column[:column.find(".")-1]}s ON {self.table}.{column.replace("s.", "_")} = {column} "
        if filter is not None: qry+=' '+filter.replace("table.", f"{self.table}.")
        qry += ";"
        
        data = read_table(qry)
        df = None
        column_names = [list(row) for row in zip(*self.columns)][0]
        if len(self.foreign_columns):            
            for column in self.foreign_columns:
                column_names.append(f"{column.replace(".id", "_name")}")
                
        if data:
            indexes = [list(i) for i in zip(*data)][0]
            df = pd.DataFrame(data=data, columns=column_names, index=indexes)
        return df 
    
    def add(self, fields, values):
        f = []
        for field in fields: f.append(field)
        v = []
        for value in values: v.append(value)
        
        columns = list(map(list, zip(*self.columns)))[0]
        for field, value in zip(fields, values):
            if field not in columns:
                v.pop(f.index(field))
                f.pop(f.index(field))
            else:
                pass
                #print(f'field in columns = {field}')
                               
        formatted_values = convert_sqlite_python(columns=self.columns, fields=f, values=v)
        #print(f'formatted values = {formatted_values}')
        qry = f"INSERT INTO {self.table} ({','.join(f)}) VALUES ({','.join(formatted_values)});"
        return write_table(qry)  

    def update(self, id, fields, values):
        formatted_values = convert_sqlite_python(columns=self.columns, fields=fields, values=values)
        cols = []
        for field, value in zip(fields, formatted_values):
            cols.append(f"{field}={value}")

        qry = f"UPDATE {self.table} SET {','.join(cols)} WHERE id={id};"
        return write_table(qry)
    
    def delete(self, id):
        qry = f'DELETE FROM {self.table} WHERE id={id}'
        return write_table(qry) 

    
class competition_participants():
    table = 'competition_participants'   
    columns = None
    foreign_columns = None
    
    def __init__(self):
        self.columns = read_table_columns_full(self.table)
        self.foreign_columns = read_table_foreign_keys(self.table)

    def read(self, filter=None):
        qry = f"SELECT {self.table}.* "
        if len(self.foreign_columns):            
            for column in self.foreign_columns:
                qry += f", {column.replace(".id", ".name")} {column.replace(".id", "_name")} "
        qry += f"FROM {self.table} "
        if len(self.foreign_columns):
            for column in self.foreign_columns:
                qry += f"LEFT JOIN {column[:column.find(".")-1]}s ON {self.table}.{column.replace("s.", "_")} = {column} "
        if filter is not None: qry+=' '+filter.replace("table.", f"{self.table}.")
        qry += ";"
        
        data = read_table(qry)
        df = None
        column_names = [list(row) for row in zip(*self.columns)][0]
        if len(self.foreign_columns):            
            for column in self.foreign_columns:
                column_names.append(f"{column.replace(".id", "_name")}")
                
        if data:
            indexes = [list(i) for i in zip(*data)][0]
            df = pd.DataFrame(data=data, columns=column_names, index=indexes)
        return df 
    
    def add(self, fields, values):
        f = []
        for field in fields: f.append(field)
        v = []
        for value in values: v.append(value)
        
        columns = list(map(list, zip(*self.columns)))[0]
        for field, value in zip(fields, values):
            if field not in columns:
                v.pop(f.index(field))
                f.pop(f.index(field))
            else:
                pass
                #print(f'field in columns = {field}')
                               
        formatted_values = convert_sqlite_python(columns=self.columns, fields=f, values=v)
        #print(f'formatted values = {formatted_values}')
        qry = f"INSERT INTO {self.table} ({','.join(f)}) VALUES ({','.join(formatted_values)});"
        return write_table(qry)  

    def update(self, id, fields, values):
        formatted_values = convert_sqlite_python(columns=self.columns, fields=fields, values=values)
        cols = []
        for field, value in zip(fields, formatted_values):
            cols.append(f"{field}={value}")

        qry = f"UPDATE {self.table} SET {','.join(cols)} WHERE id={id};"
        return write_table(qry)
    
    def delete(self, id):
        qry = f'DELETE FROM {self.table} WHERE id={id}'
        return write_table(qry) 


class eclectics():
    table = 'eclectics'
    columns = None
    foreign_columns = None
    
    def __init__(self):
        self.columns = read_table_columns_full(self.table)
        self.foreign_columns = read_table_foreign_keys(self.table)

    def read(self, filter=None):
        qry = f"SELECT {self.table}.* "
        if len(self.foreign_columns):            
            for column in self.foreign_columns:
                qry += f", {column.replace(".id", ".name")} {column.replace(".id", "_name")} "
        qry += f"FROM {self.table} "
        if len(self.foreign_columns):
            for column in self.foreign_columns:
                qry += f"LEFT JOIN {column[:column.find(".")-1]}s ON {self.table}.{column.replace("s.", "_")} = {column} "
        if filter is not None: qry+=' '+filter.replace("table.", f"{self.table}.")
        qry += ";"
        
        data = read_table(qry)
        df = None
        column_names = [list(row) for row in zip(*self.columns)][0]
        if len(self.foreign_columns):            
            for column in self.foreign_columns:
                column_names.append(f"{column.replace(".id", "_name")}")
                
        if data:
            indexes = [list(i) for i in zip(*data)][0]
            df = pd.DataFrame(data=data, columns=column_names, index=indexes)
        return df 
    
    def add(self, fields, values):
        f = []
        for field in fields: f.append(field)
        v = []
        for value in values: v.append(value)
        
        columns = list(map(list, zip(*self.columns)))[0]
        for field, value in zip(fields, values):
            if field not in columns:
                v.pop(f.index(field))
                f.pop(f.index(field))
            else:
                pass
                #print(f'field in columns = {field}')
                               
        formatted_values = convert_sqlite_python(columns=self.columns, fields=f, values=v)
        #print(f'formatted values = {formatted_values}')
        qry = f"INSERT INTO {self.table} ({','.join(f)}) VALUES ({','.join(formatted_values)});"
        return write_table(qry)  

    def update(self, id, fields, values):
        formatted_values = convert_sqlite_python(columns=self.columns, fields=fields, values=values)
        cols = []
        for field, value in zip(fields, formatted_values):
            cols.append(f"{field}={value}")

        qry = f"UPDATE {self.table} SET {','.join(cols)} WHERE id={id};"
        return write_table(qry)
    
    def delete(self, id):
        qry = f'DELETE FROM {self.table} WHERE id={id}'
        return write_table(qry) 
 

class events():
    table = 'events'
    columns = None
    foreign_columns = None
    
    def __init__(self):
        self.columns = read_table_columns_full(self.table)
        self.foreign_columns = read_table_foreign_keys(self.table)

    def read(self, filter=None):
        qry = f"SELECT {self.table}.* "
        if len(self.foreign_columns):            
            for column in self.foreign_columns:
                qry += f", {column.replace(".id", ".name")} {column.replace(".id", "_name")} "
        qry += f"FROM {self.table} "
        if len(self.foreign_columns):
            for column in self.foreign_columns:
                qry += f"LEFT JOIN {column[:column.find(".")-1]}s ON {self.table}.{column.replace("s.", "_")} = {column} "
        if filter is not None: qry+=' '+filter.replace("table.", f"{self.table}.")
        qry += ";"
        
        data = read_table(qry)
        df = None
        column_names = [list(row) for row in zip(*self.columns)][0]
        if len(self.foreign_columns):            
            for column in self.foreign_columns:
                column_names.append(f"{column.replace(".id", "_name")}")
                
        if data:
            indexes = [list(i) for i in zip(*data)][0]
            df = pd.DataFrame(data=data, columns=column_names, index=indexes)
        return df 
    
    def add(self, fields, values):
        f = []
        for field in fields: f.append(field)
        v = []
        for value in values: v.append(value)
        
        columns = list(map(list, zip(*self.columns)))[0]
        for field, value in zip(fields, values):
            if field not in columns:
                v.pop(f.index(field))
                f.pop(f.index(field))
            else:
                pass
                #print(f'field in columns = {field}')
                               
        formatted_values = convert_sqlite_python(columns=self.columns, fields=f, values=v)
        #print(f'formatted values = {formatted_values}')
        qry = f"INSERT INTO {self.table} ({','.join(f)}) VALUES ({','.join(formatted_values)});"
        return write_table(qry)  

    def update(self, id, fields, values):
        formatted_values = convert_sqlite_python(columns=self.columns, fields=fields, values=values)
        cols = []
        for field, value in zip(fields, formatted_values):
            cols.append(f"{field}={value}")

        qry = f"UPDATE {self.table} SET {','.join(cols)} WHERE id={id};"
        return write_table(qry)
    
    def delete(self, id):
        qry = f'DELETE FROM {self.table} WHERE id={id}'
        return write_table(qry) 
    

class event_groups():
    table = 'event_groups'   
    columns = None
    foreign_columns = None
    
    def __init__(self):
        self.columns = read_table_columns_full(self.table)
        self.foreign_columns = read_table_foreign_keys(self.table)

    def read(self, filter=None):
        qry = f"SELECT {self.table}.* "
        if len(self.foreign_columns):            
            for column in self.foreign_columns:
                qry += f", {column.replace(".id", ".name")} {column.replace(".id", "_name")} "
        qry += f"FROM {self.table} "
        if len(self.foreign_columns):
            for column in self.foreign_columns:
                qry += f"LEFT JOIN {column[:column.find(".")-1]}s ON {self.table}.{column.replace("s.", "_")} = {column} "
        if filter is not None: qry+=' '+filter.replace("table.", f"{self.table}.")
        qry += ";"
        
        data = read_table(qry)
        df = None
        column_names = [list(row) for row in zip(*self.columns)][0]
        if len(self.foreign_columns):            
            for column in self.foreign_columns:
                column_names.append(f"{column.replace(".id", "_name")}")
                
        if data:
            indexes = [list(i) for i in zip(*data)][0]
            df = pd.DataFrame(data=data, columns=column_names, index=indexes)
        return df 
    
    def add(self, fields, values):
        f = []
        for field in fields: f.append(field)
        v = []
        for value in values: v.append(value)
        
        columns = list(map(list, zip(*self.columns)))[0]
        for field, value in zip(fields, values):
            if field not in columns:
                v.pop(f.index(field))
                f.pop(f.index(field))
            else:
                pass
                #print(f'field in columns = {field}')
                               
        formatted_values = convert_sqlite_python(columns=self.columns, fields=f, values=v)
        #print(f'formatted values = {formatted_values}')
        qry = f"INSERT INTO {self.table} ({','.join(f)}) VALUES ({','.join(formatted_values)});"
        return write_table(qry)  

    def update(self, id, fields, values):
        formatted_values = convert_sqlite_python(columns=self.columns, fields=fields, values=values)
        cols = []
        for field, value in zip(fields, formatted_values):
            cols.append(f"{field}={value}")

        qry = f"UPDATE {self.table} SET {','.join(cols)} WHERE id={id};"
        return write_table(qry)
    
    def delete(self, id):
        qry = f'DELETE FROM {self.table} WHERE id={id}'
        return write_table(qry) 


class event_validated_rounds():
    table = 'event_validated_rounds'   
    columns = None
    foreign_columns = None
    
    def __init__(self):
        self.columns = read_table_columns_full(self.table)
        self.foreign_columns = read_table_foreign_keys(self.table)

    def read(self, filter=None):
        qry = f"SELECT {self.table}.* "
        if len(self.foreign_columns):            
            for column in self.foreign_columns:
                qry += f", {column.replace(".id", ".name")} {column.replace(".id", "_name")} "
        qry += f"FROM {self.table} "
        if len(self.foreign_columns):
            for column in self.foreign_columns:
                qry += f"LEFT JOIN {column[:column.find(".")-1]}s ON {self.table}.{column.replace("s.", "_")} = {column} "
        if filter is not None: qry+=' '+filter.replace("table.", f"{self.table}.")
        qry += ";"
        
        data = read_table(qry)
        df = None
        column_names = [list(row) for row in zip(*self.columns)][0]
        if len(self.foreign_columns):            
            for column in self.foreign_columns:
                column_names.append(f"{column.replace(".id", "_name")}")
                
        if data:
            indexes = [list(i) for i in zip(*data)][0]
            df = pd.DataFrame(data=data, columns=column_names, index=indexes)
        return df 
    
    def add(self, fields, values):
        f = []
        for field in fields: f.append(field)
        v = []
        for value in values: v.append(value)
        
        columns = list(map(list, zip(*self.columns)))[0]
        for field, value in zip(fields, values):
            if field not in columns:
                v.pop(f.index(field))
                f.pop(f.index(field))
            else:
                pass
                #print(f'field in columns = {field}')
                               
        formatted_values = convert_sqlite_python(columns=self.columns, fields=f, values=v)
        #print(f'formatted values = {formatted_values}')
        qry = f"INSERT INTO {self.table} ({','.join(f)}) VALUES ({','.join(formatted_values)});"
        return write_table(qry)  

    def update(self, id, fields, values):
        formatted_values = convert_sqlite_python(columns=self.columns, fields=fields, values=values)
        cols = []
        for field, value in zip(fields, formatted_values):
            cols.append(f"{field}={value}")

        qry = f"UPDATE {self.table} SET {','.join(cols)} WHERE id={id};"
        return write_table(qry)
    
    def delete(self, id):
        qry = f'DELETE FROM {self.table} WHERE id={id}'
        return write_table(qry) 


class event_validated_holes():
    table = 'event_validated_holes'   
    columns = None
    foreign_columns = None
    
    def __init__(self):
        self.columns = read_table_columns_full(self.table)
        self.foreign_columns = read_table_foreign_keys(self.table)

    def read(self, filter=None):
        qry = f"SELECT {self.table}.* "
        if len(self.foreign_columns):            
            for column in self.foreign_columns:
                qry += f", {column.replace(".id", ".name")} {column.replace(".id", "_name")} "
        qry += f"FROM {self.table} "
        if len(self.foreign_columns):
            for column in self.foreign_columns:
                qry += f"LEFT JOIN {column[:column.find(".")-1]}s ON {self.table}.{column.replace("s.", "_")} = {column} "
        if filter is not None: qry+=' '+filter.replace("table.", f"{self.table}.")
        qry += ";"
        
        data = read_table(qry)
        df = None
        column_names = [list(row) for row in zip(*self.columns)][0]
        if len(self.foreign_columns):            
            for column in self.foreign_columns:
                column_names.append(f"{column.replace(".id", "_name")}")
                
        if data:
            indexes = [list(i) for i in zip(*data)][0]
            df = pd.DataFrame(data=data, columns=column_names, index=indexes)
        return df 
    
    def add(self, fields, values):
        f = []
        for field in fields: f.append(field)
        v = []
        for value in values: v.append(value)
        
        columns = list(map(list, zip(*self.columns)))[0]
        for field, value in zip(fields, values):
            if field not in columns:
                v.pop(f.index(field))
                f.pop(f.index(field))
            else:
                pass
                #print(f'field in columns = {field}')
                               
        formatted_values = convert_sqlite_python(columns=self.columns, fields=f, values=v)
        #print(f'formatted values = {formatted_values}')
        qry = f"INSERT INTO {self.table} ({','.join(f)}) VALUES ({','.join(formatted_values)});"
        return write_table(qry)  

    def update(self, id, fields, values):
        formatted_values = convert_sqlite_python(columns=self.columns, fields=fields, values=values)
        cols = []
        for field, value in zip(fields, formatted_values):
            cols.append(f"{field}={value}")

        qry = f"UPDATE {self.table} SET {','.join(cols)} WHERE id={id};"
        return write_table(qry)
    
    def delete(self, id):
        qry = f'DELETE FROM {self.table} WHERE id={id}'
        return write_table(qry) 

    
class event_participants():
    table = 'event_participants'   
    columns = None
    foreign_columns = None
    
    def __init__(self):
        self.columns = read_table_columns_full(self.table)
        self.foreign_columns = read_table_foreign_keys(self.table)

    def read(self, filter=None):
        qry = f"SELECT {self.table}.* "
        if len(self.foreign_columns):            
            for column in self.foreign_columns:
                qry += f", {column.replace(".id", ".name")} {column.replace(".id", "_name")} "
        qry += f"FROM {self.table} "
        if len(self.foreign_columns):
            for column in self.foreign_columns:
                qry += f"LEFT JOIN {column[:column.find(".")-1]}s ON {self.table}.{column.replace("s.", "_")} = {column} "
        if filter is not None: qry+=' '+filter.replace("table.", f"{self.table}.")
        qry += ";"
        
        data = read_table(qry)
        df = None
        column_names = [list(row) for row in zip(*self.columns)][0]
        if len(self.foreign_columns):            
            for column in self.foreign_columns:
                column_names.append(f"{column.replace(".id", "_name")}")
                
        if data:
            indexes = [list(i) for i in zip(*data)][0]
            df = pd.DataFrame(data=data, columns=column_names, index=indexes)
        return df 
    
    def add(self, fields, values):
        f = []
        for field in fields: f.append(field)
        v = []
        for value in values: v.append(value)
        
        columns = list(map(list, zip(*self.columns)))[0]
        for field, value in zip(fields, values):
            if field not in columns:
                v.pop(f.index(field))
                f.pop(f.index(field))
            else:
                pass
                #print(f'field in columns = {field}')
                               
        formatted_values = convert_sqlite_python(columns=self.columns, fields=f, values=v)
        #print(f'formatted values = {formatted_values}')
        qry = f"INSERT INTO {self.table} ({','.join(f)}) VALUES ({','.join(formatted_values)});"
        return write_table(qry)  

    def update(self, id, fields, values):
        formatted_values = convert_sqlite_python(columns=self.columns, fields=fields, values=values)
        cols = []
        for field, value in zip(fields, formatted_values):
            cols.append(f"{field}={value}")

        qry = f"UPDATE {self.table} SET {','.join(cols)} WHERE id={id};"
        return write_table(qry)
    
    def delete(self, id):
        qry = f'DELETE FROM {self.table} WHERE id={id}'
        return write_table(qry) 


class matches():    
    table = 'matchs'
    columns = None
    foreign_columns = None
    
    def __init__(self):
        self.columns = read_table_columns_full(self.table)
        self.foreign_columns = read_table_foreign_keys(self.table)

    def read(self, filter=None):
        qry = f"SELECT {self.table}.* "
        if len(self.foreign_columns):            
            for column in self.foreign_columns:
                qry += f", {column.replace(".id", ".name")} {column.replace(".id", "_name")} "
        qry += f"FROM {self.table} "
        if len(self.foreign_columns):
            for column in self.foreign_columns:
                qry += f"LEFT JOIN {column[:column.find(".")-1]}s ON {self.table}.{column.replace("s.", "_")} = {column} "
        if filter is not None: qry+=' '+filter.replace("table.", f"{self.table}.")
        qry += ";"
        
        data = read_table(qry)
        df = None
        column_names = [list(row) for row in zip(*self.columns)][0]
        if len(self.foreign_columns):            
            for column in self.foreign_columns:
                column_names.append(f"{column.replace(".id", "_name")}")
                
        if data:
            indexes = [list(i) for i in zip(*data)][0]
            df = pd.DataFrame(data=data, columns=column_names, index=indexes)
        return df 
    
    def add(self, fields, values):
        f = []
        for field in fields: f.append(field)
        v = []
        for value in values: v.append(value)
        
        columns = list(map(list, zip(*self.columns)))[0]
        for field, value in zip(fields, values):
            if field not in columns:
                v.pop(f.index(field))
                f.pop(f.index(field))
            else:
                pass
                #print(f'field in columns = {field}')
                               
        formatted_values = convert_sqlite_python(columns=self.columns, fields=f, values=v)
        #print(f'formatted values = {formatted_values}')
        qry = f"INSERT INTO {self.table} ({','.join(f)}) VALUES ({','.join(formatted_values)});"
        return write_table(qry)  

    def update(self, id, fields, values):
        formatted_values = convert_sqlite_python(columns=self.columns, fields=fields, values=values)
        cols = []
        for field, value in zip(fields, formatted_values):
            cols.append(f"{field}={value}")

        qry = f"UPDATE {self.table} SET {','.join(cols)} WHERE id={id};"
        return write_table(qry)
    
    def delete(self, id):
        qry = f'DELETE FROM {self.table} WHERE id={id}'
        return write_table(qry) 


class match_groups():    
    table = 'match_groups'
    columns = None
    foreign_columns = None
    
    def __init__(self):
        self.columns = read_table_columns_full(self.table)
        self.foreign_columns = read_table_foreign_keys(self.table)

    def read(self, filter=None):
        qry = f"SELECT {self.table}.* "
        if len(self.foreign_columns):            
            for column in self.foreign_columns:
                qry += f", {column.replace(".id", ".name")} {column.replace(".id", "_name")} "
        qry += f"FROM {self.table} "
        if len(self.foreign_columns):
            for column in self.foreign_columns:
                qry += f"LEFT JOIN {column[:column.find(".")-1]}s ON {self.table}.{column.replace("s.", "_")} = {column} "
        if filter is not None: qry+=' '+filter.replace("table.", f"{self.table}.")
        qry += ";"
        
        data = read_table(qry)
        df = None
        column_names = [list(row) for row in zip(*self.columns)][0]
        if len(self.foreign_columns):            
            for column in self.foreign_columns:
                column_names.append(f"{column.replace(".id", "_name")}")
                
        if data:
            indexes = [list(i) for i in zip(*data)][0]
            df = pd.DataFrame(data=data, columns=column_names, index=indexes)
        return df 
    
    def add(self, fields, values):
        f = []
        for field in fields: f.append(field)
        v = []
        for value in values: v.append(value)
        
        columns = list(map(list, zip(*self.columns)))[0]
        for field, value in zip(fields, values):
            if field not in columns:
                v.pop(f.index(field))
                f.pop(f.index(field))
            else:
                pass
                #print(f'field in columns = {field}')
                               
        formatted_values = convert_sqlite_python(columns=self.columns, fields=f, values=v)
        #print(f'formatted values = {formatted_values}')
        qry = f"INSERT INTO {self.table} ({','.join(f)}) VALUES ({','.join(formatted_values)});"
        return write_table(qry)  

    def update(self, id, fields, values):
        formatted_values = convert_sqlite_python(columns=self.columns, fields=fields, values=values)
        cols = []
        for field, value in zip(fields, formatted_values):
            cols.append(f"{field}={value}")

        qry = f"UPDATE {self.table} SET {','.join(cols)} WHERE id={id};"
        return write_table(qry)
    
    def delete(self, id):
        qry = f'DELETE FROM {self.table} WHERE id={id}'
        return write_table(qry) 


class match_participants():    
    table = 'match_participants'
    columns = None
    foreign_columns = None
    
    def __init__(self):
        self.columns = read_table_columns_full(self.table)
        self.foreign_columns = read_table_foreign_keys(self.table)

    def read(self, filter=None):
        qry = f"SELECT {self.table}.* "
        if len(self.foreign_columns):            
            for column in self.foreign_columns:
                qry += f", {column.replace(".id", ".name")} {column.replace(".id", "_name")} "
        qry += f"FROM {self.table} "
        if len(self.foreign_columns):
            for column in self.foreign_columns:
                qry += f"LEFT JOIN {column[:column.find(".")-1]}s ON {self.table}.{column.replace("s.", "_")} = {column} "
        if filter is not None: qry+=' '+filter.replace("table.", f"{self.table}.")
        qry += ";"
        
        data = read_table(qry)
        df = None
        column_names = [list(row) for row in zip(*self.columns)][0]
        if len(self.foreign_columns):            
            for column in self.foreign_columns:
                column_names.append(f"{column.replace(".id", "_name")}")
                
        if data:
            indexes = [list(i) for i in zip(*data)][0]
            df = pd.DataFrame(data=data, columns=column_names, index=indexes)
        return df 
    
    def add(self, fields, values):
        f = []
        for field in fields: f.append(field)
        v = []
        for value in values: v.append(value)
        
        columns = list(map(list, zip(*self.columns)))[0]
        for field, value in zip(fields, values):
            if field not in columns:
                v.pop(f.index(field))
                f.pop(f.index(field))
            else:
                pass
                #print(f'field in columns = {field}')
                               
        formatted_values = convert_sqlite_python(columns=self.columns, fields=f, values=v)
        #print(f'formatted values = {formatted_values}')
        qry = f"INSERT INTO {self.table} ({','.join(f)}) VALUES ({','.join(formatted_values)});"
        return write_table(qry)  

    def update(self, id, fields, values):
        formatted_values = convert_sqlite_python(columns=self.columns, fields=fields, values=values)
        cols = []
        for field, value in zip(fields, formatted_values):
            cols.append(f"{field}={value}")

        qry = f"UPDATE {self.table} SET {','.join(cols)} WHERE id={id};"
        return write_table(qry)
    
    def delete(self, id):
        qry = f'DELETE FROM {self.table} WHERE id={id}'
        return write_table(qry) 
      

class match_holes():    
    table = 'match_holes'
    columns = None
    foreign_columns = None
    
    def __init__(self):
        self.columns = read_table_columns_full(self.table)
        self.foreign_columns = read_table_foreign_keys(self.table)

    def read(self, filter=None):
        qry = f"SELECT {self.table}.* "
        if len(self.foreign_columns):            
            for column in self.foreign_columns:
                qry += f", {column.replace(".id", ".name")} {column.replace(".id", "_name")} "
        qry += f"FROM {self.table} "
        if len(self.foreign_columns):
            for column in self.foreign_columns:
                qry += f"LEFT JOIN {column[:column.find(".")-1]}s ON {self.table}.{column.replace("s.", "_")} = {column} "
        if filter is not None: qry+=' '+filter.replace("table.", f"{self.table}.")
        qry += ";"
        
        data = read_table(qry)
        df = None
        column_names = [list(row) for row in zip(*self.columns)][0]
        if len(self.foreign_columns):            
            for column in self.foreign_columns:
                column_names.append(f"{column.replace(".id", "_name")}")
                
        if data:
            indexes = [list(i) for i in zip(*data)][0]
            df = pd.DataFrame(data=data, columns=column_names, index=indexes)
        return df 
    
    def add(self, fields, values):
        f = []
        for field in fields: f.append(field)
        v = []
        for value in values: v.append(value)
        
        columns = list(map(list, zip(*self.columns)))[0]
        for field, value in zip(fields, values):
            if field not in columns:
                v.pop(f.index(field))
                f.pop(f.index(field))
            else:
                pass
                #print(f'field in columns = {field}')
                               
        formatted_values = convert_sqlite_python(columns=self.columns, fields=f, values=v)
        #print(f'formatted values = {formatted_values}')
        qry = f"INSERT INTO {self.table} ({','.join(f)}) VALUES ({','.join(formatted_values)});"
        return write_table(qry)  

    def update(self, id, fields, values):
        formatted_values = convert_sqlite_python(columns=self.columns, fields=fields, values=values)
        cols = []
        for field, value in zip(fields, formatted_values):
            cols.append(f"{field}={value}")

        qry = f"UPDATE {self.table} SET {','.join(cols)} WHERE id={id};"
        return write_table(qry)
    
    def delete(self, id):
        qry = f'DELETE FROM {self.table} WHERE id={id}'
        return write_table(qry) 
      

class scoring_cards():
    table = 'scoring_cards'
    columns = None
    foreign_columns = None
    
    def __init__(self):
        self.columns = read_table_columns_full(self.table)
        self.foreign_columns = read_table_foreign_keys(self.table)

    def read(self, filter=None):
        qry = f"SELECT {self.table}.* "
        if len(self.foreign_columns):            
            for column in self.foreign_columns:
                qry += f", {column.replace(".id", ".name")} {column.replace(".id", "_name")} "
        qry += f"FROM {self.table} "
        if len(self.foreign_columns):
            for column in self.foreign_columns:
                qry += f"LEFT JOIN {column[:column.find(".")-1]}s ON {self.table}.{column.replace("s.", "_")} = {column} "
        if filter is not None: qry+=' '+filter.replace("table.", f"{self.table}.")
        qry += ";"
        
        data = read_table(qry)
        df = None
        column_names = [list(row) for row in zip(*self.columns)][0]
        if len(self.foreign_columns):            
            for column in self.foreign_columns:
                column_names.append(f"{column.replace(".id", "_name")}")
                
        if data:
            indexes = [list(i) for i in zip(*data)][0]
            df = pd.DataFrame(data=data, columns=column_names, index=indexes)
        return df 
    
    def add(self, fields, values):
        f = []
        for field in fields: f.append(field)
        v = []
        for value in values: v.append(value)
        
        columns = list(map(list, zip(*self.columns)))[0]
        for field, value in zip(fields, values):
            if field not in columns:
                v.pop(f.index(field))
                f.pop(f.index(field))
            else:
                pass
                #print(f'field in columns = {field}')
                               
        formatted_values = convert_sqlite_python(columns=self.columns, fields=f, values=v)
        #print(f'formatted values = {formatted_values}')
        qry = f"INSERT INTO {self.table} ({','.join(f)}) VALUES ({','.join(formatted_values)});"
        return write_table(qry)  

    def update(self, id, fields, values):
        formatted_values = convert_sqlite_python(columns=self.columns, fields=fields, values=values)
        cols = []
        for field, value in zip(fields, formatted_values):
            cols.append(f"{field}={value}")

        qry = f"UPDATE {self.table} SET {','.join(cols)} WHERE id={id};"
        return write_table(qry)
    
    def delete(self, id):
        qry = f'DELETE FROM {self.table} WHERE id={id}'
        return write_table(qry) 


class scoring_card_groups():
    table = 'scoring_card_groups'   
    columns = None
    foreign_columns = None
    
    def __init__(self):
        self.columns = read_table_columns_full(self.table)
        self.foreign_columns = read_table_foreign_keys(self.table)

    def read(self, filter=None):
        qry = f"SELECT {self.table}.* "
        if len(self.foreign_columns):            
            for column in self.foreign_columns:
                qry += f", {column.replace(".id", ".name")} {column.replace(".id", "_name")} "
        qry += f"FROM {self.table} "
        if len(self.foreign_columns):
            for column in self.foreign_columns:
                qry += f"LEFT JOIN {column[:column.find(".")-1]}s ON {self.table}.{column.replace("s.", "_")} = {column} "
        if filter is not None: qry+=' '+filter.replace("table.", f"{self.table}.")
        qry += ";"
        
        data = read_table(qry)
        df = None
        column_names = [list(row) for row in zip(*self.columns)][0]
        if len(self.foreign_columns):            
            for column in self.foreign_columns:
                column_names.append(f"{column.replace(".id", "_name")}")
                
        if data:
            indexes = [list(i) for i in zip(*data)][0]
            df = pd.DataFrame(data=data, columns=column_names, index=indexes)
        return df 
    
    def add(self, fields, values):
        f = []
        for field in fields: f.append(field)
        v = []
        for value in values: v.append(value)
        
        columns = list(map(list, zip(*self.columns)))[0]
        for field, value in zip(fields, values):
            if field not in columns:
                v.pop(f.index(field))
                f.pop(f.index(field))
            else:
                pass
                #print(f'field in columns = {field}')
                               
        formatted_values = convert_sqlite_python(columns=self.columns, fields=f, values=v)
        #print(f'formatted values = {formatted_values}')
        qry = f"INSERT INTO {self.table} ({','.join(f)}) VALUES ({','.join(formatted_values)});"
        return write_table(qry)  

    def update(self, id, fields, values):
        formatted_values = convert_sqlite_python(columns=self.columns, fields=fields, values=values)
        cols = []
        for field, value in zip(fields, formatted_values):
            cols.append(f"{field}={value}")

        qry = f"UPDATE {self.table} SET {','.join(cols)} WHERE id={id};"
        return write_table(qry)
    
    def delete(self, id):
        qry = f'DELETE FROM {self.table} WHERE id={id}'
        return write_table(qry) 

    
class scoring_card_participants():
    table = 'scoring_card_participants'   
    columns = None
    foreign_columns = None
    
    def __init__(self):
        self.columns = read_table_columns_full(self.table)
        self.foreign_columns = read_table_foreign_keys(self.table)

    def read(self, filter=None):
        qry = f"SELECT {self.table}.* "
        if len(self.foreign_columns):            
            for column in self.foreign_columns:
                qry += f", {column.replace(".id", ".name")} {column.replace(".id", "_name")} "
        qry += f"FROM {self.table} "
        if len(self.foreign_columns):
            for column in self.foreign_columns:
                qry += f"LEFT JOIN {column[:column.find(".")-1]}s ON {self.table}.{column.replace("s.", "_")} = {column} "
        if filter is not None: qry+=' '+filter.replace("table.", f"{self.table}.")
        qry += ";"
        
        data = read_table(qry)
        df = None
        column_names = [list(row) for row in zip(*self.columns)][0]
        if len(self.foreign_columns):            
            for column in self.foreign_columns:
                column_names.append(f"{column.replace(".id", "_name")}")
                
        if data:
            indexes = [list(i) for i in zip(*data)][0]
            df = pd.DataFrame(data=data, columns=column_names, index=indexes)
        return df 
    
    def add(self, fields, values):
        f = []
        for field in fields: f.append(field)
        v = []
        for value in values: v.append(value)
        
        columns = list(map(list, zip(*self.columns)))[0]
        for field, value in zip(fields, values):
            if field not in columns:
                v.pop(f.index(field))
                f.pop(f.index(field))
            else:
                pass
                #print(f'field in columns = {field}')
                               
        formatted_values = convert_sqlite_python(columns=self.columns, fields=f, values=v)
        #print(f'formatted values = {formatted_values}')
        qry = f"INSERT INTO {self.table} ({','.join(f)}) VALUES ({','.join(formatted_values)});"
        return write_table(qry)  

    def update(self, id, fields, values):
        formatted_values = convert_sqlite_python(columns=self.columns, fields=fields, values=values)
        cols = []
        for field, value in zip(fields, formatted_values):
            cols.append(f"{field}={value}")

        qry = f"UPDATE {self.table} SET {','.join(cols)} WHERE id={id};"
        return write_table(qry)
    
    def delete(self, id):
        qry = f'DELETE FROM {self.table} WHERE id={id}'
        return write_table(qry) 


class scoring_rounds():
    table = 'scoring_rounds'
    columns = None
    foreign_columns = None
    
    def __init__(self):
        self.columns = read_table_columns_full(self.table)
        self.foreign_columns = read_table_foreign_keys(self.table)

    def read(self, filter=None):
        qry = f"SELECT {self.table}.* "
        if len(self.foreign_columns):            
            for column in self.foreign_columns:
                qry += f", {column.replace(".id", ".name")} {column.replace(".id", "_name")} "
        qry += f"FROM {self.table} "
        if len(self.foreign_columns):
            for column in self.foreign_columns:
                qry += f"LEFT JOIN {column[:column.find(".")-1]}s ON {self.table}.{column.replace("s.", "_")} = {column} "
        if filter is not None: qry+=' '+filter.replace("table.", f"{self.table}.")
        qry += ";"
        
        data = read_table(qry)
        df = None
        column_names = [list(row) for row in zip(*self.columns)][0]
        if len(self.foreign_columns):            
            for column in self.foreign_columns:
                column_names.append(f"{column.replace(".id", "_name")}")
                
        if data:
            indexes = [list(i) for i in zip(*data)][0]
            df = pd.DataFrame(data=data, columns=column_names, index=indexes)
        return df 
    
    def add(self, fields, values):
        f = []
        for field in fields: f.append(field)
        v = []
        for value in values: v.append(value)
        
        columns = list(map(list, zip(*self.columns)))[0]
        for field, value in zip(fields, values):
            if field not in columns:
                v.pop(f.index(field))
                f.pop(f.index(field))
            else:
                pass
                #print(f'field in columns = {field}')
                               
        formatted_values = convert_sqlite_python(columns=self.columns, fields=f, values=v)
        #print(f'formatted values = {formatted_values}')
        qry = f"INSERT INTO {self.table} ({','.join(f)}) VALUES ({','.join(formatted_values)});"
        return write_table(qry)  

    def update(self, id, fields, values):
        formatted_values = convert_sqlite_python(columns=self.columns, fields=fields, values=values)
        cols = []
        for field, value in zip(fields, formatted_values):
            cols.append(f"{field}={value}")

        qry = f"UPDATE {self.table} SET {','.join(cols)} WHERE id={id};"
        return write_table(qry)
    
    def delete(self, id):
        qry = f'DELETE FROM {self.table} WHERE id={id}'
        return write_table(qry) 


class scoring_holes():
    table = 'scoring_holes'
    columns = None
    foreign_columns = None
    
    def __init__(self):
        self.columns = read_table_columns_full(self.table)
        self.foreign_columns = read_table_foreign_keys(self.table)

    def read(self, filter=None):
        qry = f"SELECT {self.table}.* "
        if len(self.foreign_columns):            
            for column in self.foreign_columns:
                qry += f", {column.replace(".id", ".name")} {column.replace(".id", "_name")} "
        qry += f"FROM {self.table} "
        if len(self.foreign_columns):
            for column in self.foreign_columns:
                qry += f"LEFT JOIN {column[:column.find(".")-1]}s ON {self.table}.{column.replace("s.", "_")} = {column} "
        if filter is not None: qry+=' '+filter.replace("table.", f"{self.table}.")
        qry += ";"
        
        data = read_table(qry)
        df = None
        column_names = [list(row) for row in zip(*self.columns)][0]
        if len(self.foreign_columns):            
            for column in self.foreign_columns:
                column_names.append(f"{column.replace(".id", "_name")}")
                
        if data:
            indexes = [list(i) for i in zip(*data)][0]
            df = pd.DataFrame(data=data, columns=column_names, index=indexes)
        return df 
    
    def add(self, fields, values):
        f = []
        for field in fields: f.append(field)
        v = []
        for value in values: v.append(value)
        
        columns = list(map(list, zip(*self.columns)))[0]
        for field, value in zip(fields, values):
            if field not in columns:
                v.pop(f.index(field))
                f.pop(f.index(field))
            else:
                pass
                #print(f'field in columns = {field}')
                               
        formatted_values = convert_sqlite_python(columns=self.columns, fields=f, values=v)
        #print(f'formatted values = {formatted_values}')
        qry = f"INSERT INTO {self.table} ({','.join(f)}) VALUES ({','.join(formatted_values)});"
        return write_table(qry)  

    def update(self, id, fields, values):
        formatted_values = convert_sqlite_python(columns=self.columns, fields=fields, values=values)
        cols = []
        for field, value in zip(fields, formatted_values):
            cols.append(f"{field}={value}")

        qry = f"UPDATE {self.table} SET {','.join(cols)} WHERE id={id};"
        return write_table(qry)
    
    def delete(self, id):
        qry = f'DELETE FROM {self.table} WHERE id={id}'
        return write_table(qry) 


class courses():
    table = 'courses'
    columns = None
    foreign_columns = None
    
    def __init__(self):
        self.columns = read_table_columns_full(self.table)
        self.foreign_columns = read_table_foreign_keys(self.table)

    def read(self, filter=None):
        qry = f"SELECT {self.table}.* "
        if len(self.foreign_columns):            
            for column in self.foreign_columns:
                qry += f", {column.replace(".id", ".name")} {column.replace(".id", "_name")} "
        qry += f"FROM {self.table} "
        if len(self.foreign_columns):
            for column in self.foreign_columns:
                qry += f"LEFT JOIN {column[:column.find(".")-1]}s ON {self.table}.{column.replace("s.", "_")} = {column} "
        if filter is not None: qry+=' '+filter.replace("table.", f"{self.table}.")
        qry += ";"
        
        data = read_table(qry)
        df = None
        column_names = [list(row) for row in zip(*self.columns)][0]
        if len(self.foreign_columns):            
            for column in self.foreign_columns:
                column_names.append(f"{column.replace(".id", "_name")}")
                
        if data:
            indexes = [list(i) for i in zip(*data)][0]
            df = pd.DataFrame(data=data, columns=column_names, index=indexes)
        return df 
    
    def add(self, fields, values):
        f = []
        for field in fields: f.append(field)
        v = []
        for value in values: v.append(value)
        
        columns = list(map(list, zip(*self.columns)))[0]
        for field, value in zip(fields, values):
            if field not in columns:
                v.pop(f.index(field))
                f.pop(f.index(field))
            else:
                pass
                #print(f'field in columns = {field}')
                               
        formatted_values = convert_sqlite_python(columns=self.columns, fields=f, values=v)
        #print(f'formatted values = {formatted_values}')
        qry = f"INSERT INTO {self.table} ({','.join(f)}) VALUES ({','.join(formatted_values)});"
        return write_table(qry)  

    def update(self, id, fields, values):
        formatted_values = convert_sqlite_python(columns=self.columns, fields=fields, values=values)
        cols = []
        for field, value in zip(fields, formatted_values):
            cols.append(f"{field}={value}")

        qry = f"UPDATE {self.table} SET {','.join(cols)} WHERE id={id};"
        return write_table(qry)
    
    def delete(self, id):
        qry = f'DELETE FROM {self.table} WHERE id={id}'
        return write_table(qry) 


class course_tees():
    table = 'course_tees'
    columns = None
    foreign_columns = None
    
    def __init__(self):
        self.columns = read_table_columns_full(self.table)
        self.foreign_columns = read_table_foreign_keys(self.table)

    def read(self, filter=None):
        qry = f"SELECT {self.table}.* "
        if len(self.foreign_columns):            
            for column in self.foreign_columns:
                qry += f", {column.replace(".id", ".name")} {column.replace(".id", "_name")} "
        qry += f"FROM {self.table} "
        if len(self.foreign_columns):
            for column in self.foreign_columns:
                qry += f"LEFT JOIN {column[:column.find(".")-1]}s ON {self.table}.{column.replace("s.", "_")} = {column} "
        if filter is not None: qry+=' '+filter.replace("table.", f"{self.table}.")
        qry += ";"
        
        data = read_table(qry)
        df = None
        column_names = [list(row) for row in zip(*self.columns)][0]
        if len(self.foreign_columns):            
            for column in self.foreign_columns:
                column_names.append(f"{column.replace(".id", "_name")}")
                
        if data:
            indexes = [list(i) for i in zip(*data)][0]
            df = pd.DataFrame(data=data, columns=column_names, index=indexes)
        return df 
    
    def add(self, fields, values):
        f = []
        for field in fields: f.append(field)
        v = []
        for value in values: v.append(value)
        
        columns = list(map(list, zip(*self.columns)))[0]
        for field, value in zip(fields, values):
            if field not in columns:
                v.pop(f.index(field))
                f.pop(f.index(field))
            else:
                pass
                #print(f'field in columns = {field}')
                               
        formatted_values = convert_sqlite_python(columns=self.columns, fields=f, values=v)
        #print(f'formatted values = {formatted_values}')
        qry = f"INSERT INTO {self.table} ({','.join(f)}) VALUES ({','.join(formatted_values)});"
        return write_table(qry)  

    def update(self, id, fields, values):
        formatted_values = convert_sqlite_python(columns=self.columns, fields=fields, values=values)
        cols = []
        for field, value in zip(fields, formatted_values):
            cols.append(f"{field}={value}")

        qry = f"UPDATE {self.table} SET {','.join(cols)} WHERE id={id};"
        return write_table(qry)
    
    def delete(self, id):
        qry = f'DELETE FROM {self.table} WHERE id={id}'
        return write_table(qry) 
               

class groups():
    table = 'groups'
    columns = None
    foreign_columns = None
    
    def __init__(self):
        self.columns = read_table_columns_full(self.table)
        self.foreign_columns = read_table_foreign_keys(self.table)

    def read(self, filter=None):
        qry = f"SELECT {self.table}.* "
        if len(self.foreign_columns):            
            for column in self.foreign_columns:
                qry += f", {column.replace(".id", ".name")} {column.replace(".id", "_name")} "
        qry += f"FROM {self.table} "
        if len(self.foreign_columns):
            for column in self.foreign_columns:
                qry += f"LEFT JOIN {column[:column.find(".")-1]}s ON {self.table}.{column.replace("s.", "_")} = {column} "
        if filter is not None: qry+=' '+filter.replace("table.", f"{self.table}.")
        qry += ";"
        
        data = read_table(qry)
        df = None
        column_names = [list(row) for row in zip(*self.columns)][0]
        if len(self.foreign_columns):            
            for column in self.foreign_columns:
                column_names.append(f"{column.replace(".id", "_name")}")
                
        if data:
            indexes = [list(i) for i in zip(*data)][0]
            df = pd.DataFrame(data=data, columns=column_names, index=indexes)
        return df 
    
    def add(self, fields, values):
        f = []
        for field in fields: f.append(field)
        v = []
        for value in values: v.append(value)
        
        columns = list(map(list, zip(*self.columns)))[0]
        for field, value in zip(fields, values):
            if field not in columns:
                v.pop(f.index(field))
                f.pop(f.index(field))
            else:
                pass
                #print(f'field in columns = {field}')
                               
        formatted_values = convert_sqlite_python(columns=self.columns, fields=f, values=v)
        #print(f'formatted values = {formatted_values}')
        qry = f"INSERT INTO {self.table} ({','.join(f)}) VALUES ({','.join(formatted_values)});"
        return write_table(qry)  

    def update(self, id, fields, values):
        formatted_values = convert_sqlite_python(columns=self.columns, fields=fields, values=values)
        cols = []
        for field, value in zip(fields, formatted_values):
            cols.append(f"{field}={value}")

        qry = f"UPDATE {self.table} SET {','.join(cols)} WHERE id={id};"
        return write_table(qry)
    
    def delete(self, id):
        qry = f'DELETE FROM {self.table} WHERE id={id}'
        return write_table(qry) 

    
class participants():
    table = 'participants'
    columns = None
    foreign_columns = None
    
    def __init__(self):
        self.columns = read_table_columns_full(self.table)
        self.foreign_columns = read_table_foreign_keys(self.table)

    def read(self, filter=None):
        qry = f"SELECT {self.table}.* "
        if len(self.foreign_columns):            
            for column in self.foreign_columns:
                qry += f", {column.replace(".id", ".name")} {column.replace(".id", "_name")} "
        qry += f"FROM {self.table} "
        if len(self.foreign_columns):
            for column in self.foreign_columns:
                qry += f"LEFT JOIN {column[:column.find(".")-1]}s ON {self.table}.{column.replace("s.", "_")} = {column} "
        if filter is not None: qry+=' '+filter.replace("table.", f"{self.table}.")
        qry += ";"
        
        data = read_table(qry)
        df = None
        column_names = [list(row) for row in zip(*self.columns)][0]
        if len(self.foreign_columns):            
            for column in self.foreign_columns:
                column_names.append(f"{column.replace(".id", "_name")}")
               
        if data:
            indexes = [list(i) for i in zip(*data)][0]
            df = pd.DataFrame(data=data, columns=column_names, index=indexes)
        return df 
    
    def add(self, fields, values):
        f = []
        for field in fields: f.append(field)
        v = []
        for value in values: v.append(value)
        
        columns = list(map(list, zip(*self.columns)))[0]
        for field, value in zip(fields, values):
            if field not in columns:
                v.pop(f.index(field))
                f.pop(f.index(field))
            else:
                pass
                #print(f'field in columns = {field}')
                               
        formatted_values = convert_sqlite_python(columns=self.columns, fields=f, values=v)
        #print(f'formatted values = {formatted_values}')
        qry = f"INSERT INTO {self.table} ({','.join(f)}) VALUES ({','.join(formatted_values)});"
        return write_table(qry)  

    def update(self, id, fields, values):
        formatted_values = convert_sqlite_python(columns=self.columns, fields=fields, values=values)
        cols = []
        for field, value in zip(fields, formatted_values):
            cols.append(f"{field}={value}")

        qry = f"UPDATE {self.table} SET {','.join(cols)} WHERE id={id};"
        return write_table(qry)
    
    def delete(self, id):
        qry = f'DELETE FROM {self.table} WHERE id={id}'
        return write_table(qry) 


class formats():    
    table = 'formats'
    columns = None
    foreign_columns = None
    
    def __init__(self):
        self.columns = read_table_columns_full(self.table)
        self.foreign_columns = read_table_foreign_keys(self.table)

    def read(self, filter=None):
        qry = f"SELECT {self.table}.* "
        if len(self.foreign_columns):            
            for column in self.foreign_columns:
                qry += f", {column.replace(".id", ".name")} {column.replace(".id", "_name")} "
        qry += f"FROM {self.table} "
        if len(self.foreign_columns):
            for column in self.foreign_columns:
                qry += f"LEFT JOIN {column[:column.find(".")-1]}s ON {self.table}.{column.replace("s.", "_")} = {column} "
        if filter is not None: qry+=' '+filter.replace("table.", f"{self.table}.")
        qry += ";"
        
        data = read_table(qry)
        df = None
        column_names = [list(row) for row in zip(*self.columns)][0]
        if len(self.foreign_columns):            
            for column in self.foreign_columns:
                column_names.append(f"{column.replace(".id", "_name")}")
                
        if data:
            indexes = [list(i) for i in zip(*data)][0]
            df = pd.DataFrame(data=data, columns=column_names, index=indexes)
        return df 
    
    def add(self, fields, values):
        f = []
        for field in fields: f.append(field)
        v = []
        for value in values: v.append(value)
        
        columns = list(map(list, zip(*self.columns)))[0]
        for field, value in zip(fields, values):
            if field not in columns:
                v.pop(f.index(field))
                f.pop(f.index(field))
            else:
                pass
                #print(f'field in columns = {field}')
                               
        formatted_values = convert_sqlite_python(columns=self.columns, fields=f, values=v)
        #print(f'formatted values = {formatted_values}')
        qry = f"INSERT INTO {self.table} ({','.join(f)}) VALUES ({','.join(formatted_values)});"
        return write_table(qry)  

    def update(self, id, fields, values):
        formatted_values = convert_sqlite_python(columns=self.columns, fields=fields, values=values)
        cols = []
        for field, value in zip(fields, formatted_values):
            cols.append(f"{field}={value}")

        qry = f"UPDATE {self.table} SET {','.join(cols)} WHERE id={id};"
        return write_table(qry)
    
    def delete(self, id):
        qry = f'DELETE FROM {self.table} WHERE id={id}'
        return write_table(qry) 
          
    
class sequences():
    table = 'sequences'
    columns = None
    
    def __init__(self):
        self.columns = read_table_columns(self.table)
        
    def read(self, filter=None):
        qry = f"SELECT * FROM {self.table}"
        if filter is not None: qry+=' '+filter
        data = read_table(qry)
        df = None
        if data:
            indexes = [list(i) for i in zip(*data)][0]
            df = pd.DataFrame(data=data, columns=self.columns, index=indexes)
        return df  

    def add(self, name, description=None, rating=None, sequence_group_id=None, participant_id=None, sequence_template_id=None):
        qry = f"INSERT INTO {self.table} (name, description, rating, sequence_group_id, participant_id, sequence_template_id) VALUES ('{name}', '{description}', {rating}, {sequence_group_id}, {participant_id}, {sequence_template_id});"        
        return write_table(qry)               


class sequence_templates():
    table = 'sequence_templates'
    columns = None
    
    def __init__(self):
        self.columns = read_table_columns(self.table)
        
    def read(self, filter=None):
        qry = f"SELECT * FROM {self.table}"
        if filter is not None: qry+=' '+filter
        data = read_table(qry)
        df = None
        if data:
            indexes = [list(i) for i in zip(*data)][0]
            df = pd.DataFrame(data=data, columns=self.columns, index=indexes)
        return df  

    def add(self, name, description=None, pars=None, strokes=None, distances=None):
        # Build pars strings
        if pars is not None:
            cols_par = list()
            vals_par = list()
            for entry in range(1,19):
                cols_par.append(f't{entry}_par')
            cols_par.append('t_par')
            cols_par = ', '+', '.join(cols_par)
            for entry in pars:
                vals_par.append(str(entry))
            vals_par.append(str(sum(pars)))
            vals_par = ', '+', '.join(vals_par) 
        else:
            cols_par = ''
            vals_par = ''

        # Build strokes strings
        if strokes is not None:
            cols_stroke = list()
            vals_stroke = list()
            for entry in range(1,19):
                cols_stroke.append(f't{entry}_stroke')
            cols_stroke = ', '+', '.join(cols_stroke)
            for entry in strokes:
                vals_stroke.append(str(entry))
            vals_stroke = ', '+', '.join(vals_stroke) 
        else:
            cols_stroke = ''
            vals_stroke = ''

        # Build distances strings
        if distances is not None:
            cols_distance = list()
            vals_distance = list()
            for entry in range(1,19):
                cols_distance.append(f't{entry}_distance')
            cols_distance.append('t_distance')
            cols_distance = ', '+', '.join(cols_distance)
            for entry in distances:
                vals_distance.append(str(entry))
            vals_distance.append(str(sum(distances)))
            vals_distance = ', '+', '.join(vals_distance) 
        else:
            cols_distance = ''
            vals_distance = ''
            
        qry = f"INSERT INTO {self.table} (name, description {cols_par} {cols_stroke} {cols_distance}) VALUES ('{name}', '{description}' {vals_par} {vals_stroke} {vals_distance});"
        return write_table(qry)         


class tests():
    table = 'tests'
    columns = None
    
    def __init__(self):
        self.columns = read_table_columns(self.table)
        
    def read(self, filter=None):
        qry = f"SELECT * FROM {self.table}"
        if filter is not None: qry+=' '+filter
        data = read_table(qry)
        df = None
        if data:
            indexes = [list(i) for i in zip(*data)][0]
            df = pd.DataFrame(data=data, columns=self.columns, index=indexes)
        return df  
    
    def add(self, name, description=None, sequence_id=None):
        qry = f"INSERT INTO {self.table} (name, description, sequence_id) VALUES ('{name}', '{description}', {sequence_id});"
        return write_table(qry)
    
    def update_description(self, test_id=None, description=None):
        qry = f"UPDATE {self.table} SET description = '{description}' WHERE id = {test_id};"
        return write_table(qry)
    
    def update_outcome(self, test_id=None, outcome=None):
        qry = f"UPDATE {self.table} SET outcome = '{outcome}' WHERE id = {test_id};"
        return write_table(qry)
