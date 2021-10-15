#  Copyright (c) 2021 IBM Corporation
#  Henry Feldman, MD (CMO Development, IBM Watson Health)

import logging
import secrets
from logging.config import dictConfig
from typing import List

import click
import urllib.parse
from flask import Flask, redirect, request, abort, render_template, jsonify
from flask_session import Session
from flask_wtf.csrf import CSRFProtect

from ..nlp_analyzer import Nlp_Analyzer
from ..nlp_setup import setup

from LabDao import LabDao
from ..InsuranceDao import InsuranceDao
from ..PatientsDao import PatientsDao
from ..NoteEventDao import NoteEventDao
from ..database_classes import Payer, PatientCoverage, DLabItem, LabEvent, ProblemListItem, Noteevent


logging.basicConfig(filename='flask_app.log', level=logging.DEBUG, format=f'%(asctime)s %(levelname)s %(name)s %(threadName)s : %(message)s')

csrf_protect = CSRFProtect()

insuranceDao:InsuranceDao = InsuranceDao()
labDao:LabDao = LabDao()
analyzer:Nlp_Analyzer = Nlp_Analyzer()
nlp_setup:setup = setup()

payerDict = insuranceDao.fetchPayerDict()
payerNameDict = {}

secret_key = secrets.token_urlsafe(16)

#configure logging for the app
dictConfig({
    'version': 1,
    'formatters': {'default': {
        'format': '[%(asctime)s] %(levelname)s in %(module)s: %(message)s',
    }},
    'handlers': {'wsgi': {
        'class': 'logging.StreamHandler',
        'stream': 'ext://flask.logging.wsgi_errors_stream',
        'formatter': 'default'
    }},
    'root': {
        'level': 'INFO',
        'handlers': ['wsgi']
    }
})

app = Flask(__name__)
patientDao: PatientsDao = PatientsDao()
noteEventDao:NoteEventDao = NoteEventDao()
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

@app.errorhandler(404)
def resource_not_found(e):
    return jsonify(error=str(e)), 404

@app.route('/requests', methods=['GET'])
@click.argument("requests")
def selectPayer():
    global payerDict
    if request.method == 'GET':
        if request.args.get('payerselect') == None:
            abort(404, description="payerselect cannot be null: "+request.args.get('payerselect'))
        payerName = request.args.get("payerselect")
        app.logger.info('payer name for respond - ' + request.args.get("payerselect"))
        payer = payerNameDict[payerName]
        # make a dict by patient ID for every patient so we can map patients to coverage
        patientDict = {}
        for patient in patientDao.getPatientForPayer(payer.id):
            patientDict[patient.ROW_ID] = patient
        requestDict = {}
        # make a dict of the pending requests for each member for the payer so we can show next to the member detail link as a badge
        for eligibilityRequest in insuranceDao.getAllActiveEligibitilityRequestsForPayer(payer.id):
            if eligibilityRequest.member_id not in requestDict:
                requestDict[eligibilityRequest.member_id] = []
            requestDict[eligibilityRequest.member_id].append(eligibilityRequest)
        #now make a list of patient coverage and patient tuples
        patientCoverageTupleList = []
        for coverage in insuranceDao.getAllPatientCoverageForPayerId(payer.id):
            patientCoverageTupleList.append((patientDict[coverage.patient_id],coverage))

        payerAddress:str = payer.street+'<br>'+payer.city+", "+payer.state+" "+payer.zip
        return render_template('view_requests.html',
                               payer=payer, patientCoverageTupleList = patientCoverageTupleList, requestDict=requestDict, currentPayerName=payer.Name, currentPayerAddress=payerAddress)

