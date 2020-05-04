from mongo_connect import *
class IpManage(Document):
  setting = DictField()
  mode = StringField()