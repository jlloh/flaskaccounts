from flask import Blueprint,render_template,g,request,redirect,url_for,session,flash
import bcrypt

newuser=Blueprint('newuser',__name__)

@newuser.route('/register',methods=['GET','POST'])
def register():
    error='';userlist=[];newuser=''
    if request.method=='POST':
        newuser=request.form['username']
        userlist=[username for username, in g.db.execute('SELECT username from users')]
        #for row in g.db.execute('SELECT username from users'):
        #    username,=row
        #    userlist.append(str(username))
        if newuser in userlist:
            error='Username exists. Pick another username'
            flash(error)
        else:
            flash('Success')
            session['username']=newuser
            return redirect(url_for('.register_pw'))
    return render_template('users/register.html',error=error,userlist=userlist,newuser=newuser)

@newuser.route('/register_pw')
def register_pw():
    currentuser=''
    try:
        currentuser=session['username']
    except KeyError:
        return redirect(url_for('existinguser.login'))
    userlist=[username for username, in g.db.execute('SELECT username from users')]
    if currentuser in userlist:
        return redirect(url_for('display.listall'))
    return render_template('users/register_pw.html',currentuser=currentuser)