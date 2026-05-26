import os
import grpc
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

GRPC_HOST = os.environ.get("GRPC_HOST", "grpc-server:50051")

app = FastAPI()


def _get_pb2():
    import node_registry_pb2
    return node_registry_pb2


def _get_pb2_grpc():
    import node_registry_pb2_grpc
    return node_registry_pb2_grpc


def get_stub():
    channel = grpc.insecure_channel(GRPC_HOST)
    return _get_pb2_grpc().NodeRegistryStub(channel)


class RegisterRequest(BaseModel):
    name: str
    host: str
    port: int


@app.get("/health")
def health():
    return {"status": "ok"}


@app.post("/nodes", status_code=201)
def register_node(req: RegisterRequest):
    pb2 = _get_pb2()
    stub = get_stub()
    try:
        response = stub.Register(pb2.RegisterRequest(name=req.name, host=req.host, port=req.port))
    except grpc.RpcError as e:
        raise HTTPException(status_code=502, detail=str(e))
    n = response.node
    return {"id": n.id, "name": n.name, "host": n.host, "port": n.port}


@app.get("/nodes")
def list_nodes():
    pb2 = _get_pb2()
    stub = get_stub()
    try:
        response = stub.List(pb2.Empty())
    except grpc.RpcError as e:
        raise HTTPException(status_code=502, detail=str(e))
    return [{"id": n.id, "name": n.name, "host": n.host, "port": n.port} for n in response.nodes]


@app.get("/nodes/{node_id}")
def get_node(node_id: str):
    pb2 = _get_pb2()
    stub = get_stub()
    try:
        response = stub.Get(pb2.GetRequest(id=node_id))
    except grpc.RpcError as e:
        if e.code() == grpc.StatusCode.NOT_FOUND:
            raise HTTPException(status_code=404, detail="Node not found")
        raise HTTPException(status_code=502, detail=str(e))
    n = response.node
    return {"id": n.id, "name": n.name, "host": n.host, "port": n.port}


@app.delete("/nodes/{node_id}", status_code=204)
def delete_node(node_id: str):
    pb2 = _get_pb2()
    stub = get_stub()
    try:
        stub.Delete(pb2.DeleteRequest(id=node_id))
    except grpc.RpcError as e:
        if e.code() == grpc.StatusCode.NOT_FOUND:
            raise HTTPException(status_code=404, detail="Node not found")
        raise HTTPException(status_code=502, detail=str(e))
