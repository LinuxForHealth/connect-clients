"""
fhir.py

fhir.py provides a REST interface and method for sending FHIR messages to an Ethereum blockchain.
"""
import logging
from datetime import datetime
from ethereum.clients.ethereum import get_ethereum_client
from fastapi import Body, Depends, HTTPException, Response
from fastapi.routing import APIRouter


router = APIRouter()
logger = logging.getLogger(__name__)


@router.post("/{resource_type}")
async def post_fhir_resource(
    resource_type: str,
    request_data: dict = Body(...)):

    try:
        return handle_fhir_resource(resource_type, request_data)
    except Exception as ex:
        raise HTTPException(status_code=500, detail=ex)


def handle_fhir_resource(resource_type: str, request_data: dict):
    """
    Handle a message coming from either NATS or REST and send to the
    Ethereum client to send to the blockchain.

    :param resource_type: FHIR type of the resource, e.g. Patient
    :param request_data: The dict representation of the FHIR resource
    :return: The hash of the submitted transaction or None
    """
    client = get_ethereum_client()
    path = f"{resource_type}/{request_data['id']}"

    if resource_type == "Coverage":
        coverage_start = datetime.strptime(request_data['period']['start'], '%Y-%m-%d').timestamp()
        coverage_end = datetime.strptime(request_data['period']['end'], '%Y-%m-%d').timestamp()
        return client.add_coverage_resource(path, request_data,
                                            request_data['payor'][0]['reference'],
                                            request_data['subscriber']['reference'],
                                            int(coverage_start),
                                            int(coverage_end))
    elif resource_type == "CoverageEligibilityRequest":
        return client.check_eligibility(path, request_data,
                                        request_data['insurer']['reference'],
                                        request_data['patient']['reference'],
                                        request_data['insurance'][0]['coverage']['reference'],
                                        int(datetime.now().timestamp()))
    else:
        return client.add_fhir_resource(resource_type, path, request_data)