@app.route('/respond', methods=['POST'])
@click.argument("respond")
def repondToRequest():
    request_id = request.form['requestId']
    if request_id:
        eligibilityRequest = insuranceDao.getEligibilityRequest(request_id)
        if request.form.get('approved_check'):
            eligibilityRequest.processed=True
        else:
            eligibilityRequest.processed=False
        for key in request.form.keys():
            app.logger.info("form key=" + key + "form value=" + request.form.get(key))
        insuranceDao.saveEligibilityRequest(eligibilityRequest)
        payerName = request.form.get("payer_name")
        app.logger.info('payer name for respond - ' + request.form.get("payer_name"))
        return redirect('/requests?payerselect='+payerName)
    else:
        abort(404, description="either invalid payer or invalid eligibility request")


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
    memberEligibilityRequestDict = {}
    eligibilityRequests = insuranceDao.getAllActiveEligibitilityRequestsForPayer(coverage.payer_id)
    memberEligibilityRequestDict = {}
    benefitMatchIds = []
    #now figure out if our extra search match the other benefits in the coverage of the patient. Obviously the member_id has to match or there is no point checking.
    for eligibilityRequest in eligibilityRequests:
        memberEligibilityRequestDict[eligibilityRequest.member_id]=eligibilityRequest
        benefit_1:str = None
        benefit_2:str = None
        benefit_3:str = None
        match_approve:bool = False
        for benefit in coverage.coveragePlanData:
            if eligibilityRequest.coverage_option_1 and benefit.name and eligibilityRequest.coverage_option_1 in benefit.name:
                benefit_1 = benefit.name + " matched benefit 1"
                matched = True
                if benefit.id not in benefitMatchIds:
                    benefitMatchIds.append(benefit.id)
            if eligibilityRequest.coverage_option_2 and benefit.name and eligibilityRequest.coverage_option_2 in benefit.name:
                benefit_2 = benefit.name + " matched benefit 2"
                matched = True
                if benefit.id not in benefitMatchIds:
                    benefitMatchIds.append(benefit.id)
            if benefit.name and eligibilityRequest.coverage_option_3 and eligibilityRequest.coverage_option_3 in benefit.name:
                matched = True
                benefit_3 = benefit.name + " matched benefit 3"
                if benefit.id not in benefitMatchIds:
                    benefitMatchIds.append(benefit.id)
            if eligibilityRequest.coverage_option_1 and benefit.name and eligibilityRequest.coverage_option_1 in benefit.name:
                matched = True
                benefit_1 = benefit.name + " matched benefit 1"
                if benefit.id not in benefitMatchIds:
                    benefitMatchIds.append(benefit.id)
            if eligibilityRequest.coverage_option_2 and benefit.name and eligibilityRequest.coverage_option_2 in benefit.name:
                matched = True
                benefit_2 = benefit.name + " matched benefit 2"
                if benefit.id not in benefitMatchIds:
                    benefitMatchIds.append(benefit.id)
            if benefit.name and eligibilityRequest.coverage_option_3 and eligibilityRequest.coverage_option_3 in benefit.name:
                matched = True
                benefit_3 = benefit.name + " matched benefit 3"
                if benefit.id not in benefitMatchIds:
                    benefitMatchIds.append(benefit.id)
                # repeat for value after doing name
            if eligibilityRequest.coverage_option_1 and benefit.value and eligibilityRequest.coverage_option_1 in benefit.value:
                matched = True
                benefit_1 = benefit.value + " matched benefit 1"
                if benefit.id not in benefitMatchIds:
                    benefitMatchIds.append(benefit.id)
            if eligibilityRequest.coverage_option_2 and benefit.value and eligibilityRequest.coverage_option_2 in benefit.value:
                matched = True
                benefit_2 = benefit.name + " matched benefit 2"
                if benefit.id not in benefitMatchIds:
                    benefitMatchIds.append(benefit.id)
            if benefit.name and eligibilityRequest.coverage_option_3 and eligibilityRequest.coverage_option_3 in benefit.value:
                matched = True
                benefit_3 = benefit.value + " matched benefit 3"
                if benefit.id not in benefitMatchIds:
                    benefitMatchIds.append(benefit.id)
            if eligibilityRequest.coverage_option_1 and benefit.value and eligibilityRequest.coverage_option_1 in benefit.value:
                matched = True
                benefit_1 = benefit.value + " matched benefit 1"
                if benefit.id not in benefitMatchIds:
                    benefitMatchIds.append(benefit.id)
            if eligibilityRequest.coverage_option_2 and benefit.value and eligibilityRequest.coverage_option_2 in benefit.value:
                matched = True
                benefit_2 = benefit.value + " matched benefit 2"
                if benefit.id not in benefitMatchIds:
                    benefitMatchIds.append(benefit.id)
            if benefit.name and eligibilityRequest.coverage_option_3 and eligibilityRequest.coverage_option_3 in benefit.value:
                matched = True
                benefit_3 = benefit.value + " matched benefit 3"
                if benefit.id not in benefitMatchIds:
                    benefitMatchIds.append(benefit.id)

            match_approve = True

    # get all the historical eligilibility requests to show as badge
    requestList = []
    requestListSize = 0
    if eligibilityRequest.patient_id in memberEligibilityRequestDict:
        requestList =  memberEligibilityRequestDict[eligibilityRequest.patient_id]
        requestListSize = len(requestList)
    requestDate = eligibilityRequest.request_date.strftime("%m/%d/%Y")
    eligibilityRequestList = insuranceDao.getAllEligiilityRequestsForPatientForPayer(eligibilityRequest.patient_id, eligibilityRequest.payer_id)

    fullLabInfo = []
    dLabItemList:List[str] = []
    for lab in labDao.getLabsForPatient(patient.SUBJECT_ID):
        if lab.labItem.LABEL not in dLabItemList:
            dLabItemList.append(lab.labItem.LABEL)
            labTuple = (lab.labItem.ROW_ID, lab.labItem.LABEL)
            fullLabInfo.append(labTuple)

    problemList:List[ProblemListItem] = getProblemsFromNotes(patient.SUBJECT_ID)

    return render_template('coverage_detail.html', coverage=coverage, patient=patient, payer=payer, requestDate=requestDate, eligibilityRequest=eligibilityRequest, requestList=requestList, requestListSize=requestListSize, benefit_1=benefit_1, benefit_2=benefit_2, benefit_3=benefit_3, match_approve=match_approve, benefitMatchIds=benefitMatchIds, fullLabInfo=fullLabInfo, problemList=problemList)

