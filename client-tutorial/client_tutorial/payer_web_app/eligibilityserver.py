#  Copyright (c) 2021 IBM Corporation
#  Henry Feldman, MD (CMO Development, IBM Watson Health)
from datetime import datetime
import os

from flask import Flask, redirect, session, request, url_for, flash, send_from_directory, jsonify, render_template_string, render_template
from flask_sqlalchemy import SQLAlchemy
import click
from flask_wtf.csrf import CSRFProtect
from flask_session import Session
from ..InsuranceDao import InsuranceDao
from typing import List
from ..database_classes import Patient, Payer, PatientCoverage
from ..PatientsDao import PatientsDao
from typing import TypedDict, List
import uuid
import secrets
import logging


logging.basicConfig(filename='flask_app.log', level=logging.DEBUG, format=f'%(asctime)s %(levelname)s %(name)s %(threadName)s : %(message)s')

csrf_protect = CSRFProtect()

insuranceDao:InsuranceDao = InsuranceDao()

payerDict = insuranceDao.fetchPayerDict()
payerNameDict = {}

secret_key = secrets.token_urlsafe(16)

app = Flask(__name__)
patientDao: PatientsDao = PatientsDao()
print(secret_key)
# app.config['SECRET_KEY'] = secret_key
app.config['WTF_CSRF_ENABLED'] = False

# Setup session
sess = Session(app)
sess.init_app(app)

payerList: List[Payer] = insuranceDao.getAllPayers()

for payer in payerList:
    payerNameDict[payer.Name] = payer

# Define bootstrap_is_hidden_field for flask-bootstrap's bootstrap_wtf.html
from wtforms.fields import HiddenField


def is_hidden_field_filter(field):
    return isinstance(field, HiddenField)


app.jinja_env.globals['bootstrap_is_hidden_field'] = is_hidden_field_filter



@app.route('/requests', methods=['GET'])
@click.argument("requests")
def selectPayer():
    global payerDict
    if request.method == 'GET':
        payerName = request.args.get("payerselect")
        app.logger.debug(payerName)
        print("PAYER NAME: "+ payerName)
        payer = payerNameDict[payerName]
        # make a dict by patient ID for every patient so we can map patients to coverage
        patientDict = {}
        for patient in patientDao.getPatientForPayer(payer.id):
            patientDict[patient.ROW_ID] = patient

        #now make a list of patient coverage and patient tuples
        patientCoverageTupleList = []
        for coverage in insuranceDao.getAllPatientCoverageForPayerId(payer.id):
            patientCoverageTupleList.append((patientDict[coverage.patient_id],coverage))

        payerAddress:str = payer.street+'<br>'+payer.city+", "+payer.state+" "+payer.zip
        return render_template('view_requests.html',
                               payer=payer, patientCoverageTupleList = patientCoverageTupleList, currentPayerName=payer.Name, currentPayerAddress=payerAddress)


# The User page is accessible to authenticated users (users that have logged in)
@app.route('/payer', methods=['GET'])
def payer_list():
    global payerDict
    payerNames = []
    for payer in payerDict.values():
        payerNames.append(payer.Name)
    return render_template('payer_base.html', payerNames = payerNames)

@app.route('/coveragedetail', methods=['GET'])
def coverageDetail():
    global payerDict
    coverageId:int = request.args.get("coverageId")
    coverage: PatientCoverage = insuranceDao.getPatientCoverage(coverageId)
    patient = patientDao.getPatientByRowId(coverage.patient_id)
    payer = coverage.payer
    return render_template('coverage_detail.html', coverage=coverage, patient=patient, payer=payer)


@app.route("/")
def default():
    return redirect('/payer')

@app.route('/patients')
def hello():
    patient = patientDao.getPatient(959595)
    return patient.__str__()
