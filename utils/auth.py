import hashlib
from utils.database import create_connection

# ---------------- HASH PASSWORD ----------------
def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

# ---------------- SIGNUP ----------------
def signup(username, password):
    conn = create_connection()
    cursor = conn.cursor()

    try:
        cursor.execute(
            "INSERT INTO users (username, password) VALUES (?, ?)",
            (username, hash_password(password))
        )
        conn.commit()
        return True

    except:
        return False

    finally:
        conn.close()

# ---------------- LOGIN ----------------
def login(username, password):
    conn = create_connection()
    cursor = conn.cursor()

    cursor.execute(
        "SELECT * FROM users WHERE username=? AND password=?",
        (username, hash_password(password))
    )

    user = cursor.fetchone()
    conn.close()

    return user