VERSION = "1.0.0"

import asyncio
from functools import cached_property

from django_ws import WebSocketHandler, TASK_WS_CLOSED
from graphene_django.settings import graphene_settings

try:
    from loguru import logger

except ImportError:
    import logging
    logger = logging.getLogger(__name__)


class GraphQLSubscriptionHandler(WebSocketHandler):
    @cached_property
    def schema(self):
        return graphene_settings.SCHEMA

    async def accept_connection(self):
        await self._send({'type': 'websocket.accept', 'subprotocol': 'graphql-transport-ws'})

    async def on_message(self, data):
        mname = f"process_{data['type']}"
        method = getattr(self, mname, None)
        if method:
            if mname == 'process_subscribe':
                task_id = data['id']

            else:
                task_id = mname

            self.start_task(task_id, method, callback=None, args=[data])

        else:
            logger.info("Unknown OP Type: {}", data)
            await self.close()

    async def graphql_send(self, id=None, op_type=None, payload=None):
        message = {}

        if id is not None:
            message["id"] = id
        if op_type is not None:
            message["type"] = op_type
        if payload is not None:
            message["payload"] = payload

        await self.send(message)

    async def process_connection_init(self, data):
        await self.graphql_send(op_type='connection_ack')

    async def process_complete(self, data):
        op_id = data['id']
        if op_id in self.tasks and not self.tasks[op_id].done():
            self.tasks[op_id].cancel(msg=TASK_WS_CLOSED)

    async def process_subscribe(self, data):
        op_id = data.get('id')

        result = await self.schema.subscribe(
            data['payload'].get("query"),
            context=self.request,
            variables=data['payload'].get("variables"),
            operation_name=data['payload'].get("operationName"),
        )

        if hasattr(result, '__aiter__'):
            async for item in result:
                await self.graphql_send(id=op_id, op_type='next', payload=item.formatted)

        else:
            if result.errors:
                await self.graphql_send(id=op_id, op_type='error', payload=result.formatted)

            else:
                await self.graphql_send(id=op_id, op_type='next', payload=result.formatted)

        await self.graphql_send(id=op_id, op_type='complete')
