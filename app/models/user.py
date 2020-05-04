from mongo_connect import *
class User(Document):
  user = StringField()
  password = PasswordField(algorithm="sha1")
  is_admin = BooleanField(default=False)
  def confirm_password(self,value):
    return PasswordField.confirm_password(self.password,value)