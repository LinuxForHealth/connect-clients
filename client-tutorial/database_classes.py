# coding: utf-8
from sqlalchemy import orm
from sqlalchemy import Column, ForeignKey, DECIMAL, Date, DateTime, Index, Integer, JSON, String, Text, text
from sqlalchemy.dialects.mysql import INTEGER, MEDIUMINT, MEDIUMTEXT, SMALLINT, TINYINT, VARCHAR
from sqlalchemy.ext.declarative import declarative_base
from typing import List, TypedDict
from MedActionPotential import MedicationActionPotential
from datetime import date, datetime
import string


Base = declarative_base()
metadata = Base.metadata

class Admission(Base):
    __tablename__ = 'ADMISSIONS'
    __table_args__ = (
        Index('ADMISSIONS_IDX01', 'SUBJECT_ID', 'HADM_ID'),
        Index('ADMISSIONS_IDX02', 'ADMITTIME', 'DISCHTIME', 'DEATHTIME')
    )

    ROW_ID = Column(MEDIUMINT, primary_key=True)
    SUBJECT_ID = Column(MEDIUMINT, nullable=False)
    HADM_ID = Column(MEDIUMINT, nullable=False, index=True)
    ADMITTIME = Column(DateTime, nullable=False)
    DISCHTIME = Column(DateTime, nullable=False)
    LENGTH_OF_STAY = Column(Integer, nullable=False, index=True)
    DEATHTIME = Column(DateTime)
    ADMISSION_TYPE = Column(String(50), nullable=False, index=True)
    ADMISSION_LOCATION = Column(String(50), nullable=False)
    DISCHARGE_LOCATION = Column(String(50), nullable=False)
    EDREGTIME = Column(DateTime)
    EDOUTTIME = Column(DateTime)
    DIAGNOSIS = Column(String(255))
    HOSPITAL_EXPIRE_FLAG = Column(TINYINT, nullable=False)
    HAS_CHARTEVENTS_DATA = Column(TINYINT, nullable=False)

    def __str__(self):
        elements = []
        elements.append((self.__class__.__name__+ ': ').upper())
        skip = False
        for key, value in self.__dict__.items():
            if skip:
                elements.append("{key}='{value}'".format(key=key, value=value))
            else:
                skip = True
        return ', '.join(elements)

class Hospital(Base):
    __tablename__ = 'hospital'

    id = Column(MEDIUMINT, primary_key=True, autoincrement=True)
    name = Column(String(256), nullable=False, index=True)
    subsidiary_of_id = Column(MEDIUMINT, ForeignKey('Hospital.id'))
    street = Column(String(256), nullable=False, index=True)
    city = Column(String(128), nullable=False, index=False)
    state = Column(String(2), nullable=False, index=True)
    has_inpatient = Column(TINYINT(1), nullable=False, index=True)
    has_ambulatory = Column(TINYINT(1), nullable=False, index=True)
    website = Column(String(256), nullable=False, index=True)
    fhir_json = Column(String(2000), nullable=False)

    def __str__(self):
        elements = []
        elements.append((self.__class__.__name__+ ': ').upper())
        skip = False
        for key, value in self.__dict__.items():
            if skip:
                elements.append("{key}='{value}'".format(key=key, value=value))
            else:
                skip = True
        return ', '.join(elements)

class Caregiver(Base):
    __tablename__ = 'CAREGIVERS'
    __table_args__ = (
        Index('CAREGIVERS_IDX01', 'CGID', 'LABEL'),
    )

    ROW_ID = Column(MEDIUMINT, primary_key=True)
    CGID = Column(SMALLINT, nullable=False, unique=True)
    first_name = Column(String(128), nullable=False, index=True)
    last_name = Column(VARCHAR(128), nullable=False, index=True)
    NPI_number = Column(String(11), nullable=False, index=True)
    gender = Column(String(16), nullable=False, index=True)
    LABEL = Column(String(15))
    DESCRIPTION = Column(String(30))
    works_for_hospital_id = Column(Integer, ForeignKey('Hospital.id'))
    fhir_json = Column(String(2000), nullable=False)

    def __str__(self):
        elements = []
        elements.append((self.__class__.__name__ + ': ').upper())
        skip = False
        for key, value in self.__dict__.items():
            if skip:
                elements.append("{key}='{value}'".format(key=key, value=value))
            else:
                skip = True
        return ', '.join(elements)

