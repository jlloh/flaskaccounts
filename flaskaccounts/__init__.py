import sqlite3
import os
from flask import Flask,request,session,g,redirect,url_for,render_template

from .views.existinguser import existinguser
from .views.display import display
from .views.controller import controller

accounts={'PREMIER':'PREMIER','ADVANCED':'ADVANCED','SAVINGS':'SAVINGS','TIME DEPOSITS':'TIME DEPOSITS','DSARA GW':'DSARA GROUNDWORKS','DSARA PL':'DSARA PILING','CASH':'CASH','DSARA IN':'DSARA IN'}
currencylist=['GBP','MYR']

#create app
app=Flask(__name__,instance_relative_config=True)
app.config.from_object('config') #looks for capitalized variables declared
app.config.from_pyfile('config.py')

app.config['DATABASE']=os.path.join(app.instance_path,'database.db')

app.register_blueprint(existinguser)
app.register_blueprint(display)
app.register_blueprint(controller)

#session['logged_in']=False
#session.pop('username',None)


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

#view functions


@app.route('/')
@app.route('/summary')
def summary():
	try:
		if session['logged_in']==False:
			return redirect(url_for('existinguser.login'))
	except KeyError:
		return redirect(url_for('existinguser.login'))

	premier={};savings={};advanced={};dsaragw={};dsarapl={};dsarain={};fd={}
	#for row in g.db.execute('SELECT * FROM ENTRIES WHERE ACCOUNT="PREMIER"'):
	for row in g.db.execute('SELECT * FROM ENTRIES'):
		(ID,YEAR,MONTH,DAY,ACCOUNT,AMOUNT,CURRENCY,DESCRIPTION)=row
		if ACCOUNT=='PREMIER':
			premier[ID]=[YEAR,MONTH,DAY,ACCOUNT,AMOUNT,CURRENCY,DESCRIPTION]
		elif ACCOUNT=='SAVINGS':
			savings[ID]=[YEAR,MONTH,DAY,ACCOUNT,AMOUNT,CURRENCY,DESCRIPTION]
		elif ACCOUNT=='ADVANCED':
			advanced[ID]=[YEAR,MONTH,DAY,ACCOUNT,AMOUNT,CURRENCY,DESCRIPTION]
		elif ACCOUNT=='DSARA GROUNDWORKS':
			dsaragw[ID]=[YEAR,MONTH,DAY,ACCOUNT,AMOUNT,CURRENCY,DESCRIPTION]
		elif ACCOUNT=='DSARA PILING':
			dsarapl[ID]=[YEAR,MONTH,DAY,ACCOUNT,AMOUNT,CURRENCY,DESCRIPTION]
		elif ACCOUNT=='DSARA IN':
			dsarain[ID]=[YEAR,MONTH,DAY,ACCOUNT,AMOUNT,CURRENCY,DESCRIPTION]
		elif ACCOUNT=='TIME DEPOSITS':
			fd[ID]=[YEAR,MONTH,DAY,ACCOUNT,AMOUNT,CURRENCY,DESCRIPTION]

	premier_sum=sum([premier[key][4] for key in premier])
	savings_sum=sum([savings[key][4] for key in savings])
	advanced_sum=sum([advanced[key][4] for key in advanced])
	dsaragw_sum=sum([dsaragw[key][4] for key in dsaragw])
	dsarapl_sum=sum([dsarapl[key][4] for key in dsarapl])
	dsarain_sum=sum([dsarain[key][4] for key in dsarain])
	fd_sum=sum([fd[key][4] for key in fd])

	return render_template('summary.html',premier='%.2f'%premier_sum,savings='%.2f'%savings_sum,advanced='%.2f'%advanced_sum,dsaragw='%.2f'%dsaragw_sum,fd='%.2f'%fd_sum,dsarapl='%.2f'%dsarapl_sum,dsarain='%.2f'%dsarain_sum,state3="active",username=session['username'])

if __name__=='__main__':
    app.run(host='0.0.0.0',port=5200)
