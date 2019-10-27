from socketioModel import SocketIOOutput, SocketBlueprint, SocketIOInput
import asyncio
import inspect
import json
import logging
import uuid
from functools import partial
from asyncio import Queue, CancelledError
from sanic import Sanic, Blueprint, response
from sanic.request import Request
from sanic_cors import CORS
from typing import Text, List, Dict, Any, Optional, Callable, Iterable, Awaitable
import rasa.core
import rasa.utils
import rasa.utils.io
from rasa.core import constants, utils
from rasa.core.agent import load_agent, Agent
from rasa.core.channels import BUILTIN_CHANNELS, InputChannel, console
from rasa.core.interpreter import NaturalLanguageInterpreter
from rasa.core.tracker_store import TrackerStore
from rasa.core.utils import AvailableEndpoints, configure_file_logging
from rasa.model import get_model_subdirectories, get_model
from rasa.utils.common import update_sanic_log_level, class_from_module_path
from rasa.core.channels.channel import UserMessage
from rasa.utils.endpoints import EndpointConfig
try:
    from urlparse import urljoin
except ImportError:
    from urllib.parse import urljoin
logger = logging.getLogger(__name__)

channel = "socketio"
port = 5005
credentials = "credentials.md"
cors = None
auth_token = None
enable_api = True
jwt_secret = None
jwt_method = None
endpoints = None
remote_storage = None
log_file = None
route = "/webhooks/"

sio_input_channel = SocketIOInput(user_message_evt = "user_uttered",
        bot_message_evt = "bot_uttered",
        namespace = None,
        session_persistence = False,
        socketio_path = "/socket.io",)

import server
app = server.create_app(
            cors_origins=cors,
            auth_token=auth_token,
            jwt_secret=jwt_secret,
            jwt_method=jwt_method,
        )


action_endpoint = EndpointConfig(url="http://localhost:5055/webhook")
agentVericast = Agent.load("./Vericast/",action_endpoint = action_endpoint)


async def handle_message(
    message: UserMessage,
    message_preprocessor: Optional[Callable[[Text], Text]] = None,
    **kwargs
) -> Optional[List[Text]]:
    """Handle a single message."""
    response = await agentVericast.handle_message(message)
    return(response)

async def handler(*args, **kwargs):
    #await app.agent.handle_message(*args, **kwargs)
    await handle_message(*args, **kwargs)

if route:
    p = urljoin(route, sio_input_channel.url_prefix())
else:
    p = None
app.blueprint(sio_input_channel.blueprint(handler), url_prefix=p)

# configure async loop logging
async def configure_async_logging():
    if logger.isEnabledFor(logging.DEBUG):
        rasa.utils.io.enable_async_loop_debugging(asyncio.get_event_loop())

app.add_task(configure_async_logging)

logger.info(
        "Starting server on "
        "{}".format(constants.DEFAULT_SERVER_FORMAT.format(port))
    )

model_path = ""

app.run(host="0.0.0.0", port=port)

