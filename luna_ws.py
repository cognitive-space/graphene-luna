VERSION = "0.4.0"

import asyncio
import json
import traceback

from django.conf import settings
from django.core.handlers.asgi import ASGIRequest
from django.utils.module_loading import import_string

from graphene_django.settings import graphene_settings

from websockets.exceptions import ConnectionClosedOK, ConnectionClosedError

try:
    from loguru import logger

except ImportError:
    import logging
    logger = logging.getLogger(__name__)


class GraphqlRequest(ASGIRequest):

    def __init__(self, scope, body_file):
        scope['method'] = 'GET'
        super().__init__(scope, body_file)


class GraphQLWebSocket:

    def __init__(self, scope):
        self.scope = scope
        self.connected = False
        self.closed = False
        self.request = GraphqlRequest(scope, None)
        self.complete = {}


class JsonSend:

    def __init__(self, send):
        self.send = send

    async def __call__(self, message):
        if 'json' in message:
            message['text'] = json.dumps(message['json'])
            del message['json']

        return await self.send(message)


class GraphQLWebSocketHandler:

    def __new__(cls, *args, **kwargs):
        if not hasattr(cls, '_middleware'):
            cls._middleware = []
            cls._msg_middleware = []

            if hasattr(settings, 'GRAPHQL_WS_MIDDLEWARE'):
                for middleware_path in reversed(settings.GRAPHQL_WS_MIDDLEWARE):
                    middleware = import_string(middleware_path)
                    cls._middleware.append(middleware)

            if hasattr(settings, 'GRAPHQL_MESSAGE_MIDDLEWARE'):
                for middleware_path in reversed(settings.GRAPHQL_MESSAGE_MIDDLEWARE):
                    middleware = import_string(middleware_path)
                    cls._msg_middleware.append(middleware)

        return super().__new__(cls)

    def __init__(self, schema):
        self.schema = schema

    async def graphql_send(self, ws, send, id=None, op_type=None, payload=None):
        message = {}

        if id is not None:
            message["id"] = id
        if op_type is not None:
            message["type"] = op_type
        if payload is not None:
            message["payload"] = payload

        try:
            await send({'type': 'websocket.send', 'json': message})

        except ConnectionClosedOK:
            ws.closed = True

        except ConnectionClosedError:
            ws.closed = True

    async def handle(self, scope, receive, send):
        ws = GraphQLWebSocket(scope)
        func = self._handle
        for m in self._middleware:
            func = m(func)

        return await func(ws, receive, send)

    async def _handle(self, ws, receive, send):
        tasks = {}
        send = JsonSend(send)

        while 1:
            if ws.closed:
                break

            event = await receive()

            if event['type'] == 'websocket.connect':
                logger.info('Websocket Opened')
                await send({'type': 'websocket.accept', 'subprotocol': 'graphql-transport-ws'})
                ws.connected = True

            elif event['type'] == 'websocket.disconnect':
                logger.info('Websocket Disconnected')
                ws.closed = True

            elif event['type'] == 'websocket.receive':
                data = json.loads(event['text'])
                print(data)
                mname = f"process_{data['type']}"
                method = getattr(self, mname, None)
                if method:
                    if method == 'process_subscribe':
                        # send task to the background since it's probably long running
                        op_id = data['id']
                        tasks[op_id] = asyncio.create_task(method(ws, send, data))

                    else:
                        for m in self._msg_middleware:
                            method = m(method)

                        await method(ws, send, data)

                else:
                    logger.info("Unknown OP Type: {}", data)

    async def process_connection_init(self, ws, send, data):
        await self.graphql_send(ws, send, op_type='connection_ack')

    async def process_complete(self, ws, send, data):
        op_id = data['id']
        ws.complete[op_id] = True

    async def process_subscribe(self, ws, send, data):
        op_id = data.get('id')

        result = await self.schema.subscribe(
            data['payload'].get("query"),
            context=ws.request,
            variables=data['payload'].get("variables"),
            operation_name=data['payload'].get("operationName"),
        )

        if hasattr(result, '__aiter__'):
            async for item in result:
                if ws.closed:
                    break

                if op_id in ws.complete:
                    del ws.complete[op_id]
                    break

                await self.graphql_send(ws, send, id=op_id, op_type='next', payload=item.formatted)

        else:
            if result.errors:
                await self.graphql_send(ws, send, id=op_id, op_type='error', payload=result.formatted)

            else:
                await self.graphql_send(ws, send, id=op_id, op_type='next', payload=result.formatted)

        await self.graphql_send(ws, send, id=op_id, op_type='complete')


def add_ws_app(original_app, schema=None):
    if schema is None:
        schema = graphene_settings.SCHEMA

    handler = GraphQLWebSocketHandler(schema)

    async def graphql_app(scope, receive, send):
        if scope["type"] == "websocket":
            # todo: check URL path and sub-protocol
            try:
                await handler.handle(scope, receive, send)
            except Exception as e:
                logger.error(traceback.format_exc())
            finally:
                logger.info('Websocket Closed')

        else:
            await original_app(scope, receive, send)

    return graphql_app
