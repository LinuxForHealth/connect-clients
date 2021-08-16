from databaseUtil import DatabaseUtil
from database_classes import Payer
from sqlalchemy import select
from typing import List
from typing import TypedDict


class InsuranceCompanyDict(TypedDict):
    id: int
    payer: Payer


class InsuranceDao:
    """
    class for accessing payer records in the database, claims, etc
    """
    session = None
    payerDict: InsuranceCompanyDict = None

    def __init__(self):
        """
         setup and fetch the database session from the database utility.
        """
        dbUtil = DatabaseUtil()
        self.session = dbUtil.getSession()
        self.payerDict = self.fetchPayerDict()


    def fetchPayerDict(self)->InsuranceCompanyDict:
        """
        gets a dictionary of the payers to get the definition of a patient's insurance record
        :return:
        :rtype:
        """
        global session
        payerDict = InsuranceCompanyDict()
        for payer in self.session.query(Payer).all():
            payerDict[payer.id] = payer
        return payerDict

    def getPayerDict(self)->InsuranceCompanyDict:
        return self.payerDict
