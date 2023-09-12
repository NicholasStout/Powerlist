#!/usr/bin/env python
# coding: utf-8

# In[1]:


from flask import Flask
from flask import request
from flask_sqlalchemy import SQLAlchemy

# create the extension
db = SQLAlchemy()
func = db.sql.functions
# create the app
app = Flask(__name__)
# configure the SQLite database, relative to the app instance folder
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///project.db"
# initialize the app with the extension
db.init_app(app)

#planning on using flask-login (flask-oauth?) and flask principal for authentication and role separation





#User class, in the event that multiple users wish to have lists
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String, unique=True, nullable=False)
    creationDateTime = db.Column(db.DateTime, server_default=func.now(), nullable=False)
    lastEditDateTime = db.Column(db.DateTime, server_default=func.now(), onupdate=func.now(), nullable=False)





#The actual list database
class List(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    name = db.Column(db.String, nullable=False)
    columnCount = db.Column(db.Integer, server_default='0', nullable=False)
    entryCount = db.Column(db.Integer, server_default='0', nullable=False)
    sublistCount = db.Column(db.Integer, server_default='0',  nullable=False)
    sublistOf = db.Column(db.Integer, db.ForeignKey("entry.id"))
    creationDateTime = db.Column(db.DateTime, server_default=func.now(), nullable=False)
    lastEditDateTime = db.Column(db.DateTime, server_default=func.now(), onupdate=func.now(), nullable=False)
    lastEditBy = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)





#columns in the a list, in the event that a user would like to separate a list into columns (i.e. a kanban chart)
class Column(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    lst = db.Column(db.Integer, db.ForeignKey("list.id"), nullable=False)
    order = db.Column(db.Integer, autoincrement=True)
    name = db.Column(db.String, nullable=False)
    creationDateTime = db.Column(db.DateTime, server_default=func.now(), nullable=False)
    lastEditDateTime = db.Column(db.DateTime, server_default=func.now(), onupdate=func.now(), nullable=False)
    lastEditBy = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)





#entries, each that can have their own sub lists
class Entry(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    lst = db.Column(db.Integer, db.ForeignKey("list.id"), nullable=False)
    column = db.Column(db.Integer, db.ForeignKey("column.id"), nullable=False)
    order = db.Column(db.Integer, autoincrement=True)
    title = db.Column(db.String, nullable=False)
    content = db.Column(db.String, nullable=True)
    hasSublist = db.Column(db.Boolean, nullable=False)
    creationDateTime = db.Column(db.DateTime, server_default=func.now(), nullable=False)
    lastEditDateTime = db.Column(db.DateTime, server_default=func.now(), onupdate=func.now(), nullable=False)
    lastEditBy = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)





with app.app_context():
    db.create_all()


def create_json(data):
    return [{col.name: getattr(d, col.name) for col in d.__table__.columns} for d in data]


@app.route("/users")
def user_list():
    #users = db.session.execute(db.select(User).order_by(User.username)).scalars()
    users = User.query.all()
    #return render_template("user/list.html", users=users)
    #print(users[0])
    return create_json(users)

@app.route("/users/create", methods=["GET", "POST"])
def user_create():
    if request.method == "POST":
        user = User(
            username=request.get_json()["username"],
        )
        db.session.add(user)
        db.session.commit()
        return str(user.id)

    return render_template("user/create.html")

@app.route("/user/<int:uid>")
def user_detail(uid):
    #user = db.get_or_404(User, id)
    return create_json(User.query.filter_by(id=uid).all())
    #return render_template("user/detail.html", user=user)

@app.route("/user/<int:uid>/delete", methods=["GET", "POST"])
def user_delete(uid):
    user = db.get_or_404(User, uid)

    if request.method == "POST":
        db.session.delete(user)
        db.session.commit()
        return redirect(url_for("user_list"))

    #return render_template("user/delete.html", user=user)
    

#list api
#     id = db.Column(db.Integer, primary_key=True)
#    user = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
#    name = db.Column(db.String, nullable=False)
#    public = db.Column(db.Boolean, nullable=False)
#    columnCount = db.Column(db.Integer, nullable=False)
#    entryCount = db.Column(db.Integer, nullable=False)
#    sublistCount = db.Column(db.Integer, nullable=False)
#    SublistOf = db.Column(db.Integer, db.ForeignKey("entry.id"))
#    creationDateTime = db.Column(db.DateTime, server_default=func.now(), nullable=False)
#    lastEditDateTime = db.Column(db.DateTime, server_default=func.now(), onupdate=func.now(), nullable=False)
#    lastEditBy = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
@app.route("/user/<int:uid>/lists")
def list_list(uid):
    lists = List.query.all()
    #return render_template("user/list.html", users=users)
    #print(users[0])
    return create_json(lists)

@app.route("/user/<int:uid>/lists/create", methods=["GET", "POST"])
def list_create(uid):
    if request.method == "POST":
        public = True
        sublistOf = None
        if 'public' in request.get_json().keys():
            public = request.get_json()["public"]
        if 'sublistOf' in request.get_json().keys():
            public = request.get_json()["sublistOf"]
        request.get_json
        l = List(
            user=uid,
            name=request.get_json()["title"],
            public=public,
            sublistOf=sublistOf,
            lastEditBy=uid
        )
        db.session.add(l)
        db.session.commit()
        return str(l.id)

    return render_template("user/create.html")

@app.route("/user/<int:uid>/list/<int:lid>")
def list_detail(uid, lid):
    #user = db.get_or_404(User, id)
    return create_json(List.query.filter_by(id=lid,user=uid).all())
    return l
    #return render_template("user/detail.html", user=user)

@app.route("/user/<int:id>/list/<int:lid>/delete", methods=["GET", "POST"])
def list_delete(uid, lid):
    user = db.get_or_404(User, id)

    if request.method == "POST":
        db.session.delete(user)
        db.session.commit()
        return redirect(url_for("user_list"))

    #return render_template("user/delete.html", user=user)
    
#    id = db.Column(db.Integer, primary_key=True)
#    user = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
#    lst = db.Column(db.Integer, db.ForeignKey("list.id"), nullable=False)
#    name = db.Column(db.String, nullable=False)
#    creationDateTime = db.Column(db.DateTime, server_default=func.now(), nullable=False)
#    lastEditDateTime = db.Column(db.DateTime, server_default=func.now(), onupdate=func.now(), nullable=False)
#    lastEditBy = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)    











