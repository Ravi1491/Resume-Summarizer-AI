import sqlite3

class UserService():
  def get_user_by_email(self, email):
    with sqlite3.connect('database.db') as conn:
      cursor = conn.cursor()
      cursor.execute('SELECT * FROM users WHERE email = ?', (email,))
      return cursor.fetchone()

  def create_user(name,email,password):
    with sqlite3.connect('database.db') as conn:
      cursor = conn.cursor()
      cursor.execute('INSERT INTO users (name,email,password) VALUES (?,?,?)', (name,email,password,))
      conn.commit()
          