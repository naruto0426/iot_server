######!!!! index.py in  /var/www/html !!!#####
from flask import Flask, request, session, redirect, url_for, Blueprint, render_template, abort
import re
#import pymongo
import time
import base64
import datetime
import json
from bson.objectid import ObjectId
app = Flask(__name__)
app.config["SECRET_KEY"] = "6osDR9dGpukOwZHaQB2t1HXN"
import os 
os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '1'
global client_id
global client_secret
client_id = '868346509131-j9a170ie67tj0cc9dcp0gv5tbseom28n.apps.googleusercontent.com'
client_secret = '6osDR9dGpukOwZHaQB2t1HXN'

from requests_oauthlib import OAuth2Session
from google.oauth2 import id_token
from google.auth.transport import requests
from models import *
# Get the authorization verifier code from the callback url
class GoogleBlueprint(Blueprint):
    def render_template(self, name, **kwargs):
        return render_template(name, **kwargs)
def main():
    def root_url():
        return 'http://demo-applejenny.dev.rulingcom.com'
    app = GoogleBlueprint('google', __name__, template_folder='../views')
    @app.route('/google_callback')
    def google_callback():
        global client_id
        global client_secret
        scope = [
             "https://www.googleapis.com/auth/userinfo.email","openid"
        ]
        token_url = "https://www.googleapis.com/oauth2/v4/token"
        redirect_uri = root_url() + '/google_callback'
        google = OAuth2Session(client_id, scope=scope, redirect_uri=redirect_uri,
                state=session['oauth_state'])
        token = google.fetch_token(token_url, client_secret=client_secret,
               authorization_response=request.url)
        id_info = id_token.verify_oauth2_token(token['id_token'],
                requests.Request(),
                client_id)
        email = id_info['email']
        session['user'] = email
        user = User.objects(user=email).first()
        if user == None:
            user = User(user=email,password=client_secret)
            user.save()
        return redirect(root_url())
    @app.route('/google')
    def google_login():
        global client_id
        global client_secret
        authorization_base_url = "https://accounts.google.com/o/oauth2/v2/auth"
        token_url = "https://www.googleapis.com/oauth2/v4/token"
        scope = [
             "https://www.googleapis.com/auth/userinfo.email","openid"
        ]
        redirect_uri = root_url() + '/google_callback'
        google = OAuth2Session(client_id, scope=scope, redirect_uri=redirect_uri)
        # Redirect user to Google for authorization
        authorization_url, state = google.authorization_url(authorization_base_url,
        # offline for refresh token
        # force to always make user click authorize
        access_type="offline", prompt="select_account")
        redirect_response = root_url() + '/google_callback'
        # Fetch the access token
        session['oauth_state'] = state
        #google.fetch_token(token_url, client_secret=client_secret,authorization_response = redirect_response)
        # Fetch a protected resource, i.e. user profile
        r = google.get('https://www.googleapis.com/auth/userinfo.email')
        print(r.content)
        return redirect(authorization_url)
    return app