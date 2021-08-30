"""
main.py

Bootstraps the Fast API application and Uvicorn processes
"""
import os
import uvicorn
from ethereum.config import get_settings
from ethereum.routes.api import router
from ethereum import __version__
from ethereum.server_handlers import (
    close_internal_clients,
    configure_internal_integrations,
    configure_logging,
    log_configuration,
    http_exception_handler,
)
from fastapi import FastAPI, HTTPException
from fastapi.middleware.httpsredirect import HTTPSRedirectMiddleware
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from slowapi.middleware import SlowAPIMiddleware
from slowapi.util import get_remote_address


def get_app() -> FastAPI:
    """
    Creates the Fast API application instance
    :return: The application instance
    """
    settings = get_settings()

    app = FastAPI(
        title="LinuxForHealth Ethereum Client",
        description="LinuxForHealth Ethereum Client for interacting with Ethereum blockchains",
        version=__version__,
    )
    app.add_middleware(HTTPSRedirectMiddleware)
    app.include_router(router)
    app.add_event_handler("startup", configure_logging)
    app.add_event_handler("startup", log_configuration)
    app.add_event_handler("startup", configure_internal_integrations)
    app.add_event_handler("shutdown", close_internal_clients)
    app.add_exception_handler(HTTPException, http_exception_handler)

    # use the slowapi rate limiter
    app.add_middleware(SlowAPIMiddleware)
    limiter = Limiter(
        key_func=get_remote_address, default_limits=[settings.ethereum_rate_limit]
    )
    app.state.limiter = limiter
    app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

    return app


if __name__ == "__main__":
    settings = get_settings()

    uvicorn_params = {
        "app": settings.uvicorn_app,
        "host": settings.uvicorn_host,
        "log_config": None,
        "port": settings.uvicorn_port,
        "reload": settings.uvicorn_reload,
        "ssl_keyfile": os.path.join(
            settings.ethereum_ca_path, settings.ethereum_cert_key_name
        ),
        "ssl_certfile": os.path.join(
            settings.ethereum_ca_path, settings.ethereum_cert_name
        ),
    }

    uvicorn.run(**uvicorn_params)
