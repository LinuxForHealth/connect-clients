from ibm_whcs_sdk import annotator_for_clinical_data as acd
from ibm_cloud_sdk_core.authenticators.iam_authenticator import IAMAuthenticator
import time
import configparser


# Run variables
APIKEY = "EiKq_KEsTNyJTk9CcxOB4jhMgvwyt-hpQqKpRcdSEnlE" # DO NOT COMMIT THE KEY
VERSION = "2020-06-01"
URL = "https://us-east.wh-acd.cloud.ibm.com/wh-acd/api"
# The next 3 parameters are for the Cartridge Deployment APIs
CARTRIDGE_ZIP = "<CARTRIDGE_ZIP_LOCATION_HERE>"
CARTRIDGE_ID = "henry_test_cartridge"
CARTRIDGES_CONTENT_TYPE = "application/octet-stream" # SELECT ONE CONTENT TYPE
#CARTRIDGES_CONTENT_TYPE = "multipart/form-data"

class setup():

    def getService(self) -> acd:
        """
        Get the ACD service object
        """
        # we use a config file (called nlp.ini) to read in the NLP config
        config = configparser.ConfigParser()
        config.read('nlp.ini')
        config.sections()
        print(config['NLP_ENGINE']['NLP_URL'])
        service = acd.AnnotatorForClinicalDataV1(
        authenticator=IAMAuthenticator(apikey=config['NLP_ENGINE']['APIKEY']),
        version=config['NLP_ENGINE']['API_VERSION']
        )
        service.set_service_url(config['NLP_ENGINE']['NLP_URL'])
        return service
