from databaseUtil import DatabaseUtil
from database_classes import Payer, PatientCoverage, CoveragePlanData, EligibilityRequest, EligibilityRequestResponse
from typing import TypedDict, List


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

    def getAllPayers(self)->List[Payer]:
        """
        gets the list of all the Payers
        @return: payerList
        @rtype: List[Payer]
        """
        global session
        return self.session.query(Payer).all()

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
        if len(self.payerDict.keys()) < 1:
            self.payerDict = self.fetchPayerDict()
        return self.payerDict

    def getAllPatientCoverage(self)->List[PatientCoverage]:
        global session
        return self.session.query(PatientCoverage).all()

    def getAllPatientCoverageForPatient(self, subjectId:int)->List[PatientCoverage]:
        """
        get the patient's coverage record from the database
        @param subjectId:
        @type subjectId:
        @return: coverageList
        @rtype: List[PatientCoverage]
        """
        global session
        return self.session.query(PatientCoverage).all()

    def getPatientCoverage(self, id:int)->PatientCoverage:
        """
        gets a specific patient coverage records by the id
        @return: patientCoverage
        @rtype: PatientCoverage
        """
        global session
        return self.session.query(PatientCoverage).get(id)

    def getPayer(self, id:int):
        """
        get payer by id
        @param id: the payer id
        @type id:
        @return: the Payer
        @rtype: Payer
        """
        global session
        return self.session.query(Payer).filter(Payer.id==id).one()

    def savePatientCoverage(self, patientCoverage:PatientCoverage)->PatientCoverage:
        """
        save the patient coverage back to the database and returned the persisted version
        @param patientCoverage:
        @type patientCoverage:
        @return: patientCoverage
        @rtype: PatientCoverage
        """
        global session
        self.session.add(patientCoverage)
        self.session.commit()
        return patientCoverage

    def getAllCoveragePlanData(self)->List[CoveragePlanData]:
        """
        gets all the coverage plan data to assemble the coverage details for a given patientcoverage
        @return: coverage plan data records
        @rtype: List[CoveragePlanData]
        """
        global session
        return self.session.query(CoveragePlanData).all()

    def getAllEligibilityRequest(self)->List[EligibilityRequest]:
        global session
        return self.session.query(EligibilityRequest).all()

    def getEligibilityRequest(self, id:int)->EligibilityRequest:
        """
        gets an eligibility request via its primary key id
        @param id: the id of the request
        @type id: int
        @return: eligibilityRequest
        @rtype: EligibilityRequest
        """
        global session
        return self.session.query(EligibilityRequest).get(id)

    def getAllEligiilityRequestsForPatientForPayer(self, patientId:int, payerId:int):
        global session
        return self.session.query(EligibilityRequest).filter(
            EligibilityRequest.payer_id == payerId and EligibilityRequest.patient_id == patientId).all()

    def getAllPatientCoverageForPayerId(self, payerId:int)->List[PatientCoverage]:
        """
        gets all the coverage plan data to assemble the coverage details for a given patientcoverage
        @return: coverage plan data records
        @rtype: List[CoveragePlanData]
        """
        global session
        return self.session.query(PatientCoverage).filter(PatientCoverage.payer_id == payerId).all()

    def getAllEligibitilityRequestsForPayer(self, payerId:int)->List[EligibilityRequest]:
        """
        gets all the eligibility requests for a specigic payer
        @param payerId:
        @type payerId:
        @return: eligibilityRequestList
        @rtype: List[EligibilityRequest]
        """
        global session
        return self.session.query(EligibilityRequest).filter(EligibilityRequest.payer_id == payerId).all()

    def getAllActiveEligibitilityRequestsForPayer(self, payerId:int)->List[EligibilityRequest]:
        """
        gets all the eligibility requests for a specigic payer
        @param payerId:
        @type payerId:
        @return: eligibilityRequestList
        @rtype: List[EligibilityRequest]
        """
        global session
        return self.session.query(EligibilityRequest).filter(EligibilityRequest.payer_id == payerId and EligibilityRequest.processed == None).all()

    def saveEligibilityRequest(self, eligibilityRequest:EligibilityRequest)->EligibilityRequest:
        """
        gets all the eligibility requests for a specigic payer
        @param eligibilityRequest:
        @type eligibilityRequest:
        @return:
        @rtype:
        """
        global session
        self.session.add(eligibilityRequest)
        self.session.commit()
        return eligibilityRequest
