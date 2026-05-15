

import bcrypt
from database import connect_db


def register_user(username,password,email):

    conn = connect_db()
    cur = conn.cursor()

    hashed = bcrypt.hashpw(password.encode(),bcrypt.gensalt())

    cur.execute(
        "INSERT INTO users(username,password,email) VALUES(?,?,?)",
        (username, hashed.decode(), email)
    )

    conn.commit()
    conn.close()


def login_user(username,password):

    conn = connect_db()
    cur = conn.cursor()

    cur.execute(
        "SELECT * FROM users WHERE username=?",
        (username,)
    )

    user = cur.fetchone()

    conn.close()

    if user and bcrypt.checkpw(password.encode(),user[2].encode()):
        return user

    return None