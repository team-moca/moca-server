default: python

python:
	python -m grpc_tools.protoc -I./proto --python_out=. --grpc_python_out=. ./proto/*.proto

all: python

clean:
	rm -rf *_pb2.py
	rm -rf *_pb2_grpc.py

watch:
	@echo "Waiting for file changes..."
	@while true; do \
		make $(WATCHMAKE); \
		inotifywait -qre close_write .; \
	done