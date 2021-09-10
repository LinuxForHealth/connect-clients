#  Copyright (c) 2021 IBM Corporation
#  Henry Feldman, MD (CMO Development, IBM Watson Health)
from datetime import datetime
import os

from flask import Flask, session, request, url_for, flash, send_from_directory, jsonify, render_template_string, render_template
from flask_sqlalchemy import SQLAlchemy
import click
from flask_wtf.csrf import CSRFProtect
from flask_session import Session
from ..InsuranceDao import InsuranceDao
from typing import List
from ..database_classes import Patient, Payer
from ..PatientsDao import PatientsDao
from typing import TypedDict, List

csrf_protect = CSRFProtect()

insuranceDao:InsuranceDao = InsuranceDao()

payerDict = insuranceDao.fetchPayerDict()


app = Flask(__name__)
patientDao: PatientsDao = PatientsDao()

# Setup session
Session(app)

payerList: List[Payer] = insuranceDao.getAllPayers()

# Setup WTForms CSRFProtect
csrf_protect.init_app(app)

# Define bootstrap_is_hidden_field for flask-bootstrap's bootstrap_wtf.html
from wtforms.fields import HiddenField


def is_hidden_field_filter(field):
    return isinstance(field, HiddenField)


app.jinja_env.globals['bootstrap_is_hidden_field'] = is_hidden_field_filter



@app.route('/payer_select', methods=['GET', 'POST'])
@click.argument("payerSelect")
def selectPayer(payerId:int):
    global payerDict
    if request.method == 'POST':
        payer = payerDict[payerId]
        memberList = patientDao.getPatientForPayer(payerId)
    return render_template('view_requests.html',
                           payer=payer, memberList=memberList)

# The User page is accessible to authenticated users (users that have logged in)
@app.route('/payer', methods=['GET'])
def payer_list():
    global payerDict
    payerNames = []
    for payer in payerDict.values():
        payerNames.append(payer.Name)
    return render_template('payer_base.html', payerNames = payerNames)

@app.route("/")
def hello_world():
    return "<p>Hello, World!</p>"

@app.route('/patients')
def hello():
    patient = patientDao.getPatient(959595)
    return patient.__str__()
