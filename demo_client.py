import client_connector_pb2_grpc as client_grpc
import client_connector_pb2 as client
import grpc
import time
from google.protobuf.timestamp_pb2 import Timestamp

channel = grpc.insecure_channel('localhost:50051')
stub = client_grpc.ClientConnectorStub(channel)

timestamp = Timestamp()
timestamp.GetCurrentTime()

message_meta = client.MessageMeta(
    message_id = "M01",
    service_id = "S01",
    user_id = "U01",
    timestamp = timestamp
)

message = client.Message(
    meta = message_meta,
    content = "Lorem ipsum"
)

response = stub.SendMessage(message)
print(response.status)

response = stub.SendPollMessage(message)
print(response.status)