from flask import Blueprint,render_template,g,request,redirect,url_for,session

controller=Blueprint('controller',__name__)

#To-do. Move this to the database.
#accounts={'PREMIER':'PREMIER','ADVANCED':'ADVANCED','SAVINGS':'SAVINGS','TIME DEPOSITS':'TIME DEPOSITS','DSARA GW':'DSARA GROUNDWORKS','DSARA PL':'DSARA PILING','CASH':'CASH','DSARA IN':'DSARA IN'}
#accounts=['PREMIER','ADVANCED','SAVINGS','TIME DEPOSITS']
currencylist=['GBP','MYR']

@controller.route('/add',methods=['GET','POST'])
def add_entry():
    accounts=[]
    if session['logged_in']==False:
        return redirect(url_for('users.login',username=session['username']))

    if request.method=='GET':
        #return render_template('controls/add.html',accounts=accounts)
	for row in g.db.execute("SELECT username,account FROM ACCOUNTNAME where username=?",[session['username']]):
            username,account=row
            accounts.append(str(account.upper()))
        return render_template('controls/add.html',accounts=accounts)

    elif request.method=='POST':
        date=request.form['date']
	#return render_template('controls/add.html',date=date)
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


@controller.route('/convert',methods=['GET','POST'])
def convert():
    if session['logged_in']==False:
        return redirect(url_for('users.login'))

    if request.method=='GET':
	return render_template('controls/convert.html',username=session['username'])
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

@controller.route('/transfer',methods=['GET','POST'])
def transfer():
    accounts=[]
    if session['logged_in']==False:
	return redirect(url_for('users.login'))

    if request.method=='GET':
        for row in g.db.execute("SELECT username,account FROM ACCOUNTNAME where username=?",[session['username']]):
            username,account=row
            accounts.append(str(account.upper()))
	return render_template('controls/transfer.html',accounts=accounts,username=session['username'])

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

@controller.route('/delete/<int:id_no>')
def delete_entry(id_no):
    if session['logged_in']==False:
	return redirect(url_for('login'))
    g.db.execute('DELETE FROM ENTRIES WHERE ID=?',[id_no])
    g.db.commit()
    return redirect(url_for('display.listall',no_rows_limit=20))

@controller.route('/edit/<int:id_no>',methods=['GET','POST'])
def edit_entry(id_no):
    accounts=[]
    if session['logged_in']==False:
	return redirect(url_for('users.login'))
    if request.method=='GET':
        for row in g.db.execute("SELECT username,account FROM ACCOUNTNAME where username=?",[session['username']]):
            username,account=row
            accounts.append(str(account.upper()))
	for row in g.db.execute('SELECT * FROM ENTRIES WHERE ID=?',[id_no]):
            (ID,YEAR,MONTH,DAY,ACCOUNT,AMOUNT,CURRENCY,DESCRIPTION)=row
            rowlist=[YEAR,MONTH,DAY,ACCOUNT,AMOUNT,CURRENCY,DESCRIPTION]
            #         0    1     2     3      4      5         6
        return render_template('controls/edit.html',rowlist=rowlist,accounts=accounts,id1=id_no,currency=currencylist,username=session['username'])
    elif request.method=='POST':
	date=request.form['date']
	#return render_template('controls/add.html',date=date)
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
