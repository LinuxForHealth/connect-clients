#  Copyright (c) 2021 IBM Corporation
#  Henry Feldman, MD (CMO Development, IBM Watson Health)
from fhir.resources.patient import Patient
from fhir.resources.documentreference import DocumentReference
from fhir.resources.observation import Observation
from fhir.resources.narrative import Narrative
from fhir.resources.practitioner import Practitioner
from fhir.resources.practitionerrole import PractitionerRole
from fhir.resources.attachment import Attachment
from fhir.resources.humanname import HumanName
from datetime import date
import database_classes
import cgi
import base64

class FhirConverters:
    """
    creates fhir resources from the internal database classes So you have handy convience methods here which take the database
    entities from SqlAlchemy (from database_classes.py) and converts them handily to full fhir implementations.
    """

    def getPatientAsFhir(self, dbpatient:database_classes.Patient )->Patient:
        """
        returns the json representation of the Patient class as the Fhir Resource Patient
        @param dbpatient:
        @type database_classes.dbpatient:
        @return: fhirPatient
        @rtype: fhir.resources.patient.Patient
        """
        genderString = ''
        if dbpatient.GENDER == 'M':
            genderString = 'male'
        else:
            genderString = 'female'

        humanName: HumanName = HumanName()
        humanName.family = dbpatient.last_name
        humanName.given = [dbpatient.first_name]
        humanName.use = "official"
        humanName.text = dbpatient.first_name + " " + dbpatient.last_name
        json_dict = {"resourceType": "Patient", "id": dbpatient.SUBJECT_ID,
                    "name": [humanName], "active": True, "gender": genderString, "birthDate": dbpatient.DOB.strftime("%Y-%m-%d"),
                    "address": [{
                    "use": "home", "type": "postal", "line": [dbpatient.street], "city": dbpatient.city,
                    "state": dbpatient.state, "postalCode": dbpatient.zip, "country": "USA"}],
                    "identifier": [{"value": dbpatient.SUBJECT_ID,
                    "type": {"coding": [{"system": "http://terminology.hl7.org/CodeSystem/v2-0203"}]},
                    "system": "http://https://mimic.physionet.org/identifiers/subjectid"}]}
        fhirPatient = Patient.parse_obj(json_dict)
        return fhirPatient

    def getNoteEventsAsFhir(self, noteEvent:database_classes.Noteevent)->DocumentReference:
        """
        returns the json representation of the NoteEvent class as the FhirResource DocumentReference
        @param noteEvent:
        @type noteEvent:
        @return: documentReference
        @rtype: DocumentReference
        """
        # fhir note text has to be enclosed in a xhtml div
        noteDiv:str = "<div xmlns=\"http://www.w3.org/1999/xhtml\">"+noteEvent.TEXT+"</div>"
        attachment:Attachment = Attachment()
        attachment.contentType = "text/plain"
        attachment.data = base64.b64encode(bytes(noteDiv, 'utf-8'))

        narrative:Narrative = Narrative
        narrative.status = 'additional'
        narrative.div = noteDiv

        json_dict = {"resourceType": "DocumentReference", "text": {"status" : "generated",  "div" : noteDiv}, "status": "current",
                   "id": noteEvent.ROW_ID, "content": [{"attachment": attachment}],
                    "description": noteEvent.DESCRIPTION, "type": { "coding": [{"code": "47039-3"}]},
                    "identifier": [{"value": noteEvent.SUBJECT_ID,
                    "type": {"coding": [{"system": "http://terminology.hl7.org/CodeSystem/v2-0203"}]},
                    "system": "http://https://mimic.physionet.org/identifiers/subjectid"}]}
        return DocumentReference.parse_obj(json_dict)


    def getLabEventAsFhir(self, labEvent:database_classes.LabEvent,  labDefinition:database_classes.DLabItem )->Observation:
        """
        returns the json representation of the Observation (lab) class as the FhirResource Observation
        @param labEvent: the lab from the database
        @type database_classes.LabEvent:
        @param: labDefinition
        @type: database_classes.DLabItem
        @return: observation
        @rtype: Observation
        """
        uom:str = None
        loinc:str = None
        interpretation:str = None
        if labEvent.FLAG != None:
            interpretation = labEvent.FLAG
        else:
            interpretation = "normal"
        if labEvent.VALUEUOM == None:
            uom = 'N/A'

        json_dict = {"code": {"coding": [
            {"code": labDefinition.LOINC_CODE, "system": "http://loinc.org", "display": labDefinition.LABEL}]},
                     "status": "final", "subject": {"identifier": {"id": labEvent.SUBJECT_ID, "type": {
                "id": "http://terminology.hl7.org/CodeSystem/v2-0203", "text": "MR"}, "value": labEvent.SUBJECT_ID,
                                                                   "system": "http://https://mimic.physionet.org/identifiers/subjectid"}},
                     "category": [{"coding": [
                         {"code": "laboratory", "system": "http://hl7.org/fhir/ValueSet/observation-category"}]}],
                     "identifier": [{"use": "usual"}], "resourceType": "Observation",
                     "valueQuantity": {"unit": labEvent.VALUEUOM, "value": labEvent.VALUENUM},
                     "interpretation": [{"text": interpretation}]}
        return Observation.parse_obj(json_dict)

    def getCareGiverAsFhir(self,careGiver:database_classes.Caregiver)->Practitioner:
        """
        returns the json representation of the Caregiver (practicioner) class as the FhirResource Practicioner
        @param careGiver:
        @type careGiver:
        @return: practicioner
        @rtype: Practitioner
        """
        gender:str = None
        if careGiver.gender == 'M':
            gender = 'male'
        else:
            gender = 'female'
        json_dict = {"resourceType": "Practitioner",
                     "identifier": [{"system": "http://hl7.org/fhir/sid/us-npi", "value": careGiver.NPI_number}],
                     "name": [{"family": careGiver.last_name, "given": [careGiver.first_name]}], "gender": gender}
        return Practitioner.parse_obj(json_dict)

    def getPracticionerRoleAsFhir(self,careGiver:database_classes.Caregiver)->PractitionerRole:
        roleTitle=None
        if careGiver.DESCRIPTION == 'Attending' or careGiver.DESCRIPTION == 'Resident/Fellow/PA/NP':
            roleTitle='Physician'
        elif careGiver.DESCRIPTION == 'RN' or  careGiver.DESCRIPTION == 'Case Manager':
            roleTitle = 'RN'
        elif careGiver.DESCRIPTION == 'Rehabilitation':
            roleTitle = 'Physical Therapist'
        elif careGiver.DESCRIPTION == 'Dietitian':
            roleTitle = 'Registered Dietician'
        elif careGiver.DESCRIPTION == 'Respiratory':
            roleTitle = 'Respiratory Therapist'
        elif careGiver.DESCRIPTION == 'Respiratory':
            roleTitle = 'Social Worker'
        elif careGiver.DESCRIPTION == 'UCO':
            roleTitle = 'Administration'
        elif careGiver.DESCRIPTION == 'Pharmacist':
            roleTitle = 'Pharmacist'
