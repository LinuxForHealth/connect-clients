from ibm_whcs_sdk import annotator_for_clinical_data as acd
from ibm_cloud_sdk_core.authenticators.iam_authenticator import IAMAuthenticator
import os, sys
from nlp_setup import setup
dbClasses = __import__('client-tutorial.database_classes')
from typing import List

class Nlp_Analyzer():
    def getProblemListItemsFromNoteText(self,textToAnalyze:str) -> List[dbClasses.ProblemListItem]:
        """
        takes text from a NoteEvent object and returns a list of ProblemListItems. The way this works is assuming a full
        progress note with sections (such as "Assessment and Plan" which is then analyzed for bullet lists of
        problems which are then parsed for the list of those diagnoses (problems)
        @param textToAnalyze: a text block
        @type textToAnalyze:str
        @return: A list of ProblemListItems
        @rtype: List[ProblemListItem]
        """
