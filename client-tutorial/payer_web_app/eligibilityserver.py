#  Copyright (c) 2021 IBM Corporation
#  Henry Feldman, MD (CMO Development, IBM Watson Health)
from flask import Flask
from ..PatientsDao import PatientsDao
from ..database_classes import Patient

app = Flask(__name__)
patientDao: PatientsDao = PatientsDao()

@app.route("/")
def hello_world():
    return "<p>Hello, World!</p>"

@app.route('/patients')
def hello():
    patient = patientDao.getPatient(959595)
    return patient.__str__()
