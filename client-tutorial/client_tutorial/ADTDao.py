from databaseUtil import DatabaseUtil
from database_classes import Caregiver, Admission, DRGCode, DiagnosisIcd, DIcdDiagnoses, CPTEvent, DCPT, Hospital
from sqlalchemy import select
from typing import List, TypedDict

class CareGiverDict(TypedDict):
    id: int
    name: Caregiver

class CPTDefsDict(TypedDict):
    id: int
    name: DCPT


class AdtDao:
    """
    Is the database access object for the all the administrative entities, such as admission, caregivers (doctors, etc), ICD, CPT and DRG coding.
    """
    session = None


    def __init__(self):
        """
         setup and fetch the database session from the database utility.
        """
        dbUtil = DatabaseUtil()
        self.session = dbUtil.getSession()


    def getCareGiverDict(self) -> CareGiverDict:
        """
        This gets list list of caregivers as a dictionary of dict{ITEMID, Caregiver}.
        :return: careGiverDict
        :rtype: dict(int,Caregiver)
        """
        global session
        careGiverDict = CareGiverDict()
        for caregiver in  self.session.query(Caregiver).all():
            careGiverDict[caregiver.CGID] = caregiver
        return careGiverDict

    def saveCareGiver(self, careGiver:Caregiver)->Caregiver:
        """
        update or save the CareGiver entitiy to the database
        @param careGiver: The caregiver to save
        @type careGiver: Caregiver
        @return: The updated caregiver
        @rtype: Caregiver
        """
        global session
        self.session.add(careGiver)
        self.session.commit()
        return careGiver

    def getCareGiverForCGID(self,CGID:int)->Caregiver:
        """
        return a given caregiver (rather than using the entire dict)
        @param CGID: the linked value from other tables
        @type CGID: int
        @return: the caregiver (doctor)
        @rtype: Caregiver
        """
        global session
        return self.session.query(Caregiver).filter(Caregiver.CGID==CGID).one()


    def getAdmissionsForSubjectId(self, subjectId: int) -> List[Admission]:
        """
         Get all the Admissions for a given Patient.
         :param subjectId:
         :type subjectId:
         :return: admissions
         :rtype: List[Admission]
         """
        global session
        return self.session.query(Admission).filter(Admission.SUBJECT_ID == subjectId).all()

    def getCPTEventsForAdmission(self, admissionId: int) -> List:
        """
        gets the list of CPT events (i.e. bills) for a given admission
        :param admissionId:
        :type admissionId:
        :return: cptList
        :rtype: List[CPTEvent]
        """
        global session
        return self.session.query(CPTEvent).filter(CPTEvent.HADM_ID == admissionId).all()

    def getDRGsForAdmission(self, admissionId: int) -> List[DRGCode]:
        """
        gets the list of DRG codes (i.e. facility bills) for a given admission
        :param admissionId:
        :type admissionId:
        :return: cptList
        :rtype: List[DRGCode]
        """
        global session
        return self.session.query(DRGCode).filter(DRGCode.HADM_ID == admissionId).all()

    def getICDDefinitions(self) -> dict:
        """
        Pulls the definition for a given ICD Diagnosis code in a dict by the ICD code (used to fill in the DiagnosisIcd class)
        :return: icdCodeDefnintionDict
        :rtype: Dict
        """
        global session
        icdCodeDefnintionDict = {}
        for icdCodeDefnition in self.session.query(DIcdDiagnoses).all():
            icdCodeDefnintionDict[icdCodeDefnition.ICD9_CODE] = icdCodeDefnition
        return icdCodeDefnintionDict

    def getIcdCodesForAdmission(self, admissionId: int) -> List[DiagnosisIcd]:
        """
        returns the ICD diagnosis codes for the admission. Thd
        :param admissionId:
        :type admissionId:
        :return:
        :rtype:
        """
        global session
        return self.session.query(DiagnosisIcd).filter(DiagnosisIcd.HADM_ID == admissionId).all()

    def getCptEventsForAdmission(self, admissionId: int) -> List[CPTEvent]:
        """
        get the CPT (procedural codes) for a specific admission
        :param admissionId:
        :type admissionId:
        :return: cptEventList
        :rtype: List[CptEvent]
        """
        global session
        return self.session.query(CPTEvent).filter(CPTEvent.HADM_ID == admissionId).all()

    def getCptEventDefinitions(self) -> CPTDefsDict:
        """
        Returns the definition dictionary for the CPTEvents
        :return: cptDict
        :rtype: Dict(str,DCPT)
        """
        global session
        cptDict = CPTDefsDict()
        for cptDefinition in self.session.query(DCPT).all():
            cptDict[cptDefinition.CATEGORY] = cptDefinition

    def getAllHospitals(self)->List[Hospital]:
        """
        Gets the list of defined hospitals
        @return: hospitalList
        @rtype: List[Hospital]
        """
        global session
        return self.session.query(Hospital).all()

    def saveHospital(self,hospital:Hospital)->Hospital:
        """
        save or update the hospital
        @param hospital:
        @type hospital:
        @return:
        @rtype:
        """
        global session
        self.session.add(hospital)
        self.session.commit()
        return hospital
