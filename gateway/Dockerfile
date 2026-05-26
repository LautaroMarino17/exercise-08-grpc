FROM python:3.11-slim
WORKDIR /app
COPY . .
RUN pip install --no-cache-dir -r gateway/requirements.txt
RUN python -m grpc_tools.protoc -I proto --python_out=. --grpc_python_out=. proto/node_registry.proto
CMD ["uvicorn", "gateway.app:app", "--host", "0.0.0.0", "--port", "8080"]
