from .databaseUtil import DatabaseUtil
from .database_classes import Patient, Payer
from sqlalchemy import select
from typing import List
from .InsuranceDao import InsuranceDao, InsuranceCompanyDict
import string

class PatientsDao:
    """
    Is the database access object for the ORM that handles the Patient class. Databse access to Patients should always
    go through this class. Given this is for a demo we do not have full CRUD functionality here.
    """
    session = None

    payerDict: InsuranceCompanyDict = None
    insuranceDao:InsuranceDao = InsuranceDao()

    def __init__(self):
        """
        setup and fetch the database session from the database utility.
        """
        dbUtil = DatabaseUtil()
        self.session = dbUtil.getSession()

    def getAllPatients(self) -> List:
        """
        returs a List of Patients sorted in default order (primary key)
        :return: Patients
        :rtype: List[Patient]
        """
        global session
        return self.session.execute(select(Patient).order_by(Patient.last_name))

    def getPatient(self, subjectId: int) -> Patient:
        """
        fetches a specific patient for subjectId (which should be unique)
        :param subjectId:
        :type subjectId:
        :return: patient
        :rtype: Patient
        """
        global session
        global globalPatient
        global globalMilitaryInfo
        return self.session.query(Patient).filter(Patient.SUBJECT_ID==subjectId).one()

    def getPatientSummary(self, patient:Patient)->str:
        """
        Gets the text summary version of a patient as a handy utility
        @param patient: the patient you want a text summary of
        @type patient: Patient
        @return: the text description
        @rtype: str
        """
        payer: Payer = self.insuranceDao.getPayerDict()[patient.insurance]
        return f'Patient: {patient.last_name}, {patient.first_name}\nMRN: {patient.SUBJECT_ID}\nInsurance: {payer.Name} {payer.plan_type}\nDOB: {patient.DOB.strftime("%m/%d/%Y")} ({patient.calculate_age()})\n\n{patient.street}, {patient.city} {patient.state} {patient.zip}'

    def savePatient(self, patient:Patient)->Patient:
        """
        saves the patient to the database and returns the persisted version
        @param patient:
        @type patient:
        @return: patient
        @rtype: Patient
        """
        global session
        self.session.add(patient)
        self.session.commit()
        return patient
