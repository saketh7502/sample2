from flask import Flask, request, render_template, g
from flask_bootstrap import Bootstrap5
import sqlite3
import os

app = Flask(__name__)
bootstrap = Bootstrap5(app)

# Database directory
DB_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'database')
if not os.path.exists(DB_DIR):
    os.makedirs(DB_DIR)

# Database initialization
def init_dbs():
    # Main database for Challenge 1
    conn = sqlite3.connect(os.path.join(DB_DIR, 'main.db'))
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS users 
                 (id INTEGER PRIMARY KEY, username TEXT, password TEXT)''')
    c.execute('''CREATE TABLE IF NOT EXISTS flags
                 (id INTEGER PRIMARY KEY, flag TEXT)''')
    c.execute("INSERT OR IGNORE INTO users VALUES (1, 'admin', 'secret_pass1234')")
    c.execute("INSERT OR IGNORE INTO flags VALUES (1, 'picoCTF{MAIN-DB-12345}')")
    conn.commit()
    conn.close()

    # Inventory database for Challenge 2
    conn = sqlite3.connect(os.path.join(DB_DIR, 'inventory.db'))
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS inventory
                 (id INTEGER PRIMARY KEY, 
                  item_name TEXT, 
                  quantity INTEGER,
                  category TEXT)''')
    c.execute('''CREATE TABLE IF NOT EXISTS hidden_flags
                 (id INTEGER PRIMARY KEY, flag TEXT)''')
    c.execute("INSERT OR IGNORE INTO inventory VALUES (1, 'USB Cable', 50, 'Electronics')")
    c.execute("INSERT OR IGNORE INTO hidden_flags VALUES (1, 'picoCTF{INVENTORY-DB-ABCDE}')")
    conn.commit()
    conn.close()

    # Challenge 4 database initialization
    conn = sqlite3.connect(os.path.join(DB_DIR, 'login.db'))
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS users (
                     id INTEGER PRIMARY KEY, 
                     username TEXT, 
                     password TEXT)''')
    c.execute("INSERT OR IGNORE INTO users VALUES (1, 'admin', 'admin_pa$$')")
    c.execute('''CREATE TABLE IF NOT EXISTS flags (
                     id INTEGER PRIMARY KEY, 
                     flag TEXT)''')
    c.execute("INSERT OR IGNORE INTO flags VALUES (1, 'picoCTF{CHALLENGE4-LOGIN}')")
    conn.commit()
    conn.close()

    # Library database for Challenge 3
    conn = sqlite3.connect(os.path.join(DB_DIR, 'library.db'))
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS books 
                 (id INTEGER PRIMARY KEY, title TEXT, author TEXT)''')
    c.execute('''CREATE TABLE IF NOT EXISTS library_secrets
                 (id INTEGER PRIMARY KEY, secret_code TEXT)''')
    c.execute("INSERT OR IGNORE INTO books VALUES (1, 'The Great Gatsby', 'F. Scott Fitzgerald')")
    c.execute("INSERT OR IGNORE INTO library_secrets VALUES (1, 'picoCTF{LIBRARY-DB-BOOKWORM}')")
    conn.commit()
    conn.close()

init_dbs()

# Database helpers
def get_db(name):
    db = getattr(g, f'_{name}', None)
    if db is None:
        db = sqlite3.connect(os.path.join(DB_DIR, f'{name}.db'))
        setattr(g, f'_{name}', db)
    return db

@app.teardown_appcontext
def close_connection(exception):
    for db_name in ['main', 'inventory', 'library', 'login']:
        db = getattr(g, f'_{db_name}', None)
        if db is not None:
            db.close()

# Home page
@app.route('/')
def index():
    challenges = [
        {"endpoint": "/challenge1", "name": "Basic UNION-based Injection", "description": "SQL injection vulnerability allowing extraction of data through UNION queries.", "cvss": "6.5"},
        {"endpoint": "/challenge2", "name": "Multi-Column UNION Injection", "description": "Advanced SQL injection requiring matching multiple columns in UNION statements.", "cvss": "7.8"},
        {"endpoint": "/challenge3", "name": "UNION Injection with WHERE clause", "description": "SQL injection in a search feature with filtering mechanisms.", "cvss": "6.3"},
        {"endpoint": "/challenge4", "name": "Login Form SQL Injection", "description": "Authentication bypass vulnerability in the login system.", "cvss": "8.2"}
    ]
    return render_template('index.html', challenges=challenges)

# Challenge 1: Basic UNION-based Injection
@app.route('/challenge1', methods=['GET', 'POST'])
def challenge1():
    result = None
    if request.method == 'POST':
        username = request.form.get('username')
        query = f"SELECT username FROM users WHERE username = '{username}'"
        db = get_db('main')
        cur = db.execute(query)
        result = cur.fetchall()
    return render_template('challenge1.html', result=result)

# Challenge 2: Multi-Column UNION Injection
@app.route('/challenge2', methods=['GET', 'POST'])
def challenge2():
    result = None
    if request.method == 'POST':
        product_id = request.form.get('product_id')
        query = f"SELECT item_name, quantity, category FROM inventory WHERE id = {product_id}"
        db = get_db('inventory')
        try:
            cur = db.execute(query)
            result = cur.fetchall()
        except sqlite3.Error as e:
            result = [f"Error: {str(e)}"]
    return render_template('challenge2.html', result=result)

# Challenge 3: UNION Injection with WHERE clause
@app.route('/challenge3', methods=['GET', 'POST'])
def challenge3():
    result = None
    if request.method == 'POST':
        author = request.form.get('author', '')
        query = f"SELECT title, author FROM books WHERE author = '{author}'"
        db = get_db('library')
        try:
            cur = db.execute(query)
            result = cur.fetchall()
        except sqlite3.Error as e:
            result = [f"Error: {str(e)}"]
    return render_template('challenge3.html', result=result)

# Challenge 4: Login Form and Forgot Password
@app.route('/challenge4', methods=['GET', 'POST'])
def challenge4():
    message = ''
    message_class = ''
    
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')

        # Use prepared SQL statements for secure login
        query = "SELECT username FROM users WHERE username = ? AND password = ?"
        db = get_db('login')
        cur = db.execute(query, (username, password))
        result = cur.fetchone()

        if result:
            # Fetch the flag upon successful login
            flag_query = "SELECT flag FROM flags WHERE id = 1"
            cur = db.execute(flag_query)
            flag_result = cur.fetchone()
            return render_template('challenge4_success.html', flag=flag_result[0])
        else:
            message = "Invalid credentials"
            message_class = "danger"

    return render_template('challenge4.html', message=message, message_class=message_class)

@app.route('/challenge4/forgot_password', methods=['GET', 'POST'])
def forgot_password():
    message = ''
    message_class = ''
    
    if request.method == 'POST':
        username = request.form.get('username')
        
        # Vulnerable to SQL injection
        query = f"SELECT username FROM users WHERE username = '{username}'"
        db = get_db('login')
        try:
            cur = db.execute(query)
            result = cur.fetchone()
            
            if result:
                message = f"Password reset link sent to user: {result[0]}"
                message_class = "success"
                
            else:
                message = "User not found"
                message_class = "danger"
        except sqlite3.Error as e:
            message = f"Error: {str(e)}"
            message_class = "danger"

    return render_template('forgot_password.html', message=message, message_class=message_class)

if __name__ == '__main__':
    app.run(debug=True)
