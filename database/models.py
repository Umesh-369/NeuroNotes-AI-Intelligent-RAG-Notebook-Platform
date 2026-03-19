import sqlite3
import os

DB_PATH = os.path.join(os.path.dirname(__file__), 'database.db')

def get_db_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Users Table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            email TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Notebooks Table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS notebooks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            title TEXT NOT NULL,
            description TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY(user_id) REFERENCES users(id) ON DELETE CASCADE
        )
    ''')
    
    # Documents Table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS documents (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            notebook_id INTEGER NOT NULL,
            filename TEXT NOT NULL,
            filepath TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY(notebook_id) REFERENCES notebooks(id) ON DELETE CASCADE
        )
    ''')
    
    # Insights Table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS insights (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            notebook_id INTEGER NOT NULL,
            content TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY(notebook_id) REFERENCES notebooks(id) ON DELETE CASCADE
        )
    ''')
    
    conn.commit()
    conn.close()

# Helper Functions
def create_user(email, password):
    conn = get_db_connection()
    try:
        conn.execute('INSERT INTO users (email, password) VALUES (?, ?)', (email, password))
        conn.commit()
        return True
    except sqlite3.IntegrityError:
        return False
    finally:
        conn.close()

def get_user_by_email(email):
    conn = get_db_connection()
    user = conn.execute('SELECT * FROM users WHERE email = ?', (email,)).fetchone()
    conn.close()
    return user

def create_notebook(user_id, title, description=""):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('INSERT INTO notebooks (user_id, title, description) VALUES (?, ?, ?)', (user_id, title, description))
    conn.commit()
    notebook_id = cursor.lastrowid
    conn.close()
    return notebook_id

def get_user_notebooks(user_id):
    conn = get_db_connection()
    notebooks = conn.execute('SELECT * FROM notebooks WHERE user_id = ? ORDER BY created_at DESC', (user_id,)).fetchall()
    conn.close()
    return [dict(n) for n in notebooks]

def delete_notebook(notebook_id, user_id):
    conn = get_db_connection()
    conn.execute('DELETE FROM notebooks WHERE id = ? AND user_id = ?', (notebook_id, user_id))
    conn.commit()
    conn.close()

def add_document(notebook_id, filename, filepath):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('INSERT INTO documents (notebook_id, filename, filepath) VALUES (?, ?, ?)', (notebook_id, filename, filepath))
    conn.commit()
    doc_id = cursor.lastrowid
    conn.close()
    return doc_id

def get_notebook_documents(notebook_id):
    conn = get_db_connection()
    docs = conn.execute('SELECT * FROM documents WHERE notebook_id = ? ORDER BY created_at DESC', (notebook_id,)).fetchall()
    conn.close()
    return [dict(d) for d in docs]

def save_insight(notebook_id, content):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('INSERT INTO insights (notebook_id, content) VALUES (?, ?)', (notebook_id, content))
    conn.commit()
    insight_id = cursor.lastrowid
    conn.close()
    return insight_id

def get_notebook_insights(notebook_id):
    conn = get_db_connection()
    insights = conn.execute('SELECT * FROM insights WHERE notebook_id = ? ORDER BY created_at DESC', (notebook_id,)).fetchall()
    conn.close()
    return [dict(i) for i in insights]

def get_document_by_id(doc_id):
    conn = get_db_connection()
    doc = conn.execute('SELECT * FROM documents WHERE id = ?', (doc_id,)).fetchone()
    conn.close()
    return dict(doc) if doc else None

def delete_document(doc_id):
    conn = get_db_connection()
    conn.execute('DELETE FROM documents WHERE id = ?', (doc_id,))
    conn.commit()
    conn.close()

def delete_insight(insight_id):
    conn = get_db_connection()
    conn.execute('DELETE FROM insights WHERE id = ?', (insight_id,))
    conn.commit()
    conn.close()
