#  Copyright (c) 2021 IBM Corporation
#  Henry Feldman, MD (CMO Development, IBM Watson Health)

from FhirUtil import FhirConverters
from database_classes import Patient, Noteevent, LabEvent, DLabItem, Caregiver, Hospital
from PatientsDao import PatientsDao
from NoteEventDao import NoteEventDao
from ADTDao import AdtDao
from LabDao import LabDao, DLabItemDict
from fhir.resources.patient import Patient
from fhir.resources.documentreference import DocumentReference
from typing import TypedDict

patientDao = PatientsDao()
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
    print(fhirUtil.getLabEventAsFhir(labEvent, labItem))
adtDao = AdtDao()
careGiverDict = adtDao.getCareGiverDict()
for id in careGiverDict.keys():
    if careGiverDict[id].NPI_number != None and careGiverDict[id].NPI_number:
        print(fhirUtil.getCareGiverAsFhir(careGiverDict[id]))

for hospital in adtDao.getAllHospitals():
    print(hospital)