class DCPT(Base):
    __tablename__ = 'D_CPT'

    ROW_ID = Column(TINYINT, primary_key=True)
    CATEGORY = Column(TINYINT, nullable=False)
    SECTIONRANGE = Column(String(100), nullable=False)
    SECTIONHEADER = Column(String(50), nullable=False)
    SUBSECTIONRANGE = Column(String(100), nullable=False, unique=True)
    SUBSECTIONHEADER = Column(String(255), nullable=False)
    CODESUFFIX = Column(String(5))
    MINCODEINSUBSECTION = Column(MEDIUMINT, nullable=False)
    MAXCODEINSUBSECTION = Column(MEDIUMINT, nullable=False, unique=True)

    def __str__(self):
        elements = []
        elements.append((self.__class__.__name__ + ': ').upper())
        skip = False
        for key, value in self.__dict__.items():
            if skip:
                elements.append("{key}='{value}'".format(key=key, value=value))
            else:
                skip = True
        return ', '.join(elements)

class DIcdDiagnoses(Base):
    __tablename__ = 'D_ICD_DIAGNOSES'

    ROW_ID = Column(MEDIUMINT, primary_key=True)
    ICD9_CODE = Column(String(10), nullable=False, unique=True)
    SHORT_TITLE = Column(String(50), nullable=False, index=True)
    LONG_TITLE = Column(String(255), nullable=False)

    def __str__(self):
        elements = []
        elements.append((self.__class__.__name__ + ': ').upper())
        skip = False
        for key, value in self.__dict__.items():
            if skip:
                elements.append("{key}='{value}'".format(key=key, value=value))
            else:
                skip = True
        return ', '.join(elements)

class DItem(Base):
    __tablename__ = 'D_ITEMS'
    __table_args__ = (
        Index('D_ITEMS_idx02', 'LABEL', 'DBSOURCE'),
    )

    ROW_ID = Column(MEDIUMINT, primary_key=True)
    ITEMID = Column(MEDIUMINT, nullable=False, unique=True)
    LABEL = Column(String(200))
    ABBREVIATION = Column(String(100))
    DBSOURCE = Column(String(20), nullable=False)
    LINKSTO = Column(String(50))
    CATEGORY = Column(String(100), index=True)
    UNITNAME = Column(String(100))
    PARAM_TYPE = Column(String(30))
    CONCEPTID = Column(Integer)

    def __str__(self):
        elements = []
        elements.append((self.__class__.__name__ + ': ').upper())
        skip = False
        for key, value in self.__dict__.items():
            if skip:
                elements.append("{key}='{value}'".format(key=key, value=value))
            else:
                skip = True
        return ', '.join(elements)

class DLabItem(Base):
    __tablename__ = 'D_LABITEMS'
    __table_args__ = (
        Index('D_LABITEMS_idx02', 'LABEL', 'FLUID', 'CATEGORY'),
    )

    ROW_ID = Column(MEDIUMINT, primary_key=True)
    ITEMID = Column(SMALLINT, nullable=False, unique=True)
    LABEL = Column(String(100), nullable=False)
    FLUID = Column(String(100), nullable=False)
    CATEGORY = Column(String(100), nullable=False)
    LOINC_CODE = Column(String(100), index=True)

    def __str__(self):
        elements = []
        elements.append((self.__class__.__name__ + ': ').upper())
        skip = False
        for key, value in self.__dict__.items():
            if skip:
                elements.append("{key}='{value}'".format(key=key, value=value))
            else:
                skip = True
        return ', '.join(elements)


