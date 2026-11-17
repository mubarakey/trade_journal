
import sqlite3
from collections.abc import Mapping

from config import DATABASE_MODE, DATABASE_URL


DATABASE = "trades.db"


class HybridRow(Mapping):
    """Allow database rows to be accessed by column name or position."""

    def __init__(self, description, values):
        self.columns = [
            column.name if hasattr(column, "name") else column[0]
            for column in description
        ]
        self.values = tuple(values)
        self.data = dict(zip(self.columns, self.values))

    def __getitem__(self, key):
        if isinstance(key, int):
            return self.values[key]

        return self.data[key]

    def __iter__(self):
        return iter(self.columns)

    def __len__(self):
        return len(self.columns)


def hybrid_row(cursor):
    """Create HybridRow objects for PostgreSQL query results."""

    def make_row(values):
        return HybridRow(cursor.description, values)

    return make_row


class CompatibleCursor:
    """Adapt SQL placeholders while preserving normal cursor behaviour."""

    def __init__(self, cursor, database_mode):
        self.cursor = cursor
        self.database_mode = database_mode

    def execute(self, query, parameters=None):
        if self.database_mode == "postgresql":
            query = query.replace("?", "%s")

        if parameters is None:
            return self.cursor.execute(query)

        return self.cursor.execute(query, parameters)

    def __getattr__(self, name):
        return getattr(self.cursor, name)


class CompatibleConnection:
    """Preserve the existing connection interface."""

    def __init__(self, connection, database_mode):
        self.connection = connection
        self.database_mode = database_mode

    def cursor(self):
        if self.database_mode == "postgresql":
            cursor = self.connection.cursor(row_factory=hybrid_row)
        else:
            cursor = self.connection.cursor()

        return CompatibleCursor(cursor, self.database_mode)

    def __getattr__(self, name):
        return getattr(self.connection, name)


def get_connection():
    if DATABASE_MODE == "postgresql":
        import psycopg

        connection = psycopg.connect(DATABASE_URL)

    else:
        connection = sqlite3.connect(DATABASE)
        connection.row_factory = sqlite3.Row

    return CompatibleConnection(connection, DATABASE_MODE)


def create_tables():
    connection = get_connection()
    cursor = connection.cursor()

    if DATABASE_MODE == "postgresql":
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS trades (
                id BIGSERIAL PRIMARY KEY,
                trade_date TEXT NOT NULL DEFAULT '',
                pair TEXT NOT NULL,
                direction TEXT NOT NULL,
                risk DOUBLE PRECISION NOT NULL,
                result_r DOUBLE PRECISION NOT NULL,
                entry_type TEXT NOT NULL,
                liquidity_sweep BOOLEAN NOT NULL,
                bos BOOLEAN NOT NULL,
                structural_liquidity BOOLEAN NOT NULL,
                poi BOOLEAN NOT NULL,
                exit_type TEXT NOT NULL,
                planned_tp DOUBLE PRECISION NOT NULL,
                mistake BOOLEAN NOT NULL,
                mistake_type TEXT NOT NULL
            )
        """)

        cursor.execute("""
            ALTER TABLE trades
            ADD COLUMN IF NOT EXISTS trade_date TEXT NOT NULL DEFAULT ''
        """)

    else:
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

        cursor.execute("PRAGMA table_info(trades)")

        columns = cursor.fetchall()
        column_names = [column[1] for column in columns]

        if "trade_date" not in column_names:
            cursor.execute("""
                ALTER TABLE trades
                ADD COLUMN trade_date TEXT NOT NULL DEFAULT ''
            """)

    connection.commit()
    connection.close()
