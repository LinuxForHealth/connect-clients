from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy import app
from PatientsDao import PatientsDao
from database_classes import Patient, Noteevent, Admission, DRGCode, DIcdDiagnoses, DiagnosisIcd
from MedicationDao import MedicationDao
from NoteEventDao import NoteEventDao
from LabDao import LabDao
from InsuranceDao import InsuranceDao, InsuranceCompanyDict
from ADTDao import AdtDao
from httpx import AsyncClient
import asyncio
from kivy.app import App
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from datetime import datetime
from DateUtil import calculate_age
from billing import billing
from config import get_settings


# subjectId 48632
# SELECT * FROM `noteevents` WHERE MATCH(TEXT) against ('post-obstructive pneumonia', in natural language mode);

from kivy.uix.widget import Widget
from kivy.properties import (
    NumericProperty, ReferenceListProperty, ObjectProperty
)
from kivy.vector import Vector
from kivy.clock import Clock

settings = get_settings()

fhir_r4_externalserver_patient = 'https://localhost:5000/fhir/Patient'

fhir_r4_externalserver_notes = 'https://localhost:5000/fhir/DocumentReference'

fhir_r4_externalserver_medication = 'https://localhost:5000/fhir/MedicationRequest'

fhir_r4_externalserver_lab = 'https://localhost:5000/fhir/Observation'

fhir_r4_externalserver_Radiology = 'https://localhost:5000/fhir/DiagnosticReport'

patientSubjectId = settings.tutorial_subject_id

globalPatient = None

globalNoteEvent = None

LfhTutorialApp = None

mrnField = TextInput(multiline=False, text=str(patientSubjectId), cursor_blink=True, font_size=36)

boxLayout = None
'''
This is the primary entry point for the Linux For Health demo. It will launch as a separate GUI Kivy application. 
You must configure the database connection in databaseUtil.py along. The database code assumes the database is 
MySql 8+, but should support any database that the SqlAlchemy ORM supports.
'''

# send the patient resource
async def send_fhir_to_connect(json, fhirserverurl):
    """
    Sends the json payload to the Fhir Server URL (which must contain the resource type as in https://localhost:5000/fhir/MedicationRequest).
    Note the destination is almost always localhost (where the connect service is running not necessarily the fhir server itself
    :param json: (this is the fhir content)
    :type json: 
    :param fhirserverurl: (the URL as in the above text)
    :type fhirserverurl: 
    :return: 
    :rtype: 
    """
    try:
        async with AsyncClient(verify=False) as client:
            result = await client.post(fhirserverurl, json=json)
            print(f"Header: {result.text}")
    except:
        raise


async def TransmitPatient(patient:Patient):
    """
    Fetches the FHIR resource for a given patient using their subject ID (Medical record number) which for the demo has premade fhir json in the database.
    This function is asynchronous and will call the
    :param subjectId: 
    :type subjectId: 
    :return: 
    :rtype: 
    """
    await send_fhir_to_connect(patient.fhir_json, fhir_r4_externalserver_patient)


async def transmitNotesForPatient(noteEvent:Noteevent):
    """
    fetches the clinical notes for the patient by pulling the source material from the database and constucting a note for this
    patient. Then adds the structured fields as extensions to the FHIR resource. it then calls connect to send them to the FHIR
    server via connect
    :param subjectId:
    :type subjectId:
    :return:
    :rtype:
    """
    await send_fhir_to_connect(noteEvent.fhir_json, fhir_r4_externalserver_notes)


async def trransmitMedicationsForPatient(subjectId):
    """
    fetches the medication orders for the patient by pulling the source material from the database creating MedicationRequests from each record.
    Then adds the structured fields as extensions to the FHIR resource. it then calls connect to send them to the FHIR
    server via connect
    :param subjectId:
    :type subjectId:
    :return:
    :rtype:
    """
    medicationDao = MedicationDao()
    for prescription in medicationDao.getPrescriptionsForPatient(subjectId):
        print(prescription.fhir_json)
        await send_fhir_to_connect(prescription.fhir_json, fhir_r4_externalserver_medication)


