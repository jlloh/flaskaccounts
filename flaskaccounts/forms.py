from flask_wtf import Form
from wtforms import StringField,PasswordField
from wtforms.validators import Required

class UserPWForm(Form):
    username=StringField('username',validators=[Required()])
    password=PasswordField('password',validators=[Required()])