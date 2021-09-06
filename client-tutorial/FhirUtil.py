#  Copyright (c) 2021 IBM Corporation
#  Henry Feldman, MD (CMO Development, IBM Watson Health)
import json
from fhir.resources.patient import Patient
from fhir.resources.documentreference import DocumentReference
from fhir.resources.domainresource import DomainResource
from fhir.resources.observation import Observation
from fhir.resources.narrative import Narrative
from fhir.resources.practitioner import Practitioner
from fhir.resources.practitionerrole import PractitionerRole
from fhir.resources.diagnosticreport import DiagnosticReport
from fhir.resources.organization import Organization
from fhir.resources.reference import Reference
from fhir.resources.coverageeligibilityrequest import CoverageEligibilityRequest
from fhir.resources.coverage import Coverage
from fhir.resources.extension import Extension
from fhir.resources.attachment import Attachment
from fhir.resources.humanname import HumanName
from datetime import date
from database_classes import Patient, Noteevent, LabEvent, DLabItem, Caregiver, Hospital, EKGReport, RadiologyReport, Payer, PatientCoverage, CoveragePlanData
import cgi
import base64
from httpx import AsyncClient
import asyncio
import pprint
from datetime import datetime

class FhirConverters:
    """
    creates fhir resources from the internal database classes So you have handy convience methods here which take the database
    entities from SqlAlchemy (from database_classes.py) and converts them handily to full fhir implementations.
    """

    def getPatientAsFhir(self, dbpatient: Patient) -> Patient:
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
                     "name": [humanName], "active": True, "gender": genderString,
                     "birthDate": dbpatient.DOB.strftime("%Y-%m-%d"),
                     "address": [{
                         "use": "home", "type": "postal", "line": [dbpatient.street], "city": dbpatient.city,
                         "state": dbpatient.state, "postalCode": dbpatient.zip, "country": "USA"}],
                     "identifier": [{"value": dbpatient.SUBJECT_ID, "extension": [{"url": "http://hl7.org/fhir/StructureDefinition/geolocation", "extension": [{"url": "latitude", "valueDecimal": dbpatient.latitude}, {"url": "longitude", "valueDecimal": dbpatient.longitude}]}],
                                     "type": {"coding": [{"system": "http://terminology.hl7.org/CodeSystem/v2-0203"}]},
                                     "system": "http://https://mimic.physionet.org/identifiers/subjectid"}]}
        fhirPatient = Patient.parse_obj(json_dict)
        return fhirPatient

    def getRadiologyReportAsFhir(self,report:RadiologyReport)->DiagnosticReport:
        """
        returns a fhir resource of a radiology report entity to FHIR
        @param report: a radiology report
        @type report: database_classes.RadiologyReport
        @return: the diagnostic report
        @rtype: DiagnosticReport
        """
        reportDiv: str = "<div xmlns=\"http://www.w3.org/1999/xhtml\">" + report.TEXT + "</div>"
        attachment: Attachment = Attachment()
        attachment.contentType = "text/plain"
        attachment.data = base64.b64encode(bytes(reportDiv, 'utf-8'))
        json_dict = {"resourceType": "DocumentReference", "text": {"status": "generated", "div": reportDiv},
                     "status": "current",
                     "id": report.ROW_ID, "content": [{"attachment": attachment}],
                     "description": report.DESCRIPTION, "type": {"coding": [{"code": "68604-8"}]},
                     "impression":report.Impression,
                     "identifier": [{"value": report.SUBJECT_ID,
                                     "type": {"coding": [{"system": "http://terminology.hl7.org/CodeSystem/v2-0203"}]},
                                     "system": "http://https://mimic.physionet.org/identifiers/subjectid"}]}


    def getEKGReportAsFhir(self,report:EKGReport)->DiagnosticReport:
        """
        returns a fhir resource of a EKG report entity to FHIR
        @param report: an EKG report
        @type report: database_classes.EKGReport
        @return: the diagnostic report
        @rtype: DiagnosticReport
        """
        reportDiv: str = "<div xmlns=\"http://www.w3.org/1999/xhtml\">" + report.TEXT + "</div>"
        attachment: Attachment = Attachment()
        attachment.contentType = "text/plain"
        attachment.data = base64.b64encode(bytes(reportDiv, 'utf-8'))
        json_dict = {"resourceType": "DocumentReference", "text": {"status": "generated", "div": reportDiv},
                     "status": "current",
                     "id": report.ROW_ID, "content": [{"attachment": attachment}],
                     "description": report.DESCRIPTION, "type": {"coding": [{"code": "28010-7"}]},
                     "identifier": [{"value": report.SUBJECT_ID,
                                     "type": {"coding": [{"system": "http://terminology.hl7.org/CodeSystem/v2-0203"}]},
                                     "system": "http://https://mimic.physionet.org/identifiers/subjectid"}]}

    def getNoteEventsAsFhir(self, noteEvent: Noteevent) -> DocumentReference:
        """
        returns the json representation of the NoteEvent class as the FhirResource DocumentReference
        @param noteEvent:
        @type noteEvent:
        @return: documentReference
        @rtype: DocumentReference
        """
        # fhir note text has to be enclosed in a xhtml div
        noteDiv: str = "<div xmlns=\"http://www.w3.org/1999/xhtml\">" + noteEvent.TEXT + "</div>"
        attachment: Attachment = Attachment()
        attachment.contentType = "text/plain"
        attachment.data = base64.b64encode(bytes(noteDiv, 'utf-8'))

        narrative: Narrative = Narrative
        narrative.status = 'additional'
        narrative.div = noteDiv

        json_dict = {"resourceType": "DocumentReference", "text": {"status": "generated", "div": noteDiv},
                     "status": "current",
                     "id": noteEvent.ROW_ID, "content": [{"attachment": attachment}],
                     "description": noteEvent.DESCRIPTION, "type": {"coding": [{"code": "47039-3"}]},
                     "identifier": [{"value": noteEvent.SUBJECT_ID,
                                     "type": {"coding": [{"system": "http://terminology.hl7.org/CodeSystem/v2-0203"}]},
                                     "system": "http://https://mimic.physionet.org/identifiers/subjectid"}]}
        return DocumentReference.parse_obj(json_dict)

    def getLabEventAsFhir(self, labEvent: LabEvent,
                          labDefinition: DLabItem) -> Observation:
        """
        returns the json representation of the Observation (lab) class as the FhirResource Observation
        @param labEvent: the lab from the database
        @type database_classes.LabEvent:
        @param: labDefinition
        @type: database_classes.DLabItem
        @return: observation
        @rtype: Observation
        """
        uom: str = None
        loinc: str = None
        interpretation: str = None
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

    def getHospitalAsFhir(self, hospital:Hospital)->Organization:
        """
        returns the json representation of the hospital class as the FhirResource Organization
        @param hospital:
        @type hospital:
        @return:
        @rtype:
        """
        json_dict = {
              "resourceType": "Organization",
              "id": "2.16.840.1.113883.19.5",
              "text": {
                "status": "generated",
                "div": "<div xmlns=\"http://www.w3.org/1999/xhtml\">\n      \n      <p>"+hospital.name+"\n"+hospital.street+"<br>\n"+ hospital.city+",  "+hospital.state+ "  "+hospital.zip+"</p>\n    </div>"
              },
              "identifier": [
                {
                "use": "official",
                "type": {
                "text": hospital.name
                },
                "system": hospital.website,
                "value": "bidmc.org"
                }
                ],"active": "true",
              "type": [
                {
                  "coding": [
                    {
                      "system": "http://snomed.info/sct",
                      "code": "405608006",
                      "display": "Academic Medical Center"
                    },
                    {
                      "system": "http://terminology.hl7.org/CodeSystem/organization-type",
                      "code": "prov"
                    }
                  ]
                }
              ],
              "name": hospital.name,
              "telecom": [
                {
                  "system": "phone",
                  "value": hospital.telecom,
                  "use": "work"
                }
              ],
              "address": [
                {
                  "use": "work",
                  "line": [
                    hospital.street
                  ],
                  "city": hospital.city,
                  "postalCode": hospital.zip,
                  "country": hospital.country
                }
              ]
            }
        return Organization.parse_obj(json_dict)


    def getCareGiverAsFhir(self, careGiver: Caregiver) -> Practitioner:
        """
        returns the json representation of the Caregiver (practicioner) class as the FhirResource Practicioner
        @param careGiver:
        @type careGiver:
        @return: practicioner
        @rtype: Practitioner
        """
        gender: str = None
        if careGiver.gender == 'M':
            gender = 'male'
        else:
            gender = 'female'

        system: str = None
        idValue: str = None
        idText:str = None
        if (careGiver.NPI_number and careGiver.NPI_number):
            system = 'http://hl7.org/fhir/sid/us-npi'
            idValue = careGiver.NPI_number
            idText = 'NPI'
        else:
            system = "http://terminology.hl7.org/CodeSystem/v2-0203"
            idValue = careGiver.CGID
            idText = 'EI'
        json_dict = {"resourceType": "Practitioner",
                     "identifier": [{"use": "official", "type": {"text": idText}, "system": system, "value": idValue}], "name": [{"family": careGiver.last_name, "given": [careGiver.first_name]}], "gender": gender}
        practicioner = Practitioner.parse_obj(json_dict)
        if practicioner == None:
            print("********** BEGIN PARSE FAILURE *************")
            print(json_dict)
            print("********** END PARSE FAILURE *************")
        """
        if practicioner.Config:
            error:str = practicioner.Config.error_msg_templates['value_error.extra']
            print("***** ERROR IN FHIR: getCareGiverAsFhir(): "+error)
            practicioner= None
        """
        return practicioner

    def getPracticionerRoleAsFhir(self, careGiver: Caregiver, hospital:Hospital ) -> PractitionerRole:
        """
        returns the json representation of the PractitionerRole (job title essentially) class as the FhirResource PractitionerRole
        @param careGiver: the enetity for a practicioner in the EMR/DB
        @type careGiver: database_classes.Caregiver
        @param hospital: hospital data records
        @type hospital: database_classes.Hospital
        @return: the practicioner role resource
        @rtype: PractitionerRole
        """
        roleTitle:str = None
        roleSystem:str = None
        roleCode:str = None
        if careGiver.DESCRIPTION == 'Attending' or careGiver.DESCRIPTION == 'Resident/Fellow/PA/NP':
            self.roleTitle = 'Physician'
            self.roleSystem = 'http://terminology.hl7.org/CodeSystem/practitioner-role'
            self.roleCode = 'Doctor'
            if careGiver.LABEL:
                if 'PA' in careGiver.LABEL:
                    self.roleTitle = 'Physician Assistant'
                    self.roleSystem = 'http://snomed.info/sct'
                    self.roleCode = '449161006'
                elif 'Res' in careGiver.LABEL:
                    self.roleTitle = 'Physician Assistant'
                    self.roleSystem = 'http://snomed.info/sct'
                    self.roleCode = '405277009'
                elif 'NP' in careGiver.LABEL:
                    self.roleTitle = 'Nurse Practicioner'
                    self.roleSystem = 'http://snomed.info/sct'
                    self.roleCode = '224571005'
            else:
                self.roleTitle = careGiver.DESCRIPTION
                self.roleSystem = 'http://snomed.info/sct'
                self.roleCode = '224598009'
        elif careGiver.DESCRIPTION == 'RN' or careGiver.DESCRIPTION == 'Case Manager':
            self.roleTitle = 'RN'
            self.roleSystem = 'http://terminology.hl7.org/CodeSystem/practitioner-role'
            self.roleCode = 'Nurse'
        elif careGiver.DESCRIPTION == 'Rehabilitation':
            self.roleTitle = 'Physical Therapist'
            self.roleSystem = 'http://snomed.info/sct'
            self.roleCode = '36682004'
        elif careGiver.DESCRIPTION == 'Dietitian':
            self.roleTitle = 'Dietitian (general)'
            self.roleSystem = 'http://snomed.info/sct'
            self.roleCode = '40127002'
        elif careGiver.DESCRIPTION == 'Respiratory':
            self.roleTitle = 'Respiratory Therapist'
            self.roleSystem = 'http://snomed.info/sct'
            self.roleCode = '442867008'
        elif careGiver.DESCRIPTION == 'Respiratory':
            self.roleTitle = 'Social Worker'
        elif careGiver.DESCRIPTION == 'UCO':
            self.roleSystem = 'http://snomed.info/sct'
            self.roleCode = '6868009'
            self.roleTitle = 'Administration'
        elif careGiver.DESCRIPTION == 'Pharmacist':
            self.roleTitle = 'Pharmacist'
            self.roleSystem = 'http://terminology.hl7.org/CodeSystem/practitioner-role'
            self.roleCode = 'Pharmacist'
        if careGiver.LABEL:
            if careGiver.DESCRIPTION == None and careGiver.LABEL and 'MD' in careGiver.LABEL:
                self.roleTitle = 'Physician'
                self.roleSystem = '	http://terminology.hl7.org/CodeSystem/practitioner-role'
                self.roleCode = 'Doctor'
            elif careGiver.DESCRIPTION == None and careGiver.LABEL and 'ST' in careGiver.LABEL or 'St' in careGiver.LABEL  or 'st' in careGiver.LABEL  or 'MS' in careGiver.LABEL:
                self.roleTitle = 'Medical Student'
                self.roleSystem = 'http://snomed.info/sct'
                self.roleCode = '398130009'
            elif careGiver.DESCRIPTION == None and careGiver.LABEL and 'RRT' in careGiver.LABEL:
                self.roleTitle = 'Respiratory Therapist'
                self.roleSystem = 'http://snomed.info/sct'
                self.roleCode = '442867008'
            elif careGiver.DESCRIPTION == None and careGiver.LABEL and 'OT' in careGiver.LABEL:
                self.roleTitle = 'Occupational Therapist'
                self.roleSystem = 'http://snomed.info/sct'
                self.roleCode = '80546007'
            elif careGiver.DESCRIPTION == None and careGiver.LABEL and 'PCT' in careGiver.LABEL:
                self.roleTitle = 'Patient Care Technician'
                self.roleSystem = 'http://snomed.info/sct'
                self.roleCode = '5275007'
            elif careGiver.DESCRIPTION == None and careGiver.LABEL and 'LICSW' in careGiver.LABEL:
                self.roleTitle = 'Social Worker'
                self.roleSystem = 'http://snomed.info/sct'
                self.roleCode = '224598009'
            else:
                self.roleTitle = careGiver.DESCRIPTION
                self.roleSystem = 'http://snomed.info/sct'
                self.roleCode = '224598009'
        json_dict = {
                            "practitioner": {
                                "reference": "Practitioner/f007",
                                "display": careGiver.first_name+" "+careGiver.last_name
                            },
                            "organization": {
                                "reference": "Organization/f001",
                                "display": hospital.name
                            },
                            "code": [
                                {
                                    "coding": [
                                        {
                                            "system": self.roleSystem,
                                            "code": self.roleCode,
                                            "display": self.roleTitle
                                        }
                                    ],
                                    "text": roleTitle
                                }
                            ],
                            "specialty": [
                                {
                                    "coding": [
                                        {
                                            "system": "urn:oid:2.16.840.1.113883.2.4.15.111",
                                            "code": "01.015",
                                            "display": roleTitle
                                        }
                                    ],
                                    "text": "specialization"
                                }
                            ]
                    }

        return PractitionerRole.parse_obj(json_dict)

    def getPracticionerWithRoleAsFhir(self, careGiver:Caregiver, hospital:Hospital )->Practitioner:
        """
        Retuend a Practicioner resource with the role set as the "contained"
        @param careGiver: the doctor/nurse/etc
        @type careGiver: database_classes.Caregiver
        @param hospital: The hospital the caregiver works for (related via the hospital_works_for_id)
        @type database_classes.Hospital:
        @return: the practicioner with role embedded
        @rtype: Practitioner
        """
        if careGiver != None and hospital != None:
            practicioner: Practitioner = self.getCareGiverAsFhir(careGiver)
            if practicioner:
                practicionerRole: PractitionerRole = self.getPracticionerRoleAsFhir(careGiver, hospital)
                practicioner.contained = [practicionerRole]
            else:
                print("NULL PRACTICTIONER ERROR:")
                if careGiver == None:
                    print("CareGiver was null")
                    print(careGiver)
                elif hospital == None:
                    print('Hospital was null')
                    print(hospital)
                    print(careGiver.works_for_hospital_id)
            return practicioner

    # send the patient resource
    async def send_fhir_to_connect(self, resource: str, fhirserverurl: str):
        """
        Sends the json payload to the Fhir Server URL (which must contain the resource type as in https://localhost:5000/fhir/MedicationRequest) which we assemble below.
        Note the destination is almost always localhost (where the connect service is running not necessarily the fhir server itself
        :param json: (this is the fhir content)
        :type json:
        :param fhirserverurl: (the URL as in the above text)
        :type fhirserverurl:
        :return: None
        :rtype: None
        """
        if (fhirserverurl) :
            try:
                async with AsyncClient(verify=False) as client:
                    fhir_json = json.loads(resource)
                    result = await client.post(fhirserverurl, json=fhir_json)
                    # print(f"Header: {result.text}")
            except:
                raise

    async def sendFhirJsonStringToConnectLFH(self, fhirJson:str, resourceType:str):
        """
        This takes a FHIR resource repseneted as a string (cached in the database for instance( and sends it onto LFH Connect. we need to know the resource type, we need to modify our endpoint URL to include the resource type which we will get below.
        @param fhirJson: The text of the fhir json
        @type fhirJson:
        @param resourceType: the name of the FHIR resource of this string (e.g. Patient)
        @type resourceType: str
        @return: None
        @rtype: None
        """
        fhir_r4_externalserver_url:str = 'https://localhost:5000/fhir/'+resourceType
        # pprint.pprint(fhirResource.json(), indent=1, depth=5, width=80)

        await self.send_fhir_to_connect(fhirJson, fhir_r4_externalserver_url)

    async def sendFhirResourceToConnectLFH(self, fhirResource:DomainResource):
        """
        This takes a FHIR resource and sends it onto LFH Connect. Since we are using the generic domain resource type (let's all be inclusive here!)
        which is the parent of all FHIR resources, we need to modify our endpoint URL to include the resource type which we will get below.
        @param fhirResource: The fhir resource generated by one of the above
        @type fhirResource:
        @return: None
        @rtype: None
        """

        fhir_r4_externalserver_url:str = 'https://localhost:5000/fhir/'+fhirResource.resource_type
        # pprint.pprint(fhirResource.json(), indent=1, depth=5, width=80)

        await self.send_fhir_to_connect(fhirResource.json(), fhir_r4_externalserver_url)

    def getPlanData(self, coveragePlanData:CoveragePlanData)-> {}:
        """
        returns the json for the plan data for eligibility
        @param coveragePlanData:
        @type coveragePlanData:
        @return: json_dict
        @rtype: Dict
        """
        json_dict = {
                  "type": {
                    "coding": [
                      {
                        "system": "http://terminology.hl7.org/CodeSystem/coverage-class",
                        "code": coveragePlanData.type,
                        "name": coveragePlanData.name
                      }
                    ]
                  },
                  "value": coveragePlanData.value
                }
        return json_dict

    def getBeneficiary(self, coverage:PatientCoverage)->Reference:
        """
        gets the patient reference as a logical reference using the patient's id number (SubjectId)
        @param coverage: coverage
        @type coverage: PatientCoverage
        @return: referenceObject
        @rtype: {}
        """
        json_dict = {
                "beneficiary": {
                    "identifier": [
                        {
                            "type": {
                                "coding": [
                                    {
                                        "system": "http://terminology.hl7.org/CodeSystem/v2-0203",
                                        "code": "MR"
                                    }
                                ]
                            },
                            "value": coverage.patient_id
                        }
                    ]
                }
            }
        return Reference.parse_obj(json_dict)



    def getPayerReference(self, payer_id:int)->Reference:
        """
        gets the patient reference as a logical reference using the payer's id number (id field)
        @param coverage: coverage
        @type coverage: PatientCoverage
        @return: referenceObject
        @rtype: {}
        """
        json_dict = {
                "Organization": {
                    "identifier": [
                        {
                            "type": {
                                "coding": [
                                    {
                                        "system": "http://terminology.hl7.org/CodeSystem/v3-IdentifierScope",
                                        "code": "OBJ"
                                    }
                                ]
                            },
                            "value": payer_id
                        }
                    ]
                }
            }
        return Reference.parse_obj(json_dict)


    def getCoverageAsFhir(self, patient:Patient, coverage:PatientCoverage, payer:Payer)->Coverage:
        """
        returns the json representation of the CoverageEligibilityRequest (check if the patient has this actual coverage) class as the FhirResource CoverageEligibilityRequest

        @param patient:
        @type patient: database_classes.Patient
        @param coverage:
        @type coverage: database_classes.PatientCoverage
        @param payer:
        @type payer: database_classes.Payer
        @return:
        @rtype:
        """

        result = []
        for planInfo in coverage.coveragePlanData:
            data = self.getPlanData(planInfo)
            result.append(data)

        start:datetime = datetime.strptime('Jan 1 '+ str(date.today().year)+' 12:00AM', '%b %d %Y %I:%M%p')
        end:datetime = datetime.strptime('Dec 31 '+ str(date.today().year)+' 11:59PM', '%b %d %Y %I:%M%p')
        # we set the coverage period to the current year
        print(coverage)
        json_dict = {"resourceType": "Coverage",
                      "id": str(coverage.id),
                      "text": {
                        "status": "generated",
                        "div": "<div xmlns=\"http://www.w3.org/1999/xhtml\">"+str(coverage)+"</div>"
                      },
                      "identifier": [
                        {
                          "system": "http://benefitsinc.com/certificate",
                          "value": coverage.payer_plan_id
                        }
                      ],
                      "status": "active",
                      "type": {
                        "coding": [
                          {
                            "system": "http://terminology.hl7.org/CodeSystem/v3-ActCode",
                            "code": "EHCPOL",
                            "display": "extended healthcare"
                          }
                        ]
                      },
                     "subscriberId": coverage.member_id,
                     "beneficiary": [self.getBeneficiary(coverage)]
        ,
                      "dependent": "0",
                      "relationship":
                        {
                        "coding": [
                          {
                            "code": "self"
                          }
                        ]
                      }
        ,
                    "period": {
                                  "start": start,
                                  "end": end
                              },
                              "payor": [
            {
                "reference": self.getPayerReference(coverage.payer_id)
            }
        ],
        "class": [result.append(data)]
        }
        return Coverage.parse_obj(json_dict)
