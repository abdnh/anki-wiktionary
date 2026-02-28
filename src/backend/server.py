from __future__ import annotations

from ..consts import consts
from ..log import logger
from ..proto.routes import add_api_routes
from ..vendor.ankiutils import sveltekit

server: sveltekit.SveltekitServer | None = None


def init_server() -> sveltekit.SveltekitServer:
    global server
    if server is None:
        server = sveltekit.init_server(consts, logger)
        add_api_routes(server)
    return server


def get_server() -> sveltekit.SveltekitServer:
    if server is None:
        raise sveltekit.SveltekitServerNotInitializedError()
    return server
