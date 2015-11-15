from flask import Blueprint,render_template,g,request,redirect,url_for,session

display=Blueprint('display',__name__)


@display.route('/show',defaults={'no_rows_limit':None})
@display.route('/show/<int:no_rows_limit>')
def listall(no_rows_limit):
	#return render_template('body.html')
	dictionary={}
	if session['logged_in']==False:
		return redirect(url_for('users.login'))


	for row in g.db.execute('SELECT * FROM ENTRIES'):
		(ID,YEAR,MONTH,DAY,ACCOUNT,AMOUNT,CURRENCY,DESCRIPTION)=row
		dictionary[ID]=[YEAR,MONTH,DAY,ACCOUNT,AMOUNT,CURRENCY,DESCRIPTION]
		max_rows=len(dictionary)

		if no_rows_limit!=None:
			min_row=max_rows-no_rows_limit
		else:
			min_row=0
	return render_template('display/main.html',output=dictionary,min_row=min_row,username=session['username'],state2="active")

@display.route('/filter',methods=['POST'])
def filter1():
	if session['logged_in']==False:
		return redirect(url_for('login'))
	if request.method=='POST':
		dictionary={}
		for row in g.db.execute('SELECT * FROM ENTRIES'):
			keyword=str(request.form['keyword'])
			(ID,YEAR,MONTH,DAY,ACCOUNT,AMOUNT,CURRENCY,DESCRIPTION)=row
			if keyword in DESCRIPTION:
				dictionary[ID]=[YEAR,MONTH,DAY,ACCOUNT,AMOUNT,CURRENCY,DESCRIPTION]

		return render_template('display/main.html',output=dictionary,min_row=0,username=session['username'],state2="active",keyword=keyword)

@display.route('/sortdate',defaults={'no_rows':None})
@display.route('/sortdate/<int:no_rows>')
def sortdate(no_rows):
	if session['logged_in']==False:
		return redirect(url_for('login'))

	dictionary={};dictionary2={}
	for row in g.db.execute('SELECT * FROM ENTRIES'):
		(ID,YEAR,MONTH,DAY,ACCOUNT,AMOUNT,CURRENCY,DESCRIPTION)=row
		datesort=int(YEAR)*10000+int(MONTH)*100+DAY
		dictionary.setdefault(datesort,[]).append({ID:[YEAR,MONTH,DAY,ACCOUNT,AMOUNT,CURRENCY,DESCRIPTION]})

		if no_rows!=None:
			min_row=0
		else:
			min_row=0

	return render_template('display/datesort.html',output=dictionary,no_rows=min_row,username=session['username'],state4="active")