from database_classes import Noteevent, ProblemListItem, Caregiver, Patient
from NoteEventDao import NoteEventDao
from nlp_analyzer import Nlp_Analyzer
from InsuranceDao import InsuranceCompanyDict
from PatientsDao import PatientsDao
from ADTDao import AdtDao
from ADTDao import AdtDao
from database_classes import ProblemListItem, ProblemProcedure, ProblemMedication

noteId:int = 314537
noteEventDao = NoteEventDao()
nlpAnalyzer = Nlp_Analyzer()
adtDao = AdtDao()
patientDao = PatientsDao()
noteEvent = noteEventDao.getNoteEventById(noteId)
patient: Patient = patientDao.getPatient(noteEvent.SUBJECT_ID)
print(patientDao.getPatientSummary(patient))
print('NoteEvent: '+str(noteEvent.ROW_ID))
if noteEvent.CGID:
    author:Caregiver = adtDao.getCareGiverForCGID(noteEvent.CGID)
    print('NOTE TYPE: %s\nWritten By: %s, %s' % (noteEvent.DESCRIPTION, author.last_name, author.first_name))
else:
    print('NOTE TYPE: %s\nWritten By: Unknown Authors' % (noteEvent.DESCRIPTION))
print('-------------------------------------')
print("PROBLEMS FOUND IN ASSESSMENT AND PLAN:")
for problemListItem in nlpAnalyzer.getProblemListItemsFromNoteText(noteEvent.TEXT,'henry_test_cartridge_v1.0_aap_test_flow'):
    print('\n\nDIAGNOSIS: %s ICD10: %s  SNOMED: %s' % (problemListItem.name, problemListItem.icd_code, problemListItem.cui))
    if len(problemListItem.getMedicationsForProblem()) > 0:
        print('\tMEDICATIONS:')
        for medication in problemListItem.getMedicationsForProblem():
            print('\t\t %s - RxNorm: %s ................... predicted action: %s ' % (medication.name, medication.rxnorm_id,  medication.action))
    if len(problemListItem.getProceduresForProblem())>0:
        print('\tPROCEDURES:')
        for procedure in problemListItem.procedures:
            print('\t\t%s - %s' % (procedure.name, procedure.cui))
