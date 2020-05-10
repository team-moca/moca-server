default: all

client_connector:
	python -m grpc_tools.protoc -I./protos --python_out=. --grpc_python_out=. ./protos/client_connector.proto

service_connector:
	python -m grpc_tools.protoc -I./protos --python_out=. --grpc_python_out=. ./protos/service_connector.proto

all: client_connector service_connector

clean:
	rm -rf *_pb2.py
	rm -rf *_pb2_grpc.py




watch:
	@echo "Waiting for file changes..."
	@while true; do \
		make $(WATCHMAKE); \
		inotifywait -qre close_write .; \
	done