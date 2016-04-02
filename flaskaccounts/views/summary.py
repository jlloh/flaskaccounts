from flask import Blueprint,render_template,g,request,redirect,url_for,session
from flask.ext.login import LoginManager,login_required,current_user

summarize=Blueprint('summarize',__name__)

@summarize.route('/')
@summarize.route('/summary')
@login_required
def getsummary():
	accounts={}
	for row in g.db.execute('select account,sum(amount) as sum from entries group by account having sum!=0'):
		account,total=row
		accounts[account]=total

	return render_template('summary/summary2.html',accounts=accounts,state3='active',username=current_user.username)
