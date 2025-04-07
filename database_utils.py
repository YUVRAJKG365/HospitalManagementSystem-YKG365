import mysql.connector as sq
import logging
import numpy as np
import pandas as pd
import streamlit as st

def insert_data(query, values):
    try:
        values = tuple(int(val) if isinstance(val, (np.int64, np.int32)) else val for val in values)
        con = connection()
        if con:
            cur = con.cursor()
            cur.execute(query, values)
            con.commit()
    except sq.Error as er:
        st.error(f"Error: {er}")
        logging.error(f"Error inserting data: {er}")

def connection():
    try:
        con = sq.connect(
            host="localhost",
            user="root",
            password=".#RamJi.",
            database="HospitalManagement"
        )
        if con.is_connected():
            logging.info("Database connection established successfully.")
            return con
        else:
            logging.error("Database connection failed.")
            return None
    except sq.Error as er:
        logging.error(f"Database connection error: {er}")
        return None

def fetch_data(query, table_name, columns=None, default_columns=None, params=None):
    try:
        con = connection()
        if con:
            cur = con.cursor()
            if params:
                cur.execute(query, params)
            else:
                cur.execute(query)
            data = cur.fetchall()

            if columns:
                col_names = columns
            else:
                if "COUNT" in query or "SUM" in query or "GROUP BY" in query:
                    col_names = ["category", "count"]
                else:
                    cur.execute(f"SHOW COLUMNS FROM {table_name}")
                    col_names = [col[0] for col in cur.fetchall()]

            con.close()

            if not data:
                return pd.DataFrame(columns=default_columns or col_names)

            if len(data[0]) != len(col_names):
                col_names = col_names[:len(data[0])]

            return pd.DataFrame(data, columns=col_names)
        else:
            return pd.DataFrame(columns=default_columns or columns if columns else [])
    except sq.Error as er:
        logging.error(f"Error fetching data: {er}")
        return pd.DataFrame(columns=default_columns or columns if columns else [])