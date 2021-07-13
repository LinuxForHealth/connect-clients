from databaseUtil import DatabaseUtil
from database_classes import Prescription
from sqlalchemy import select
from typing import List

class MedicationDao:
    """
    Is the database access object for the ORM that handles the Prescription class (medication Orders). Database access to Prescriptions should always
    go through this class. Given this is for a demo we do not have full CRUD functionality here.
    """
    session = None

    def __init__(self):
        """
        setup and fetch the database session from the database utility.
        """
        dbUtil = DatabaseUtil()
        self.session = dbUtil.getSession()

    def getAllPrescriptions(self) -> List[Prescription]:
        """
        Get the entire list of prescriptions as a list sorted by default (primary key)
        :return: prescriptionList
        :rtype: List[Prescription]
        """
        global session
        return self.session.execute(select(Prescription).order_by(Prescription.DRUG_NAME_POE))

    def getPrescriptionsForPatient(self, subjectId: int) -> List[Prescription]:
        """
        Get the entire list of prescriptions as a list sorted by default (primary key)
        :param subjectId:
        :type subjectId:
        :return: prescriptionList
        :rtype: List[Prescription]
        """
        global session
        return self.session.query(Prescription).filter(Prescription.SUBJECT_ID==subjectId).all()

    def getPrescriptionByRowId(self, rowId: int) -> Prescription:
        """
        Gets a specific prescription by its primary key
        :param rowId:
        :type rowId:
        :return: prescription
        :rtype: Prescription
        """
        global session
        return self.session.query(Prescription).filter(Prescription.ROW_ID == rowId).one()
