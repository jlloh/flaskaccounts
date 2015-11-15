from flask import Blueprint,render_template,g,request,redirect,url_for,session,flash
import hashlib

existinguser=Blueprint('existinguser',__name__)

@existinguser.route('/login',methods=['GET','POST'])
def login():
	error=None
	if request.method=='POST':
		username=request.form['username']
		password=request.form['password']

		userdict={}
		for row in g.db.execute('SELECT username,salt,hash from users'):
			usernames,salt,hash1=row
			userdict[usernames]=[salt,hash1]


		if username not in userdict.keys():
			error='Unregistered User'
		#elif password != (app.config['USERS'])[username]:
		#	error='Invalid Password'
		else:
			#unencode the salt
			usersalt=userdict[username][0].decode('base64')
			#usersalted=usersalt+str(password)
			hashresult=hashlib.sha256(userdict[username][0]+str(password)).hexdigest()
			#hashed_object=hashlib.sha256(usersalt+str(password))
			#compare hashes
			if hashresult!=userdict[username][1]:
				error='Password Does Not Match'
			else:
				session['logged_in']=True
				session['username']=username
				flash('Log In Successful')
				return redirect(url_for('display.listall',no_rows_limit=20))

	return render_template('users/login.html',error=error)

@existinguser.route('/logout',methods=['GET','POST'])
def logout():
	session['logged_in']=False
	session.pop('username',None)
	return redirect(url_for('.login'))
	#return render_template('')