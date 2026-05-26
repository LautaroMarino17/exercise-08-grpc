import sys
sys.path.append("/app")

from fastapi import FastAPI, Response
import grpc
import node_registry_pb2
import node_registry_pb2_grpc

app = FastAPI()

GRPC_HOST = "grpc-server:50051"


def get_stub():
    channel = grpc.insecure_channel(GRPC_HOST)
    return node_registry_pb2_grpc.NodeRegistryServiceStub(channel)


@app.get("/health")
def health():
    return {"status": "ok"}


@app.post("/api/nodes", status_code=201)
def register_node(node: dict):
    stub = get_stub()
    response = stub.RegisterNode(
        node_registry_pb2.NodeRequest(name=node.get("name", ""), ip=node.get("ip", ""))
    )
    return {"message": response.message}


@app.get("/api/nodes")
def get_nodes():
    stub = get_stub()
    response = stub.GetNodes(node_registry_pb2.Empty())
    return [{"name": n.name, "ip": n.ip} for n in response.nodes]


@app.delete("/api/nodes/{name}", status_code=204)
def delete_node(name: str):
    stub = get_stub()
    try:
        stub.DeleteNode(node_registry_pb2.NodeRequest(name=name, ip=""))
    except Exception:
        pass
    return Response(status_code=204)
