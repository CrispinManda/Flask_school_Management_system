from flask import Flask, render_template, request, redirect, url_for, flash, session
import sqlite3

app = Flask(__name__)
app.secret_key = "supersecretkey"

# Hardcoded admin credentials
ADMIN_USERNAME = "Kingori"
ADMIN_PASSWORD = "nice"

# Initialize database
def init_db():
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    
    cursor.execute('''CREATE TABLE IF NOT EXISTS students (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        student_id TEXT UNIQUE NOT NULL,
        password TEXT NOT NULL
    )''')
    
    cursor.execute('''CREATE TABLE IF NOT EXISTS teachers (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        teacher_id INTERGER UNIQUE NOT NULL,
        password TEXT NOT NULL
    )''')
    
    cursor.execute('''CREATE TABLE IF NOT EXISTS announcements (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        title TEXT NOT NULL,
        content TEXT NOT NULL,
        posted_by TEXT NOT NULL
    )''')

    conn.commit()
    conn.close()

@app.route('/')
def home():
    return render_template('home.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        student_id = request.form.get('student_id')
        password = request.form.get('password')

        if not student_id or not password:
            flash('Student ID and Password are required!', 'danger')
            return redirect(url_for('register'))

        try:
            conn = sqlite3.connect('database.db')
            cursor = conn.cursor()
            cursor.execute('INSERT INTO students (student_id, password) VALUES (?, ?)', (student_id, password))
            conn.commit()
            conn.close()
            flash('Registration successful! You can now log in.', 'success')
            return redirect(url_for('login'))
        except Exception as e:
            flash('Error registering student.', 'danger')

    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        identifier = request.form.get('identifier')
        password = request.form.get('password')

        if identifier == ADMIN_USERNAME and password == ADMIN_PASSWORD:
            session['user_type'] = 'admin'
            flash('Admin Login Successful!', 'success')
            return redirect(url_for('admin_dashboard'))

        conn = sqlite3.connect('database.db')
        cursor = conn.cursor()

        cursor.execute('SELECT * FROM teachers WHERE teacher_id = ? AND password = ?', (identifier, password))
        teacher = cursor.fetchone()
        if teacher:
            session['user_type'] = 'teacher'
            flash('Teacher Login Successful!', 'success')
            return redirect(url_for('teacher_dashboard'))

        cursor.execute('SELECT * FROM students WHERE student_id = ? AND password = ?', (identifier, password))
        student = cursor.fetchone()
        if student:
            session['user_type'] = 'student'
            flash('Student Login Successful!', 'success')
            return redirect(url_for('student_dashboard'))

        conn.close()
        flash('Invalid Credentials!', 'danger')

    return render_template('login.html')

@app.route('/logout')
def logout():
    session.clear()
    flash('Logged out successfully!', 'info')
    return redirect(url_for('home'))

@app.route('/admin_dashboard')
def admin_dashboard():
    if session.get('user_type') != 'admin':
        flash('Access Denied!', 'danger')
        return redirect(url_for('home'))
    return render_template('admin_dashboard.html')

@app.route('/add_teacher', methods=['GET', 'POST'])
def add_teacher():
    if session.get('user_type') != 'admin':
        flash('Access Denied!', 'danger')
        return redirect(url_for('home'))

    if request.method == 'POST':
        teacher_id = request.form.get('teacher_id')  # Ensure form name matches
        password = request.form.get('password')

        if not teacher_id or not password:  # Check if values are None or empty
            flash('Teacher ID and Password are required!', 'danger')
            return redirect(url_for('add_teacher'))  # Reload the form
        
        with sqlite3.connect('database.db') as conn:
            cursor = conn.cursor()
            cursor.execute('INSERT INTO teachers (teacher_id, password) VALUES (?, ?)', (teacher_id, password))
            conn.commit()

        flash('Teacher added successfully!', 'success')
        return redirect(url_for('admin_dashboard'))

    return render_template('add_teacher.html')


@app.route('/announcements', methods=['GET', 'POST'])
def announcements():
    print("Current session data:", session) 
    if request.method == 'POST':
        if 'user_type' not in session or session['user_type'] not in ['admin', 'teacher']:
            flash('Only Admins and Teachers can post announcements!', 'danger')
            return redirect(url_for('login'))

        title = request.form.get('title')
        content = request.form.get('content')
        posted_by = session['user_type'].capitalize()

        conn = sqlite3.connect('database.db')
        cursor = conn.cursor()
        cursor.execute('INSERT INTO announcements (title, content, posted_by) VALUES (?, ?, ?)', (title, content, posted_by))
        conn.commit()
        conn.close()

        flash('Announcement posted successfully!', 'success')

    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM announcements')
    all_announcements = cursor.fetchall()
    conn.close()
    return render_template('announcements.html', announcements=all_announcements)

@app.route('/teacher_dashboard')
def teacher_dashboard():
    if session.get('user_type') != 'teacher':
        flash('Access Denied!', 'danger')
        return redirect(url_for('home'))
    return render_template('teacher_dashboard.html')

@app.route('/student_dashboard')
def student_dashboard():
    if session.get('user_type') != 'student':
        flash('Access Denied!', 'danger')
        return redirect(url_for('home'))
    return render_template('student_dashboard.html')

if __name__ == '__main__':
    init_db()
    app.run(debug=True)
