import ADTDao
import PatientsDao
from database_classes import Patient

class billing():

    def createHospitalBilling(self):
        """
        create the printed summary of the claims activity for the hospitalization
        :param self:
        :type self:
        :return: nothing
        :rtype: Nonetype
        """
        patient:Patient = PatientsDao.getPatient(959595)
        print(patient.payer)
        print(patient.textSummary())

        adtDao = ADTDao.AdtDao()
        icdDict = adtDao.getICDDefinitions()
        print(len(icdDict.keys()))
        for admission in adtDao.getAdmissionsForSubjectId(patient.SUBJECT_ID):
            print("Admission: %s, Date: %s\n" % (admission.ADMISSION_LOCATION, admission.ADMITTIME.strftime("%m/%d/%Y %H:%M")))
            for drg in adtDao.getDRGsForAdmission(admission.HADM_ID):
                print('\n\n\t - DRG: %s: %s : Severity/Mortality: %d/%d  %s' % (drg.DRG_CODE, drg.DRG_TYPE, drg.DRG_SEVERITY,
                      drg.DRG_MORTALITY, drg.DESCRIPTION))
                print('\t\tICD Codes')
                for icdCode in adtDao.getIcdCodesForAdmission(admission.HADM_ID):
                    print('\t\t%s - %s' % (icdCode.ICD9_CODE, icdDict.get(icdCode.ICD9_CODE).LONG_TITLE))

            print('\n\n\nCPT CODES:\n')
            for cptEvent in adtDao.getCPTEventsForAdmission(admission.HADM_ID):
                print('\t%s %s:  - %s/%s: %s' % (cptEvent.CHARTDATE.strftime("%m/%d/%Y"), cptEvent.CPT_CD, cptEvent.SECTIONHEADER, cptEvent.SUBSECTIONHEADER, cptEvent.DESCRIPTION))