class Payer(Base):
    __tablename__ = 'payer'

    id = Column(Integer, primary_key=True)
    Name = Column(VARCHAR(128), index=True)
    plan_type = Column(VARCHAR(32), index=True)
    street = Column(VARCHAR(256), index=False)
    city = Column(VARCHAR(64), index=False)
    state = Column(VARCHAR(2), index=True)
    zip = Column(VARCHAR(16), index=False)
    endpoint_url = Column(VARCHAR(256), index=False)
    fhir_json = Column(JSON)

    def __str__(self):
        elements = []
        elements.append((self.__class__.__name__ + ': ').upper())
        skip = False
        for key, value in self.__dict__.items():
            if skip:
                elements.append("{key}='{value}'".format(key=key, value=value))
            else:
                skip = True
        return ', '.join(elements)


class Patient(Base):
    __tablename__ = 'PATIENTS'

    ROW_ID = Column(MEDIUMINT, primary_key=True)
    SUBJECT_ID = Column(MEDIUMINT, nullable=False, unique=True)
    first_name = Column(String(128), nullable=False, index=True)
    last_name = Column(String(128), nullable=False, index=True)
    street = Column(String(256), nullable=False)
    city = Column(String(256), nullable=False)
    state = Column(String(2), nullable=False, index=True)
    zip = Column(String(10), nullable=False, index=True)
    latitude = Column(DECIMAL(22, 11))
    longitude = Column(DECIMAL(22, 11))
    GENDER = Column(String(5), nullable=False)
    race = Column(String(32), nullable=False, index=True)
    language = Column(String(32), nullable=False, index=True)
    ethnicity = Column(String(64), nullable=False, index=True)
    religion = Column(String(32), nullable=False, index=True)
    marital_status = Column(String(64), nullable=False, index=True)
    insurance = Column(Integer, nullable=False, index=True)
    DOB = Column(Date, nullable=False, index=True)
    DOD = Column(Date)
    DOD_HOSP = Column(Date)
    EXPIRE_FLAG = Column(TINYINT, nullable=False, index=True)
    acd_study_patient = Column(TINYINT(1), nullable=False, index=True, server_default=text("'0'"))
    fhir_json = Column(JSON)

    def calculate_age(self) -> int:
        """
        calculate the age of a patient based on the supplied dob. This of course does not take account time zones (like the person
        was born in singapore and is now in New York which crosses the international date line... (it';'s a demo)
        :return: age in years
        :rtype: int
        """
        today = date.today()
        return today.year - self.DOB.year - ((today.month, today.day) < (self.DOB.month, self.DOB.day))

    def __str__(self):
        elements = []
        elements.append((self.__class__.__name__ + ': ').upper())
        skip = False
        for key, value in self.__dict__.items():
            if skip:
                elements.append("{key}='{value}'".format(key=key, value=value))
            else:
                skip = True
        return ', '.join(elements)

class Prescription(Base):
    __tablename__ = 'PRESCRIPTIONS'
    __table_args__ = (
        Index('PRESCRIPTIONS_idx01', 'SUBJECT_ID', 'HADM_ID'),
        Index('PRESCRIPTIONS_idx05', 'STARTDATE', 'ENDDATE')
    )

    ROW_ID = Column(MEDIUMINT, primary_key=True)
    SUBJECT_ID = Column(MEDIUMINT, nullable=False)
    HADM_ID = Column(MEDIUMINT, nullable=False, index=True)
    ICUSTAY_ID = Column(MEDIUMINT, index=True)
    STARTDATE = Column(DateTime, index=True)
    ENDDATE = Column(DateTime)
    DRUG_TYPE = Column(String(100), nullable=False, index=True)
    DRUG = Column(String(100), index=True)
    DRUG_NAME_POE = Column(String(100))
    DRUG_NAME_GENERIC = Column(String(100))
    FORMULARY_DRUG_CD = Column(String(120))
    GSN = Column(String(200))
    NDC = Column(String(120), index=True)
    rxNormId = Column(String(32), nullable=False, index=True)
    PROD_STRENGTH = Column(String(120))
    DOSE_VAL_RX = Column(String(120))
    DOSE_UNIT_RX = Column(String(120))
    FORM_VAL_DISP = Column(String(120))
    FORM_UNIT_DISP = Column(String(120))
    ROUTE = Column(String(120))
    acd_study_med = Column(TINYINT(1), nullable=False, index=True)
    fhir_json = Column(JSON, nullable=False)

    def __str__(self):
        elements = []
        elements.append((self.__class__.__name__ + ': ').upper())
        skip = False
        for key, value in self.__dict__.items():
            if skip:
                elements.append("{key}='{value}'".format(key=key, value=value))
            else:
                skip = True
        return ', '.join(elements)

