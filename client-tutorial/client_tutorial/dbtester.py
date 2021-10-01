#  Copyright (c) 2021 IBM Corporation
#  Henry Feldman, MD (CMO Development, IBM Watson Health)


from InsuranceDao import InsuranceDao
from database_classes import EligibilityRequest
from typing import List
import random

insuranceDao = InsuranceDao()
purposes = ['auth-requirements', 'benefits', 'discovery', 'validation']

print('STARTING PURPOSE FIXING')
#patientList = patientDao.getPatientForPayer(payer_id)
for eligiblityRequest in insuranceDao.getAllEligibilityRequest():
    random_index = random.randint(0, len(purposes) - 1)
    eligiblityRequest.request_purpose = purposes[random_index]
    insuranceDao.saveEligibilityRequest(eligiblityRequest)
print('FINISHED')
