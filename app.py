from flask import Flask, render_template, redirect, url_for, request, session
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime, timedelta

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///library.db'
app.config['SECRET_KEY'] = 'secret'
db = SQLAlchemy(app)

from models import User, Book, UserBook

@app.before_first_request
def create_tables():
    db.create_all()

@app.route('/')
def home():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    user = User.query.get(session['user_id'])
    if user.role == 'student':
        books = UserBook.query.filter_by(user_id=user.id).all()
        return render_template('dashboard.html', books=books, user=user)
    elif user.role == 'librarian':
        return redirect(url_for('manage_books'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        user = User.query.filter_by(email=email).first()
        if user and check_password_hash(user.password, password):
            session['user_id'] = user.id
            return redirect(url_for('home'))
    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        name = request.form['name']
        dob = request.form['dob']
        email = request.form['email']
        password = generate_password_hash(request.form['password'])
        role = request.form['role']
        user = User(name=name, dob=dob, email=email, password=password, role=role)
        db.session.add(user)
        db.session.commit()
        return redirect(url_for('login'))
    return render_template('register.html')

@app.route('/logout')
def logout():
    session.pop('user_id', None)
    return redirect(url_for('login'))

@app.route('/profile')
def profile():
    user = User.query.get(session['user_id'])
    return render_template('profile.html', user=user)

@app.route('/manage_books', methods=['GET', 'POST'])
def manage_books():
    user = User.query.get(session['user_id'])
    if user.role != 'librarian':
        return redirect(url_for('home'))
    students = User.query.filter_by(role='student').all()
    books = Book.query.all()
    if request.method == 'POST':
        student_id = request.form['student_id']
        book_id = request.form['book_id']
        due_date = datetime.now() + timedelta(days=30)
        user_book = UserBook(user_id=student_id, book_id=book_id, due_date=due_date)
        db.session.add(user_book)
        db.session.commit()
    return render_template('manage_books.html', students=students, books=books)

@app.route('/remove_book/<int:userbook_id>')
def remove_book(userbook_id):
    userbook = UserBook.query.get(userbook_id)
    db.session.delete(userbook)
    db.session.commit()
    return redirect(url_for('manage_books'))

@app.route('/students_list')
def students_list():
    user = User.query.get(session['user_id'])
    if user.role != 'librarian':
        return redirect(url_for('home'))
    students = User.query.filter_by(role='student').all()
    return render_template('students_list.html', students=students)

if __name__ == '__main__':
    app.run(debug=True)
