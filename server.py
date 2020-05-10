import client_connector_pb2_grpc as client_grpc
import client_connector_pb2 as client
import grpc
from concurrent import futures
import logging

class ClientConnectorServicer(client_grpc.ClientConnectorServicer):
    def SendMessage(self, request, context):
        print(request)
        return client.SendMessageResponse(status=client.SendMessageStatus.OK)

def serve():
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    client_grpc.add_ClientConnectorServicer_to_server(
        ClientConnectorServicer(), server)
    server.add_insecure_port('[::]:50051')
    server.start()
    server.wait_for_termination()

if __name__ == '__main__':
    logging.basicConfig()
    serve()