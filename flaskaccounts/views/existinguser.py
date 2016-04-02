from flask import Blueprint,render_template,g,request,redirect,url_for,session,flash,current_app
import bcrypt
from flask.ext.login import login_user,logout_user
from ..forms import UserPWForm
from ..model import User
from flask.ext.login import current_user

existinguser=Blueprint('existinguser',__name__)

@existinguser.route('/login',methods=['GET','POST'])
def login():
	form=UserPWForm()
	error=None
	if form.validate_on_submit():
		username=form.username.data
		password=form.password.data

		user=User(username,current_app.config['DATABASE'])
		if user.is_anonymous()==True:
			error='Unregistered User'
		else:
			user.authenticate(password)
			if user.is_authenticated0==True:
				login_user(user)
				#next = flask.request.args.get('next')

				#session['username']=username
				#session['logged_in']=True

				return redirect(url_for('display.listall',no_rows_limit=20))
			else:
				error='Password Does Not Match'
		'''for row in g.db.execute('SELECT username,hashed from users where username=?',[str(username)]):
			usernames,hashed=row
			#userdict[usernames]=hashed

		if 'usernames' not in globals():
			error='Unregistered User'

		else:
			hashedresult=bcrypt.hashpw(password,hashed)
			if hashedresult==str(hashed):
				session['logged_in']=True
				#session['username']=username
				flash('Log In Successful')
				return redirect(url_for('display.listall',no_rows_limit=20))
			else:
				error='Password Does Not Match'''

	return render_template('users/login.html',error=error,form=form)

@existinguser.route('/logout',methods=['GET','POST'])
def logout():
	logout_user()
	#session['logged_in']=False
	#session.pop('username',None)
	return redirect(url_for('.login'))
	#return render_template('')