#94196

def getProblemsFromNotes(self, subejctId:int)->List[ProblemListItem]:
    """
    gets the list of problems via ACD in the patient's notes (for prior auth/or other claims processing)
    @param self:
    @type self:
    @param subejctId: the patient's subject_id
    @type subejctId: int
    @return: the list of found active problems in the notes
    @rtype: List[ProblemListItem]
    """
    problemsList:List[ProblemListItem] = []
    service = nlp_setup.setup()
    for noteEvent in noteEventDao.getAllNotesForPatient(subejctId):
        problemsList.extend(analyzer.getProblemListItemsFromNoteText(noteEvent.TEXT))
    return problemsList

@app.route("/")
def default():
    return redirect('/payer')

@app.route('/patients')
def hello():
    patient = patientDao.getPatient(959595)
    return patient.__str__()

@app.route('/labnames', methods=['GET'])
def getLabNames():
    labItems:List[DLabItem] = labDao.searchDLabItems(request.args.get('labnamesearch'))

@app.route('/graph', methods=['GET'])
def grapher():
    subjectId = request.args.get('subjectId')
    subjectId = 397
    coverageId = request.args.get('coverageId')
    labItemId = request.args.get('labnamesearch')
    labItemId = 50983
    labsForPatient =  labDao.getSpecificLabForPatient(subjectId, labItemId)

    logging.info('searching for lab: '+ str(labItemId) +' for patient '+str(subjectId))
    #dbpatient.DOB.strftime("%Y-%m-%d")
    labels:List[str] = []
    values = []
    for labs in labsForPatient:
        labels.append(labs.CHARTTIME.strftime("%Y-%m-%d"))
        values.append(labs.VALUE)
        logging.info("Lab "+ labs.CHARTTIME.strftime("%Y-%m-%d"))
    legend = None
    title = None

    if labsForPatient:
        legend = labsForPatient[0].VALUEUOM
        title = labsForPatient[0].labItem.LABEL + ': '+labsForPatient[0].labItem.FLUID
    else:
        legend = "No Labs Found"
        title = "unknown lab selected"
    #    return render_template('coverage_detail.html', coverage=coverage, patient=patient, payer=payer, requestDate=requestDate, eligibilityRequest=eligibilityRequest, requestList=requestList, requestListSize=requestListSize, benefit_1=benefit_1, benefit_2=benefit_2, benefit_3=benefit_3, match_approve=match_approve, benefitMatchIds=benefitMatchIds, fullLabInfo=fullLabInfo)

    #logging.info('got '+str(len(labsForPatient))+ ' labs for patient '+subjectId)
    return render_template('labgraph.html', legend=legend, values=values, labels=labels, coverageId=coverageId, title=title)
