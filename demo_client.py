import client_connector_pb2_grpc as client_grpc
import client_connector_pb2 as client
import messages_pb2
import grpc
import time
from google.protobuf.timestamp_pb2 import Timestamp
from uuid import UUID, uuid4

channel = grpc.insecure_channel('localhost:50051')
stub = client_grpc.ClientConnectorStub(channel)

timestamp = Timestamp()
timestamp.GetCurrentTime()

message_meta = messages_pb2.MessageMeta(
    message_id = uuid4().bytes,
    service_id = UUID("54b4ae1c-1c6f-4f7e-b2b9-efd7bf5e894b").bytes,
    from_user_id = UUID("8c43ba0c-92b3-11ea-bb37-0242ac130002").bytes,
    to_user_id = UUID("78f3647d-1e12-4bca-8ce5-a6e5f2da0508").bytes,
    timestamp = timestamp
)

response = stub.SendMessage(messages_pb2.Message(
    meta = message_meta,
    content = messages_pb2.MessageContent(
        text_message = messages_pb2.TextMessageContent(content="Lorem ipsum")
    )
))
print(response.status)

print("-------------")


timestamp.GetCurrentTime()

message_meta = messages_pb2.MessageMeta(
    message_id = uuid4().bytes,
    service_id = UUID("54b4ae1c-1c6f-4f7e-b2b9-efd7bf5e894b").bytes,
    from_user_id = UUID("8c43ba0c-92b3-11ea-bb37-0242ac130002").bytes,
    to_user_id = UUID("78f3647d-1e12-4bca-8ce5-a6e5f2da0508").bytes,
    timestamp = timestamp
)

response = stub.SendMessage(messages_pb2.Message(
    meta = message_meta,
    content = messages_pb2.MessageContent(
        poll_message = messages_pb2.PollMessageContent()
    )
))
print(response.status)