from ibm_whcs_sdk import annotator_for_clinical_data as acd
from ibm_cloud_sdk_core.authenticators.iam_authenticator import IAMAuthenticator
import os, sys
from nlp_setup import setup
from database_classes import ProblemListItem, ProblemMedication, ProblemProcedure
from typing import List
from ibm_whcs_sdk.annotator_for_clinical_data import AttributeValueAnnotation
from MedActionPotential import MedicationActionPotential
from MedicationActionNames import Names


class Nlp_Analyzer():

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
        medicationDuplicate:List[str] = []
        problemDuplicate:List[str] = []
        # configure the NLP service (ACD)
        nlpSetup = setup()
        service = nlpSetup.getService()
        problemItemList: List[ProblemListItem] = []

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
            for attribute in attribute_values:
                if attribute.name == 'Diagnosis' and attribute.covered_text not in problemDuplicate:
                    # print('doing diagnosis: %s'%{attribute.covered_text})
                    listItem = True
                    if attribute.disambiguation_data.validity == 'VALID' and attribute.section_normalized_name == 'Assessment and plan':
                        problemListItem = ProblemListItem()
                        problemDuplicate.append(attribute.covered_text)
                        problemListItem.name = attribute.covered_text
                        problemListItem.cui = attribute.snomed_concept_id
                        problemListItem.icd_code = attribute.icd10_code
                        #problemListItem.medications = []
                        problemItemList.append(problemListItem)
                if attribute.name == 'PrescribedMedication' and ProblemListItem != None and attribute.section_normalized_name == 'Assessment and plan':
                    medication: ProblemMedication = ProblemMedication()
                    medication.name = attribute.preferred_name
                    medication.rxnorm_id = attribute.rx_norm_id
                    medication.negated = attribute.negated
                    medication.cui = attribute.snomed_concept_id
                    medication.action = self.getActionForMedicationConcept(attribute)
                    # check for duplicated med names, a common issue when the same term is repeated many time
                    problemListItem.medicationsForProblem.append(medication)
                    print('added %s to %a' %(medication.name, problemListItem.name))

                    listItem = False
                elif attribute.name == 'ICProcedure' and ProblemListItem != None and attribute.section_normalized_name == 'Assessment and plan':
                    procedure: ProblemProcedure = ProblemProcedure()
                    procedure.name = attribute.preferred_name
                    procedure.cui = attribute.snomed_concept_id
                    procedure.active = not (attribute.negated)
                    problemListItem.procedures.append(procedure)
                    listItem = False

        except acd.ACDException as ex:
            print("Error Occurred:  Code ", ex.code, " Message ", ex.message, " CorrelationId ", ex.correlation_id)
        return problemItemList
