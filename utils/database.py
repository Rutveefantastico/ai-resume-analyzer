import sqlite3

DB_PATH = "data/users.db"

# ---------------- CONNECTION ----------------
def create_connection():
    return sqlite3.connect(DB_PATH)

# ---------------- CREATE TABLES ----------------
def create_tables():
    conn = create_connection()
    cursor = conn.cursor()

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS users (
        username TEXT PRIMARY KEY,
        password TEXT
    )
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS resumes (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT,
        match_score REAL,
        ats_score REAL,
        skills TEXT,
        missing TEXT,
        suggestions TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    """)

    conn.commit()
    conn.close()

# ---------------- SAVE ----------------
def save_resume(username, match_score, ats_score, skills, missing, suggestions):
    conn = create_connection()
    cursor = conn.cursor()

    cursor.execute("""
    INSERT INTO resumes (username, match_score, ats_score, skills, missing, suggestions)
    VALUES (?, ?, ?, ?, ?, ?)
    """, (username, match_score, ats_score, str(skills), str(missing), suggestions))

    conn.commit()
    conn.close()

# ---------------- GET ----------------
def get_user_resumes(username):
    conn = create_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM resumes WHERE username=?", (username,))
    data = cursor.fetchall()

    conn.close()
    return data

# ---------------- DELETE ----------------
def delete_resume(report_id):
    conn = create_connection()
    cursor = conn.cursor()

    cursor.execute("DELETE FROM resumes WHERE id = ?", (report_id,))
    
    conn.commit()
    conn.close()