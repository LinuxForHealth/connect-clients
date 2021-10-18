from ibm_whcs_sdk import annotator_for_clinical_data as acd
from ibm_cloud_sdk_core.authenticators.iam_authenticator import IAMAuthenticator
import time
import configparser
from config import get_settings

class setup():

    def getService(self) -> acd:
        """
        Get the ACD service object from config (via the central .env file)
        """
        # we use a config file (called nlp.ini) to read in the NLP config
        settings = get_settings()

        service = acd.AnnotatorForClinicalDataV1(
        IAMAuthenticator(settings.NLP_APIKEY,
        settings.NLP_API_VERSION))

        service.set_service_url(settings.NLP_URL)
        return service
