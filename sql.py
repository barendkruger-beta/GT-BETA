import streamlit as st
import sqlite3
import math
#from sqlalchemy import text, types
import pandas as pd
from datetime import datetime
from supabase import create_client, Client

@st.cache_resource
def get_supabase_admin():
    return create_client(
            st.secrets["supabase"]["SUPABASE_URL"], 
            st.secrets["supabase"]["SUPABASE_SERVICE_KEY"]
        )

def read_db(conn=None, table=None, filter=None, legacy=False):
    # LEGACY SQLite DB
    if legacy:
        print(f"Start Legacy Read DB from table '{table}' with filter '{filter}'")
        conn = connect()
        try:
            # Step 1: Base query formation
            query = f"SELECT * FROM {table}"
            params = []
            
            # Step 2: Dynamic WHERE clause construction
            if filter is not None and len(filter) > 0:
                where_clauses = []
                for column, value in filter:
                    if isinstance(value, list):
                        # Creates 'column IN (?, ?, ?)' placeholders
                        placeholders = ", ".join(["?"] * len(value))
                        where_clauses.append(f"{column} IN ({placeholders})")
                        params.extend(value)
                    else:
                        # Creates 'column = ?' placeholder
                        where_clauses.append(f"{column} = ?")
                        params.append(value)
                
                query += " WHERE " + " AND ".join(where_clauses)
            
            # Step 3: Execute query and format output
            cursor = conn.cursor()
            cursor.execute(query, params)
            columns = [column[0] for column in cursor.description]
            
            # Convert row tuples to list of dictionaries to match Supabase structure
            all_data = [dict(zip(columns, row)) for row in cursor.fetchall()]
            return all_data

        except Exception as e:
            st.error(f"Database error (SQLite): {e}")
            return None

    # NEW" Supabase DB
    try:
        print(f"Start Read DB from table '{table}' with filter '{filter}'")
        # Read main table to see if there are any results
        select_str = "*"
        query = conn.table(table).select(select_str)       
        if filter is not None:
            for column, value in filter:
                #print(f'Filter: Column={column} Value={value}')
                if isinstance(value, list):
                    query.in_(column, value)
                else:
                    query.eq(column, value)
        response = query.execute()

        # If there are results, see if foreign key columns are included
        foreign_keys = []
        if len(response.data): 
            columns = response.data[0].keys()
            foreign_keys = [column for column in columns if '_id' in column]
            if len(foreign_keys):
                foreign_tables = [column[:-3]+'s' for column in columns if '_id' in column]
                #print(f'Foreign tables: {foreign_tables}')

            # If foreign key columns exist, adapt select_str to include these foreign columns
            if len(foreign_keys):
                select_str = "*, " + ", ".join([f"{table}(name)" for table in foreign_tables])

        # Repeat initial query to include foreign columns
        #print(select_str)
        query = conn.table(table).select(select_str)       
        if filter is not None:
            for column, value in filter:
                #print(f'Filter: Column={column} Value={value}')
                if isinstance(value, list):
                    query.in_(column, value)
                else:
                    query.eq(column, value)
        response = query.execute()

        all_data = []
        start = 0
        end = 999
        while len(response.data) == 1000:
            all_data.extend(response.data)
            start += 1000
            end += 1000
            query = conn.table(table).select(select_str).range(start, end)
            if filter is not None:
                for column, value in filter:
                    if isinstance(value, list):
                        query.in_(column, value)
                    else:
                        query.eq(column, value)
            response = query.execute()
        all_data.extend(response.data) 
        #print(all_data)
        
        # If foreign keys were included, the result must be flattened to exclude foreign key dictionaries
        if len(foreign_keys):
            flattened_data = []
            for row in all_data:
                flat_row = row.copy()

                for table in foreign_tables:
                    # Remove the nested object and extract the name safely
                    nested_obj = flat_row.pop(table, None)

                    # Assign preferred "<FOREIGNKEYTABLE>_name" format
                    if isinstance(nested_obj, dict):
                        flat_row[f"{table}_name"] = nested_obj.get("name")
                    else:
                        flat_row[f"{table}_name"] = None
                flattened_data.append(flat_row)
            all_data = flattened_data

    except Exception as e:
        st.error(f"Database error: {e}")
        all_data = None
    
    indexes = [row['id'] for row in all_data]
    data_df = pd.DataFrame(data=all_data, index=indexes)#columns=column_names
    #print(data_df)
    return data_df   

def write_db(conn=None, table=None, entry_id=None, fields=None, values=None, df=None):
    entry = None
    print('Start Write DB')
    try:
        #fields_values = dict(zip(fields, values))
        raw_dict = dict(zip(fields, values))
        # Remove NaN
        cleaned_dict = {
            k: v for k, v in raw_dict.items() 
            if not (isinstance(v, float) and math.isnan(v))
        }

        # Remove invalid columns
        response = conn.rpc("get_column_names", {"tname": table}).execute()
        valid_columns = [row["column_name"] for row in response.data]
        #print(f'valid columns: {valid_columns}')
        valid_data = {k: v for k, v in cleaned_dict.items() if k in valid_columns}
        fields_values = valid_data
   
        print(f'Field and Values to write\n{fields_values}')
        if entry_id is not None:
            # Update table entry
            print(f'Updating entry in {table}')
            query = conn.table(table).update(fields_values).eq('id', entry_id)#.select('id')
        else:
            # Insert table entry
            print(f'Inserting entry in {table}')
            query = conn.table(table).insert(fields_values)#.select('id')
        #print(query)
        response = query.execute()
        print(response)
        entry = response.data[0]['id']

    except Exception as e:
        st.error(f"Database error: {e}")
        print(f"Database error: {e}")

    return entry

def remove_db(conn=None, table=None, filter=None, legacy=False):
    print('Start Remove DB')
    if filter is None:
        return
    #qry = f'DELETE FROM {self.table} WHERE id={id}'
    
    # LEGACY SQLite DB
    if legacy:
        conn = connect()
        try:
            # Step 1: Base query formation
            query = f"DELETE * FROM {table}"
            params = []
            
            # Step 2: Dynamic WHERE clause construction
            if filter is not None and len(filter) > 0:
                where_clauses = []
                for column, value in filter:
                    if isinstance(value, list):
                        # Creates 'column IN (?, ?, ?)' placeholders
                        placeholders = ", ".join(["?"] * len(value))
                        where_clauses.append(f"{column} IN ({placeholders})")
                        params.extend(value)
                    else:
                        # Creates 'column = ?' placeholder
                        where_clauses.append(f"{column} = ?")
                        params.append(value)
                
                query += " WHERE " + " AND ".join(where_clauses)
            
            # Step 3: Execute query and format output
            cursor = conn.cursor()
            cursor.execute(query, params)
            #columns = [column[0] for column in cursor.description]
            
            ## Convert row tuples to list of dictionaries to match Supabase structure
            #all_data = [dict(zip(columns, row)) for row in cursor.fetchall()]
            #return all_data
            return True

        except Exception as e:
            st.error(f"Database error (SQLite): {e}")
            return None

    # NEW" Supabase DB
    try:
        query = conn.table(table).delete()
        if filter is not None:
            for column, value in filter:
                print(f'Filter: Column={column} Value={value}')
                if isinstance(value, list):
                    query.in_(column, value)
                else:
                    query.eq(column, value)
        response = query.execute()
        return True
    
    except Exception as e:
        st.error(f"Database error: {e}")
        return None