class Chartevent(Base):
    __tablename__ = 'chartevents'
    __table_args__ = (
        Index('CHARTEVENTS_idx03', 'CHARTTIME', 'STORETIME'),
        Index('CHARTEVENTS_idx01', 'SUBJECT_ID', 'HADM_ID', 'ICUSTAY_ID')
    )

    ROW_ID = Column(INTEGER, primary_key=True)
    SUBJECT_ID = Column(MEDIUMINT, nullable=False)
    HADM_ID = Column(MEDIUMINT)
    ICUSTAY_ID = Column(MEDIUMINT)
    ITEMID = Column(MEDIUMINT, nullable=False, index=True)
    CHARTTIME = Column(DateTime, nullable=False)
    STORETIME = Column(DateTime)
    CGID = Column(SMALLINT, index=True)
    VALUE = Column(Text)
    VALUENUM = Column(DECIMAL(22, 10))
    VALUEUOM = Column(String(50))
    WARNING = Column(TINYINT)
    ERROR = Column(TINYINT)
    RESULTSTATUS = Column(String(50))
    STOPPED = Column(String(50))
    acd_study = Column(TINYINT(1))

    def __str__(self):
        elements = []
        elements.append((self.__class__.__name__ + ': ').upper())
        skip = False
        for key, value in self.__dict__.items():
            if skip:
                elements.append("{key}='{value}'".format(key=key, value=value))
            else:
                skip = True
        return ', '.join(elements)

class Noteevent(Base):
    __tablename__ = 'noteevents'
    __table_args__ = (
        Index('NOTEEVENTS_idx01', 'SUBJECT_ID', 'HADM_ID'),
        Index('NOTEEVENTS_idx05', 'CATEGORY', 'DESCRIPTION')
    )

    ROW_ID = Column(INTEGER, primary_key=True)
    SUBJECT_ID = Column(MEDIUMINT, nullable=False, index=True)
    HADM_ID = Column(MEDIUMINT, index=True)
    CHARTDATE = Column(Date, nullable=False, index=True)
    CHARTTIME = Column(DateTime)
    STORETIME = Column(DateTime)
    CATEGORY = Column(String(50), nullable=False, index=True)
    DESCRIPTION = Column(String(255), nullable=False, index=True)
    CGID = Column(SMALLINT, index=True)
    ISERROR = Column(TINYINT)
    TEXT = Column(MEDIUMTEXT, index=True)
    acd_study_note = Column(TINYINT(1), nullable=False, index=True)
    fhir_json = Column(MEDIUMTEXT)

    def __str__(self):
        elements = []
        elements.append((self.__class__.__name__ + ': ').upper())
        skip = False
        for key, value in self.__dict__.items():
            if skip:
                elements.append("{key}='{value}'".format(key=key, value=value))
            else:
                skip = True
        return ', '.join(elements)

class CPTEvent(Base):
    __tablename__ = 'CPTEVENTS'
    __table_args__ = (
        Index('CPTEVENTS_idx02', 'CPT_CD', 'TICKET_ID_SEQ'),
        Index('CPTEVENTS_idx01', 'SUBJECT_ID', 'HADM_ID')
    )

    ROW_ID = Column(MEDIUMINT, primary_key=True)
    SUBJECT_ID = Column(ForeignKey('PATIENTS.SUBJECT_ID'), nullable=False)
    HADM_ID = Column(ForeignKey('ADMISSIONS.HADM_ID'), nullable=False, index=True)
    COSTCENTER = Column(String(10), nullable=False)
    CHARTDATE = Column(DateTime)
    CPT_CD = Column(String(10), nullable=False)
    CPT_NUMBER = Column(MEDIUMINT)
    CPT_SUFFIX = Column(String(5))
    TICKET_ID_SEQ = Column(SMALLINT)
    SECTIONHEADER = Column(String(50))
    SUBSECTIONHEADER = Column(String(255))
    DESCRIPTION = Column(String(200), index=True)

    def __str__(self):
        elements = []
        elements.append((self.__class__.__name__ + ': ').upper())
        skip = False
        for key, value in self.__dict__.items():
            if skip:
                elements.append("{key}='{value}'".format(key=key, value=value))
            else:
                skip = True
        return ', '.join(elements)

