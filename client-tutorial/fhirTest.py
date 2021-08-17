#  Copyright (c) 2021 IBM Corporation
#  Henry Feldman, MD (CMO Development, IBM Watson Health)

from FhirUtil import FhirConverters
from database_classes import Patient, Noteevent, LabEvent, DLabItem, Caregiver, Hospital, EKGReport, RadiologyReport
from PatientsDao import PatientsDao
from NoteEventDao import NoteEventDao
from ReportsDao import ReportsDao
from ADTDao import AdtDao
from LabDao import LabDao, DLabItemDict
from fhir.resources.patient import Patient
from fhir.resources.documentreference import DocumentReference
from fhir.resources.diagnosticreport import DiagnosticReport
from fhir.resources.practitioner import Practitioner
from fhir.resources.practitionerrole import PractitionerRole
from typing import TypedDict
import pprint
import json

class HospitalDict(TypedDict):
    id:int
    hospital:Hospital

patientDao = PatientsDao()
reportsDao = ReportsDao()
fhirUtil = FhirConverters()
patient = patientDao.getPatient('959595')
print(patientDao.getPatientSummary(patient))
print('sending to fhir converter')
fhirPatient  = fhirUtil.getPatientAsFhir(patient)
noteEventDao:NoteEventDao = NoteEventDao()
noteEvent:Noteevent = noteEventDao.getNoteEventById(1)
fhirDocumentReference = fhirUtil.getNoteEventsAsFhir(noteEvent)
labDao = LabDao()
labItems: DLabItemDict = None
labItem:DLabItem = None
labItems =  labDao.getAllDLabItems()
labEvents = labDao.getLabsForPatient(patient.SUBJECT_ID)
for labEvent in labEvents:
    labItem = labItems[labEvent.ITEMID]
adtDao = AdtDao()
careGiverDict = adtDao.getCareGiverDict()

hospitalDict:HospitalDict = HospitalDict()

for hospital in adtDao.getAllHospitals():
    hospitalDict[hospital.id] = hospital

#as a test send all the caregivers (MIMIC's name for practicioners) to be converted into FHIR
for careGiver in careGiverDict.values():
    hospital:Hospital = hospitalDict[careGiver.works_for_hospital_id]
    if (hospital and careGiver):
        practicioner:Practitioner = fhirUtil.getPracticionerWithRoleAsFhir(careGiver, hospital)
        #pprint.pprint(practicioner.json(), indent=1, depth=5, width=80)

for report in reportsDao.getRadiologyReportsForPatient(patient.SUBJECT_ID):
     radiologyReport:DiagnosticReport = fhirUtil.getRadiologyReportAsFhir(report)

for ekg in reportsDao.getAllEKGReportsForPatient(patient.SUBJECT_ID):
    ekgReport:DiagnosticReport = fhirUtil.getEKGReportAsFhir(ekg)
