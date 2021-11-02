"""
config.py

Contains application settings encapsulated using Pydantic BaseSettings.
Settings may be overriden using environment variables.
Example:
    override uvicorn_port default setting
    export UVICORN_PORT=5200
    or
    UVICORN_PORT=5200 python bluebutton/main.py
"""
import certifi
import os
import socket
import ssl
from functools import lru_cache
from os.path import dirname, abspath
from pydantic import BaseSettings


host_name = socket.gethostname()


class Settings(BaseSettings):
    """
    application settings
    """
    # uvicorn settings
    uvicorn_app: str = "bluebutton.asgi:app"
    uvicorn_host: str = "0.0.0.0"
    uvicorn_port: int = 5200
    uvicorn_reload: bool = False

    # general certificate settings
    # path to "standard" CA certificates
    certificate_authority_path: str = certifi.where()
    certificate_verify: bool = False

    # bluebutton package settings
    bluebutton_ca_file: str = certifi.where()
    bluebutton_ca_path: str = None
    bluebutton_cert_name: str = "lfh-bluebutton-client.pem"
    bluebutton_cert_key_name: str = "lfh-bluebutton-client.key"
    bluebutton_config_directory: str = "/home/lfh/bluebutton/config"
    bluebutton_logging_config_path: str = "logging.yaml"
    bluebutton_rate_limit: str = "5/second"
    bluebutton_timing_enabled: bool = False

    # LFH Blue Button 2.0 Client Endpoint
    bluebutton_authorize_callback: str = f"https://localhost:{uvicorn_port}/bluebutton/authorize_callback"

    # CMS Blue Button 2.0 Endpoints and settings
    cms_authorize_url: str = "https://sandbox.bluebutton.cms.gov/v2/o/authorize/"
    cms_token_url: str = "https://sandbox.bluebutton.cms.gov/v2/o/token/"
    cms_base_url: str = "https://sandbox.bluebutton.cms.gov/v2/fhir/"
    cms_scopes: str = "patient/Patient.read patient/Coverage.read patient/ExplanationOfBenefit.read"
    cms_client_id: str = "kAMZfgm43Y27HhCTJ2sZyttdV5pFvGyFvaboXqEf"
    cms_client_secret: str = "OrKYtcPdgzqWgXLx7Q2YJLvPGaybP4zxuiTTKfRlFrLhVpyZeM8PpUNRnadliV2LlPEOCzmRFiOSKGiD7jZl3RlezSC5g0mTVaCgouLLX5yun8mI3r0LQ0jb65WD6lNR"
    return_cms_result: bool = False

    # LFH connect FHIR url
    lfh_fhir_url = "https://localhost:5000/fhir"

    class Config:
        case_sensitive = False
        env_file = os.path.join(dirname(dirname(abspath(__file__))), ".env")

@lru_cache()
def get_settings() -> Settings:
    """Returns the settings instance"""
    return Settings()

@lru_cache()
def get_ssl_context(ssl_purpose: ssl.Purpose) -> ssl.SSLContext:
    """
    Returns a SSL Context configured for server auth with the certificate path
    :param ssl_purpose:
    """
    settings = get_settings()
    ssl_context = ssl.create_default_context(ssl_purpose)
    ssl_context.load_verify_locations(
        cafile=settings.bluebutton_ca_file, capath=settings.bluebutton_ca_path
    )
    return ssl_context
