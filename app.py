from flask import Flask, request, render_template, g, redirect, url_for, session
import sqlite3
import os
import random  # Add this import for randomization
from flask_bootstrap import Bootstrap5
from datetime import datetime
import argparse

app = Flask(__name__)
app.secret_key = 'some_random_secret_key'  # Needed if you use session
bootstrap = Bootstrap5(app)  # Initialize Bootstrap

# Parse command line arguments
parser = argparse.ArgumentParser(description='SQL Injection Challenge Application')
parser.add_argument('--treatment', action='store_true', help='Enable treatment condition')
args = parser.parse_args()

# Set condition based on arguments
condition = 1 if args.treatment else 0

# Get condition from environment variable
condition = 1 if os.environ.get('TREATMENT', '').lower() in ('true', '1', 'yes') else 0

# Database directory
DB_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'database')
if not os.path.exists(DB_DIR):
    os.makedirs(DB_DIR)

TREATMENT = 1

def format_qualtrics_data(qualtrics_data):
    """Format just the data portion of the qualtrics display"""
    data_str = "--- Study Data ---\n"
    for key, value in qualtrics_data.items():
        data_str += f"{key}: {value}\n"
    return data_str

def generate_qualtrics_data(problem):
    return {
        'condition': 1 if TREATMENT else 0,
        "problem": problem
    }

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

    qualtrics_data = {
            'condition': 1 if TREATMENT else 0
        }

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

@app.route('/')
def index():  
    # Hard-coded "challenges" (vulnerabilities) with CVSS & severity
    # severity can be a short label like "High", "Medium", "Low"
    challenges = [
        {
            "id": 1,
            "endpoint": "/challenge1",
            "name": "IT Department Endpoint",
            "description": "Could we use the UNION operator?",
            "cvss": round(random.uniform(6,7.99), 1),
            "severity": "High"
        },
        {
            "id": 2,
            "endpoint": "/challenge2",
            "name": "Root Credentials DB",
            "description": "I wonder what happens if multiple columns are matched with the UNION operator...",
            "cvss": round(random.uniform(8,10), 1),
            "severity": "Very High"
        },
        {
            "id": 3,
            "endpoint": "/challenge3",
            "name": "Logs Endpoint",
            "description": "WHERE could we possibly use this?",
            "cvss": round(random.uniform(2,3.99), 1),
            "severity": "Low"
        },
        {
            "id": 4,
            "endpoint": "/challenge4",
            "name": "Mailserver Endpoint",
            "description": "If you forgot your password, could they tell you what it is?",
            "cvss":  round(random.uniform(4,5.99), 1),
            "severity": "Medium"
        }
    ]
    if condition is not TREATMENT:
        random.shuffle(challenges)
    else:
        challenges = sorted(challenges, key=lambda x: x['cvss'], reverse=True)

    session['challenges'] = challenges

    # Optional: store condition in session if you want to keep it for the user
    session['condition'] = condition

    # This text acts as a placeholder for "world building" or narrative.
    story_intro = (
        "Welcome to MegaCorp's Security Operations Challenge (CTF)!\n"
        "In this scenario, you've been brought in to demonstrate the "
        "exploitation of potential vulnerabilities. Pick a vulnerability "
        "and attempt to exploit it."
    )

    return render_template('index.html',
                           condition=condition,
                           challenges=challenges,
                           story_intro=story_intro)

@app.route('/select/<int:challenge_id>', methods=['POST'])
def select_challenge(challenge_id):
    """
    Logs the participant's selection to the DB with 
    participant_id (for demonstration, use a random or session-based ID),
    and condition.
    """
    # In a real scenario, you'd have an actual participant ID
    participant_id = request.remote_addr  # e.g. just IP for demonstration

    # Find the chosen vulnerability name (in a real scenario, store them in DB)
    vulnerabilities = {
        1: "Basic UNION-based Injection",  
        2: "Multi-Column UNION Injection",
        3: "UNION Injection with WHERE clause",
        4: "Login Form SQL Injection"
    }
    chosen_vuln = vulnerabilities.get(challenge_id, "Unknown")

    # Insert selection into main.db -> selections table
    conn = sqlite3.connect(os.path.join(DB_DIR, 'main.db'))
    c = conn.cursor()
    c.execute('''
        INSERT INTO selections (participant_id, condition, vulnerability_name, chosen_at)
        VALUES (?, ?, ?, ?)
    ''', (participant_id, condition, chosen_vuln, datetime.now()))
    conn.commit()
    conn.close()

    # Redirect user to the chosen challenge or somewhere else
    return redirect(url_for(f'challenge{challenge_id}'))

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
    return render_template('challenge1.html', result=result, qualtrics_data=format_qualtrics_data(generate_qualtrics_data("problem 1")))

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
    return render_template('challenge2.html', result=result, qualtrics_data=format_qualtrics_data(generate_qualtrics_data("problem 2")))

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
    return render_template('challenge3.html', result=result, qualtrics_data=format_qualtrics_data(generate_qualtrics_data("problem 3")))

# Challenge 4: Login Form
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
            return render_template('challenge4_success.html', flag=flag_result[0], qualtrics_data=format_qualtrics_data(generate_qualtrics_data("problem 4")))
        else:
            message = "Invalid credentials"
            message_class = "danger"

    return render_template('challenge4.html', message=message, message_class=message_class, qualtrics_data=format_qualtrics_data(generate_qualtrics_data("problem 4")))

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

    return render_template('forgot_password.html', message=message, message_class=message_class, qualtrics_data=format_qualtrics_data(generate_qualtrics_data("problem 4")))

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080, debug=True)