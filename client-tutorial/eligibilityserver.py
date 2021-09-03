#  Copyright (c) 2021 IBM Corporation
#  Henry Feldman, MD (CMO Development, IBM Watson Health)
from datetime import datetime
import os

from flask import Flask, session, Blueprint, request, url_for, flash, send_from_directory, jsonify, render_template_string, render_template
from flask_sqlalchemy import SQLAlchemy
import click
from flask_wtf.csrf import CSRFProtect
from flask_session import Session
from InsuranceDao import InsuranceDao
from typing import List
from database_classes import Patient, Payer
from PatientsDao import PatientsDao

csrf_protect = CSRFProtect()

insuranceDao = InsuranceDao()

app = Flask(__name__)
patientDao: PatientsDao = PatientsDao()

# Setup session
Session(app)

payerList: List[Payer] = insuranceDao.getAllPayers()

# Setup WTForms CSRFProtect
csrf_protect.init_app(app)

# Register blueprints
main_payer_blueprint = Blueprint('payer', __name__, template_folder='/payer_web_app/templates/views')

app.register_blueprint(main_payer_blueprint)

# Define bootstrap_is_hidden_field for flask-bootstrap's bootstrap_wtf.html
from wtforms.fields import HiddenField


def is_hidden_field_filter(field):
    return isinstance(field, HiddenField)


app.jinja_env.globals['bootstrap_is_hidden_field'] = is_hidden_field_filter


# The User page is accessible to authenticated users (users that have logged in)
@main_payer_blueprint.route('/payer')
def payer_list():
    return render_template('/payer_web_app/templates/views/payer_base.html')


@main_payer_blueprint.route('/payer/select', methods=['GET', 'POST'])
@click.argument("payer_id")
def selectPayer():
    if request.method == 'POST':
        payerId = request.form['payer_id']
        payer = insuranceDao.getPayer(payerId)
        print(payer)
    return render_template('/payer_web_app/templates/views/view_requests.html',
                           payer=payer)

@app.route("/")
def hello_world():
    return "<p>Hello, World!</p>"

@app.route('/patients')
def hello():
    patient = patientDao.getPatient(959595)
    return patient.__str__()
