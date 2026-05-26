import sys
sys.path.append("/app")

from concurrent import futures
import grpc
import node_registry_pb2
import node_registry_pb2_grpc

_nodes = []


class NodeRegistryServicer(node_registry_pb2_grpc.NodeRegistryServiceServicer):

    def RegisterNode(self, request, context):
        _nodes.append({"name": request.name, "ip": request.ip})
        return node_registry_pb2.NodeResponse(message="Node registered")

    def GetNodes(self, request, context):
        return node_registry_pb2.NodeList(
            nodes=[node_registry_pb2.Node(name=n["name"], ip=n["ip"]) for n in _nodes]
        )

    def DeleteNode(self, request, context):
        global _nodes
        _nodes = [n for n in _nodes if n["name"] != request.name]
        return node_registry_pb2.NodeResponse(message="Node deleted")


def serve():
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    node_registry_pb2_grpc.add_NodeRegistryServiceServicer_to_server(NodeRegistryServicer(), server)
    server.add_insecure_port("[::]:50051")
    server.start()
    server.wait_for_termination()


if __name__ == "__main__":
    serve()
