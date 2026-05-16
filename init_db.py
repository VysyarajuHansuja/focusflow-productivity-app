from database import connect_db

def init_database():

    conn = connect_db()

    cur = conn.cursor()

    # USERS
    cur.execute("""
    CREATE TABLE IF NOT EXISTS users(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE,
        password TEXT,
        email TEXT
    )
    """)
    
    # TASKS
    cur.execute("""
    CREATE TABLE IF NOT EXISTS tasks(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER,
        task TEXT,
        description TEXT,
        category TEXT,
        priority TEXT,
        estimated_time INTEGER,
        deadline TEXT,
        reminder_time TEXT,
        attachment TEXT,
        status TEXT,
        is_daily INTEGER,
        start_time TEXT,
        end_time TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        completed_at TIMESTAMP
    )
    """)
    
    # EVENTS
    cur.execute("""
    CREATE TABLE IF NOT EXISTS events(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER,
        title TEXT,
        event_date TEXT,
        category TEXT
    )
    """)
    
    # SCORES
    cur.execute("""
    CREATE TABLE IF NOT EXISTS scores(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER,
        score INTEGER,
        date TEXT
    )
    """)
    
    # SUBTASKS
    cur.execute("""
    CREATE TABLE IF NOT EXISTS subtasks(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        task_id INTEGER,
        subtask TEXT,
        status TEXT
    )
    """)
    
    conn.commit()
    conn.close()
    
    print("Database initialized successfully.")
