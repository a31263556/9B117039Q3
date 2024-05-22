from flask import Flask, render_template, request, redirect, session, g
import sqlite3
import logging

app = Flask(__name__)
app.secret_key = 'your_secret_key'

DATABASE = 'mydb.db'

# 設置 logging
logging.basicConfig(filename='error.log', level=logging.ERROR)

def get_db():

    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = sqlite3.connect(DATABASE)
        db.row_factory = sqlite3.Row
    return db

@app.teardown_appcontext
def close_connection(exception):
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()

@app.route('/')
def index():
    if 'user_id' not in session:
        return redirect('/login')
    try:
        db = get_db()
        cursor = db.cursor()
        cursor.execute("SELECT * FROM user WHERE id = ?", (session['user_id'],))
        user = cursor.fetchone()
        return render_template('index.html', user=user)
    except Exception as e:
        logging.error(str(e))
        return render_template('error.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        try:
            db = get_db()
            cursor = db.cursor()
            cursor.execute("SELECT * FROM user WHERE username = ? AND password = ?", (username, password))
            user = cursor.fetchone()
            if user:
                session['user_id'] = user['id']
                return redirect('/')
            else:
                error = '請輸入正確的帳號密碼'
                return render_template('login.html', error=error)
        except Exception as e:
            logging.error(str(e))
            return render_template('error.html')
    return render_template('login.html')

@app.route('/edit', methods=['GET', 'POST'])
def edit():
    if 'user_id' not in session:
        return redirect('/login')
    try:
        db = get_db()
        if request.method == 'POST':
            username = request.form['username']
            password = request.form['password']
            cursor = db.cursor()
            cursor.execute("UPDATE user SET username = ?, password = ? WHERE id = ?", (username, password, session['user_id']))
            db.commit()
            return redirect('/')
        cursor = db.cursor()
        cursor.execute("SELECT * FROM user WHERE id = ?", (session['user_id'],))
        user = cursor.fetchone()
        return render_template('edit.html', user=user)
    except Exception as e:
        logging.error(str(e))
        return render_template('error.html')

@app.route('/logout')
def logout():
    session.pop('user_id', None)
    return redirect('/')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=80)
