import os
from flask import Flask, render_template, request, redirect, url_for
import sqlite3

app = Flask(__name__)

UPLOAD_FOLDER = '/path/to/upload/folder'  # Change this to your actual folder
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
ALLOWED_EXTENSIONS = {'txt'}

# Function to check allowed file types
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# Count words in the uploaded file
def count_words_in_file(filepath):
    with open(filepath, 'r') as f:
        text = f.read()
    return len(text.split())

@app.route('/register', methods=['POST'])
def register():
    username = request.form['username']
    password = request.form['password']
    firstname = request.form['firstname']
    lastname = request.form['lastname']
    email = request.form['email']

    # File handling
    file = request.files['file']

    # Save the file to the upload folder
    if file:
        filename = file.filename
        file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
        word_count = count_words_in_file(os.path.join(app.config['UPLOAD_FOLDER'], filename))
    else:
        word_count = 0

    # Save user data and word count to the database
    conn = sqlite3.connect(DATABASE)
    c = conn.cursor()
    c.execute(
        "INSERT INTO users (username, password, firstname, lastname, email, word_count, file_name) VALUES (?, ?, ?, ?, ?, ?, ?)",
         (username, password, firstname, lastname, email, word_count, filename)
    )
    conn.commit()
    conn.close()

    # Redirect to the profile page
    return redirect(url_for('profile', username=username))


@app.route('/profile/<username>')
def profile(username):
    conn = sqlite3.connect(DATABASE)
    c = conn.cursor()
    c.execute("SELECT * FROM users WHERE username=?", (username,))
    user = c.fetchone()
    conn.close()

    # Load word count and file for the user
    word_count = user[6]  # Assuming the word count is stored in column index 6
    file_name = user[7]   # Assuming the file name is stored in column index 7

    file_path = os.path.join(app.config['UPLOAD_FOLDER'], file_name)

    return render_template('profile.html', user=user, word_count=word_count, file_name=file_name, file_path=file_path)
# Define the absolute path to the database
DATABASE = '/home/ubuntu/mydatabase.db'

# Function to initialize the database and create the users table if it doesn't exist
def init_db():
    conn = sqlite3.connect(DATABASE)
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS users 
                 (id INTEGER PRIMARY KEY AUTOINCREMENT, username TEXT, password TEXT, 
                  firstname TEXT, lastname TEXT, email TEXT)''')
    conn.commit()
    conn.close()

# Route to display the registration form (home route)
@app.route('/')
def index():
    return render_template('registration.html')

# Route to handle the registration form submission


# Route to display the login form
@app.route('/login', methods=['GET', 'POST']) 
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        conn = sqlite3.connect(DATABASE)  # Use the absolute path here
        c = conn.cursor()
        c.execute("SELECT * FROM users WHERE username=? AND password=?", (username, password))
        user = c.fetchone()
        conn.close()

        if user:
            return redirect(url_for('profile', username=user[1]))  # Redirect to profile page
        else:
            return "Invalid username or password", 401

    return render_template('login.html')  # Render the login form

# Main function to start the Flask app
if __name__ == '__main__':
    init_db()  # Initialize the database before running the app
    app.run(debug=True)
