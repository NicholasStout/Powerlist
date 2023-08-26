#!/usr/bin/env python
# coding: utf-8

# In[1]:


from flask import Flask
from flask_sqlalchemy import SQLAlchemy

# create the extension
db = SQLAlchemy()
# create the app
app = Flask(__name__)
# configure the SQLite database, relative to the app instance folder
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///project.db"
# initialize the app with the extension
db.init_app(app)


# In[2]:


#User class, in the event that multiple users wish to have lists
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String, unique=True, nullable=False)


# In[3]:


#The actual list database
class Lists(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user = db.Column(db.String, db.ForeignKey("user.id"), nullable=False)
    name = db.Column(db.String, nullable=False)
    hasColumns = db.Column(db.Boolean, nullable=False)


# In[4]:


#columns in the a list, in the event that a user would like to separate a list into columns (i.e. a kanban chart)
class Columns(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    lst = db.Column(db.Integer, db.ForeignKey("lists.id"), nullable=False)
    name = db.Column(db.String, nullable=False)
    hasEntries = db.Column(db.Boolean, nullable=False)


# In[5]:


#entries, each that can have thewir own sub lists
class Entries(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    lst = db.Column(db.Integer, db.ForeignKey("lists.id"), nullable=False)
    column = db.Column(db.Integer, db.ForeignKey("columns.id"), nullable=False)
    title = db.Column(db.String, nullable=False)
    content = db.Column(db.String, nullable=True)
    parentEntry = db.Column(db.Integer, db.ForeignKey("entries.id"), nullable=True)
    hasSublist = db.Column(db.Boolean, nullable=False)


# In[6]:


with app.app_context():
    db.create_all()


# In[7]:


@app.route("/users")
def user_list():
    users = db.session.execute(db.select(User).order_by(User.username)).scalars()
    return render_template("user/list.html", users=users)

@app.route("/users/create", methods=["GET", "POST"])
def user_create():
    if request.method == "POST":
        user = User(
            username=request.form["username"],
            email=request.form["email"],
        )
        db.session.add(user)
        db.session.commit()
        return redirect(url_for("user_detail", id=user.id))

    return render_template("user/create.html")

@app.route("/user/<int:id>")
def user_detail(id):
    user = db.get_or_404(User, id)
    return render_template("user/detail.html", user=user)

@app.route("/user/<int:id>/delete", methods=["GET", "POST"])
def user_delete(id):
    user = db.get_or_404(User, id)

    if request.method == "POST":
        db.session.delete(user)
        db.session.commit()
        return redirect(url_for("user_list"))

    return render_template("user/delete.html", user=user)


# In[ ]:




