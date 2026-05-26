FROM python:3.11-slim
WORKDIR /app
COPY . .
RUN pip install --no-cache-dir -r grpc_server/requirements.txt
RUN python -m grpc_tools.protoc -I proto --python_out=. --grpc_python_out=. proto/node_registry.proto
CMD ["python", "grpc_server/server.py"]