class DiagnosisIcd(Base):
    __tablename__ = 'DIAGNOSES_ICD'
    __table_args__ = (
        Index('DIAGNOSES_ICD_idx02', 'ICD9_CODE', 'SEQ_NUM'),
        Index('DIAGNOSES_ICD_idx01', 'SUBJECT_ID', 'HADM_ID')
    )

    ROW_ID = Column(MEDIUMINT, primary_key=True)
    SUBJECT_ID = Column(MEDIUMINT, nullable=False)
    HADM_ID = Column(ForeignKey('ADMISSIONS.HADM_ID'), nullable=False, index=True)
    SEQ_NUM = Column(TINYINT)
    ICD9_CODE = Column(String(10))

    def __str__(self):
        elements = []
        elements.append((self.__class__.__name__ + ': ').upper())
        skip = False
        for key, value in self.__dict__.items():
            if skip:
                elements.append("{key}='{value}'".format(key=key, value=value))
            else:
                skip = True
        return ', '.join(elements)

class DRGCode(Base):
    __tablename__ = 'DRGCODES'
    __table_args__ = (
        Index('DRGCODES_idx03', 'DESCRIPTION', 'DRG_SEVERITY'),
        Index('DRGCODES_idx02', 'DRG_CODE', 'DRG_TYPE'),
        Index('DRGCODES_idx01', 'SUBJECT_ID', 'HADM_ID')
    )

    ROW_ID = Column(MEDIUMINT, primary_key=True)
    SUBJECT_ID = Column(ForeignKey('PATIENTS.SUBJECT_ID'), nullable=False)
    HADM_ID = Column(ForeignKey('ADMISSIONS.HADM_ID'), nullable=False, index=True)
    DRG_TYPE = Column(String(20), nullable=False)
    DRG_CODE = Column(String(20), nullable=False)
    DESCRIPTION = Column(String(255), index=True)
    DRG_SEVERITY = Column(TINYINT)
    DRG_MORTALITY = Column(TINYINT)

    def __str__(self):
        elements = []
        elements.append((self.__class__.__name__ + ': ').upper())
        skip = False
        for key, value in self.__dict__.items():
            if skip:
                elements.append("{key}='{value}'".format(key=key, value=value))
            else:
                skip = True
        return ', '.join(elements)

class LabEvent(Base):
    __tablename__ = 'LABEVENTS'
    __table_args__ = (
        Index('LABEVENTS_idx04', 'VALUE', 'VALUENUM'),
        Index('LABEVENTS_idx01', 'SUBJECT_ID', 'HADM_ID'),
        Index('acdnonzero', 'acd_study', 'VALUENUM')
    )

    ROW_ID = Column(INTEGER, primary_key=True)
    SUBJECT_ID = Column(ForeignKey('PATIENTS.SUBJECT_ID'), nullable=False)
    HADM_ID = Column(ForeignKey('ADMISSIONS.HADM_ID'), index=True)
    ITEMID = Column(ForeignKey('D_LABITEMS.ITEMID'), nullable=False, index=True)
    CHARTTIME = Column(DateTime, nullable=False, index=True)
    VALUE = Column(String(200))
    VALUENUM = Column(DECIMAL(22, 10))
    VALUEUOM = Column(String(20))
    FLAG = Column(String(20))
    acd_study = Column(TINYINT(1), nullable=False, index=True, server_default=text("'0'"))
    fhir_json = Column(JSON)

    def __str__(self):
        elements = []
        elements.append((self.__class__.__name__ + ': ').upper())
        skip = False
        for key, value in self.__dict__.items():
            if skip:
                elements.append("{key}='{value}'".format(key=key, value=value))
            else:
                skip = True
        return ', '.join(elements)

