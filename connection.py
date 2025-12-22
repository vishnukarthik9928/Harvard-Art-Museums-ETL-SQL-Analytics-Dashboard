# connection.py

import mysql.connector
from config import DB_CONFIG

def get_conn():
    conn = mysql.connector.connect(**DB_CONFIG)
    conn.autocommit = False
    return conn
