import logging
import asyncio
from concurrent import futures
from uuid import UUID, uuid4
import time
from libmoca import client_connector_pb2 as client
from libmoca import client_connector_grpc as client_grpc
import grpc
from libmoca import messages_pb2
from google.protobuf.timestamp_pb2 import Timestamp
from purerpc import Server

class ClientConnector(client_grpc.ClientConnectorServicer):
    def __init__(self):
        print("starting server")

    async def SendMessage(self, message):

        if message.content.HasField("text_message"):
            return messages_pb2.SendMessageResponse(
                status=messages_pb2.SendMessageStatus.OK
            )

        return messages_pb2.SendMessageResponse(
            status=messages_pb2.SendMessageStatus.MESSAGE_CONTENT_NOT_IMPLEMENTED_FOR_SERVICE
        )

    async def SubscribeToMessages(self, message):
        print("subscribing to new messages...")

        while True:
            timestamp = Timestamp()
            timestamp.GetCurrentTime()

            message_meta = messages_pb2.MessageMeta(
                message_id=uuid4().bytes,
                service_id=UUID("54b4ae1c-1c6f-4f7e-b2b9-efd7bf5e894b").bytes,
                from_user_id=str(UUID("8c43ba0c-92b3-11ea-bb37-0242ac130002")),
                to_user_id=str(UUID("78f3647d-1e12-4bca-8ce5-a6e5f2da0508")),
                timestamp=timestamp,
            )

            message = messages_pb2.Message(
                meta=message_meta,
                content=messages_pb2.MessageContent(
                    text_message=messages_pb2.TextMessageContent(
                        content="You subscribed to messages"
                    )
                ),
            )
            yield message
            await asyncio.sleep(1)


server = Server(50051)
server.add_service(ClientConnector().service)
server.serve(backend="asyncio")
