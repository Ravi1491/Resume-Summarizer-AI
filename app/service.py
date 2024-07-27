import sqlite3
import os
from flask import current_app, flash

create_user_table = '''
  CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    email TEXT NOT NULL UNIQUE,
    password TEXT NOT NULL
  )
'''

create_resume_table = '''
  CRAETE TABLE IF NOT EXISTS user_resumes (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    filename TEXT NOT NULL,
    original_text TEXT NULL,
    ai_text TEXT NULL,
  ) 
'''

def init_db():
    with sqlite3.connect('database.db') as conn:
        cursor = conn.cursor()
        cursor.execute('''CREATE TABLE IF NOT EXISTS pdfs (
                            id INTEGER PRIMARY KEY AUTOINCREMENT,
                            filename TEXT NOT NULL,
                            text TEXT NULL,
                            ai_text TEXT NULL,
                            user_id INTEGER NOT NULL
                        )''')
        cursor.execute(create_user_table)
        conn.commit()

def get_user_email(email):
    with sqlite3.connect('database.db') as conn:
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM users WHERE email = ?', (email,))
        return cursor.fetchone()

def create_user(name,email,password):
    with sqlite3.connect('database.db') as conn:
        cursor = conn.cursor()
        cursor.execute('INSERT INTO users (name,email,password) VALUES (?,?,?)', (name,email,password,))
        conn.commit()
        
def get_all_pdfs():
    with sqlite3.connect('database.db') as conn:
        cursor = conn.cursor()
        cursor.execute('SELECT id, filename, text, ai_text FROM pdfs')
        return cursor.fetchall()

def get_pdf_by_id(id):
    with sqlite3.connect('database.db') as conn:
        cursor = conn.cursor()
        cursor.execute('SELECT filename, text, ai_text FROM pdfs WHERE id = ?', (id,))
        return cursor.fetchone()
    
def get_resumes_by_user_id(user_id):
    with sqlite3.connect('database.db') as conn:
        cursor = conn.cursor()
        cursor.execute('SELECT id, filename, text, ai_text FROM pdfs WHERE user_id = ?', (user_id,))
        return cursor.fetchall()

def delete_pdf_entry(id):
    with sqlite3.connect('database.db') as conn:
        cursor = conn.cursor()
        cursor.execute('SELECT filename FROM pdfs WHERE id = ?', (id,))
        pdf = cursor.fetchone()
        if pdf:
            filename = pdf[0]
            cursor.execute('DELETE FROM pdfs WHERE id = ?', (id,))
            conn.commit()
            os.remove(os.path.join(current_app.config['UPLOAD_FOLDER'], filename))
            flash(f'Successfully deleted: {filename}')
        else:
            flash('PDF not found')
