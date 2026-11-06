import sqlite3

DATABASE = "trades.db"

import sqlite3

def get_connection():
    connection = sqlite3.connect("trades.db")   
    connection.row_factory = sqlite3.Row        
    return connection
def create_tables():
    connection = get_connection()

    cursor = connection.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS trades (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            trade_date TEXT NOT NULL DEFAULT '',
            pair TEXT NOT NULL,
            direction TEXT NOT NULL,
            risk REAL NOT NULL,
            result_r REAL NOT NULL,
            entry_type TEXT NOT NULL,
            liquidity_sweep INTEGER NOT NULL,
            bos INTEGER NOT NULL,
            structural_liquidity INTEGER NOT NULL,
            poi INTEGER NOT NULL,
            exit_type TEXT NOT NULL,
            planned_tp REAL NOT NULL,
            mistake INTEGER NOT NULL,
            mistake_type TEXT NOT NULL
        )
    """)

    cursor.execute("""
        PRAGMA table_info(trades)
    """)

    columns = cursor.fetchall()

    column_names = [column[1] for column in columns]

    if "trade_date" not in column_names:
        cursor.execute("""
            ALTER TABLE trades
            ADD COLUMN trade_date TEXT NOT NULL DEFAULT ''
        """)



    connection.commit()
    connection.close()