"""
nats.py
NATS message subscribers and message handlers
"""
import ethereum.routes.fhir as fhir
import json
import logging
import os
import ssl
from asyncio import get_running_loop
from ethereum.config import (
    get_settings,
    get_ssl_context,
    nats_sync_subject
)
from ethereum.encoding import decode_to_dict
from nats.aio.client import Client as NatsClient, Msg
from typing import Callable, List, Optional


logger = logging.getLogger(__name__)
nats_client = None
nats_clients = []


async def create_nats_subscribers():
    """
    Create NATS subscribers.  Add additional subscribers as needed.
    """
    await start_sync_event_subscribers()


async def start_sync_event_subscribers():
    """
    Create a NATS subscriber for 'nats_sync_subject' for the local NATS server/cluster and
    for each NATS server defined by 'nats_sync_subscribers' in config.py.
    """
    settings = get_settings()

    # subscribe to nats_sync_subject from the local NATS server or cluster
    client = await get_nats_client()
    await subscribe(
        client,
        nats_sync_subject,
        nats_sync_event_handler,
        "".join(settings.nats_servers),
    )

    # subscribe to nats_sync_subject from any additional NATS servers
    for server in settings.nats_sync_subscribers:
        client = await create_nats_client(server)
        nats_clients.append(client)
        await subscribe(client, nats_sync_subject, nats_sync_event_handler, server)


async def subscribe(client: NatsClient, subject: str, callback: Callable, servers: str):
    """
    Subscribe a NATS client to a subject.

    :param client: a connected NATS client
    :param subject: the NATS subject to subscribe to
    :param callback: the callback to call when a message is received on the subscription
    """
    await client.subscribe(subject, cb=callback)
    logger.debug(f"Subscribed {servers} to NATS subject {subject}")


async def nats_sync_event_handler(msg: Msg):
    """
    Callback for NATS 'nats_sync_subject' messages

    :param msg: a message delivered from the NATS server
    """
    subject = msg.subject
    reply = msg.reply
    data = msg.data.decode()
    logger.trace(f"nats_sync_event_handler: received a message on {subject} {reply}")

    # send the message to the blockchain
    message = json.loads(data)
    msg_data = decode_to_dict(message["data"])
    try:
        fhir.handle_fhir_resource(msg_data["resourceType"], msg_data)
    except Exception as ex:
        logger.error(f"Exception: {ex}")


async def stop_nats_clients():
    """
    Gracefully stop all NATS clients prior to shutdown, including
    unsubscribing from all subscriptions.
    """
    for client in nats_clients:
        await client.close()


async def get_nats_client() -> Optional[NatsClient]:
    """
    Create or return a NATS client connected to the local
    NATS server or cluster defined by 'nats_servers' in config.py.

    :return: a connected NATS client instance
    """
    global nats_client

    if not nats_client:
        settings = get_settings()
        nats_client = await create_nats_client(settings.nats_servers)
        nats_clients.append(nats_client)

    return nats_client


async def create_nats_client(servers: List[str]) -> Optional[NatsClient]:
    """
    Create a NATS client for any NATS server or NATS cluster configured to accept this installation's NKey.

    :param servers: List of one or more NATS servers.  If multiple servers are
    provided, they should be in the same NATS cluster.
    :return: a connected NATS client instance
    """
    settings = get_settings()

    client = NatsClient()
    await client.connect(
        servers=servers,
        nkeys_seed=os.path.join(
            settings.ethereum_config_directory, settings.nats_nk_file
        ),
        loop=get_running_loop(),
        tls=get_ssl_context(ssl.Purpose.SERVER_AUTH),
        allow_reconnect=settings.nats_allow_reconnect,
        max_reconnect_attempts=settings.nats_max_reconnect_attempts,
    )
    logger.info("Created NATS client")
    logger.debug(f"Created NATS client for servers = {servers}")

    return client
