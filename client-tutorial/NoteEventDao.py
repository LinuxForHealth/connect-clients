from databaseUtil import DatabaseUtil
from database_classes import Noteevent, RadiologyReport
from sqlalchemy import select
from typing import List, Dict

class NoteEventDao:
    """
    Is the database access object for the ORM that handles the NoteEvent class (clinical notes). Database access to Notes should always
    go through this class. Given this is for a demo we do not have full CRUD functionality here. Note radiology reporrts and EKGs are also notes, so are handled here
    """

    ession = None

    def __init__(self):
        """
             setup and fetch the database session from the database utility.
        """
        dbUtil = DatabaseUtil()
        self.session = dbUtil.getSession()

    def getAllNoteEvents(self) -> List[Noteevent]:
        """
        get all the noteEvents
        :param self:
        :type self:
        :return: NoteEvents
        :rtype: List[NoteEvent]
        """
        global session
        return self.session.query(Noteevent).all()

    def getAllNotesForPatient(self, SubjectId: int) -> List[Noteevent]:
        """
        gets all the clinical notes for a patient
        :param self:
        :type self:
        :param SubjectId:
        :type SubjectId:
        :return: noteEvents
        :rtype: List[NoteEvent]
        """
        global session
        return self.session.query(Noteevent).filter(Noteevent.SUBJECT_ID==SubjectId).all()

    def getAllRadiologyReports(self) -> List[RadiologyReport]:
        """
        fetches all radiology reports which are similar to noteevents exvept have an additional concept of the impression
        which is the extraction of the impression (or the various names for it) section of the report exctracted out
        :param self:
        :type self:
        :return: radiologyReports
        :rtype: List[RadiologyReport]
        """
        global session
        return self.session.query(RadiologyReport).all()

    def getAllRadiologyReportsForPatient(self, SubjectId: int) -> List[RadiologyReport]:
        """
        Get the radiology reports for a given patient.
        :param self:
        :type self:
        :param SubjectId:
        :type SubjectId:
        :return: radiologyReports
        :rtype: List[RadiologyReport]
        """
        global session
        return self.session.query(RadiologyReport).filter(RadiologyReport.SUBJECT_ID==SubjectId).all()
