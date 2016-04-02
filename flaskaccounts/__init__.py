import sqlite3
import os
from flask import Flask,request,session,g,redirect,url_for,render_template
from flask.ext.login import LoginManager,login_required,current_user

from .views.existinguser import existinguser
from .views.display import display
from .views.controller import controller
from .views.newuser import newuser
from .views.summary import summarize
from .model import User

#accounts={'PREMIER':'PREMIER','ADVANCED':'ADVANCED','SAVINGS':'SAVINGS','TIME DEPOSITS':'TIME DEPOSITS','DSARA GW':'DSARA GROUNDWORKS','DSARA PL':'DSARA PILING','CASH':'CASH','DSARA IN':'DSARA IN'}
currencylist=['GBP','MYR']

#create app
app=Flask(__name__,instance_relative_config=True)
app.config.from_object('config') #looks for capitalized variables declared
app.config.from_pyfile('config.py')

app.config['DATABASE']=os.path.join(app.instance_path,'database.db')

app.register_blueprint(existinguser)
app.register_blueprint(display)
app.register_blueprint(controller)
app.register_blueprint(newuser)
app.register_blueprint(summarize)

#session['logged_in']=False
#session.pop('username',None)

#Flask-Login crap
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view =  "existinguser.login"

#Function to connect to database
def connect_db():
    return sqlite3.connect(app.config['DATABASE'])

#Special functions to request connection
@app.before_request
def before_request():
    g.db = connect_db()
@app.teardown_request
def teardown_request(exeption):
    db = getattr(g, 'db', None)
    if db is not None:
        db.close()
@app.after_request
def add_header(response):
	response.headers['Cache-Control']='public,max-age=0'
	return response


@login_manager.user_loader
def load_user(userid):
    username=str(userid)
    return User(username,app.config['DATABASE'])


if __name__=='__main__':
    app.run(host='0.0.0.0',port=5200)
