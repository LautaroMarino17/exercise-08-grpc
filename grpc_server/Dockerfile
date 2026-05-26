FROM python:3.12-slim
WORKDIR /app
COPY grpc_server/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY proto/ proto/
RUN python -m grpc_tools.protoc -I proto --python_out=. --grpc_python_out=. proto/node_registry.proto
COPY grpc_server/server.py .
CMD ["python", "server.py"]
