import sqlite3

DATABASE = "trades.db"

def get_connection():
    return sqlite3.connect(DATABASE)

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