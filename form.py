from flask_wtf import FlaskForm as Form
from wtforms import validators
from wtforms import StringField, PasswordField
from wtforms.validators import Email
import model
from google.appengine.ext import ndb
import hashlib


class SignUpForm(Form):
    username = StringField('username',[validators.DataRequired()])
    password = PasswordField('password',[validators.DataRequired()])
    email = StringField('email',[validators.DataRequired(), Email()])

    def uniqueValidate(self):
        if not Form.validate(self):
            return False
        try:
            idInput = self.username.data
            validKey = ndb.Key(model.UserAccount, idInput).get().key
            if validKey:
                self.username.errors.append("This username is already taken. Try another one.")
        except:
            return True


class LogForm(Form):
    username = StringField('username',[validators.DataRequired()])
    password = PasswordField('password',[validators.DataRequired()])

    def __init__(self, *args, **kwargs):
        Form.__init__(self, *args, **kwargs)

    def validate(self):
        if not Form.validate(self):
            return False
        try:
            idInput = self.username.data
            pswInput = self.password.data
            hashed_psw = hashlib.sha256(pswInput).hexdigest()
            dataDict = [dict(p.to_dict(), **dict(id=p.key.id())) for p in
                        model.UserAccount.query(model.UserAccount.username == idInput)]
            accountPsw = dataDict[0]['password']
            if accountPsw == hashed_psw:
                return True
            else:
                self.username.errors.append("Invalid username or password")
        except:
            self.username.errors.append("Invalid username or password")
