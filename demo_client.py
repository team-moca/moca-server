import client_connector_pb2_grpc as client_grpc
import client_connector_pb2 as client
import messages_pb2
import grpc
import time
from google.protobuf.timestamp_pb2 import Timestamp

channel = grpc.insecure_channel('localhost:50051')
stub = client_grpc.ClientConnectorStub(channel)

timestamp = Timestamp()
timestamp.GetCurrentTime()

message_meta = messages_pb2.MessageMeta(
    message_id = "M01",
    service_id = "S01",
    from_user_id = "U01",
    to_user_id = "U02",
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

response = stub.SendMessage(messages_pb2.Message(
    meta = message_meta,
    content = messages_pb2.MessageContent(
        poll_message = messages_pb2.PollMessageContent()
    )
))
print(response.status)