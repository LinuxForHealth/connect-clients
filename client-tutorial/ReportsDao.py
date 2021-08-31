#  Copyright (c) 2021 IBM Corporation
#  Henry Feldman, MD (CMO Development, IBM Watson Health)
from .databaseUtil import DatabaseUtil
from typing import List
from .database_classes import RadiologyReport, EKGReport


class ReportsDao:
    """
    the collection of methods to fetch report entities (radiology, EKG...) from the database
    """

    session = None

    def __init__(self):
        """
        setup and fetch the database session from the database utility.
        """
        dbUtil = DatabaseUtil()
        self.session = dbUtil.getSession()

    def getAllRadiologyReports(self)->List[RadiologyReport]:
        """
        gets the list of radiology reports out of the database
        @return: radiologyReportsList
        @rtype: List[RadiologyReport]
        """
        global session
        return self.session.query(RadiologyReport).all()

    def getRadiologyReportsForPatient(self,subjectId:int)->List[RadiologyReport]:
        """
        gets the list of radiology reports out of the database for a specific aptient by their subjectid\
        @param subjectId:
        @type subjectId:
        @return: radiologyReportsList
        @rtype: List[RadiologyReport]
        """
        global session
        return self.session.query(RadiologyReport).filter(RadiologyReport.SUBJECT_ID==subjectId).all()

    def getAllEKGReports(self)->List[EKGReport]:
        """
        gets the list of EKG reports out of the database
        @return: ekgReports
        @rtype: List[EKGReport]
        """
        global session
        return self.session.query(EKGReport).all()

    def getAllEKGReportsForPatient(self,subjectId:int) -> List[EKGReport]:
        """
        gets the list of EKG reports out of the database
        @return: ekgReports
        @rtype: List[EKGReport]
        """
        global session
        return self.session.query(EKGReport).filter(EKGReport.SUBJECT_ID==subjectId).all()
