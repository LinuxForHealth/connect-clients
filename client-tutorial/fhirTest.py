#  Copyright (c) 2021 IBM Corporation
#  Henry Feldman, MD (CMO Development, IBM Watson Health)

from typing import List
from FhirUtil import FhirConverters
from database_classes import Patient, Noteevent, LabEvent, DLabItem, Caregiver, Hospital, EKGReport, RadiologyReport
from PatientsDao import PatientsDao
from NoteEventDao import NoteEventDao
from ReportsDao import ReportsDao
from ADTDao import AdtDao
from LabDao import LabDao, DLabItemDict
from fhir.resources.domainresource import DomainResource
from fhir.resources.organization import Organization
from fhir.resources.patient import Patient
from fhir.resources.documentreference import DocumentReference
from fhir.resources.diagnosticreport import DiagnosticReport
from fhir.resources.practitioner import Practitioner
from fhir.resources.practitionerrole import PractitionerRole
from typing import TypedDict
import pprint
import json
import asyncio

class HospitalDict(TypedDict):
    id:int
    hospital:Hospital

class PracticionerDict(TypedDict):
    id:int
    practictioner:Practitioner

# make a list for holding all the fhir to send (not because we can't send individually but it's a good demo that you can do this)
fhirList:List[DomainResource] = []
loop = asyncio.get_event_loop()

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
print(patient)
fhirPatient  = fhirUtil.getPatientAsFhir(patient)
#now we have the Patient resource (we're going to ignore it here)
# pprint.pprint(fhirPatient.json(), indent=1, depth=5, width=80)
fhirList.append(fhirPatient)
loop.run_until_complete(fhirUtil.sendFhirResourceToConnectLFH(fhirPatient))

# now get this patient's notes (uncomment the pprint statement to see the contents)
print('Sending Note to Fhir converter')
noteEventDao:NoteEventDao = NoteEventDao()
noteEvent:Noteevent = noteEventDao.getNoteEventById(1)
fhirDocumentReference = fhirUtil.getNoteEventsAsFhir(noteEvent)
# pprint.pprint(fhirDocumentReference.json(), indent=1, depth=5, width=80)
fhirList.append(fhirDocumentReference)
loop.run_until_complete(fhirUtil.sendFhirResourceToConnectLFH(fhirDocumentReference))

print('starting lab setup - may take a while')
#Make a dictionary of the lab definitions compared to the item codes in the LabEvent entity
labItems: DLabItemDict = None
labItem:DLabItem = None
#make the caregiver dict for later
practicionerDict:PracticionerDict = PracticionerDict()

# get all the labs from the database
labItems =  labDao.getAllDLabItems()
#that query returns the dictionary from the database
labList:List[LabEvent] = labDao.getLabsForPatient(patient.SUBJECT_ID)
print("doing Labs ("+str(len(labList))+" records)")
for labEvent in labList:
    # iterate over each lab event for this patient (severral hundred) and then convert them into FHIR resources. In this
    # case they just fall on the floor but you could do something useful here (like transmit them somewhere)
    labItem = labItems[labEvent.ITEMID]
    labFhir = fhirUtil.getLabEventAsFhir(labEvent, labItem)
    if labFhir:
        # pprint.pprint(labFhir.json(), indent=1, depth=5, width=80)
        fhirList.append(labFhir)
        loop.run_until_complete(fhirUtil.sendFhirResourceToConnectLFH(labFhir))

# now let's create the Practicioners (called aregivers in the original MIMIC III) as fhir resources
careGiverDict = adtDao.getCareGiverDict()
#we're going to make a practicioner dict for later in the diagnostic reports
# make a dict to hold all the hospitals, but let's do it right (and feel free to make more) (well there is only 1)
hospitalDict:HospitalDict = HospitalDict()
# get all the hospitals and stick them (it) into the dict by the id
print("Doing Hospitals")
for hospital in adtDao.getAllHospitals():
    hospitalDict[hospital.id] = hospital
    organization:Organization = fhirUtil.getHospitalAsFhir(hospital)
    hospital.fhir_json = organization.json()
    #adtDao.saveHospital(hospital)

# as a test send all the caregivers (MIMIC's name for practicioners) to be converted into FHIR
totalCareGivers:int = len(careGiverDict.values())
print("doing Practicioners ("+str(totalCareGivers)+" records) - this is a huge amount of data, be patient")
count:int = 0
for careGiver in careGiverDict.values():
    # Now it is important to understand what this method is doing, which is creating 2 FHIR resources (Practicioner and a
    # PracticionerRole) but rather than return them as a tuple fhir allows a "contained" resource where you can store a
    # related item directly in the resource. This Makes it easy to keep them together.
    count+=1
    if count % 100 == 0:
        print('\t'+str(count) + "/"+str(totalCareGivers))
    hospital:Hospital = hospitalDict[careGiver.works_for_hospital_id]
    if (hospital and careGiver):
        #practicioner:Practitioner = fhirUtil.getPracticionerWithRoleAsFhir(careGiver, hospital)
        #pprint.pprint(practicioner.json(), indent=1, depth=5, width=80)
        #practicionerDict[careGiver.CGID] = practicioner
        # pprint.pprint(practicioner.json(), indent=1, depth=5, width=80)
        #fhirList.append(practicioner)
        # careGiver.fhir_json = practicioner.json()
        # adtDao.saveCareGiver(careGiver)
        if careGiver.fhir_json:
            print(careGiver)
            loop.run_until_complete(fhirUtil.sendFhirJsonStringToConnectLFH(careGiver.fhir_json,'Practitioner'))

#now let's do radiology reports
print("doing RadiologyReports->DiagnosticReport")
for report in reportsDao.getRadiologyReportsForPatient(patient.SUBJECT_ID):
    radiologyReport:DiagnosticReport = fhirUtil.getRadiologyReportAsFhir(report)
    # Put the practicioner as a contained resource
    if radiologyReport:
        radiologyReport.contained = practicionerDict[report.CGID]
    # pprint.pprint(radiologyReport.json(), indent=1, depth=5, width=80)
    fhirList.append(radiologyReport)

# do EKG reports
print("doing EKGReports->DiagnosticReport")
for ekg in reportsDao.getAllEKGReportsForPatient(patient.SUBJECT_ID):
    ekgReport:DiagnosticReport = fhirUtil.getEKGReportAsFhir(ekg)
    # Put the practicioner as a contained resource
    if ekgReport:
        ekgReport.contained = practicionerDict[report.CGID]
    # pprint.pprint(ekgReport.json(), indent=1, depth=5, width=80)
    fhirList.append(ekgReport)

#now send all the resources to Connect
print('Actually Sending '+str(len(fhirList))+" resources to FHIR via LFH Connect")

#for fhirResource in fhirList:
#    if fhirResource:
#        loop.run_until_complete(fhirUtil.sendFhirResourceToConnectLFH(fhirResource))
loop.close()
print('completed FHIR sending to LFH Connect')
