from bluebutton import __version__
from bluebutton.main import get_app
from fastapi.openapi.utils import get_openapi

app = get_app()


def custom_openapi():
    if app.openapi_schema:
        return app.openapi_schema

    # get the default schema
    openapi_schema = get_openapi(
        title="LinuxForHealth Blue Button Client",
        description="LinuxForHealth Blue Button Client for the CMS Blue Button 2.0 API",
        version=__version__,
        routes=app.routes,
    )

    # add securitySchemes
    securitySchemes = {
        "bearerAuth": {
            "type": "http",
            "scheme": "bearer",
            "bearerFormat": "basic"
        }
    }
    openapi_schema["components"]["securitySchemes"] = securitySchemes

    # add security to the endpoint
    security = [{
        "bearerAuth": []
    }]
    openapi_schema["paths"]["/bluebutton/{resource_type}"]["get"]["security"] = security

    app.openapi_schema = openapi_schema
    return app.openapi_schema


# Customize the Open API schema
app.openapi = custom_openapi