class RadiologyReport(Base):
    __tablename__ = 'radiology_reports'

    ROW_ID = Column(INTEGER, primary_key=True)
    SUBJECT_ID = Column(MEDIUMINT, nullable=False, index=True)
    HADM_ID = Column(MEDIUMINT)
    CHARTDATE = Column(Date, nullable=False)
    CHARTTIME = Column(DateTime)
    STORETIME = Column(DateTime)
    CATEGORY = Column(VARCHAR(50), nullable=False, index=True)
    DESCRIPTION = Column(VARCHAR(255), nullable=False)
    CGID = Column(SMALLINT, index=True)
    ISERROR = Column(TINYINT)
    TEXT = Column(MEDIUMTEXT, index=True)
    Impression = Column(String(2048), index=True)
    acd_study_note = Column(TINYINT(1), nullable=False)
    fhir_json = Column(JSON)
    linked_3d_study_id = Column(String(64), nullable=False, index=True)

    def __str__(self):
        elements = []
        elements.append((self.__class__.__name__ + ': ').upper())
        skip = False
        for key, value in self.__dict__.items():
            if skip:
                elements.append("{key}='{value}'".format(key=key, value=value))
            else:
                skip = True
        return ', '.join(elements)

class ProblemMedication(Base):
    __tablename__ = 'problem_medication'

    id = Column(Integer, primary_key=True)
    name = Column(String(256), nullable=False)
    description = Column(String(1024), nullable=False)
    problemListItemId = Column(Integer, nullable=False, index=True)
    rxnorm_id = Column(String(16), nullable=False)
    negated = Column(TINYINT(1), nullable=False)
    cui = Column(String(32), nullable=False)
    action:MedicationActionPotential = None

    def __str__(self):
        elements = []
        elements.append((self.__class__.__name__ + ': ').upper())
        skip = False
        for key, value in self.__dict__.items():
            if skip:
                elements.append("{key}='{value}'".format(key=key, value=value))
            else:
                skip = True
        return ', '.join(elements)

class ProblemProcedure(Base):
    __tablename__ = 'problem_procedure'

    id = Column(Integer, primary_key=True)
    problemListItemId = Column(Integer, nullable=False, index=True)
    name = Column(String(256), nullable=False)
    description = Column(String(1024), nullable=False)
    active = Column(TINYINT(1), nullable=False, index=True)
    cui = Column(String(32), nullable=False)

    def __str__(self):
        elements = []
        elements.append((self.__class__.__name__ + ': ').upper())
        skip = False
        for key, value in self.__dict__.items():
            if skip:
                elements.append("{key}='{value}'".format(key=key, value=value))
            else:
                skip = True
        return ', '.join(elements)

class ProblemListItem(Base):
    __tablename__ = 'problem_list_item'

    # we need a regular init and the special ORM init in case the obejct was made by the ORM
    def __init__(self):
        self.medicationsForProblem: List[ProblemProcedure] = []
        self.procedures: List[ProblemProcedure] = []

    @orm.reconstructor
    def init_on_load(self):
        self.medicationsForProblem: List[ProblemProcedure] = []
        self.procedures: List[ProblemProcedure] = []

    def getMedicationsForProblem(self)->List[ProblemMedication]:
        """
        returns dynamic unmapped medication list
        @return: medicationsForProblem
        @rtype: List[ProblemMedication]
        """
        return self.medicationsForProblem

    def getProceduresForProblem(self)->List[ProblemProcedure]:
        """
        returns dynamic unmapped procedure list
        @return: procedures
        @rtype: List[ProblemProcedure]
        """
        return self.procedures

    id = Column(Integer, primary_key=True)
    name = Column(String(256), nullable=False, index=True)
    icd_code = Column(String(32), nullable=False)
    cui = Column(String(32), nullable=False, index=True)
    note_event_id = Column(Integer, nullable=False, index=True)
    hadm_id = Column(Integer, nullable=False, index=True)

    def __str__(self):
        elements = []
        elements.append((self.__class__.__name__ + ': ').upper())
        skip = False
        for key, value in self.__dict__.items():
            if skip:
                elements.append("{key}='{value}'".format(key=key, value=value))
            else:
                skip = True
        return ', '.join(elements)
