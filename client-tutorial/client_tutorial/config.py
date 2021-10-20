"""
config.py

Contains application settings encapsulated using Pydantic BaseSettings.
Settings may be overriden using environment variables.
Example:
    override MySQL server URI
    export TUTORIAL_MYSQL_URI="mysql+pymysql://root:secret@localhost:3306/kafkaFhirDemoDb"
"""
import os
from functools import lru_cache
from os.path import dirname, abspath
from pydantic import BaseSettings


class Settings(BaseSettings):
    """
    application settings
    """

    nlp_apikey = 'EiKq_KEsTNyJTk9CcxOB4jhMgvwyt-hpQqKpRcdSEnlE'
    nlp_version='2020-06-01'
    nlp_url = 'https://us-east.wh-acd.cloud.ibm.com/wh-acd/api'
    nlp_module_name = 'henry_test_cartridge'
    nlp_type = 'ACD'
    cartridges_content_type = 'application/octet-stream'
    flow_name = 'henry_test_cartridge_v1.0_aap_test_flow'

    # test server: 'mysql+pymysql://credentialuser:dxbcamel@192.168.1.24:3306/kafkaFhirDemoDb'
    tutorial_mysql_url: str = 'mysql+pymysql://credentialuser:dxbcamel@192.168.1.24:3306/mimiciiiv14'

    #this is the patient id for all the tutorial clinical data
    tutorial_subject_id:int = 959595

    class Config:
        case_sensitive = False
        env_file = os.path.join(dirname(dirname(abspath(__file__))), ".env")


@lru_cache()
def get_settings() -> Settings:
    """Returns the settings instance"""
    return Settings()
