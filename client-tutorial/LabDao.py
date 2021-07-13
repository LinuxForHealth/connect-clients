from databaseUtil import DatabaseUtil
from database_classes import DLabItem, LabEvent
from sqlalchemy import select
from typing import List, TypedDict


class DLabItemDict(TypedDict):
    id: int
    name: str

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
        labItemDict = DLabItemDict()
        for labItem in  self.session.execute(select(DLabItem).all()):
            labItemDict[labItem.ITEMID] = labItem.LABEL
        return labItemDict

    def getLabsForPatient(self, subjectId: int) -> List:
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
