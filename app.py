from flask import Flask, render_template, request, redirect, session, url_for
import sqlite3
import os
import logging

app = Flask(__name__)
app.secret_key = 'your_secret_key'

DB_NAME = 'mydb.db'

# 設置錯誤記錄
logging.basicConfig(filename='error.log', level=logging.ERROR)

def get_db_connection():
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row
    return conn

@app.route('/')
def index():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    try:
        conn = get_db_connection()
        user = conn.execute('SELECT * FROM member WHERE iid = ?', (session['user_id'],)).fetchone()
        conn.close()
        if user is None:
            return redirect(url_for('login'))
        return render_template('index.html', user=user)
    except Exception as e:
        logging.error(f"Error: {e}")
        return render_template('error.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        idno = request.form['idno']
        pwd = request.form['pwd']
        try:
            conn = get_db_connection()
            user = conn.execute('SELECT * FROM member WHERE idno = ? AND pwd = ?', (idno, pwd)).fetchone()
            conn.close()
            if user:
                session['user_id'] = user['iid']
                return redirect(url_for('index'))
            else:
                error = '請輸入正確的帳號密碼'
                return render_template('login.html', error=error)
        except Exception as e:
            logging.error(f"Error: {e}")
            return render_template('error.html')
    return render_template('login.html')

@app.route('/edit', methods=['GET', 'POST'])
def edit():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    try:
        conn = get_db_connection()
        user = conn.execute('SELECT * FROM member WHERE iid = ?', (session['user_id'],)).fetchone()

        if request.method == 'POST':
            nm = request.form['nm']
            birth = request.form['birth']
            blood = request.form['blood']
            phone = request.form['phone']
            email = request.form['email']
            conn.execute('UPDATE member SET nm = ?, birth = ?, blood = ?, phone = ?, email = ? WHERE iid = ?',
                         (nm, birth, blood, phone, email, session['user_id']))
            conn.commit()
            conn.close()
            return redirect(url_for('index'))

        conn.close()
        return render_template('edit.html', user=user)
    except Exception as e:
        logging.error(f"Error: {e}")
        return render_template('error.html')

@app.route('/logout')
def logout():
    session.pop('user_id', None)
    return redirect(url_for('login'))

if __name__ == '__main__':
    app.run()
