SET FOREIGN_KEY_CHECKS=0;
START TRANSACTION;
SET time_zone = "+00:00";

CREATE DATABASE IF NOT EXISTS `lfh_demo_db` DEFAULT CHARACTER SET utf8 COLLATE utf8_general_ci;
USE `lfh_demo_db`;

DROP TABLE IF EXISTS `ADMISSIONS`;
CREATE TABLE IF NOT EXISTS `ADMISSIONS` (
  `ROW_ID` mediumint UNSIGNED NOT NULL,
  `SUBJECT_ID` mediumint UNSIGNED NOT NULL,
  `HADM_ID` mediumint UNSIGNED NOT NULL,
  `ADMITTIME` datetime NOT NULL,
  `DISCHTIME` datetime NOT NULL,
  `LENGTH_OF_STAY` int NOT NULL,
  `DEATHTIME` datetime DEFAULT NULL,
  `ADMISSION_TYPE` varchar(50) NOT NULL,
  `ADMISSION_LOCATION` varchar(50) NOT NULL,
  `DISCHARGE_LOCATION` varchar(50) NOT NULL,
  `EDREGTIME` datetime DEFAULT NULL,
  `EDOUTTIME` datetime DEFAULT NULL,
  `DIAGNOSIS` varchar(255) DEFAULT NULL,
  `HOSPITAL_EXPIRE_FLAG` tinyint UNSIGNED NOT NULL,
  `HAS_CHARTEVENTS_DATA` tinyint UNSIGNED NOT NULL,
  PRIMARY KEY (`ROW_ID`),
  UNIQUE KEY `ADMISSIONS_HADM_ID` (`HADM_ID`),
  KEY `ADMISSIONS_IDX01` (`SUBJECT_ID`,`HADM_ID`),
  KEY `ADMISSIONS_IDX02` (`ADMITTIME`,`DISCHTIME`,`DEATHTIME`),
  KEY `ADMISSIONS_IDX03` (`ADMISSION_TYPE`),
  KEY `LENGTH_OF_STAY` (`LENGTH_OF_STAY`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4  COLLATE=utf8mb4_unicode_520_ci;

DROP TABLE IF EXISTS `CALLOUT`;
CREATE TABLE IF NOT EXISTS `CALLOUT` (
  `ROW_ID` mediumint UNSIGNED NOT NULL,
  `SUBJECT_ID` mediumint UNSIGNED NOT NULL,
  `HADM_ID` mediumint UNSIGNED NOT NULL,
  `SUBMIT_WARDID` tinyint UNSIGNED DEFAULT NULL,
  `SUBMIT_CAREUNIT` varchar(15) DEFAULT NULL,
  `CURR_WARDID` tinyint UNSIGNED DEFAULT NULL,
  `CURR_CAREUNIT` varchar(15) DEFAULT NULL,
  `CALLOUT_WARDID` tinyint UNSIGNED NOT NULL,
  `CALLOUT_SERVICE` varchar(10) NOT NULL,
  `REQUEST_TELE` tinyint UNSIGNED NOT NULL,
  `REQUEST_RESP` tinyint UNSIGNED NOT NULL,
  `REQUEST_CDIFF` tinyint UNSIGNED NOT NULL,
  `REQUEST_MRSA` tinyint UNSIGNED NOT NULL,
  `REQUEST_VRE` tinyint UNSIGNED NOT NULL,
  `CALLOUT_STATUS` varchar(20) NOT NULL,
  `CALLOUT_OUTCOME` varchar(20) NOT NULL,
  `DISCHARGE_WARDID` tinyint UNSIGNED DEFAULT NULL,
  `ACKNOWLEDGE_STATUS` varchar(20) NOT NULL,
  `CREATETIME` datetime NOT NULL,
  `UPDATETIME` datetime NOT NULL,
  `ACKNOWLEDGETIME` datetime DEFAULT NULL,
  `OUTCOMETIME` datetime NOT NULL,
  `FIRSTRESERVATIONTIME` datetime DEFAULT NULL,
  `CURRENTRESERVATIONTIME` datetime DEFAULT NULL,
  PRIMARY KEY (`ROW_ID`),
  UNIQUE KEY `CALLOUT_CURRENTRESERVATIONTIME` (`CURRENTRESERVATIONTIME`),
  KEY `CALLOUT_IDX01` (`SUBJECT_ID`,`HADM_ID`),
  KEY `CALLOUT_IDX02` (`CURR_CAREUNIT`),
  KEY `CALLOUT_IDX03` (`CALLOUT_SERVICE`),
  KEY `CALLOUT_IDX04` (`CURR_WARDID`,`CALLOUT_WARDID`,`DISCHARGE_WARDID`),
  KEY `CALLOUT_IDX05` (`CALLOUT_STATUS`,`CALLOUT_OUTCOME`),
  KEY `CALLOUT_IDX06` (`CREATETIME`,`UPDATETIME`,`ACKNOWLEDGETIME`,`OUTCOMETIME`),
  KEY `callout_fk_hadm_id` (`HADM_ID`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4  COLLATE=utf8mb4_unicode_520_ci;

DROP TABLE IF EXISTS `CAREGIVERS`;
CREATE TABLE `CAREGIVERS` (
  `ROW_ID` mediumint UNSIGNED NOT NULL,
  `CGID` smallint UNSIGNED NOT NULL,
  `first_name` varchar(128) NOT NULL,
  `last_name` varchar(128) CHARACTER SET utf8 COLLATE utf8_general_ci NOT NULL,
  `NPI_number` varchar(11) NOT NULL,
  `gender` varchar(16) NOT NULL,
  `LABEL` varchar(15) DEFAULT NULL,
  `DESCRIPTION` varchar(30) DEFAULT NULL,
  `works_for_hospital_id` int NOT NULL,
  `fhir_json` json DEFAULT NULL,
   PRIMARY KEY (`ROW_ID`),
   UNIQUE KEY `CAREGIVERS_CGID` (`CGID`),
   KEY `CAREGIVERS_IDX01` (`CGID`,`LABEL`),
   KEY `first_name` (`first_name`),
   KEY `last name` (`last_name`),
   KEY `gender` (`gender`),
   KEY `npinumber` (`NPI_number`),
   KEY `works_for_hospital_id` (`works_for_hospital_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

DROP TABLE IF EXISTS `chartevents`;
CREATE TABLE IF NOT EXISTS `chartevents` (
  `ROW_ID` int UNSIGNED NOT NULL,
  `SUBJECT_ID` mediumint UNSIGNED NOT NULL,
  `HADM_ID` mediumint UNSIGNED DEFAULT NULL,
  `ICUSTAY_ID` mediumint UNSIGNED DEFAULT NULL,
  `ITEMID` mediumint UNSIGNED NOT NULL,
  `CHARTTIME` datetime NOT NULL,
  `STORETIME` datetime DEFAULT NULL,
  `CGID` smallint UNSIGNED DEFAULT NULL,
  `VALUE` text,
  `VALUENUM` decimal(22,10) DEFAULT NULL,
  `VALUEUOM` varchar(50) DEFAULT NULL,
  `WARNING` tinyint UNSIGNED DEFAULT NULL,
  `ERROR` tinyint UNSIGNED DEFAULT NULL,
  `RESULTSTATUS` varchar(50) DEFAULT NULL,
  `STOPPED` varchar(50) DEFAULT NULL,
  `acd_study` tinyint(1) DEFAULT NULL,
  PRIMARY KEY (`ROW_ID`),
  KEY `CHARTEVENTS_idx01` (`SUBJECT_ID`,`HADM_ID`,`ICUSTAY_ID`),
  KEY `CHARTEVENTS_idx02` (`ITEMID`),
  KEY `CHARTEVENTS_idx03` (`CHARTTIME`,`STORETIME`),
  KEY `CHARTEVENTS_idx04` (`CGID`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4  COLLATE=utf8mb4_unicode_520_ci;

DROP TABLE IF EXISTS `coverage_plan_data`;
CREATE TABLE IF NOT EXISTS `coverage_plan_data` (
  `id` int UNSIGNED NOT NULL AUTO_INCREMENT,
  `coverage_id` mediumint UNSIGNED NOT NULL,
  `class` varchar(256) NOT NULL,
  `type` varchar(256) NOT NULL,
  `value` varchar(256) NOT NULL,
  `name` varchar(256) CHARACTER SET utf8 COLLATE utf8_general_ci DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `coverage_id` (`coverage_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4  COLLATE=utf8mb4_unicode_520_ci;

DROP TABLE IF EXISTS `CPTEVENTS`;
CREATE TABLE IF NOT EXISTS `CPTEVENTS` (
  `ROW_ID` mediumint UNSIGNED NOT NULL,
  `SUBJECT_ID` mediumint UNSIGNED NOT NULL,
  `HADM_ID` mediumint UNSIGNED NOT NULL,
  `COSTCENTER` varchar(10) NOT NULL,
  `CHARTDATE` datetime DEFAULT NULL,
  `CPT_CD` varchar(10) NOT NULL,
  `CPT_NUMBER` mediumint UNSIGNED DEFAULT NULL,
  `CPT_SUFFIX` varchar(5) DEFAULT NULL,
  `TICKET_ID_SEQ` smallint UNSIGNED DEFAULT NULL,
  `SECTIONHEADER` varchar(50) DEFAULT NULL,
  `SUBSECTIONHEADER` varchar(255) DEFAULT NULL,
  `DESCRIPTION` varchar(200) DEFAULT NULL,
  PRIMARY KEY (`ROW_ID`),
  KEY `CPTEVENTS_idx01` (`SUBJECT_ID`,`HADM_ID`),
  KEY `CPTEVENTS_idx02` (`CPT_CD`,`TICKET_ID_SEQ`),
  KEY `cptevents_fk_hadm_id` (`HADM_ID`),
  KEY `DESCRIPTION` (`DESCRIPTION`),
  KEY `SUBJECT_ID` (`SUBJECT_ID`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4  COLLATE=utf8mb4_unicode_520_ci;

DROP TABLE IF EXISTS `DATETIMEEVENTS`;
CREATE TABLE IF NOT EXISTS `DATETIMEEVENTS` (
  `ROW_ID` mediumint UNSIGNED NOT NULL,
  `SUBJECT_ID` mediumint UNSIGNED NOT NULL,
  `HADM_ID` mediumint UNSIGNED DEFAULT NULL,
  `ICUSTAY_ID` mediumint UNSIGNED DEFAULT NULL,
  `ITEMID` mediumint UNSIGNED NOT NULL,
  `CHARTTIME` datetime NOT NULL,
  `STORETIME` datetime NOT NULL,
  `CGID` smallint UNSIGNED NOT NULL,
  `VALUE` datetime DEFAULT NULL,
  `VALUEUOM` varchar(50) NOT NULL,
  `WARNING` tinyint UNSIGNED DEFAULT NULL,
  `ERROR` tinyint UNSIGNED DEFAULT NULL,
  `RESULTSTATUS` varchar(50) DEFAULT NULL,
  `STOPPED` varchar(50) DEFAULT NULL,
  PRIMARY KEY (`ROW_ID`),
  KEY `DATETIMEEVENTS_idx01` (`SUBJECT_ID`,`HADM_ID`,`ICUSTAY_ID`),
  KEY `DATETIMEEVENTS_idx02` (`ITEMID`),
  KEY `DATETIMEEVENTS_idx03` (`CHARTTIME`),
  KEY `DATETIMEEVENTS_idx04` (`CGID`),
  KEY `DATETIMEEVENTS_idx05` (`VALUE`),
  KEY `datetimeevents_fk_hadm_id` (`HADM_ID`),
  KEY `datetimeevents_fk_icustay_id` (`ICUSTAY_ID`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4  COLLATE=utf8mb4_unicode_520_ci;

DROP TABLE IF EXISTS `DIAGNOSES_ICD`;
CREATE TABLE IF NOT EXISTS `DIAGNOSES_ICD` (
  `ROW_ID` mediumint UNSIGNED NOT NULL,
  `SUBJECT_ID` mediumint UNSIGNED NOT NULL,
  `HADM_ID` mediumint UNSIGNED NOT NULL,
  `SEQ_NUM` tinyint UNSIGNED DEFAULT NULL,
  `ICD9_CODE` varchar(10) DEFAULT NULL,
  `fhir_json` json DEFAULT NULL,
  PRIMARY KEY (`ROW_ID`),
  KEY `DIAGNOSES_ICD_idx01` (`SUBJECT_ID`,`HADM_ID`),
  KEY `DIAGNOSES_ICD_idx02` (`ICD9_CODE`,`SEQ_NUM`),
  KEY `diagnoses_icd_fk_hadm_id` (`HADM_ID`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4  COLLATE=utf8mb4_unicode_520_ci;

DROP TABLE IF EXISTS `DRGCODES`;
CREATE TABLE IF NOT EXISTS `DRGCODES` (
  `ROW_ID` mediumint UNSIGNED NOT NULL,
  `SUBJECT_ID` mediumint UNSIGNED NOT NULL,
  `HADM_ID` mediumint UNSIGNED NOT NULL,
  `DRG_TYPE` varchar(20) NOT NULL,
  `DRG_CODE` varchar(20) NOT NULL,
  `DESCRIPTION` varchar(255) DEFAULT NULL,
  `DRG_SEVERITY` tinyint UNSIGNED DEFAULT NULL,
  `DRG_MORTALITY` tinyint UNSIGNED DEFAULT NULL,
  PRIMARY KEY (`ROW_ID`),
  KEY `DRGCODES_idx01` (`SUBJECT_ID`,`HADM_ID`),
  KEY `DRGCODES_idx02` (`DRG_CODE`,`DRG_TYPE`),
  KEY `DRGCODES_idx03` (`DESCRIPTION`,`DRG_SEVERITY`),
  KEY `drgcodes_fk_hadm_id` (`HADM_ID`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4  COLLATE=utf8mb4_unicode_520_ci;

DROP TABLE IF EXISTS `D_CPT`;
CREATE TABLE IF NOT EXISTS `D_CPT` (
  `ROW_ID` tinyint UNSIGNED NOT NULL,
  `CATEGORY` tinyint UNSIGNED NOT NULL,
  `SECTIONRANGE` varchar(100) NOT NULL,
  `SECTIONHEADER` varchar(50) NOT NULL,
  `SUBSECTIONRANGE` varchar(100) NOT NULL,
  `SUBSECTIONHEADER` varchar(255) NOT NULL,
  `CODESUFFIX` varchar(5) DEFAULT NULL,
  `MINCODEINSUBSECTION` mediumint UNSIGNED NOT NULL,
  `MAXCODEINSUBSECTION` mediumint UNSIGNED NOT NULL,
  PRIMARY KEY (`ROW_ID`),
  UNIQUE KEY `D_CPT_SUBSECTIONRANGE` (`SUBSECTIONRANGE`),
  UNIQUE KEY `D_CPT_MAXCODEINSUBSECTION` (`MAXCODEINSUBSECTION`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4  COLLATE=utf8mb4_unicode_520_ci;

DROP TABLE IF EXISTS `D_ICD_DIAGNOSES`;
CREATE TABLE IF NOT EXISTS `D_ICD_DIAGNOSES` (
  `ROW_ID` mediumint UNSIGNED NOT NULL,
  `ICD9_CODE` varchar(10) NOT NULL,
  `SHORT_TITLE` varchar(50) NOT NULL,
  `LONG_TITLE` varchar(255) NOT NULL,
  PRIMARY KEY (`ROW_ID`),
  UNIQUE KEY `D_ICD_DIAGNOSES_ICD9_CODE` (`ICD9_CODE`),
  KEY `D_ICD_DIAG_idx02` (`SHORT_TITLE`),
  KEY `ICD9_CODE` (`ICD9_CODE`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4  COLLATE=utf8mb4_unicode_520_ci;

DROP TABLE IF EXISTS `D_ICD_PROCEDURES`;
CREATE TABLE IF NOT EXISTS `D_ICD_PROCEDURES` (
  `ROW_ID` mediumint UNSIGNED NOT NULL,
  `ICD9_CODE` varchar(10) NOT NULL,
  `SHORT_TITLE` varchar(50) NOT NULL,
  `LONG_TITLE` varchar(255) NOT NULL,
  PRIMARY KEY (`ROW_ID`),
  UNIQUE KEY `D_ICD_PROCEDURES_ICD9_CODE` (`ICD9_CODE`),
  UNIQUE KEY `D_ICD_PROCEDURES_SHORT_TITLE` (`SHORT_TITLE`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4  COLLATE=utf8mb4_unicode_520_ci;

DROP TABLE IF EXISTS `D_ITEMS`;
CREATE TABLE IF NOT EXISTS `D_ITEMS` (
  `ROW_ID` mediumint UNSIGNED NOT NULL,
  `ITEMID` mediumint UNSIGNED NOT NULL,
  `LABEL` varchar(200) DEFAULT NULL,
  `ABBREVIATION` varchar(100) DEFAULT NULL,
  `DBSOURCE` varchar(20) NOT NULL,
  `LINKSTO` varchar(50) DEFAULT NULL,
  `CATEGORY` varchar(100) DEFAULT NULL,
  `UNITNAME` varchar(100) DEFAULT NULL,
  `PARAM_TYPE` varchar(30) DEFAULT NULL,
  `CONCEPTID` int DEFAULT NULL,
  PRIMARY KEY (`ROW_ID`),
  UNIQUE KEY `D_ITEMS_ITEMID` (`ITEMID`),
  KEY `D_ITEMS_idx02` (`LABEL`,`DBSOURCE`),
  KEY `D_ITEMS_idx03` (`CATEGORY`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4  COLLATE=utf8mb4_unicode_520_ci;

DROP TABLE IF EXISTS `D_LABITEMS`;
CREATE TABLE IF NOT EXISTS `D_LABITEMS` (
  `ROW_ID` mediumint UNSIGNED NOT NULL,
  `ITEMID` smallint UNSIGNED NOT NULL,
  `LABEL` varchar(100) NOT NULL,
  `FLUID` varchar(100) NOT NULL,
  `CATEGORY` varchar(100) NOT NULL,
  `LOINC_CODE` varchar(100) DEFAULT NULL,
  PRIMARY KEY (`ROW_ID`),
  UNIQUE KEY `D_LABITEMS_ITEMID` (`ITEMID`),
  KEY `D_LABITEMS_idx02` (`LABEL`,`FLUID`,`CATEGORY`),
  KEY `D_LABITEMS_idx03` (`LOINC_CODE`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4  COLLATE=utf8mb4_unicode_520_ci;

DROP TABLE IF EXISTS `echo_reports`;
CREATE TABLE IF NOT EXISTS `echo_reports` (
  `ROW_ID` int UNSIGNED NOT NULL,
  `SUBJECT_ID` mediumint UNSIGNED NOT NULL,
  `HADM_ID` mediumint UNSIGNED DEFAULT NULL,
  `CHARTDATE` date NOT NULL,
  `CHARTTIME` datetime DEFAULT NULL,
  `STORETIME` datetime DEFAULT NULL,
  `CATEGORY` varchar(50) CHARACTER SET utf8 NOT NULL,
  `DESCRIPTION` varchar(255) CHARACTER SET utf8 NOT NULL,
  `CGID` smallint UNSIGNED DEFAULT NULL,
  `ISERROR` tinyint UNSIGNED DEFAULT NULL,
  `TEXT` mediumtext CHARACTER SET utf8,
  `Impression` varchar(2048) DEFAULT NULL,
  `acd_study_note` tinyint(1) NOT NULL,
  `fhir_json` JSON DEFAULT NULL,
  PRIMARY KEY (`ROW_ID`),
  KEY `SUBJECT_ID` (`SUBJECT_ID`),
  KEY `CHARTDATE` (`CHARTDATE`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4  COLLATE=utf8mb4_unicode_520_ci;

DROP TABLE IF EXISTS `ekg_reports`;
CREATE TABLE IF NOT EXISTS `ekg_reports` (
  `ROW_ID` int UNSIGNED NOT NULL,
  `SUBJECT_ID` mediumint UNSIGNED NOT NULL,
  `HADM_ID` mediumint UNSIGNED DEFAULT NULL,
  `CHARTDATE` date NOT NULL,
  `CHARTTIME` datetime DEFAULT NULL,
  `STORETIME` datetime DEFAULT NULL,
  `CATEGORY` varchar(50) CHARACTER SET utf8 NOT NULL,
  `DESCRIPTION` varchar(255) CHARACTER SET utf8 NOT NULL,
  `CGID` smallint UNSIGNED DEFAULT NULL,
  `ISERROR` tinyint UNSIGNED DEFAULT NULL,
  `TEXT` mediumtext CHARACTER SET utf8,
  `acd_study_note` tinyint(1) NOT NULL,
  `fhir_json` JSON DEFAULT NULL,
  PRIMARY KEY (`ROW_ID`),
  KEY `SUBJECT_ID` (`SUBJECT_ID`),
  KEY `CHARTDATE` (`CHARTDATE`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4  COLLATE=utf8mb4_unicode_520_ci;

DROP TABLE IF EXISTS `eligibility_request`;
CREATE TABLE IF NOT EXISTS `eligibility_request` (
  `id` int UNSIGNED NOT NULL AUTO_INCREMENT,
  `request_date` date NOT NULL DEFAULT '2021-09-20',
  `requestor_id` int NOT NULL,
  `requestor_type` varchar(64) NOT NULL,
  `requestor_name` varchar(256) DEFAULT NULL,
  `request_service_type` varchar(64) NOT NULL,
  `request_purpose` varchar(128) CHARACTER SET utf8 COLLATE utf8_general_ci NOT NULL,
  `patient_id` int UNSIGNED NOT NULL,
  `payer_id` int NOT NULL,
  `payer_plan_id` int NOT NULL,
  `member_id` bigint NOT NULL,
  `coverage_option_1` varchar(256) NOT NULL,
  `coverage_option_2` varchar(256) NOT NULL,
  `coverage_option_3` varchar(256) NOT NULL,
  `processed` tinyint(1) NOT NULL DEFAULT '0',
  `fhir_json` varchar(2048) CHARACTER SET utf8 COLLATE utf8_general_ci DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `payer_id` (`payer_id`),
  KEY `patient_id` (`patient_id`),
  KEY `procesed` (`processed`),
  KEY `request_date` (`request_date`),
  KEY `requestor_id` (`requestor_id`),
  KEY `requestor_type` (`requestor_type`),
  KEY `request_service_type` (`request_service_type`),
  KEY `request_type` (`request_purpose`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4  COLLATE=utf8mb4_unicode_520_ci;

DROP TABLE IF EXISTS `eligibility_request_response`;
CREATE TABLE IF NOT EXISTS `eligibility_request_response` (
  `id` int NOT NULL AUTO_INCREMENT,
  `patient_id` int UNSIGNED NOT NULL,
  `payer_id` int NOT NULL,
  `eligibility_request_id` int UNSIGNED NOT NULL,
  `value` tinyint(1) NOT NULL,
  `outcome` varchar(32) NOT NULL,
  `disposition` varchar(256) NOT NULL,
  `comment` varchar(1024) NOT NULL,
  `fhir_json` JSON DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `patient_id` (`patient_id`),
  KEY `payer_id` (`payer_id`),
  KEY `eligibility_request_id` (`eligibility_request_id`),
  KEY `value` (`value`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4  COLLATE=utf8mb4_unicode_520_ci;

DROP TABLE IF EXISTS `geo_location`;
CREATE TABLE IF NOT EXISTS `geo_location` (
  `id` int NOT NULL AUTO_INCREMENT,
  `zip` varchar(16) NOT NULL,
  `city` varchar(64) NOT NULL,
  `state` varchar(2) NOT NULL,
  `latitude` decimal(22,11) NOT NULL,
  `longitude` decimal(22,11) NOT NULL,
  `multiplier` int NOT NULL,
  PRIMARY KEY (`id`),
  KEY `zip` (`zip`),
  KEY `city` (`city`),
  KEY `state` (`state`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4  COLLATE=utf8mb4_unicode_520_ci;

DROP TABLE IF EXISTS `hospital`;
CREATE TABLE IF NOT EXISTS `hospital` (
  `id` int NOT NULL AUTO_INCREMENT,
  `Name` varchar(256) NOT NULL,
  `subsidiary_of_id` int DEFAULT NULL,
  `street` varchar(256) NOT NULL,
  `city` varchar(128) NOT NULL,
  `state` varchar(2) NOT NULL,
  `zip` varchar(16) NOT NULL,
  `country` varchar(128) NOT NULL,
  `telecom` varchar(64) NOT NULL,
  `has_inpatient` tinyint(1) NOT NULL,
  `has_ambulatory` int NOT NULL,
  `website` varchar(256) NOT NULL,
  `fhir_json` JSON DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `subsidiary_of_id` (`subsidiary_of_id`),
  KEY `state` (`state`),
  KEY `has_inpatient` (`has_inpatient`),
  KEY `has_ambulatory` (`has_ambulatory`),
  KEY `country` (`country`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4  COLLATE=utf8mb4_unicode_520_ci;

DROP TABLE IF EXISTS `ICUSTAYS`;
CREATE TABLE IF NOT EXISTS `ICUSTAYS` (
  `ROW_ID` mediumint UNSIGNED NOT NULL,
  `SUBJECT_ID` mediumint UNSIGNED NOT NULL,
  `HADM_ID` mediumint UNSIGNED NOT NULL,
  `ICUSTAY_ID` mediumint UNSIGNED NOT NULL,
  `DBSOURCE` varchar(20) NOT NULL,
  `FIRST_CAREUNIT` varchar(20) NOT NULL,
  `LAST_CAREUNIT` varchar(20) NOT NULL,
  `FIRST_WARDID` tinyint UNSIGNED NOT NULL,
  `LAST_WARDID` tinyint UNSIGNED NOT NULL,
  `INTIME` datetime NOT NULL,
  `OUTTIME` datetime DEFAULT NULL,
  `LOS` decimal(22,10) DEFAULT NULL,
  PRIMARY KEY (`ROW_ID`),
  UNIQUE KEY `ICUSTAYS_ICUSTAY_ID` (`ICUSTAY_ID`),
  KEY `ICUSTAYS_idx01` (`SUBJECT_ID`,`HADM_ID`),
  KEY `ICUSTAYS_idx02` (`ICUSTAY_ID`,`DBSOURCE`),
  KEY `ICUSTAYS_idx03` (`LOS`),
  KEY `ICUSTAYS_idx04` (`FIRST_CAREUNIT`),
  KEY `ICUSTAYS_idx05` (`LAST_CAREUNIT`),
  KEY `icustays_fk_hadm_id` (`HADM_ID`),
  KEY `INTIME` (`INTIME`),
  KEY `INTIME_2` (`INTIME`),
  KEY `LOS` (`LOS`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4  COLLATE=utf8mb4_unicode_520_ci;

DROP TABLE IF EXISTS `INPUTEVENTS_CV`;
CREATE TABLE IF NOT EXISTS `INPUTEVENTS_CV` (
  `ROW_ID` int UNSIGNED NOT NULL,
  `SUBJECT_ID` mediumint UNSIGNED NOT NULL,
  `HADM_ID` mediumint UNSIGNED DEFAULT NULL,
  `ICUSTAY_ID` mediumint UNSIGNED DEFAULT NULL,
  `CHARTTIME` datetime NOT NULL,
  `ITEMID` smallint UNSIGNED NOT NULL,
  `AMOUNT` decimal(22,10) DEFAULT NULL,
  `AMOUNTUOM` varchar(30) DEFAULT NULL,
  `RATE` decimal(22,10) DEFAULT NULL,
  `RATEUOM` varchar(30) DEFAULT NULL,
  `STORETIME` datetime NOT NULL,
  `CGID` smallint UNSIGNED DEFAULT NULL,
  `ORDERID` mediumint UNSIGNED NOT NULL,
  `LINKORDERID` mediumint UNSIGNED NOT NULL,
  `STOPPED` varchar(30) DEFAULT NULL,
  `NEWBOTTLE` tinyint UNSIGNED DEFAULT NULL,
  `ORIGINALAMOUNT` decimal(22,10) DEFAULT NULL,
  `ORIGINALAMOUNTUOM` varchar(30) DEFAULT NULL,
  `ORIGINALROUTE` varchar(30) DEFAULT NULL,
  `ORIGINALRATE` decimal(22,10) DEFAULT NULL,
  `ORIGINALRATEUOM` varchar(30) DEFAULT NULL,
  `ORIGINALSITE` varchar(30) DEFAULT NULL,
  PRIMARY KEY (`ROW_ID`),
  KEY `INPUTEVENTS_CV_idx01` (`SUBJECT_ID`,`HADM_ID`),
  KEY `INPUTEVENTS_CV_idx03` (`CHARTTIME`,`STORETIME`),
  KEY `INPUTEVENTS_CV_idx04` (`ITEMID`),
  KEY `INPUTEVENTS_CV_idx05` (`RATE`),
  KEY `INPUTEVENTS_CV_idx06` (`AMOUNT`),
  KEY `INPUTEVENTS_CV_idx07` (`CGID`),
  KEY `INPUTEVENTS_CV_idx08` (`LINKORDERID`,`ORDERID`),
  KEY `inputevents_cv_fk_hadm_id` (`HADM_ID`),
  KEY `inputevents_cv_fk_icustay_id` (`ICUSTAY_ID`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4  COLLATE=utf8mb4_unicode_520_ci;

DROP TABLE IF EXISTS `INPUTEVENTS_MV`;
CREATE TABLE IF NOT EXISTS `INPUTEVENTS_MV` (
  `ROW_ID` mediumint UNSIGNED NOT NULL,
  `SUBJECT_ID` mediumint UNSIGNED NOT NULL,
  `HADM_ID` mediumint UNSIGNED NOT NULL,
  `ICUSTAY_ID` mediumint UNSIGNED DEFAULT NULL,
  `STARTTIME` datetime NOT NULL,
  `ENDTIME` datetime NOT NULL,
  `ITEMID` mediumint UNSIGNED NOT NULL,
  `AMOUNT` decimal(22,10) NOT NULL,
  `AMOUNTUOM` varchar(30) NOT NULL,
  `RATE` decimal(22,10) DEFAULT NULL,
  `RATEUOM` varchar(30) DEFAULT NULL,
  `STORETIME` datetime NOT NULL,
  `CGID` smallint UNSIGNED NOT NULL,
  `ORDERID` mediumint UNSIGNED NOT NULL,
  `LINKORDERID` mediumint UNSIGNED NOT NULL,
  `ORDERCATEGORYNAME` varchar(100) NOT NULL,
  `SECONDARYORDERCATEGORYNAME` varchar(100) DEFAULT NULL,
  `ORDERCOMPONENTTYPEDESCRIPTION` varchar(20) NOT NULL,
  `ORDERCATEGORYDESCRIPTION` varchar(50) NOT NULL,
  `PATIENTWEIGHT` decimal(22,10) NOT NULL,
  `TOTALAMOUNT` decimal(22,10) DEFAULT NULL,
  `TOTALAMOUNTUOM` varchar(255) DEFAULT NULL,
  `ISOPENBAG` tinyint UNSIGNED NOT NULL,
  `CONTINUEINNEXTDEPT` tinyint UNSIGNED NOT NULL,
  `CANCELREASON` tinyint UNSIGNED NOT NULL,
  `STATUSDESCRIPTION` varchar(30) NOT NULL,
  `COMMENTS_EDITEDBY` varchar(30) DEFAULT NULL,
  `COMMENTS_CANCELEDBY` varchar(30) DEFAULT NULL,
  `COMMENTS_DATE` datetime DEFAULT NULL,
  `ORIGINALAMOUNT` decimal(22,10) NOT NULL,
  `ORIGINALRATE` decimal(22,10) NOT NULL,
  PRIMARY KEY (`ROW_ID`),
  KEY `INPUTEVENTS_MV_idx01` (`SUBJECT_ID`,`HADM_ID`),
  KEY `INPUTEVENTS_MV_idx02` (`ICUSTAY_ID`),
  KEY `INPUTEVENTS_MV_idx03` (`ENDTIME`,`STARTTIME`),
  KEY `INPUTEVENTS_MV_idx04` (`ITEMID`),
  KEY `INPUTEVENTS_MV_idx05` (`RATE`),
  KEY `INPUTEVENTS_MV_idx06` (`AMOUNT`),
  KEY `INPUTEVENTS_MV_idx07` (`CGID`),
  KEY `INPUTEVENTS_MV_idx08` (`LINKORDERID`,`ORDERID`),
  KEY `inputevents_mv_fk_hadm_id` (`HADM_ID`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4  COLLATE=utf8mb4_unicode_520_ci;

DROP TABLE IF EXISTS `LABEVENTS`;
CREATE TABLE IF NOT EXISTS `LABEVENTS` (
  `ROW_ID` int UNSIGNED NOT NULL,
  `SUBJECT_ID` mediumint UNSIGNED NOT NULL,
  `HADM_ID` mediumint UNSIGNED DEFAULT NULL,
  `ITEMID` smallint UNSIGNED NOT NULL,
  `CHARTTIME` datetime NOT NULL,
  `VALUE` varchar(200) DEFAULT NULL,
  `VALUENUM` decimal(22,10) DEFAULT NULL,
  `VALUEUOM` varchar(20) DEFAULT NULL,
  `FLAG` varchar(20) DEFAULT NULL,
  `acd_study` tinyint(1) NOT NULL DEFAULT '0',
  `fhir_json` json DEFAULT NULL,
  PRIMARY KEY (`ROW_ID`),
  KEY `LABEVENTS_idx01` (`SUBJECT_ID`,`HADM_ID`),
  KEY `LABEVENTS_idx02` (`ITEMID`),
  KEY `LABEVENTS_idx03` (`CHARTTIME`),
  KEY `LABEVENTS_idx04` (`VALUE`,`VALUENUM`),
  KEY `labevents_fk_hadm_id` (`HADM_ID`),
  KEY `acd_study` (`acd_study`),
  KEY `acdnonzero` (`acd_study`,`VALUENUM`) USING BTREE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4  COLLATE=utf8mb4_unicode_520_ci;

DROP TABLE IF EXISTS `medication_action_potential`;
CREATE TABLE IF NOT EXISTS `medication_action_potential` (
  `id` int NOT NULL AUTO_INCREMENT,
  `name` varchar(255) NOT NULL,
  `probability` float NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4  COLLATE=utf8mb4_unicode_520_ci;

DROP TABLE IF EXISTS `medication_adverse_event`;
CREATE TABLE IF NOT EXISTS `medication_adverse_event` (
  `id` int NOT NULL AUTO_INCREMENT,
  `note_row_id` int NOT NULL,
  `hadm_id` int NOT NULL,
  `ade_drug_name` varchar(256) NOT NULL,
  `rx_norm_id` varchar(16) NOT NULL,
  `ade_reaction` varchar(256) NOT NULL,
  `start_index` int NOT NULL,
  `end_index` int NOT NULL,
  `ade_score` float NOT NULL,
  `ade_valid` tinyint(1) NOT NULL,
  `ade_span` varchar(4096) NOT NULL,
  `ambiguous_phrase` tinyint(1) NOT NULL,
  PRIMARY KEY (`id`),
  KEY `note_row_id` (`note_row_id`),
  KEY `hadm_id` (`hadm_id`),
  KEY `rx_norm_id` (`rx_norm_id`),
  KEY `ambiguous_phrase` (`ambiguous_phrase`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_general_ci COMMENT='table to extract the ADEs from NoteEvents';

DROP TABLE IF EXISTS `merged_diagnoses`;
CREATE TABLE IF NOT EXISTS `merged_diagnoses` (
  `Row_ID` mediumint UNSIGNED NOT NULL,
  `SUBJECT_ID` mediumint UNSIGNED NOT NULL,
  `HADM_ID` mediumint UNSIGNED NOT NULL,
  `SEQ_NUM` tinyint UNSIGNED DEFAULT NULL,
  `ICD9_CODE` varchar(10) CHARACTER SET utf8 NOT NULL,
  `short_title` varchar(50) CHARACTER SET utf8 NOT NULL,
  `long_title` varchar(255) CHARACTER SET utf8 NOT NULL,
  PRIMARY KEY (`Row_ID`) USING BTREE,
  KEY `subject` (`SUBJECT_ID`) USING BTREE,
  KEY `icd` (`ICD9_CODE`) USING BTREE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4  COLLATE=utf8mb4_unicode_520_ci;

DROP TABLE IF EXISTS `MICROBIOLOGYEVENTS`;
CREATE TABLE IF NOT EXISTS `MICROBIOLOGYEVENTS` (
  `ROW_ID` mediumint UNSIGNED NOT NULL,
  `SUBJECT_ID` mediumint UNSIGNED NOT NULL,
  `HADM_ID` mediumint UNSIGNED DEFAULT NULL,
  `CHARTDATE` datetime NOT NULL,
  `CHARTTIME` datetime DEFAULT NULL,
  `SPEC_ITEMID` mediumint UNSIGNED DEFAULT NULL,
  `SPEC_TYPE_DESC` varchar(100) NOT NULL,
  `ORG_ITEMID` mediumint UNSIGNED DEFAULT NULL,
  `ORG_NAME` varchar(100) DEFAULT NULL,
  `ISOLATE_NUM` tinyint UNSIGNED DEFAULT NULL,
  `AB_ITEMID` mediumint UNSIGNED DEFAULT NULL,
  `AB_NAME` varchar(30) DEFAULT NULL,
  `DILUTION_TEXT` varchar(10) DEFAULT NULL,
  `DILUTION_COMPARISON` varchar(20) DEFAULT NULL,
  `DILUTION_VALUE` smallint UNSIGNED DEFAULT NULL,
  `INTERPRETATION` varchar(5) DEFAULT NULL,
  PRIMARY KEY (`ROW_ID`),
  KEY `MICROBIOLOGYEVENTS_idx01` (`SUBJECT_ID`,`HADM_ID`),
  KEY `MICROBIOLOGYEVENTS_idx02` (`CHARTDATE`,`CHARTTIME`),
  KEY `MICROBIOLOGYEVENTS_idx03` (`SPEC_ITEMID`,`ORG_ITEMID`,`AB_ITEMID`),
  KEY `microbiologyevents_fk_hadm_id` (`HADM_ID`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4  COLLATE=utf8mb4_unicode_520_ci;

DROP TABLE IF EXISTS `microbiology_reports`;
CREATE TABLE IF NOT EXISTS `microbiology_reports` (
  `ROW_ID` int NOT NULL AUTO_INCREMENT,
  `SUBJECT_ID` int NOT NULL,
  `HADM_ID` int NOT NULL,
  `CHARTDATE` datetime NOT NULL,
  `SPEC_ITEMID` int DEFAULT NULL,
  `SPEC_TYPE_DESC` varchar(64) NOT NULL,
  `ORG_ITEMID` int NOT NULL,
  `ORG_NAME` varchar(128) NOT NULL,
  `TEXT` text CHARACTER SET utf8 COLLATE utf8_general_ci NOT NULL,
  `fhir_json` json DEFAULT NULL,
   PRIMARY KEY (`ROW_ID`),
  KEY `SUBJECT_ID` (`SUBJECT_ID`),
  KEY `HADM_ID` (`HADM_ID`),
  KEY `SPEC_TYPE_DESC` (`SPEC_TYPE_DESC`),
  KEY `ORG_NAME` (`ORG_NAME`),
  KEY `CHARTDATE` (`CHARTDATE`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_general_ci COMMENT='Collated microbiology reports';

DROP TABLE IF EXISTS `military_info`;
CREATE TABLE IF NOT EXISTS `military_info` (
  `id` int NOT NULL AUTO_INCREMENT,
  `subject_id` int NOT NULL,
  `service` varchar(32) CHARACTER SET utf8 COLLATE utf8_general_ci NOT NULL,
  `rank` varchar(2) CHARACTER SET utf8 COLLATE utf8_general_ci NOT NULL,
  `unit` varchar(128) NOT NULL,
  `home_base` varchar(128) NOT NULL,
  `reserve` tinyint(1) NOT NULL,
  `national_guard` tinyint(1) NOT NULL,
  `special_handling` tinyint(1) NOT NULL,
  PRIMARY KEY (`id`),
  KEY `service` (`service`),
  KEY `reserve` (`reserve`),
  KEY `national_guard` (`national_guard`),
  KEY `home_base` (`home_base`),
  KEY `special_handling` (`special_handling`),
  KEY `subject_id` (`subject_id`),
  KEY `rank` (`rank`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4  COLLATE=utf8mb4_unicode_520_ci;

DROP TABLE IF EXISTS `noteevents`;
CREATE TABLE IF NOT EXISTS `noteevents` (
  `ROW_ID` int UNSIGNED NOT NULL,
  `SUBJECT_ID` mediumint UNSIGNED NOT NULL,
  `HADM_ID` mediumint UNSIGNED DEFAULT NULL,
  `CHARTDATE` date NOT NULL,
  `CHARTTIME` datetime DEFAULT NULL,
  `STORETIME` datetime DEFAULT NULL,
  `CATEGORY` varchar(50) NOT NULL,
  `DESCRIPTION` varchar(255) NOT NULL,
  `CGID` smallint UNSIGNED DEFAULT NULL,
  `ISERROR` tinyint UNSIGNED DEFAULT NULL,
  `TEXT` mediumtext,
  `acd_study_note` tinyint(1) NOT NULL,
  `fhir_json` json DEFAULT NULL,
  PRIMARY KEY (`ROW_ID`),
  KEY `NOTEEVENTS_idx01` (`SUBJECT_ID`,`HADM_ID`),
  KEY `NOTEEVENTS_idx02` (`CHARTDATE`),
  KEY `NOTEEVENTS_idx03` (`CGID`),
  KEY `NOTEEVENTS_idx05` (`CATEGORY`,`DESCRIPTION`),
  KEY `noteevents_fk_hadm_id` (`HADM_ID`),
  KEY `CATEGORY` (`CATEGORY`),
  KEY `description` (`DESCRIPTION`) USING BTREE,
  KEY `acd_study_note` (`acd_study_note`),
  KEY `SUBJECT_ID` (`SUBJECT_ID`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4  COLLATE=utf8mb4_unicode_520_ci;

DROP TABLE IF EXISTS `note_annotations`;
CREATE TABLE IF NOT EXISTS `note_annotations` (
  `row_id` int NOT NULL,
  `subject_id` int NOT NULL,
  `hadm_id` int NOT NULL,
  `ADVANCED_CANCER` tinyint(1) NOT NULL,
  `ADVANCED_HEART_DISEASE` tinyint(1) NOT NULL,
  `ADVANCED_LUNG_DISEASE` tinyint(1) NOT NULL,
  `ALCOHOL_ABUSE` tinyint(1) NOT NULL,
  `BATCH_ID` date NOT NULL,
  `CHRONIC_NEUROLOGICAL_DYSTROPHIES` tinyint(1) NOT NULL,
  `CHRONIC_PAIN_FIBROMYALGIA` tinyint(1) NOT NULL,
  `DEMENTIA` tinyint(1) NOT NULL,
  `DEPRESSION` tinyint(1) NOT NULL,
  `DEVELOPMENTAL_DELAY_RETARDATION` tinyint(1) NOT NULL,
  `NON_ADHERENCE` tinyint(1) NOT NULL,
  `NONE` tinyint(1) NOT NULL,
  `OBESITY` tinyint(1) NOT NULL,
  `OPERATOR` varchar(16) NOT NULL,
  `OTHER_SUBSTANCE_ABUSE` tinyint(1) NOT NULL,
  `SCHIZOPHRENIA_AND_OTHER_PSYCHIATRIC_DISORDERS` tinyint(1) NOT NULL,
  `UNSURE` tinyint(1) NOT NULL,
  PRIMARY KEY (`row_id`),
  KEY `subject_id` (`subject_id`),
  KEY `hadm_id` (`hadm_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_general_ci COMMENT='expert annotations for notes';

DROP TABLE IF EXISTS `OUTPUTEVENTS`;
CREATE TABLE IF NOT EXISTS `OUTPUTEVENTS` (
  `ROW_ID` mediumint UNSIGNED NOT NULL,
  `SUBJECT_ID` mediumint UNSIGNED NOT NULL,
  `HADM_ID` mediumint UNSIGNED DEFAULT NULL,
  `ICUSTAY_ID` mediumint UNSIGNED DEFAULT NULL,
  `CHARTTIME` datetime NOT NULL,
  `ITEMID` mediumint UNSIGNED NOT NULL,
  `VALUE` decimal(22,10) DEFAULT NULL,
  `VALUEUOM` varchar(30) DEFAULT NULL,
  `STORETIME` datetime NOT NULL,
  `CGID` smallint UNSIGNED NOT NULL,
  `STOPPED` varchar(30) DEFAULT NULL,
  `NEWBOTTLE` char(1) DEFAULT NULL,
  `ISERROR` tinyint UNSIGNED DEFAULT NULL,
  PRIMARY KEY (`ROW_ID`),
  KEY `OUTPUTEVENTS_idx01` (`SUBJECT_ID`,`HADM_ID`),
  KEY `OUTPUTEVENTS_idx02` (`ICUSTAY_ID`),
  KEY `OUTPUTEVENTS_idx03` (`CHARTTIME`,`STORETIME`),
  KEY `OUTPUTEVENTS_idx04` (`ITEMID`),
  KEY `OUTPUTEVENTS_idx05` (`VALUE`),
  KEY `OUTPUTEVENTS_idx06` (`CGID`),
  KEY `outputevents_fk_hadm_id` (`HADM_ID`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4  COLLATE=utf8mb4_unicode_520_ci;

DROP TABLE IF EXISTS `pathways`;
CREATE TABLE IF NOT EXISTS `pathways` (
  `id` int NOT NULL AUTO_INCREMENT,
  `name` varchar(128) NOT NULL,
  `description` varchar(512) NOT NULL,
  `activatingattributecode` varchar(128) NOT NULL,
  PRIMARY KEY (`id`),
  KEY `name` (`name`),
  KEY `activatingattributecode` (`activatingattributecode`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4  COLLATE=utf8mb4_unicode_520_ci;

DROP TABLE IF EXISTS `pathway_treatments`;
CREATE TABLE IF NOT EXISTS `pathway_treatments` (
  `id` int NOT NULL AUTO_INCREMENT,
  `type` varchar(128) NOT NULL,
  `pathway_id` int NOT NULL,
  `description` varchar(512) NOT NULL,
  `action_to_do` varchar(32) NOT NULL,
  `concept_id` varchar(128) NOT NULL,
  PRIMARY KEY (`id`),
  KEY `type` (`type`),
  KEY `action_to_do` (`action_to_do`),
  KEY `concept_id` (`concept_id`),
  KEY `pathway_id` (`pathway_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4  COLLATE=utf8mb4_unicode_520_ci;

DROP TABLE IF EXISTS `PATIENTS`;
CREATE TABLE IF NOT EXISTS `PATIENTS` (
  `ROW_ID` int UNSIGNED NOT NULL AUTO_INCREMENT,
  `SUBJECT_ID` mediumint UNSIGNED NOT NULL,
  `first_name` varchar(128) NOT NULL,
  `last_name` varchar(128) NOT NULL,
  `street` varchar(256) NOT NULL,
  `city` varchar(256) NOT NULL,
  `state` varchar(2) NOT NULL,
  `zip` varchar(10) NOT NULL,
  `latitude` decimal(22,11) DEFAULT NULL,
  `longitude` decimal(22,11) DEFAULT NULL,
  `GENDER` varchar(5) NOT NULL,
  `race` varchar(32) NOT NULL,
  `language` varchar(32) NOT NULL,
  `ethnicity` varchar(64) NOT NULL,
  `religion` varchar(32) NOT NULL,
  `marital_status` varchar(64) NOT NULL,
  `insurance` varchar(64) NOT NULL,
  `payer_id` int NOT NULL,
  `DOB` date NOT NULL,
  `DOD` date DEFAULT NULL,
  `DOD_HOSP` date DEFAULT NULL,
  `EXPIRE_FLAG` tinyint UNSIGNED NOT NULL,
  `acd_study_patient` tinyint(1) NOT NULL DEFAULT '0',
  `fhir_json` json DEFAULT NULL,
  PRIMARY KEY (`ROW_ID`),
  UNIQUE KEY `PATIENTS_SUBJECT_ID` (`SUBJECT_ID`),
  KEY `PATIENTS_idx01` (`EXPIRE_FLAG`),
  KEY `first_name` (`first_name`),
  KEY `last_name` (`last_name`),
  KEY `state` (`state`),
  KEY `zip` (`zip`),
  KEY `acd_study_patient` (`acd_study_patient`),
  KEY `race` (`race`),
  KEY `language` (`language`),
  KEY `religion` (`religion`),
  KEY `marital_status` (`marital_status`),
  KEY `insurance` (`insurance`),
  KEY `ethnicity` (`ethnicity`),
  KEY `DOB` (`DOB`),
  KEY `payer_id` (`payer_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4  COLLATE=utf8mb4_unicode_520_ci;

DROP TABLE IF EXISTS `patient_coverage`;
CREATE TABLE IF NOT EXISTS `patient_coverage` (
  `id` mediumint UNSIGNED NOT NULL AUTO_INCREMENT,
  `patient_id` int UNSIGNED NOT NULL,
  `payer_id` int NOT NULL,
  `payer_plan_id` int NOT NULL,
  `member_id` bigint NOT NULL,
  `fhir_json` json DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `payer_id` (`payer_id`),
  KEY `patient_id` (`patient_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4  COLLATE=utf8mb4_unicode_520_ci;

DROP TABLE IF EXISTS `payer`;
CREATE TABLE IF NOT EXISTS `payer` (
  `id` int NOT NULL AUTO_INCREMENT,
  `Name` varchar(128) NOT NULL,
  `plan_type` varchar(32) NOT NULL,
  `street` varchar(256) CHARACTER SET utf8 COLLATE utf8_general_ci DEFAULT NULL,
  `city` varchar(64) NOT NULL,
  `state` varchar(2) NOT NULL,
  `zip` varchar(16) NOT NULL,
  `endpoint_url` varchar(256) CHARACTER SET utf8 COLLATE utf8_general_ci DEFAULT NULL,
  `fhir_json` json DEFAULT NULL,
   PRIMARY KEY (`id`),
  KEY `Name` (`Name`),
  KEY `state` (`state`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4  COLLATE=utf8mb4_unicode_520_ci;

DROP TABLE IF EXISTS `PRESCRIPTIONS`;
CREATE TABLE IF NOT EXISTS `PRESCRIPTIONS` (
  `ROW_ID` mediumint UNSIGNED NOT NULL,
  `SUBJECT_ID` mediumint UNSIGNED NOT NULL,
  `HADM_ID` mediumint UNSIGNED NOT NULL,
  `ICUSTAY_ID` mediumint UNSIGNED DEFAULT NULL,
  `STARTDATE` datetime DEFAULT NULL,
  `ENDDATE` datetime DEFAULT NULL,
  `DRUG_TYPE` varchar(100) NOT NULL,
  `DRUG` varchar(100) DEFAULT NULL,
  `DRUG_NAME_POE` varchar(100) DEFAULT NULL,
  `DRUG_NAME_GENERIC` varchar(100) DEFAULT NULL,
  `FORMULARY_DRUG_CD` varchar(120) DEFAULT NULL,
  `GSN` varchar(200) DEFAULT NULL,
  `NDC` varchar(120) DEFAULT NULL,
  `rxNormId` varchar(32) NOT NULL,
  `PROD_STRENGTH` varchar(120) DEFAULT NULL,
  `DOSE_VAL_RX` varchar(120) DEFAULT NULL,
  `DOSE_UNIT_RX` varchar(120) DEFAULT NULL,
  `FORM_VAL_DISP` varchar(120) DEFAULT NULL,
  `FORM_UNIT_DISP` varchar(120) DEFAULT NULL,
  `ROUTE` varchar(120) DEFAULT NULL,
  `acd_study_med` tinyint(1) NOT NULL,
  `fhir_json` json DEFAULT NULL,
  PRIMARY KEY (`ROW_ID`),
  KEY `PRESCRIPTIONS_idx01` (`SUBJECT_ID`,`HADM_ID`),
  KEY `PRESCRIPTIONS_idx02` (`ICUSTAY_ID`),
  KEY `PRESCRIPTIONS_idx03` (`DRUG_TYPE`),
  KEY `PRESCRIPTIONS_idx04` (`DRUG`),
  KEY `PRESCRIPTIONS_idx05` (`STARTDATE`,`ENDDATE`),
  KEY `prescriptions_fk_hadm_id` (`HADM_ID`),
  KEY `ndccode` (`NDC`) USING BTREE,
  KEY `RxNorm` (`rxNormId`),
  KEY `acd_study_med` (`acd_study_med`),
  KEY `STARTDATE` (`STARTDATE`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4  COLLATE=utf8mb4_unicode_520_ci;

DROP TABLE IF EXISTS `problem_list_item`;
CREATE TABLE IF NOT EXISTS `problem_list_item` (
  `id` int NOT NULL AUTO_INCREMENT,
  `name` varchar(256) NOT NULL,
  `icd_code` varchar(32) NOT NULL,
  `cui` varchar(32) NOT NULL,
  `note_event_id` int NOT NULL,
  `hadm_id` int NOT NULL,
  PRIMARY KEY (`id`),
  KEY `cui` (`cui`),
  KEY `name` (`name`),
  KEY `hadm_id` (`hadm_id`),
  KEY `note_event_id` (`note_event_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4  COLLATE=utf8mb4_unicode_520_ci;

DROP TABLE IF EXISTS `problem_medication`;
CREATE TABLE IF NOT EXISTS `problem_medication` (
  `id` int NOT NULL AUTO_INCREMENT,
  `name` varchar(256) NOT NULL,
  `description` varchar(1024) NOT NULL,
  `problemListItemId` int NOT NULL,
  `rxnorm_id` varchar(16) NOT NULL,
  `negated` tinyint(1) NOT NULL,
  `cui` varchar(32) NOT NULL,
  `action_id` int NOT NULL,
  PRIMARY KEY (`id`),
  KEY `problemListItemId` (`problemListItemId`),
  KEY `action_id` (`action_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4  COLLATE=utf8mb4_unicode_520_ci;

DROP TABLE IF EXISTS `problem_procedure`;
CREATE TABLE IF NOT EXISTS `problem_procedure` (
  `id` int NOT NULL AUTO_INCREMENT,
  `problemListItemId` int NOT NULL,
  `name` varchar(256) NOT NULL,
  `description` varchar(1024) NOT NULL,
  `active` tinyint(1) NOT NULL,
  `cui` varchar(32) NOT NULL,
  PRIMARY KEY (`id`),
  KEY `problemListItemId` (`problemListItemId`),
  KEY `active` (`active`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4  COLLATE=utf8mb4_unicode_520_ci;

DROP TABLE IF EXISTS `PROCEDUREEVENTS_MV`;
CREATE TABLE IF NOT EXISTS `PROCEDUREEVENTS_MV` (
  `ROW_ID` mediumint UNSIGNED NOT NULL,
  `SUBJECT_ID` mediumint UNSIGNED NOT NULL,
  `HADM_ID` mediumint UNSIGNED NOT NULL,
  `ICUSTAY_ID` mediumint UNSIGNED DEFAULT NULL,
  `STARTTIME` datetime NOT NULL,
  `ENDTIME` datetime NOT NULL,
  `ITEMID` mediumint UNSIGNED NOT NULL,
  `VALUE` decimal(22,10) NOT NULL,
  `VALUEUOM` varchar(30) NOT NULL,
  `LOCATION` varchar(30) DEFAULT NULL,
  `LOCATIONCATEGORY` varchar(30) DEFAULT NULL,
  `STORETIME` datetime NOT NULL,
  `CGID` smallint UNSIGNED NOT NULL,
  `ORDERID` mediumint UNSIGNED NOT NULL,
  `LINKORDERID` mediumint UNSIGNED NOT NULL,
  `ORDERCATEGORYNAME` varchar(100) NOT NULL,
  `SECONDARYORDERCATEGORYNAME` varchar(100) DEFAULT NULL,
  `ORDERCATEGORYDESCRIPTION` varchar(50) NOT NULL,
  `ISOPENBAG` tinyint(1) NOT NULL,
  `CONTINUEINNEXTDEPT` tinyint UNSIGNED NOT NULL,
  `CANCELREASON` tinyint UNSIGNED NOT NULL,
  `STATUSDESCRIPTION` varchar(30) NOT NULL,
  `COMMENTS_EDITEDBY` varchar(30) DEFAULT NULL,
  `COMMENTS_CANCELEDBY` varchar(30) DEFAULT NULL,
  `COMMENTS_DATE` datetime DEFAULT NULL,
  PRIMARY KEY (`ROW_ID`),
  UNIQUE KEY `PROCEDUREEVENTS_MV_ORDERID` (`ORDERID`),
  KEY `PROCEDUREEVENTS_MV_idx01` (`SUBJECT_ID`,`HADM_ID`),
  KEY `PROCEDUREEVENTS_MV_idx02` (`ICUSTAY_ID`),
  KEY `PROCEDUREEVENTS_MV_idx03` (`ITEMID`),
  KEY `PROCEDUREEVENTS_MV_idx04` (`CGID`),
  KEY `PROCEDUREEVENTS_MV_idx05` (`ORDERCATEGORYNAME`),
  KEY `procedureevents_mv_fk_hadm_id` (`HADM_ID`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4  COLLATE=utf8mb4_unicode_520_ci;

DROP TABLE IF EXISTS `PROCEDURES_ICD`;
CREATE TABLE IF NOT EXISTS `PROCEDURES_ICD` (
  `ROW_ID` mediumint UNSIGNED NOT NULL,
  `SUBJECT_ID` mediumint UNSIGNED NOT NULL,
  `HADM_ID` mediumint UNSIGNED NOT NULL,
  `SEQ_NUM` tinyint UNSIGNED NOT NULL,
  `ICD9_CODE` varchar(10) NOT NULL,
  PRIMARY KEY (`ROW_ID`),
  KEY `PROCEDURES_ICD_idx01` (`SUBJECT_ID`,`HADM_ID`),
  KEY `PROCEDURES_ICD_idx02` (`ICD9_CODE`,`SEQ_NUM`),
  KEY `procedures_icd_fk_hadm_id` (`HADM_ID`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4  COLLATE=utf8mb4_unicode_520_ci;

DROP TABLE IF EXISTS `radiology_reports`;
CREATE TABLE IF NOT EXISTS `radiology_reports` (
  `ROW_ID` int UNSIGNED NOT NULL,
  `SUBJECT_ID` mediumint UNSIGNED NOT NULL,
  `HADM_ID` mediumint UNSIGNED DEFAULT NULL,
  `CHARTDATE` date NOT NULL,
  `CHARTTIME` datetime DEFAULT NULL,
  `STORETIME` datetime DEFAULT NULL,
  `CATEGORY` varchar(50) CHARACTER SET utf8 NOT NULL,
  `DESCRIPTION` varchar(255) CHARACTER SET utf8 NOT NULL,
  `CGID` smallint UNSIGNED DEFAULT NULL,
  `ISERROR` tinyint UNSIGNED DEFAULT NULL,
  `TEXT` mediumtext CHARACTER SET utf8,
  `Impression` varchar(2048) DEFAULT NULL,
  `acd_study_note` tinyint(1) NOT NULL,
  `fhir_json` json DEFAULT NULL,
  `linked_3d_study_id` varchar(64) NOT NULL,
  PRIMARY KEY (`ROW_ID`),
  KEY `linked_3d_study_id` (`linked_3d_study_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4  COLLATE=utf8mb4_unicode_520_ci;

DROP TABLE IF EXISTS `SERVICES`;
CREATE TABLE IF NOT EXISTS `SERVICES` (
  `ROW_ID` mediumint UNSIGNED NOT NULL,
  `SUBJECT_ID` mediumint UNSIGNED NOT NULL,
  `HADM_ID` mediumint UNSIGNED NOT NULL,
  `TRANSFERTIME` datetime NOT NULL,
  `PREV_SERVICE` varchar(20) DEFAULT NULL,
  `CURR_SERVICE` varchar(20) NOT NULL,
  PRIMARY KEY (`ROW_ID`),
  KEY `SERVICES_idx01` (`SUBJECT_ID`,`HADM_ID`),
  KEY `SERVICES_idx02` (`TRANSFERTIME`),
  KEY `SERVICES_idx03` (`CURR_SERVICE`,`PREV_SERVICE`),
  KEY `services_fk_hadm_id` (`HADM_ID`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4  COLLATE=utf8mb4_unicode_520_ci;

DROP TABLE IF EXISTS `social_history`;
CREATE TABLE IF NOT EXISTS `social_history` (
  `subject_id` varchar(128) NOT NULL,
  `text` mediumtext CHARACTER SET utf8 COLLATE utf8_general_ci NOT NULL,
  `hadm_id` int NOT NULL,
  `note_description` varchar(256) NOT NULL,
  KEY `subject_id` (`subject_id`),
  KEY `had_id` (`hadm_id`),
  KEY `note_description` (`note_description`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4  COLLATE=utf8mb4_unicode_520_ci;

DROP TABLE IF EXISTS `TRANSFERS`;
CREATE TABLE IF NOT EXISTS `TRANSFERS` (
  `ROW_ID` mediumint UNSIGNED NOT NULL,
  `SUBJECT_ID` mediumint UNSIGNED NOT NULL,
  `HADM_ID` mediumint UNSIGNED NOT NULL,
  `ICUSTAY_ID` mediumint UNSIGNED DEFAULT NULL,
  `DBSOURCE` varchar(20) DEFAULT NULL,
  `EVENTTYPE` varchar(20) DEFAULT NULL,
  `PREV_CAREUNIT` varchar(20) DEFAULT NULL,
  `CURR_CAREUNIT` varchar(20) DEFAULT NULL,
  `PREV_WARDID` tinyint UNSIGNED DEFAULT NULL,
  `CURR_WARDID` tinyint UNSIGNED DEFAULT NULL,
  `INTIME` datetime DEFAULT NULL,
  `OUTTIME` datetime DEFAULT NULL,
  `LOS` decimal(22,10) DEFAULT NULL,
  PRIMARY KEY (`ROW_ID`),
  KEY `TRANSFERS_idx01` (`SUBJECT_ID`,`HADM_ID`),
  KEY `TRANSFERS_idx02` (`ICUSTAY_ID`),
  KEY `TRANSFERS_idx03` (`CURR_CAREUNIT`,`PREV_CAREUNIT`),
  KEY `TRANSFERS_idx04` (`INTIME`,`OUTTIME`),
  KEY `TRANSFERS_idx05` (`LOS`),
  KEY `transfers_fk_hadm_id` (`HADM_ID`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4  COLLATE=utf8mb4_unicode_520_ci;


SET FOREIGN_KEY_CHECKS=1;
COMMIT;
