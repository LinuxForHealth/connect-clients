from database_classes import Noteevent, ProblemListItem, Caregiver
from NoteEventDao import NoteEventDao
from nlp_analyzer import Nlp_Analyzer
from ADTDao import AdtDao
from ADTDao import AdtDao
from database_classes import ProblemListItem, ProblemProcedure, ProblemMedication

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
    if len(problemListItem.medicationsForProblem) > 0:
        print('\tMEDICATIONS:')
        for medication in ProblemListItem.medicationsForProblem:
            print('\t\t %s - RxNorm: %s ................... predicted action: %s ' % (medication.name, medication.rxnorm_id,  medication.action))
    if len(problemListItem.procedures)>0:
        print('PROCEDURES:')
        for procedure in problemListItem.procedures:
            print('%s - %s' % (procedure.name, procedure.cui))
