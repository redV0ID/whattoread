import os

from flask import Flask, redirect, render_template, request, session, url_for
from flask_session import Session
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker

app = Flask(__name__)

# Configure session to use filesystem
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Set up database
engine = create_engine("postgres://qabmacgwvwjfux:a098b9fc911f60cfe0a8927f771f983b65c873840ead45cc07a270e9680a2098@ec2-54-221-192-231.compute-1.amazonaws.com:5432/dceqi3aso3lr9p")
db = scoped_session(sessionmaker(bind=engine))


@app.route("/")
def index():
    if "username" in session:
        return render_template("search.html") 
    return render_template("index.html")


@app.route("/register", methods=["POST", "GET"])
def register():
    if request.method == "POST":
        username = request.form.get('username')
        password = request.form.get('password')
        try:
            db.execute("INSERT INTO users (username, password) VALUES (:username, :password)",
                {"username": username,
                 "password": password})
            db.commit()
            session['username'] = username
            session['password'] = password
            return redirect(url_for('search'))
        except:
            return "Error in database!"
        
    return render_template("register.html")

@app.route("/login", methods=['POST', 'GET'])
def login():
    if request.method == "POST":
        username = request.form.get('username')
        password = request.form.get('password')

        if db.execute("SELECT * FROM users WHERE username = :username",
            {"username": username}).rowcount == 0:
            return render_template("error.html", message="No such user in db!")
        session['username'] = username
        session['password'] = password
        return redirect(url_for('search'))

    return render_template('login.html')


@app.route("/search", methods=['GET', 'POST'])
def search():
    if "username" in session:
        question = request.form.get('search') or ''
        books = db.execute("SELECT * FROM books WHERE title LIKE :wildcard OR author LIKE :wildcard or isbn LIKE :wildcard",
            {'wildcard': "%" + question + "%"}).fetchall()

        return render_template("search.html", books=books)
    return render_template("error.html", message="You are not logged in!")


@app.route("/logout")
def logout():
    session.pop('username', None)
    return redirect(url_for('index'))


app.secret_key = 'development_key' # in dev use maybe os.urandom(24) instead?


if __name__ == '__main__':
    
    app.run()