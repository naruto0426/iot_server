from mongo_connect import *
class WifiPos(Document):
  bssid = StringField()
  ssid = StringField()
  pos = DictField()