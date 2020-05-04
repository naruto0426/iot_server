######!!!! index.py in  /var/www/html !!!#####
from flask import Flask, request, session, redirect, url_for, Blueprint, render_template, abort
from pathlib import Path
import re
import pymongo
import time
import base64
import datetime
import json
from bson.objectid import ObjectId
import glob
from os.path import dirname, basename, isfile, join
from flask.json import JSONEncoder
from datetime import date

controllers = glob.glob(join('app/controllers', "*.py"))
app_flask = Flask(__name__,static_folder= 'static',static_url_path='/assets')
app_flask.secret_key = 'OCML3BRawWEUeaxcuKHLpw'
for controller in controllers:
    tmp = __import__(re.sub(r'/|\\','.',controller)[:-3],fromlist=[basename(controller)[:-3]])
    app_flask.register_blueprint(tmp.main())
host = 'demo-applejenny.dev.rulingcom.com'

class CustomJSONEncoder(JSONEncoder):
  def default(self, obj):
    try:
      if isinstance(obj, date):
          return obj.isoformat()

      return super().default(obj)
    except TypeError:
      pass
    return JSONEncoder.default(self, obj)
app_flask.json_encoder = CustomJSONEncoder
app_flask.run(host=host,port=5000,debug=True)
def check_db():
    myclient = pymongo.MongoClient('mongodb://localhost:27017/')
    dblist = myclient.list_database_names()
    if db_name in dblist:
        return ("數據庫已存在！")
    else:
        return ("數據庫不存在！")
