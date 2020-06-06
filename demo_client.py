import logging
import time
from uuid import UUID, uuid4

import anyio
import purerpc
from libmoca import client_connector_pb2 as client
from libmoca import client_connector_grpc as client_grpc
import grpc
from libmoca import messages_pb2
from google.protobuf.timestamp_pb2 import Timestamp

async def main():
    async with purerpc.insecure_channel("localhost", 50051) as channel:
        stub = client_grpc.ClientConnectorStub(channel)

        timestamp = Timestamp()
        timestamp.GetCurrentTime()

        message_meta = messages_pb2.MessageMeta(
            message_id=uuid4().bytes,
            service_id=UUID("54b4ae1c-1c6f-4f7e-b2b9-efd7bf5e894b").bytes,
            from_user_id=str(UUID("8c43ba0c-92b3-11ea-bb37-0242ac130002")),
            to_user_id=str(UUID("78f3647d-1e12-4bca-8ce5-a6e5f2da0508")),
            timestamp=timestamp,
        )

        response = await stub.SendMessage(
            messages_pb2.Message(
                meta=message_meta,
                content=messages_pb2.MessageContent(
                    text_message=messages_pb2.TextMessageContent(content="I'm sending a message from ☕ to ✈️")
                ),
            )
        )
        print(f"Send message status: {response.status}")

        print("-------------")

        timestamp.GetCurrentTime()

        message_meta = messages_pb2.MessageMeta(
            message_id=uuid4().bytes,
            service_id=UUID("54b4ae1c-1c6f-4f7e-b2b9-efd7bf5e894b").bytes,
            from_user_id=str(UUID("8c43ba0c-92b3-11ea-bb37-0242ac130002")),
            to_user_id=str(UUID("78f3647d-1e12-4bca-8ce5-a6e5f2da0508")),
            timestamp=timestamp,
        )

        response = await stub.SendMessage(
            messages_pb2.Message(
                meta=message_meta,
                content=messages_pb2.MessageContent(
                    poll_message=messages_pb2.PollMessageContent()
                ),
            )
        )
        print(f"Send poll message status: {response.status}")

        
        print("now subscribing to messages...")
        while True:

            async for message in stub.SubscribeToMessages(client.SubscribeToMessagesParams()):
                print(message)
        


if __name__ == "__main__":
    logging.basicConfig()
    anyio.run(main, backend="asyncio")
