from databaseUtil import DatabaseUtil
from database_classes import Patient
from sqlalchemy import select
from typing import List


class PatientsDao:
    """
    Is the database access object for the ORM that handles the Patient class. Databse access to Patients should always
    go through this class. Given this is for a demo we do not have full CRUD functionality here.
    """
    session = None

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
