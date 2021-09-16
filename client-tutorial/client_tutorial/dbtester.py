#  Copyright (c) 2021 IBM Corporation
#  Henry Feldman, MD (CMO Development, IBM Watson Health)


from PatientsDao import PatientsDao
from database_classes import Patient
from typing import List

payer_id = 4;

patientDao = PatientsDao()

listOfPatients:List[Patient] = []
#patientList = patientDao.getPatientForPayer(payer_id)
for patient in patientDao.getPatientForPayer(payer_id):
    print(patient)
    listOfPatients.append(patient)

print(len(listOfPatients))
