from flask import Flask, render_template, request, redirect, url_for, flash, session, make_response
import sqlite3
from functools import wraps
from werkzeug.security import generate_password_hash, check_password_hash
from shortages import shortages_bp  # Import the shortages blueprint

app = Flask(__name__)
app.secret_key = 'your_secret_key'

DATABASE = 'users.db'

# Utility function to connect to the database
def get_db_connection():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn

# Utility to prevent browser caching
def nocache(view):
    @wraps(view)
    def no_cache(*args, **kwargs):
        response = make_response(view(*args, **kwargs))
        response.headers['Cache-Control'] = 'no-store, no-cache, must-revalidate, post-check=0, pre-check=0, max-age=0'
        response.headers['Pragma'] = 'no-cache'
        response.headers['Expires'] = '0'
        return response
    return no_cache

# Create the users table if it doesn't exist
def create_users_table():
    conn = get_db_connection()
    conn.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            email TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL
        )
    ''')
    conn.commit()
    conn.close()

# Initialize database on app start
create_users_table()

# Register shortages Blueprint
app.register_blueprint(shortages_bp)

# Route: Default Landing Page (Redirect to Login)
@app.route('/')
@nocache
def index():
    return redirect(url_for('login'))

# Route: Login Page
@app.route('/login', methods=['GET', 'POST'])
@nocache
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']

        conn = get_db_connection()
        user = conn.execute('SELECT * FROM users WHERE email = ?', (email,)).fetchone()
        conn.close()

        if user and check_password_hash(user['password'], password):
            session['user_id'] = user['id']
            session['username'] = user['username']
            flash('Welcome back!', 'success')
            return redirect(url_for('dashboard'))
        else:
            flash('Invalid email or password', 'error')
    return render_template('login.html')

# Route: Register Page
@app.route('/register', methods=['GET', 'POST'])
@nocache
def register():
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']
        hashed_password = generate_password_hash(password)

        try:
            conn = get_db_connection()
            conn.execute('INSERT INTO users (username, email, password) VALUES (?, ?, ?)',
                         (username, email, hashed_password))
            conn.commit()
            conn.close()
            flash('Registration successful! Please log in.', 'success')
            return redirect(url_for('login'))
        except sqlite3.IntegrityError:
            flash('Email or username already exists', 'error')

    return render_template('register.html')

# Route: Dashboard
@app.route('/dashboard')
@nocache
def dashboard():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    return render_template('dashboard.html', username=session['username'], active_page='dashboard')

# Route: Crop Advisor
@app.route('/crop_advisor')
@nocache
def crop_advisor():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    return render_template('crop_advisor.html', username=session['username'], active_page='crop_advisor')

# Route: Cost Predictor
@app.route('/cost_predictor/')
@nocache
def cost_predictor():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    return render_template('cost_predictor.html', username=session['username'], active_page='cost_predictor')

@app.route('/crop_shortages')
@nocache
def crop_shortages():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    return render_template("shortages.html")  # Directly render the template


# Route: Logout
@app.route('/logout')
@nocache
def logout():
    session.clear()
    flash('You have been logged out.', 'success')
    return redirect(url_for('login'))

# Error Handling: Page Not Found (404)
@app.errorhandler(404)
@nocache
def page_not_found(e):
    return render_template('404.html'), 404

# Debug Logging for Requests
@app.before_request
def before_request():
    print(f"Requested URL: {request.url}")

@app.route('/test')
def test():
    return "Test route is working!"



if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080, debug=True)
