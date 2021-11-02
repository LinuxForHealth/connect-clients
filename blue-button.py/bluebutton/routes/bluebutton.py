"""
bluebutton.py

bluebutton.py provides a REST interface and method for sending FHIR messages to an Ethereum blockchain.
"""
import json
import logging
import webbrowser
from bluebutton.config import get_settings
from bluebutton.encoding import encode_from_str
from fastapi import Body, Depends, Query, Request
from fastapi.routing import APIRouter
from httpx import AsyncClient
from typing import Optional


router = APIRouter()
logger = logging.getLogger(__name__)


@router.get("/authorize")
async def authorize(
    settings=Depends(get_settings),
):
    """
    Use this function to authenticate with the CMS Blue Button 2.0 API server
    of medicare.gov, in order to submit healthcare records to LinuxForHealth.

    To authorize subsequent API calls via OpenAPI, copy the resulting access_token
    and click the 'Authorize' button, then paste the access_token and click "Authorize".
    """
    cms_authorize_url = (f"{settings.cms_authorize_url}?response_type=code"
        f"&client_id={settings.cms_client_id}"
        f"&redirect_uri={settings.bluebutton_authorize_callback}"
        f"&state=1")

    webbrowser.open_new_tab(cms_authorize_url)


@router.get("/authorize_callback")
async def authorize_callback(
    code: str,
    settings=Depends(get_settings),
):
    """
    The CMS Blue Button 2.0 API server calls this callback endpoint with the
    an access code as part of the OAuth2 authorization code flow.  This function
    exchanges an access code for an access token via a call to the CMS Blue
    Button /token endpoint.

    :param code: The access code to exchange for an access token
    :return: JSON result containing the access_token and patient id
    """
    data = bytes(f"grant_type=authorization_code&code={code}", "utf-8")
    auth_str = encode_from_str(f"{settings.cms_client_id}:{settings.cms_client_secret}")
    headers = {'Authorization': f"Basic {auth_str}",
               'content-type': 'application/x-www-form-urlencoded'}

    async with AsyncClient(verify=settings.certificate_verify) as client:
        response = await client.post(settings.cms_token_url, data=data, headers=headers)
        return json.loads(response.text)


@router.get("/{resource_type}")
async def get_resource(
    request: Request,
    resource_type: str,
    patient: str,
    return_cms: Optional[bool] = False,
    settings=Depends(get_settings),
):
    """
    Retrieve your records (Patient, ExplanationOfBenefit or Coverage) from your
    medicare data and send them to LinuxForHealth to include in your patient record.

    :param resource_type: Patient, ExplanationOfBenefit or Coverage
    :param patient: The patient id ('patient' field) returned from the call to /authorize
    :param return_cms: Set return_cms to True in the query string to return the CMS Blue Button response.
    :return: LinuxForHealth JSON result message
    """
    cms_resource_url = f"{settings.cms_base_url}/{resource_type}?patient={patient}"
    headers = {'Authorization': request.headers.get('Authorization'),
               "content-type": "application/json"}

    async with AsyncClient(verify=settings.certificate_verify) as client:
        bb_response = await client.get(cms_resource_url, headers=headers)
        response = bb_response

        if bb_response.status_code == 200:
            bb_result = json.loads(bb_response.text)
            result_resource_type = bb_result["resourceType"]
            lfh_url = f"{settings.lfh_fhir_url}/{result_resource_type}"
            lfh_response = await client.post(lfh_url, json=json.loads(bb_response.text))
            if not return_cms:
                response = lfh_response

        return json.loads(response.text)
