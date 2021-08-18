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

class PracticionerDict(TypedDict):
    in:int
    practictioner:Practitioner

# Set up all the dabatase access classes
patientDao = PatientsDao()
reportsDao = ReportsDao()
labDao = LabDao()
adtDao = AdtDao()

# Set up the fhir conversion utility (in FhirUtil.py)
fhirUtil = FhirConverters()

#get our patient entity from the database - we only have the one patients
patient = patientDao.getPatient('959595')
print(patientDao.getPatientSummary(patient))
# print the patient info to the screnn
print('sending to fhir converter')
fhirPatient  = fhirUtil.getPatientAsFhir(patient)
#now we have the Patient resource (we're going to ignore it here)
# pprint.pprint(fhirPatient.json(), indent=1, depth=5, width=80)

# now get this patient's notes (uncomment the pprint statement to see the contents)
noteEventDao:NoteEventDao = NoteEventDao()
noteEvent:Noteevent = noteEventDao.getNoteEventById(1)
fhirDocumentReference = fhirUtil.getNoteEventsAsFhir(noteEvent)
# pprint.pprint(fhirDocumentReference.json(), indent=1, depth=5, width=80)

#Make a dictionary of the lab definitions compared to the item codes in the LabEvent entity
labItems: DLabItemDict = None
labItem:DLabItem = None
#make the caregiver dict for later
practicionerDict:PracticionerDict = PracticionerDict()

# get all the labs from the database
labItems =  labDao.getAllDLabItems()
#that query returns the dictionary from the database
for labEvent in labDao.getLabsForPatient(patient.SUBJECT_ID):
    # iterate over each lab event for this patient (severral hundred) and then convert them into FHIR resources. In this
    # case they just fall on the floor but you could do something useful here (like transmit them somewhere)
    labItem = labItems[labEvent.ITEMID]
    labFhir = fhirUtil.getLabEventAsFhir(labEvent, labItem)
    # pprint.pprint(labFhir.json(), indent=1, depth=5, width=80)

# now let's create the Practicioners (called aregivers in the original MIMIC III) as fhir resources
careGiverDict = adtDao.getCareGiverDict()
#we're going to make a practicioner dict for later in the diagnostic reports
# make a dict to hold all the hospitals, but let's do it right (and feel free to make more) (well there is only 1)
hospitalDict:HospitalDict = HospitalDict()
# get all the hospitals and stick them (it) into the dict by the id
for hospital in adtDao.getAllHospitals():
    hospitalDict[hospital.id] = hospital

# as a test send all the caregivers (MIMIC's name for practicioners) to be converted into FHIR
for careGiver in careGiverDict.values():
    # Now it is important to understand what this method is doing, which is creating 2 FHIR resources (Practicioner and a
    # PracticionerRole) but rather than return them as a tuple fhir allows a "contained" resource where you can store a
    # related item directly in the resource. This Makes it easy to keep them together.
    hospital:Hospital = hospitalDict[careGiver.works_for_hospital_id]
    if (hospital and careGiver):
        practicioner:Practitioner = fhirUtil.getPracticionerWithRoleAsFhir(careGiver, hospital)
        #pprint.pprint(practicioner.json(), indent=1, depth=5, width=80)
        practicionerDict[careGiver.CGID] = practicioner
        # pprint.pprint(radiologyReport.json(), indent=1, depth=5, width=80)


#now let's do radiology reports
for report in reportsDao.getRadiologyReportsForPatient(patient.SUBJECT_ID):
     radiologyReport:DiagnosticReport = fhirUtil.getRadiologyReportAsFhir(report)
    # Put the practicioner as a contained resource
    radiologyReport.contained = practicionerDict[report.CGID]


# do EKG reports
for ekg in reportsDao.getAllEKGReportsForPatient(patient.SUBJECT_ID):
    ekgReport:DiagnosticReport = fhirUtil.getEKGReportAsFhir(ekg)
    # Put the practicioner as a contained resource
    ekgReport.contained = practicionerDict[report.CGID]
    # pprint.pprint(ekgReport.json(), indent=1, depth=5, width=80)
