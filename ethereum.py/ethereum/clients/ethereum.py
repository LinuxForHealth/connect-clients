"""
ethereum.py

ethereum.py contains an EthereumClient class that provides functions for interacting
with the Coverage.sol solidity contract on an Ethereum blockchain network.
"""
import asyncio
import datetime
import json
import logging
import os
from ethereum.clients.nats import get_nats_client
from ethereum.config import get_settings, nats_eligibility_subject
from ethereum.exceptions import EthereumNetworkConnectionError
from hexbytes import HexBytes
from typing import Optional, Any, List
from web3 import Web3

logger = logging.getLogger(__name__)

# client instance
eth_client = None

class EthereumClient:
    """
    Ethereum client for LFH that utilizes the Web3 library for interacting
    with an Ethereum blockchain network.
    """
    def __init__(self, **qwargs):
        logger.debug("Initializing EthereumClient")
        self.eth_network_uri = qwargs["eth_network_uri"]

        logger.debug("Initializing Web3")
        self.client: Optional[Web3] = Web3(Web3.HTTPProvider(self.eth_network_uri))
        self.from_acct = {"from": self.client.eth.accounts[0]}

        if (self.client and self.client.isConnected()):
            logger.info(f"Connected to the Ethereum network at: {self.eth_network_uri}")
            self.contract = self.client.eth.contract(address=qwargs["contract_address"],
                                                     abi=qwargs["contract_abi"])
            event_filter = self.contract.events.EligibilityResult.createFilter(fromBlock="latest")
            self.cancelled = False
            contract_event_loop = asyncio.get_event_loop()
            contract_event_loop.create_task(self.event_loop(event_filter, qwargs["event_poll_interval"]))
            logger.info(f"Connected to the contract at: {qwargs['contract_address']}")
        else:
            error_msg = f"Failed to connect to the Ethereum network at: {self.eth_network_uri}"
            logger.error(error_msg)
            raise EthereumNetworkConnectionError(error_msg)

    def add_coverage_resource(self, path: str, fhir_json: Any, payor_ref: str,
                              subscriber_ref: str, coverage_start: int, coverage_end: int):
        """
        Send a Coverage FHIR resource to the Coverage.sol contract.

        :param path: FHIR path of the resource, e.g. /Coverage/001
        :param fhir_json: The string representation of the FHIR resource
        :param payor_ref: coverage.payor[0].reference
        :param subscriber_ref: coverage.subscriber.reference
        :param coverage_start: coverage.period.start converted to a timestamp
        :param coverage_end: coverage.period.end converted to a timestamp
        :return: The hash of the submitted transaction or None
        """
        if not self.client.isConnected():
            error = f"Not connected to the Ethereum network"
            logger.error(error)
            return {"error": error}

        try:
            tx_hash = self.contract.functions.add_coverage_resource(path,
                                                                    json.dumps(fhir_json),
                                                                    payor_ref,
                                                                    subscriber_ref,
                                                                    coverage_start,
                                                                    coverage_end).transact(self.from_acct)
            tx_receipt = self.client.eth.waitForTransactionReceipt(tx_hash)
            receipt_dict = dict(tx_receipt)
            hash_str = receipt_dict["transactionHash"].hex()
            logger.info(f"tx hash: {hash_str}")
            return {"result": hash_str}
        except Exception as ex:
            error = f"Transaction error {ex}"
            logger.error(error)
            return {"error": error}

    def check_eligibility(self, path: str, fhir_json: Any, insurer_ref: str,
                          patient_ref: str, coverage_ref: str, coverage_date: int):
        """
        Send a CoverageEligibilityRequest FHIR resource to the Coverage.sol contract.

        :param path: FHIR path of the resource, e.g. /CoverageEligibilityRequest/001
        :param fhir_json: The string representation of the FHIR resource
        :param insurer_ref: coverageeligibilityrequest.insurer.reference
        :param patient_ref: coverageeligibilityrequest.patient.reference
        :param coverage_ref: coverageeligibilityrequest.insurance[0].coverage
        :param coverage_date: coverageeligibilityrequest.created converted to a timestamp
        :return: The hash of the submitted transaction or None
        """
        if not self.client.isConnected():
            error = f"Not connected to the Ethereum network"
            logger.error(error)
            return {"error": error}

        try:
            tx_hash = self.contract.functions.check_eligibility(path,
                                                                json.dumps(fhir_json),
                                                                insurer_ref,
                                                                patient_ref,
                                                                coverage_ref,
                                                                coverage_date).transact(self.from_acct)
            tx_receipt = self.client.eth.waitForTransactionReceipt(tx_hash)
            receipt_dict = dict(tx_receipt)
            hash_str = receipt_dict["transactionHash"].hex()
            logger.info(f"tx hash: {hash_str}")
            return {"result": hash_str}
        except Exception as ex:
            error = f"Transaction error {ex}"
            logger.error(error)
            return {"error": error}

    def add_fhir_resource(self, fhir_type: str, path: str, fhir_json: Any):
        """
        Send a Patient or Organization FHIR resource to the Coverage.sol contract.

        :param fhir_type: FHIR type of the resource, e.g. Patient
        :param path: FHIR path of the resource, e.g. /Patient/001
        :param fhir_json: The string representation of the FHIR resource
        :return: The hash of the submitted transaction or None
        """
        if not self.client.isConnected():
            error = f"Not connected to the Ethereum network"
            logger.error(error)
            return {"error": error}

        try:
            tx_hash = self.contract.functions.add_fhir_resource(fhir_type,
                                                                path,
                                                                json.dumps(fhir_json)).transact(self.from_acct)
            tx_receipt = self.client.eth.waitForTransactionReceipt(tx_hash)
            receipt_dict = dict(tx_receipt)
            hash_str = receipt_dict["transactionHash"].hex()
            logger.info(f"tx hash: {hash_str}")
            return {"result": hash_str}
        except Exception as ex:
            error = f"Transaction error {ex}"
            logger.error(error)
            return {"error": error}

    def close(self):
        self.cancelled = True

    async def event_loop(self, event_filter, poll_interval: int):
        while not self.cancelled:
            for event in event_filter.get_new_entries():
                await self.handle_event(json.loads(Web3.toJSON(event)))
            await asyncio.sleep(poll_interval)

    async def handle_event(self, event: dict):
        """
        Send a FHIR CoverageEligibilityResponse based on the eligibility decision from the contract.

        :param event: The JSON contract event containing the eligibility decision and supporting info.
        """
        logger.trace(f"Received contract event: {event}")
        path: List[str] = event["args"]["path"].split("/")
        request_id: str = path[1]
        result: bool = event["args"]["result"]
        disposition: str = "Policy is currently in effect."
        if not result:
            disposition = "Policy is not in effect."
        today: str = datetime.date.today().isoformat()

        message: Any = {
            "resourceType": "CoverageEligibilityResponse",
            "id": request_id,
            "text": {
                "status": "generated",
                "div": "<div xmlns=\"http://www.w3.org/1999/xhtml\">A human-readable rendering of the CoverageEligibilityResponse.</div>"
            },
            "identifier": [
                {
                    "system": "http://localhost:5000/fhir/coverageeligibilityresponse/" + request_id,
                    "value": request_id
                }
            ],
            "status": "active",
            "purpose": [
                "validation"
            ],
            "patient": {
                "reference": event["args"]["patient_ref"]
            },
            "created": today,
            "request": {
                "reference": "http://www.BenefitsInc.com/fhir/coverageeligibilityrequest/" + request_id
            },
            "outcome": "complete",
            "disposition": disposition,
            "insurer": {
                "reference": event["args"]["insurer_ref"]
            },
            "insurance": [
                {
                    "coverage": {
                        "reference": event["args"]["coverage_ref"]
                    },
                    "inforce": result
                }
            ]
        };

        nats_client = await get_nats_client()
        msg_str = json.dumps(message)
        logger.info(f"CoverageEligibilityResponse: {msg_str}")
        await nats_client.publish(nats_eligibility_subject, bytearray(msg_str, "utf-8"))
        logger.trace("Sent CoverageEligibilityResponse via NATS")


def get_ethereum_client() -> Optional[EthereumClient]:
    """
    :return: a connected EthereumClient instance
    """
    global eth_client
    if not eth_client:
        settings = get_settings()

        # load ABI file
        abi_file: str = os.path.join(settings.ethereum_config_directory, settings.ethereum_contract_abi)
        contract_info = json.load(open(abi_file))

        eth_client = EthereumClient(
            eth_network_uri=settings.ethereum_network_uri,
            contract_address=settings.ethereum_contract_address,
            contract_abi=contract_info["abi"],
            event_poll_interval=settings.ethereum_event_poll_seconds
        )

    return eth_client


def stop_ethereum_client():
    client = get_ethereum_client()
    client.close()


class HexJsonEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, HexBytes):
            return obj.hex()
        return super().default(obj)
