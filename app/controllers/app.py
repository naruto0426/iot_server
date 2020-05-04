######!!!! index.py in  /var/www/html !!!#####
from flask import Flask, request, session, redirect, url_for, Blueprint, render_template, abort, Response, jsonify
from pathlib import Path
import re
import pymongo
import time
import base64
import datetime
import json
from bson.objectid import ObjectId
import sys
import os
from os.path import dirname
sys.path.append(os.path.abspath(dirname('../../')))
import trail as trail_m
from models import *
import matplotlib.pyplot as plt

class AppBlueprint(Blueprint):
    def render_template(self, session, name, **kwargs):
        current_user = None
        kwargs['is_admin'] = False
        with trail: current_user = User.objects(user=session['user']).first()
        with trail: kwargs['current_user'] = current_user['user']
        with trail: kwargs['is_admin'] = current_user.is_admin
        return render_template(name, **kwargs)
def main():
    trail = trail_m.main()
    app = AppBlueprint('', __name__, template_folder='../views')
    def get_field_name(field_name):
        switcher = {
            'system': "系統",
            'version': "版本號",
            'machine': "電腦架構",
            'processor': "cpu處理器"
        }
        return switcher.get(field_name,field_name)
    def check_all_in_list(**dict_):
        flag = True
        print(dict_)
        target = dict_['target']
        values = dict_['values']
        for value in values:
            flag = flag & (target != value)
        return flag
    @app.before_request
    def check_valid_login():
        if (User.objects.first() == None):
            user = User(user='admin',password='admin',is_admin=True)
            user.save()
        login_valid = 'user' in session # or whatever you use to check valid login
        print(request.endpoint)
        auth_url_list = ['.annc','.recieve_client_data','.login','.register','.login_auth','.register_auth']
        if (request.endpoint and check_all_in_list(target = request.endpoint,values = auth_url_list) and not request.endpoint.startswith('static/') and not login_valid) :
            return redirect(url_for('.login', refer_url=request.url))
        elif (login_valid and not check_all_in_list(target = request.endpoint,values = auth_url_list)):
            return redirect(request.url_root)
    def menu():
        return app.render_template(session,'menu.html')
    @app.route('/logout',methods=['get'])
    def logout():
        session.clear()
        return redirect(url_for('.login'))
    @app.route('/account_management',methods=['get'])
    def account_management():
        is_admin = False
        with trail: is_admin = User.objects(user=session['user']).first().is_admin
        return app.render_template(session,
                                    'account_management.html',
                                    users = User.objects().order_by('id'),
                                    is_admin = is_admin,
                                    render_menu = menu())
    @app.route('/ip_management',methods=['get'])
    def ip_management():
        is_admin = False
        with trail: is_admin = User.objects(user=session['user']).first().is_admin
        return app.render_template(session,
                                    'ip_management.html',
                                    users = User.objects().order_by('id'),
                                    is_admin = is_admin,
                                    render_menu = menu())
    @app.route('/switch_user_admin',methods=['post'])
    def switch_user_admin():
        params = request.form
        user = None
        with trail: user = User.objects(id=params['user_id']).first()
        if (user != None):
            status = 'success'
            text = ''
            is_admin = True if params['is_admin'] == 'true' else False
            try:
                user.update(is_admin= is_admin)
            except:
                text = '更新狀態失敗'
                status = 'failed'
        else:
            status = 'failed'
            text = '帳號不存在'
        return {'status': status,'text': text}
    @app.route('/delete_user',methods=['post'])
    def delete_user():
        params = request.form
        user = None
        with trail: user = User.objects(id=params['user_id']).first()
        if (user != None):
            status = 'success'
            text = ''
            try:
                user.delete()
            except:
                text = '刪除帳號失敗'
                status = 'failed'
        else:
            status = 'failed'
            text = '帳號不存在'
        return {'status': status,'text': text}
    @app.route('/switch_device_permit',methods=['post'])
    def switch_device_permit():
        params = request.form
        device = None
        with trail: device = DeviceList.objects(id=params['device_id']).first()
        if (device != None):
            status = 'success'
            text = ''
            is_permit = True if params['is_permit'] == 'true' else False
            try:
                device.update(is_permit= is_permit)
            except:
                text = '更新狀態失敗'
                status = 'failed'
        else:
            status = 'failed'
            text = '裝置不存在'
        return {'status': status,'text': text}
    @app.route('/register_auth',methods=['post'])
    def register_auth():
        params = request.form
        user = User.objects(user=params['user']).first()
        if user != None:
            status = 'failed'
            text = '此帳號已經被註冊'
        else:
            status = 'success'
            print(params['password'])
            user = User(user=params['user'],password=params['password'])
            try:
                user.save()
                text = request.url_root + 'login?refer_url=' + params['refer_url']
            except:
                status = 'failed'
                text = '密碼不符合規定'
        return {'status': status,'text': text}
    @app.route('/register',methods=['get'])
    def register():
        params = request.args
        refer_url = ''
        with trail: refer_url = params['refer_url']
        return app.render_template(session,'register.html',refer_url=refer_url)
    @app.route('/login_auth',methods=['post'])
    def login_auth():
        params = request.form
        print(params['user'])
        user = User.objects(user=params['user']).first()
        if user == None:
            status = 'failed'
            text = '查無帳號'
        elif user.confirm_password(params['password']):
            status = 'success'
            session['user'] = user['user']
            text = params['refer_url'] or request.url_root
        else:
            status = 'failed'
            text = '密碼錯誤'
        return {'status': status,'text': text}
    @app.route('/login',methods=['get'])
    def login():
        params = request.args
        refer_url = ''
        with trail: refer_url = params['refer_url']
        user_name = ''
        with trail: user_name = params['user_name']
        return app.render_template(session,'login.html',refer_url=refer_url,user_name=user_name)
    login_auth
    @app.route('/hello')
    def helloIndex():
        return app.render_template(session,'hello_index.html')
    @app.route("/")
    # def index():
        # #name = request.args.get('name')
        # print(request.environ)
        # if 'HTTP_X_FORWARDED_FOR' in list(request.environ.keys()):
            # address = request.environ['HTTP_X_FORWARDED_FOR']
        # else:
            # address = request.remote_addr
        # user_agent = re.split('[\(\)]',request.environ['HTTP_USER_AGENT'])
        # myclient = pymongo.MongoClient('mongodb://localhost:27017/')
        # global db_name
        # mydb = myclient[db_name]
        # print(mydb)
        # print(db_name)
        # collection = mydb['device_list']
        # device = {'ip':address,'user_agent':user_agent[1]}
        # if(collection.find(device).count() == 0):
            # collection.insert_one(device)
        # response = ' <link href="https://maxcdn.bootstrapcdn.com/bootstrap/4.4.1/css/bootstrap.min.css" rel="stylesheet" type="text/css" />'+"您的ip address:"+address+'<br>您的裝置:'+user_agent[1]
        # table = '<table class="table table-striped table-primary"><thead><tr><th>ip位址</th><th>裝置</th></thead><tbody>'
        # for device in collection.find({}):
            # table += '<tr><td>'+device['ip']+'</td><td>'+str(device['user_agent'])+'</td></tr>'
        # table += '</tbody></table>'
        # return response + table
    def index():
        #name = request.args.get('name')
        print(request.environ)
        if 'HTTP_X_FORWARDED_FOR' in list(request.environ.keys()):
            address = request.environ['HTTP_X_FORWARDED_FOR']
        else:
            address = request.remote_addr
        user_agent = re.split('[\(\)]',request.environ['HTTP_USER_AGENT'])
        field_names = ['system','version','machine','processor']
        """
        time_now = timestamp(datetime.datetime.now())
        for device in DeviceList.objects():
            d = device
            time_device = timestamp(d['update_time'])
            if(d['user_agent'] == {} or time_now - time_device > 60):
                device.delete()
        """
        """
        for device in DeviceList.objects():
            data = SensorHistory.get_plot_data(device['id'])
            if len(data)>0:
                fig,ax=plt.subplots(1,1)
                ax.plot(data)
                ax.set_title('濕度感測',fontsize=12,color='r')
                fig.savefig('static/plot_'+str(device.id)+'.png')
        """
        return app.render_template(session,
                                    'index.html',
                                    render_menu=menu(),
                                    devices=DeviceList.objects.order_by('id'),#DeviceList.get_alive().order_by('id'),
                                    field_names=field_names,
                                    handle_field_catch=handle_field_catch,
                                    get_field_name=get_field_name,
                                    get_sensor_data=get_sensor_data)
    def handle_field_catch(device,field_name):
        try:
            return device['user_agent'][field_name]
        except KeyError as e:
            print(e)
            return ''
    def get_sensor_data(device_id):
        def get_s_type(v):
            return v.s_type
        def map_data(sensor_history):
            return [f'new Date({str(sensor_history.create_time.isoformat())})',sensor_history.value]
        plotdata = {'flag': False}
        data = SensorHistory.objects(device_id=str(device_id),create_time__gte=datetime.datetime.now()-datetime.timedelta(minutes=1)).order_by('create_time')
        if len(data):
            plotdata['flag'] = True
            plotdata['dataset'] = list()
            data = sorted(data,key=get_s_type)
            for key, group in groupby(data,get_s_type):
              plotdata['dataset'].append({'label':key,'data': list(map(map_data,list(group)))})
            plotdata['dataset'] = re.sub('\)\"','")',re.sub('\"new Date\(','new Date("',json.dumps(plotdata['dataset'])))
        return plotdata
    @app.route("/get_sensor_data",methods=['post'])
    def render_sensor_data():
        device_id = request.form.get('device_id')
        tmp = get_sensor_data(device_id)
        return jsonify(tmp['dataset'])
    @app.route("/client",methods=['post','get'])
    def recieve_client_data():
        if 'HTTP_X_FORWARDED_FOR' in list(request.environ.keys()):
            address = request.environ['HTTP_X_FORWARDED_FOR']
        else:
            address = request.remote_addr
        user_agent = json.loads(base64.b64decode(request.form.get('data')).decode('UTF-8'))
        ID = request.form.get('id')
        time_now = datetime.datetime.now()
        device = None
        with trail: device = DeviceList.objects(id = str(ID)).first()
        device = DeviceList() if device == None else device
        device.update_attributes(create_time = time_now,
                        update_time = time_now,
                        ip = address,
                        user_agent = user_agent)
        sensor_data = request.form.get('sensor_data')
        print(sensor_data)
        if sensor_data != None:
            sensor_data = json.loads(sensor_data)
            for ds in sensor_data:
                data = ds.get('value')
                s_type = ds.get('s_type')
                s = SensorHistory(s_type=s_type,value=data,device_id=str(device.id),create_time=time_now)
                s.save()
        device_config = request.form.get('config')
        if device_config != None and not device.config_change_flag:
            device_config = json.loads(device_config)
            device.update_attributes(config = device_config)
        if device.config_change_flag:
            device.update_attributes(config_change_flag = False)
            return {'id':str(device.id),'config_change': json.dumps(device.config)}
        else:
            return {'id':str(device.id)}
    def get_annc():
        annc_setting = AnncSetting.objects()
        if len(annc_setting) == 0:
            msg = ''
        else:
            msg = annc_setting[0]['annc_msg']
        return msg
    @app.route("/get_config",methods=['post'])
    def get_config():
        device_id = request.form.get('device_id')
        d = None
        with trail: d = DeviceList.objects(id=device_id).first()
        if d != None:
            return d.config
        else:
            return 'failed',404
    @app.route("/save_config",methods=['post'])
    def save_config():
        dict_ = request.form.to_dict(flat=True)
        print(dict_)
        device_id = dict_.get('device_id')
        d = None
        with trail: d = DeviceList.objects(id=device_id).first()
        if d != None:
            d_config = json.loads(dict_.get('config'))
            print(d_config)
            print(dict_)
            d.update_attributes(config=d_config,config_change_flag=True)
            return 'success'
        else:
            return 'failed',404
    @app.route("/annc",methods=['post','get'])
    def annc():
        device_id = request.form.get('id')
        d = None
        with trail: d = DeviceList.objects(id=device_id).first()
        if d != None and d.is_permit:
            msg = get_annc()
        else:
            msg = 'permission denied'
        return app.render_template(session,'annc.html',msg= msg)
    @app.route("/annc_setting",methods=['get'])
    def annc_setting():
        msg = get_annc()
        return app.render_template(session,'annc_setting.html',render_menu= menu(),msg= msg)
    @app.route("/annc_setting",methods=['post'])
    def annc_setting_recieve_data():
        annc_setting = AnncSetting.objects()
        if len(annc_setting) == 0:
            annc_setting = AnncSetting(annc_msg=request.form.get('annc_setting'))
            annc_setting.save()
        else:
            annc_setting[0].update(annc_msg=request.form.get('annc_setting'))
        return redirect(url_for('.annc_setting'))
    return app