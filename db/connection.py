# db/db_conn.py

import os
import psycopg2

DB = {
    "dbname": os.getenv("DB_NAME"),
    "user": os.getenv("DB_USER"),
    "password": os.getenv("DB_PASSWORD"),
    "host": os.getenv("DB_HOST"),
    "port": os.getenv("DB_PORT")
}

def get_conn():
    try:
        conn = psycopg2.connect(**DB)
        print("✅ PostgreSQL connection established")
        return conn
    except Exception as e:
        print("❌ PostgreSQL connection failed:", e)
        raise
