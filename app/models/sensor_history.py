from mongo_connect import *
from itertools import groupby
import json
class SensorHistory(Document):
  s_type = StringField()
  device_id = StringField()
  create_time = DateTimeField(default=datetime.datetime.now())
  value = FloatField(default=0)