from databaseUtil import DatabaseUtil
from database_classes import DLabItem, LabEvent
from typing import List, TypedDict
from sqlalchemy import and_

class DLabItemDict(TypedDict):
    id: int
    name: DLabItem

class LabDao:
    """
    Is the database access object for the ORM that handles the LabEvent class. Database access to Labs should always
    go through this class. Given this is for a demo we do not have full CRUD functionality here.
    """
    session = None

    def __init__(self):
        """
             setup and fetch the database session from the database utility.
        """
        dbUtil = DatabaseUtil()
        self.session = dbUtil.getSession()

    def getAllDLabItems(self) -> DLabItemDict:
        """
        This gets list list of Lab Definitions as a dictionary of dict{itemId, itemdef}. This is the mapping to a lab
        name and LOINC code
        :return: labItemDict
        :rtype: dict(int,DLabItem)
        """
        global session
        labItemDict:DLabItemDict = DLabItemDict()
        for labItem in  self.session.query(DLabItem).all():
            labItemDict[labItem.ITEMID] = labItem
        return labItemDict

    def searchDLabItems(self, searchString:str) -> DLabItemDict:
        global session
        labItemDict: DLabItemDict = DLabItemDict()
        for labItem in self.session.query(DLabItem).filter(DLabItem.LABEL.contains(searchString)).all():
            labItemDict[labItem.ITEMID] = labItem
        return labItemDict

    def getLabsForPatient(self, subjectId: int) -> List[LabEvent]:
        """
        Get all the lab events for a given Patient. The labs need to get mapped to the DItem from @getAllDLabItems for
        filling in the critical fields for FHIR conversion.
        :param subjectId:
        :type subjectId:
        :return: labEvents
        :rtype: List[LabEvent]
        """
        global session
        return self.session.query(LabEvent).filter(LabEvent.SUBJECT_ID==subjectId).all()

    def getSpecificLabForPatient(self, subjectId: int, labItemId: int) -> List[LabEvent]:
        """
        returns the list of labevents for that specific patient for that specific lab (e.g. get me all the sodiums for patient x)
        @param subjectId: the subject id for the patients
        @type subjectId: int
        @param labItemId: the DLabItem.ROW_ID field
        @type labItemId: int
        @return: lab results
        @rtype: List[LabEvent]
        """
        global session
        return self.session.query(LabEvent).filter(and_(LabEvent.SUBJECT_ID == subjectId , LabEvent.ITEMID==labItemId)).all()

    def getLebEventByRowId(self, rowId: int) -> LabEvent:
        """
        Get a specific lab event by its primary key
        :param rowId:
        :type rowId:
        :return: labEvent
        :rtype: LabEvent
        """
        global session
        return self.session.query(LabEvent).filter(LabEvent.ROW_ID == rowId).one()

    def saveLabEvent(self,labEvent:LabEvent)->LabEvent:
        """
        save or update the lab to the database
        @param labEvent: the Lab entity
        @type labEvent: labEvent
        @return: labEvent after database saving
        @rtype: LabEvent
        """
        global session
        self.session.add(labEvent)
        self.session.commit()
        return labEvent
