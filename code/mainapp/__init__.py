import paypalrestsdk
from flask import Flask,session
from flask_admin import Admin
from flask_login import LoginManager
from flask_sqlalchemy import SQLAlchemy
# from flask_mail import Mail, Message

import os
# settings.py
#from dotenv import load_dotenv
#load_dotenv()


app = Flask(__name__)
# mail = Mail(app=app)
app.secret_key = os.urandom(24)
    # app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://'+ str(os.environ.get('DATABASE_USERNAME')) +':'+ str(os.environ.get('DATABASE_PASSWORD')) + '@localhost/login?charset=utf8mb4'
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:0898654463@localhost/quanlyhocsinh?charset=utf8mb4'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True
app.config['JSON_AS_ASCII'] = False

db =SQLAlchemy(app=app)

admin = Admin(app=app, name='QUAN LY HOC SINH', template_mode='bootstrap3')
login_manager = LoginManager(app=app)

login_manager.init_app(app)


paypalrestsdk.configure({
  "mode": "sandbox", # sandbox or live
  "client_id": "AdpFE5uzDjkw12pjMNkYIUxvlr1sVYntW2o5jrqxABbHxW-7tcUvl7Otd0KVOEsL_RV8sfDgQlqPn1_z",
  "client_secret": "EJ3XBSzYJH7Zs28pQGkHv_PlqJhxC2xZ_c2hbGgAk09vPV0m7luYrbz7nMCnDIVawKY3I5tADjeb5kAG" })



