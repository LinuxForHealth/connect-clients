"""
config.py

Contains application settings encapsulated using Pydantic BaseSettings.
Settings may be overriden using environment variables.
Example:
    override uvicorn_port default setting
    export UVICORN_PORT=5050
    or
    UVICORN_PORT=5050 python ethereum/main.py
"""
import certifi
import os
import socket
import ssl
from functools import lru_cache
from os.path import dirname, abspath
from pydantic import BaseSettings
from typing import List


host_name = socket.gethostname()
nats_sync_subject = "EVENTS.sync"
nats_eligibility_subject = "EVENTS.coverageeligibilityresponse"


class Settings(BaseSettings):
    """
    application settings
    """

    # uvicorn settings
    uvicorn_app: str = "ethereum.asgi:app"
    uvicorn_host: str = "0.0.0.0"
    uvicorn_port: int = 5100
    uvicorn_reload: bool = False

    # general certificate settings
    # path to "standard" CA certificates
    certificate_authority_path: str = certifi.where()
    certificate_verify: bool = False

    # ethereum package settings
    ethereum_ca_file: str = certifi.where()
    ethereum_ca_path: str = None
    ethereum_cert_name: str = "lfh-ethereum-client.pem"
    ethereum_cert_key_name: str = "lfh-ethereum-client.key"
    ethereum_config_directory: str = "/home/lfh/ethereum/config"
    ethereum_logging_config_path: str = "logging.yaml"
    ethereum_rate_limit: str = "5/second"
    ethereum_timing_enabled: bool = False

    # nats client settings
    nats_servers: List[str] = ["tls://nats-server:4222"]
    nats_sync_subscribers: List[str] = []
    nats_allow_reconnect: bool = True
    nats_max_reconnect_attempts: int = 10
    nats_nk_file: str = "nats-server.nk"

    # ethereum client settings
    ethereum_network_uri: str = "http://host.docker.internal:7545"
    ethereum_contract_address: str = "0x7Bad280884c907bBf3955c21351ce41122aB88eB"
    ethereum_contract_abi: str = "EligibilityCheck.json"
    ethereum_event_poll_seconds: int = 2

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
        cafile=settings.ethereum_ca_file, capath=settings.ethereum_ca_path
    )
    return ssl_context
