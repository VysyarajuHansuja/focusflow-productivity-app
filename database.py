import sqlite3


def connect_db():

    conn = sqlite3.connect(
        "task_manager.db",
        check_same_thread=False
    )

    conn.row_factory = sqlite3.Row

    return conn
