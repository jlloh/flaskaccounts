import sqlite3
import os
from flask import Flask,request,session,g,redirect,url_for,render_template

from .views.existinguser import existinguser
from .views.display import display

accounts={'PREMIER':'PREMIER','ADVANCED':'ADVANCED','SAVINGS':'SAVINGS','TIME DEPOSITS':'TIME DEPOSITS','DSARA GW':'DSARA GROUNDWORKS','DSARA PL':'DSARA PILING','CASH':'CASH','DSARA IN':'DSARA IN'}
currencylist=['GBP','MYR']

#create app
app=Flask(__name__,instance_relative_config=True)
app.config.from_object('config') #looks for capitalized variables declared
app.config.from_pyfile('config.py')

app.config['DATABASE']=os.path.join(app.instance_path,'database.db')

app.register_blueprint(existinguser)
app.register_blueprint(display)

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

@app.route('/add',methods=['GET','POST'])
def add_entry():
	if session['logged_in']==False:
		return redirect(url_for('login'))

	if request.method=='GET':
		return render_template('add.html',accounts=accounts)
	elif request.method=='POST':
		date=request.form['date']
		#return render_template('add.html',date=date)
		(year,month,day)=date.split('-')
		account=request.form['account']
		amount=request.form['amount']
		description=request.form['description']
		currency=request.form['currency']

		if len(str(year))<4:
			year=2000+int(year)

		g.db.execute('INSERT INTO ENTRIES (YEAR,MONTH,DAY,ACCOUNT,AMOUNT,CURRENCY,DESCRIPTION) VALUES(?,?,?,?,?,?,?)',[int(year),int(month),int(day),account,amount,currency,description])
		g.db.commit()
		return redirect(url_for('display.listall',no_rows_limit=20))

@app.route('/convert',methods=['GET','POST'])
def convert():
	if session['logged_in']==False:
		return redirect(url_for('login'))

	if request.method=='GET':
		return render_template('convert.html')
	elif request.method=='POST':
		date=request.form['date']
		(year,month,day)=date.split('-')
		fromaccount=request.form['fromaccount']
		toaccount=request.form['toaccount']
		amount=float(request.form['amount'])*-1
		rate=request.form['rate']
		amount_conv='%.2f'%(float(rate)*float(amount)*-1)
		currency1='GBP'
		currency2='MYR'
		description='GBP to MYR @ %s'%(str(rate))

		#First entry. From premier
		g.db.execute('INSERT INTO ENTRIES (YEAR,MONTH,DAY,ACCOUNT,AMOUNT,CURRENCY,DESCRIPTION) VALUES(?,?,?,?,?,?,?)',[int(year),int(month),int(day),fromaccount,amount,currency1,description])
		g.db.execute('INSERT INTO ENTRIES (YEAR,MONTH,DAY,ACCOUNT,AMOUNT,CURRENCY,DESCRIPTION) VALUES(?,?,?,?,?,?,?)',[int(year),int(month),int(day),toaccount,amount_conv,currency2,description])

		g.db.commit()

		return redirect(url_for('display.listall',no_rows_limit=20))

@app.route('/transfer',methods=['GET','POST'])
def transfer():
	if session['logged_in']==False:
		return redirect(url_for('login'))

	if request.method=='GET':
		return render_template('transfer.html',accounts=accounts)
	elif request.method=='POST':
		date=request.form['date']
		(year,month,day)=date.split('-')
		fromaccount=request.form['fromaccount']
		toaccount=request.form['toaccount']
		amount=float(request.form['amount'])*-1
		amount2=float(request.form['amount'])
		currency=request.form['currency']
		description=request.form['description']

		#First entry. From premier
		g.db.execute('INSERT INTO ENTRIES (YEAR,MONTH,DAY,ACCOUNT,AMOUNT,CURRENCY,DESCRIPTION) VALUES(?,?,?,?,?,?,?)',[int(year),int(month),int(day),fromaccount,amount,currency,description])
		g.db.execute('INSERT INTO ENTRIES (YEAR,MONTH,DAY,ACCOUNT,AMOUNT,CURRENCY,DESCRIPTION) VALUES(?,?,?,?,?,?,?)',[int(year),int(month),int(day),toaccount,amount2,currency,description])

		g.db.commit()

		return redirect(url_for('display.listall',no_rows_limit=20))

@app.route('/delete/<int:id_no>')
def delete_entry(id_no):
	if session['logged_in']==False:
		return redirect(url_for('login'))
	g.db.execute('DELETE FROM ENTRIES WHERE ID=?',[id_no])
	g.db.commit()
	return redirect(url_for('display.listall',no_rows_limit=20))

@app.route('/edit/<int:id_no>',methods=['GET','POST'])
def edit_entry(id_no):
	if session['logged_in']==False:
		return redirect(url_for('login'))

	if request.method=='GET':
		for row in g.db.execute('SELECT * FROM ENTRIES WHERE ID=?',[id_no]):
			(ID,YEAR,MONTH,DAY,ACCOUNT,AMOUNT,CURRENCY,DESCRIPTION)=row
			rowlist=[YEAR,MONTH,DAY,ACCOUNT,AMOUNT,CURRENCY,DESCRIPTION]
			#         0    1     2     3      4      5         6
		return render_template('edit.html',rowlist=rowlist,accounts=accounts,id1=id_no,currency=currencylist,username=session['username'])
	elif request.method=='POST':
		date=request.form['date']
		#return render_template('add.html',date=date)
		(year,month,day)=date.split('-')
		account=request.form['account']
		amount=request.form['amount']
		description=request.form['description']
		currency=request.form['currency']

		if len(str(year))<4:
			year=2000+int(year)

		g.db.execute('UPDATE ENTRIES SET YEAR=?,MONTH=?,DAY=?,ACCOUNT=?,AMOUNT=?,CURRENCY=?,DESCRIPTION=? WHERE ID=?',[int(year),int(month),int(day),account,amount,currency,description,id_no])
		g.db.commit()
		return redirect(url_for('display.listall',no_rows_limit=20))

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