async def tansmitLabsForPatient(subjectId):
    """
    fetches the lab results for the patient by pulling the lab events from the database creating Observations from each record.
    Then adds the structured fields as extensions to the FHIR resource. it then calls connect to send them to the FHIR
    server via connect
    :param subjectId:
    :type subjectId:
    :return:
    :rtype:
    """
    labDao = LabDao()
    for lab in labDao.getLabsForPatient(subjectId):
        await send_fhir_to_connect(lab.fhir_json, fhir_r4_externalserver_lab)


class PatientSearchScreen(BoxLayout):
    """
    This creates the start screen for the Kivy application (as a box layout with vertical orientation) It then lays out the buttons/fields and binds the callback
    for the button to handle the click of the search button.
    """
    def __init__(self, **kwargs):
        global boxLayout
        global mrnField
        super(PatientSearchScreen, self).__init__(**kwargs)
        boxLayout = self
        self.orientation='vertical'
        self.cols = 1
        boxLayout.add_widget(Label(text='Patient MRN', font_size=36))
        boxLayout.add_widget(mrnField)
        self.searchButton = Button(text="Search for Patient")
        self.searchButton.bind(on_press=self.patientCallBack)
        boxLayout.add_widget(self.searchButton)

    def patientCallBack(self, event):
        """
        Click Handler for the patient search button from PatientSearchScreen=.SearchButton,, and delegates to handleSearchResult to perform
        the actual selection of the patient
        :param event:
        :type event:
        :return:
        :rtype:
        """
        global patientSubjectId
        global globalPatient
        global mrnField
        global boxLayout
        patientSubjectId = mrnField.text
        boxLayout.clear_widgets()
        insuranceDao = InsuranceDao()
        insuranceDict = insuranceDao.getPayerDict()
        patientsDao = PatientsDao()
        globalPatient = patientsDao.getPatient(patientSubjectId)
        self.resultLabel = Label(text='%s, %s\nMRN: %d\nInsurance: %s (%s)\nDOB: %s (%d)\n\n%s\n%s, %s %s' % (
        globalPatient.last_name, globalPatient.first_name, globalPatient.SUBJECT_ID, insuranceDict[globalPatient.insurance].Name, insuranceDict[globalPatient.insurance].plan_type, globalPatient.DOB.strftime("%m/%d/%Y"), calculate_age(globalPatient.DOB), globalPatient.street, globalPatient.city, globalPatient.state, globalPatient.zip))
        boxLayout.add_widget(self.resultLabel)
        self.writeNoteButton = Button(text="Write Clinical Note For Patient")
        boxLayout.add_widget(self.writeNoteButton)
        self.writeNoteButton.bind(on_press=self.createNoteCallback)

    def handleSearchResult(self):
        """
        Pulls the additional data around the patient, such as their military info and shows their military info (unit, etc)
        on screen
        :return:
        :rtype:
        """
        global boxLayout
        global patientSubjectId
        global globalPatient
        patientsDao = PatientsDao()
        insuranceDao = InsuranceDao()
        insuranceDict = insuranceDao.getPayerDict()
        globalPatient = patientsDao.getPatient(patientSubjectId)
        self.resultLabel = Label(text='%s, %s\nMRN: %d\nInsurance: %s' % (globalPatient.last_name, globalPatient.first_name, globalPatient.SUBJECT_ID, insuranceDict[globalPatient.insurance].Name))
        boxLayout.add_widget(self.resultLabel)
        self.writeNoteButton =  Button(text="Write Clinical Note For Patient")
        boxLayout.add_widget(self.writeNoteButton)
        self.writeNoteButton.bind(on_press=self.createNoteCallback)

    def createNoteCallback(self, instance):
        """
        Call Back to handle the handleSearchResult.writeNoteButton click. It goes ahead and tees up the ability to gennerate
        the patient note (DocumentReference) by assembling all the relevant data
        :param instance:
        :type instance:
        :return:
        :rtype:
        """
        global patientSubjectId
        global mrnField
        global boxLayout
        boxLayout.clear_widgets()
        print("button pressed to create Note")
        patientSubjectId = mrnField.text
        boxLayout.clear_widgets()
        self.handleNoteCreation()

    def sendToFhirCallback(self, instance):
        """
        this is the click handler callback for the handleTccccCreation.sendFhirButton which will then send off all the
        content generated in the above as FHIR resources to the FHIR server via synch network queuing.
        :param instance:
        :type instance:
        :return:
        :rtype:
        """
        global boxLayout
        global globalPatient
        global patientSubjectId
        global globalNoteEvent
        boxLayout.clear_widgets()
        boxLayout.add_widget(Label(text='Sending to FHIR via LFH', font_size=36))

        boxLayout.add_widget(Label(text='Sent FHIR Patient'))
        asyncio.run(TransmitPatient(globalPatient))

        boxLayout.add_widget(Label(text='Sent Note DocumentReference'))
        asyncio.run(transmitNotesForPatient(globalNoteEvent))

        boxLayout.add_widget(Label(text='Sent MedicationRequests'))
        asyncio.run(trransmitMedicationsForPatient(patientSubjectId))

        boxLayout.add_widget(Label(text='Sent Observations'))
        asyncio.run(tansmitLabsForPatient(patientSubjectId))

        self.quitButton = Button(text='Quit Tutorrial')
        self.quitButton.bind(on_press=self.exitCallback)
        boxLayout.add_widget(self.quitButton)
        print('records sent to FHIR')

    def exitCallback(self, instance):
        global LfhTutorialApp
        App.get_running_app().stop()

    def handleNoteCreation(self):
        """
        This is the screen at the end where we display the clinical note content (or a small portion of it - the first
        512 characters as it is too large for the screen)
        :return:
        :rtype:
        """
        global boxLayout
        global patientSubjectId
        global globalPatient
        global globalNoteEvent
        noteEventDao = NoteEventDao()
        globalNoteEvent = noteEventDao.getAllNotesForPatient(globalPatient.SUBJECT_ID)[0]
        # we crop the text because this note is very long. Note we delibertaely take the fist note as this is just a demo
        self.noteTextLabel = Label(text=globalNoteEvent.TEXT[0:1024],font_size=18)
        boxLayout.add_widget(self.noteTextLabel)
        self.fetchRadiologyButton = Button(text="Fetch Radiology reports for patient")
        self.fetchRadiologyButton.bind(on_press=self.radiologyReportsCallback)
        boxLayout.add_widget(self.fetchRadiologyButton)

    def radiologyReportsCallback(self, instance):
        """
        Pulls the radiology reports and gets them ready for sending to the FHIR server
        :return:
        :rtype:
        """
        global boxLayout
        global patientSubjectId
        global globalPatient
        boxLayout.clear_widgets()
        noteEventDao = NoteEventDao()
        biller = billing()
        sb = ['RADIOLOGY REPORTS:\n\n']
        # pack all the radiology study info together
        for radiologyReport in noteEventDao.getAllRadiologyReportsForPatient(globalPatient.SUBJECT_ID):
            sb.append(radiologyReport.CATEGORY+":\n"+radiologyReport.Impression+'\n')
        reports =''
        self.reportsLabel = Label(text=reports.join(sb), font_size=24)
        boxLayout.add_widget(self.reportsLabel)
        self.fetchRadiologyButton =  Button(text="Send Note, Radiology, Labs, Patient, and records To Fhir via LFH")
        self.fetchRadiologyButton.bind(on_press=self.sendToFhirCallback)
        # at this step we are creating demo billing
        biller.createHospitalBilling()
        boxLayout.add_widget(self.fetchRadiologyButton)


class LfhTutorialApp(App):
    """
    builds and shows the Kivy application (and instantiates the PatientSearchScreen
    """

    def build(self):
        return PatientSearchScreen()

# calls the Kivy app runner to build and deploy
if __name__ == '__main__':
    LfhTutorialApp().run()
