import os
import grpc
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import node_registry_pb2
import node_registry_pb2_grpc

GRPC_HOST = os.environ.get("GRPC_HOST", "grpc-server:50051")

app = FastAPI()


def get_stub():
    channel = grpc.insecure_channel(GRPC_HOST)
    return node_registry_pb2_grpc.NodeRegistryStub(channel)


class RegisterRequest(BaseModel):
    name: str
    host: str
    port: int


@app.post("/nodes", status_code=201)
def register_node(req: RegisterRequest):
    stub = get_stub()
    response = stub.Register(
        node_registry_pb2.RegisterRequest(name=req.name, host=req.host, port=req.port)
    )
    n = response.node
    return {"id": n.id, "name": n.name, "host": n.host, "port": n.port}


@app.get("/nodes")
def list_nodes():
    stub = get_stub()
    response = stub.List(node_registry_pb2.Empty())
    return [{"id": n.id, "name": n.name, "host": n.host, "port": n.port} for n in response.nodes]


@app.get("/nodes/{node_id}")
def get_node(node_id: str):
    stub = get_stub()
    try:
        response = stub.Get(node_registry_pb2.GetRequest(id=node_id))
        n = response.node
        return {"id": n.id, "name": n.name, "host": n.host, "port": n.port}
    except grpc.RpcError as e:
        if e.code() == grpc.StatusCode.NOT_FOUND:
            raise HTTPException(status_code=404, detail="Node not found")
        raise HTTPException(status_code=500, detail=str(e))


@app.delete("/nodes/{node_id}", status_code=204)
def delete_node(node_id: str):
    stub = get_stub()
    try:
        stub.Delete(node_registry_pb2.DeleteRequest(id=node_id))
    except grpc.RpcError as e:
        if e.code() == grpc.StatusCode.NOT_FOUND:
            raise HTTPException(status_code=404, detail="Node not found")
        raise HTTPException(status_code=500, detail=str(e))
