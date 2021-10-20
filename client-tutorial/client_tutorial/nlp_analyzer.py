from pprint import pprint

from ibm_whcs_sdk import annotator_for_clinical_data as acd
from ibm_cloud_sdk_core.authenticators.iam_authenticator import IAMAuthenticator
import os, sys
from nlp_setup import setup
from database_classes import ProblemListItem, ProblemMedication, ProblemProcedure
from typing import List
from ibm_whcs_sdk.annotator_for_clinical_data import AttributeValueAnnotation
from MedActionPotential import MedicationActionPotential
from MedicationActionNames import Names
from .NoteEventDao import NoteEventDao



class Nlp_Analyzer():
    problemItemList: List[ProblemListItem] = []
    #print('blanking problemlist at start')

    noteEventDao:NoteEventDao = NoteEventDao()

    def getActionForMedicationConcept(self, concept: AttributeValueAnnotation) -> MedicationActionPotential:
        """
        Gets an action potential for the attribute based on the probabilities
        @param concept: the Attribute
        @type concept: AttributeValueAnnotation
        @return: The medication Action potential filled in
        @rtype: MedActionPotential
        """
        # get a dictionary of reponse, temporary patch for missing attribute API item
        attribute_dict = concept._to_dict()
        #print('INSIGHT: %s' % (attribute_dict['insightModelData']['medication']['startedEvent']['score']))
        actionPotentials: List[MedicationActionPotential] = []
        actions = Names()
        actionPotentials.append(MedicationActionPotential(actions.START, float(attribute_dict['insightModelData']['medication']['startedEvent']['score'])))
        actionPotentials.append(MedicationActionPotential(actions.DC, float(attribute_dict['insightModelData']['medication']['stoppedEvent']['score'])))
        actionPotentials.append(MedicationActionPotential(actions.MODIFY, float(attribute_dict['insightModelData']['medication']['doseChangedEvent']['score'])))
        actionPotentials.sort()
        highestProbActionItem:MedicationActionPotential = actionPotentials[-1]
        return highestProbActionItem

    def getProblemListItemsFromNoteText(self, textToAnalyze: str, nlpModuleName: str) -> List[ProblemListItem]:
        """
        takes text from a NoteEvent object and returns a list of ProblemListItems. The way this works is assuming a full
        progress note with sections (such as "Assessment and Plan" which is then analyzed for bullet lists of
        problems which are then parsed for the list of those diagnoses (problems)
        @param textToAnalyze: a text block
        @type textToAnalyze:str
        @param nlpModuleName: Most NLP tooling has some sort of workflow id, in ACD this is called a "flow" and this is the ID of that flow
        @type nlpModuleName:str
        @return: A list of ProblemListItems
        @rtype: List[ProblemListItem]
        """
        global problemItemList
        medicationDuplicate:List[str] = []
        problemDuplicate:List[str] = []
        # configure the NLP service (ACD)
        nlpSetup = setup()
        service = nlpSetup.getService()

        # now do the analysis
        try:
            response = service.analyze_with_flow(nlpModuleName, textToAnalyze)

            sectionCounter = 0
            begin = 0
            end = 0
            sectionList: List[acd.Section] = response.sections
            for section in sectionList:
                if section.trigger.section_normalized_name == 'Assessment and plan':
                    # lets cut the text out for this section. We need to add 1 character to the start since there is normally a colon at the end
                    if len(sectionList) == sectionCounter:
                        # this is the last section, important as otherwise we would run off the end of the text
                        begin = section.trigger.end + 1
                        end = len(textToAnalyze) - 1
                    else:
                        # this is not the last section, so cut between them
                        begin = section.trigger.end + 1
                        end = len(textToAnalyze)
                    sectionCounter += 1
            assessmentAndPlan: str = textToAnalyze[begin:end]
            # print(assessmentAndPlan)

            problemListItem: ProblemListItem = None
            # now generate the problem list
            attribute_values: List[AttributeValueAnnotation] = response.attribute_values
            listItem: bool = False
            #if self.problemItemList:
                #print('problem list size: ' + str(len(self.problemItemList)))
            if attribute_values:
                for attribute in attribute_values:
                    if attribute.name and attribute.name == 'Diagnosis' and attribute.covered_text not in problemDuplicate:
                        # print('doing diagnosis: %s in section %s' %(attribute.covered_text, attribute.section_normalized_name))
                        listItem = True
                        if attribute.disambiguation_data.validity == 'VALID' and ('assessment' in attribute.section_normalized_name.lower() or 'plan' in attribute.section_normalized_name.lower() or 'discharge' in attribute.section_normalized_name.lower()):
                            problemListItem = ProblemListItem()
                            problemDuplicate.append(attribute.covered_text)
                            problemListItem.name = attribute.covered_text
                            problemListItem.cui = attribute.snomed_concept_id
                            problemListItem.icd_code = attribute.icd10_code
                            #problemListItem.medications = []
                            self.problemItemList.append(problemListItem)
                            # print('problem list size: '+str(len(self.problemItemList)))
                    if problemListItem and attribute and attribute.section_normalized_name and attribute.name and attribute.name == 'PrescribedMedication'  and ('assessment' in attribute.section_normalized_name.lower() or 'plan' in attribute.section_normalized_name.lower() or 'discharge' in attribute.section_normalized_name.lower()):
                        #pprint(attribute.to_dict())
                        # print('name: '+ attribute.name)
                        medication: ProblemMedication = ProblemMedication()
                        medication.name = attribute.preferred_name
                        medication.rxnorm_id = attribute.rx_norm_id
                        medication.negated = attribute.negated
                        medication.cui = attribute.snomed_concept_id
                        if 'insightModelData' in attribute._to_dict() and 'medication' in attribute._to_dict()['insightModelData']:
                            medication.action = self.getActionForMedicationConcept(attribute)
                        # check for duplicated med names, a common issue when the same term is repeated many time
                        print('Medication: ' + medication.name + ' '+ str(medication.rxnorm_id))
                        if medication and problemListItem:
                            # print('Added Medication: ' + medication.name+ ' to '+ problemListItem.name)
                            problemListItem.getMedicationsForProblem().append(medication)
                        #print('added %s to %a' %(medication.name, problemListItem.name))

                        listItem = False
                    elif  attribute.name and attribute.section_normalized_name and problemListItem and attribute.name.__contains__('DiagnosticProcedure') and attribute.section_normalized_name == 'Assessment and plan':
                        procedure: ProblemProcedure = ProblemProcedure()
                        procedure.name = attribute.preferred_name
                        procedure.cui = attribute.snomed_concept_id
                        procedure.active = not (attribute.negated)
                        problemListItem.getProceduresForProblem().append(procedure)
                        listItem = False
        except acd.ACDException as ex:
            print("Error Occurred:  Code ", ex.code, " Message ", ex.message, " CorrelationId ", ex.correlation_id)
        print('problem list size: ' + str(len(self.problemItemList)))
        return self.problemItemList

    def getProblemsFromNotes(self, subjectId:int, nlpName:str)->List[ProblemListItem]:
        """
        gets the list of problems via ACD in the patient's notes (for prior auth/or other claims processing)
        @param self:
        @type self:
        @param subejctId: the patient's subject_id
        @type subejctId: int
        @return: the list of found active problems in the notes
        @rtype: List[ProblemListItem]
        """
        global noteEventDao
        global problemItemList
        # logging.info("getProblemsFromNotes: Analyzing problems for patient "+ str(subjectId))
        for noteEvent in self.noteEventDao.getAllNotesForPatient(subjectId):
            self.getProblemListItemsFromNoteText(noteEvent.TEXT, nlpName)
            #print('note id: '+str(noteEvent.ROW_ID))
        return self.problemItemList
