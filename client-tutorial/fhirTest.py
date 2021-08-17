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

class HospitalDict(TypedDict):
    id:int
    hospital:Hospital

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

hospitalDict:HospitalDict = HospitalDict()

for hospital in adtDao.getAllHospitals():
    hospitalDict[hospital.id] = hospital

for careGiver in careGiverDict.values():
    # tmporary block on null NPIs but will accomodate other roles shortly with the PracticionerRole
    if careGiver.NPI_number != None and careGiver.NPI_number:
        hospital:Hospital = hospitalDict[careGiver.works_for_hospital_id]
        print(hospital)
        print(careGiver)
        if (hospital and careGiver):
            print(fhirUtil.getPracticionerRoleAsFhir(careGiver, hospital))

print(fhirUtil.getPracticionerRoleAsFhir())
