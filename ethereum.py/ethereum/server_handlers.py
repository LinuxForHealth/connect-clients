import logging
import logging.config
import os
import sys
import yaml
from ethereum.config import get_settings
from ethereum.clients.nats import (
    create_nats_subscribers,
    get_nats_client,
    stop_nats_clients,
)
from ethereum.clients.ethereum import stop_ethereum_client
from fastapi import HTTPException, Request
from fastapi.responses import JSONResponse
from yaml import YAMLError


logger = logging.getLogger(__name__)


def add_trace_logging():
    """
    Adds trace level logging support to logging and the root logging class
    """

    def trace(self, message, *args, **kwargs):
        """
        Generates a TRACE log record
        """
        self.log(5, message, *args, **kwargs)

    logging.addLevelName(5, "TRACE")
    logging.getLoggerClass().trace = trace


def configure_logging() -> None:
    """
    Configures logging for the ethereum application.
    Logging configuration is parsed from the setting/environment variable LOGGING_CONFIG_PATH, if present.
    If LOGGING_CONFIG_PATH is not found, a basic config is applied.
    """

    def apply_basic_config():
        """Applies a basic config for console logging"""
        add_trace_logging()
        logging.basicConfig(
            stream=sys.stdout,
            level=logging.INFO,
            format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        )

    settings = get_settings()

    if os.path.exists(settings.ethereum_logging_config_path):
        with open(settings.ethereum_logging_config_path, "r") as f:
            try:
                logging_config = yaml.safe_load(f)
                logging.config.dictConfig(logging_config)
                logger.info(
                    f"Loaded logging configuration from {settings.ethereum_logging_config_path}"
                )
                add_trace_logging()
            except YAMLError as e:
                apply_basic_config()
                logger.error(f"Unable to load logging configuration from file: {e}.")
                logger.info("Applying basic logging configuration.")
    else:
        apply_basic_config()
        logger.info(
            "Logging configuration not found. Applying basic logging configuration."
        )


def log_configuration() -> None:
    """
    Logs Connect configuration settings.
    "General" settings are logged at an INFO level.
    "Internal" settings for clients/components are logged at a DEBUG level.
    """
    settings = get_settings()
    header_footer_length = 50

    logger.debug("*" * header_footer_length)
    logger.debug("Connect Configuration Settings")
    logger.debug("=" * header_footer_length)
    logger.debug(f"UVICORN_APP: {settings.uvicorn_app}")
    logger.debug(f"UVICORN_HOST: {settings.uvicorn_host}")
    logger.debug(f"UVICORN_PORT: {settings.uvicorn_port}")
    logger.debug(f"UVICORN_RELOAD: {settings.uvicorn_reload}")
    logger.debug("=" * header_footer_length)

    logger.debug(f"CERTIFICATE_AUTHORITY_PATH: {settings.certificate_authority_path}")
    logger.debug(f"LOGGING_CONFIG_PATH: {settings.ethereum_logging_config_path}")
    logger.debug("=" * header_footer_length)

    logger.debug(f"ETHEREUM_CA_FILE: {settings.ethereum_ca_file}")
    logger.debug(f"ETHEREUM_CA_PATH: {settings.ethereum_ca_path}")
    logger.debug(f"ETHEREUM_CONFIG_DIRECTORY: {settings.ethereum_config_directory}")
    logger.debug(f"ETHEREUM_CERT: {settings.ethereum_cert_name}")
    logger.debug(f"ETHEREUM_CERT_KEY: {settings.ethereum_cert_key_name}")
    logger.debug("=" * header_footer_length)

    logger.debug(f"NATS_SERVERS: {settings.nats_servers}")
    logger.debug(f"NATS_ALLOW_RECONNECT: {settings.nats_allow_reconnect}")
    logger.debug(f"NATS_MAX_RECONNECT_ATTEMPTS: {settings.nats_max_reconnect_attempts}")
    logger.debug("=" * header_footer_length)

    logger.debug("*" * header_footer_length)


async def configure_internal_integrations() -> None:
    """
    Configure internal integrations to support:
    - NATS Messaging/Jetstream
    """
    await get_nats_client()
    await create_nats_subscribers()


async def close_internal_clients() -> None:
    """
    Closes internal Connect client connections:
    - NATS
    - Ethereum
    """
    await stop_nats_clients()
    stop_ethereum_client()


async def http_exception_handler(request: Request, exc: HTTPException):
    """
    Allows HTTPExceptions to be thrown without being parsed against a response model.
    """
    return JSONResponse(
        status_code=exc.status_code, content={"detail": f"{exc.detail}"}
    )
