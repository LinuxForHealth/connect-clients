#  Copyright (c) 2021 IBM Corporation
#  Henry Feldman, MD (CMO Development, IBM Watson Health)
import json

from database_classes import Patient, Noteevent, LabEvent, DLabItem, Caregiver, Hospital, EKGReport, RadiologyReport, Payer, PatientCoverage, CoveragePlanData
from fhir.resources.coverageeligibilityrequest import CoverageEligibilityRequest
from fhir.resources.coverage import Coverage
from InsuranceDao import InsuranceDao
from PatientsDao import PatientsDao
from FhirUtil import FhirConverters
import asyncio

patientDao:PatientsDao = PatientsDao()
insuranceDao:InsuranceDao = InsuranceDao()
fhirUtil:FhirConverters = FhirConverters()
loop = asyncio.get_event_loop()

patient:Patient = patientDao.getPatient(959595)
coverage:PatientCoverage = insuranceDao.getPatientCoverage(1)
payer:Payer = insuranceDao.getPayer(coverage.payer_id)
coverageFhir:Coverage = fhirUtil.getCoverageAsFhir(patient, coverage, payer)
print(json.loads(coverageFhir))
