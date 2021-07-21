from database_classes import Noteevent, ProblemListItem, Caregiver
from NoteEventDao import NoteEventDao
from nlp_analyzer import Nlp_Analyzer
from ADTDao import AdtDao
from ADTDao import AdtDao
from database_classes import ProblemListItem

noteId:int = 1
noteEventDao = NoteEventDao()
nlpAnalyzer = Nlp_Analyzer()
adtDao = AdtDao()
noteEvent = noteEventDao.getNoteEventById(noteId)
author:Caregiver = adtDao.getCareGiverForCGID(noteEvent.CGID)
print('NOTE TYPE: %s\nWritten By: %s, %s' % (noteEvent.DESCRIPTION, author.last_name, author.first_name))
print('-------------------------------------')
print("PROBLEMS FOUND IN ASSESSMENT AND PLAN:")
for problemListItem in nlpAnalyzer.getProblemListItemsFromNoteText(noteEvent.TEXT,'henry_test_cartridge_v1.0_aap_test_flow'):
    print('Diagnosis: %s ICD10: %s  SNOMED: %s' % (problemListItem.name, problemListItem.icd_code, problemListItem.cui))
