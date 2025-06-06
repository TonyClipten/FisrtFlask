from flask import Flask, redirect, session, url_for, render_template, request, flash, Blueprint
from datetime import timedelta
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from second import second

# Create a flask instance
app = Flask(__name__)
# add second python program
app.register_blueprint(second, url_prefix="/admin")
# Secrect Key
app.secret_key = "hello"
# Add Database
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.sqlite3'
# No track modification so that we do not get a popup waning
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.permanent_session_lifetime = timedelta(minutes=5)
# Initialize The Database
db = SQLAlchemy(app)


# Create Model
class users(db.Model):
    id = db.Column("id", db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), nullable=False, unique=True)
    date_added = db.Column(db.DateTime, default=datetime.utcnow)
    

    # Create a string
    def __repr__(self):
        return '<Name %r>' % self.name


    def __init__(self, name, email):
        self.name = name
        self.email = email
        
        

@app.route("/")
def home():
    return render_template("index.html", content="Testing")

# pass users to render tyemplate
@app.route("/view")
def view():
    return render_template("view.html", values=users.query.all())

@app.route("/login", methods=["POST", "GET"])
def login():
    if request.method == "POST":
        session.permanent = True
        user = request.form["nm"]
        session["user"] = user
        
        # query
        found_user = users.query.filter_by(name=user).first()
        if found_user:
            session["email"] = found_user.email
       
        else:
            usr = users(user, "")
            db.session.add(usr)
            db.session.commit()

        flash("Login Succesfull!")
        return redirect(url_for("user"))
    else:
        if "user"in session:
            flash("Already Logged In!")
            return redirect(url_for("user"))

        return render_template("login.html")
    
@app.route("/user", methods=["POST", "GET"])
def user():
    email = None
    if "user" in session:
        user = session["user"]

        if request.method == "POST":
            email = request.form["email"]
            session["email"] = email
            found_user = users.query.filter_by(name=user).first()
            found_user.email = email
            db.session.commit()
            flash("Email was saved!")
           
        else:
            if "email" in session:
                email = session["email"]

        return render_template("user.html", email=email)
    else:
        flash("You are not logged in!")
        return redirect(url_for("login"))
    
    with app.app_context():
        db.create_all()

@app.route("/logout")    
def logout():
    flash("You have been logged out", "info")
    session.pop("user", None)
    session.pop("email", None)
    return redirect(url_for("login"))

if __name__ == "__main__":
    app.app_context().push()
    db.create_all()
    app.run(port="5001", debug=False)