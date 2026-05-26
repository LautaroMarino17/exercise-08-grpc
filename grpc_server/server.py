import os
import uuid
import grpc
from concurrent import futures
import node_registry_pb2
import node_registry_pb2_grpc
from sqlalchemy import create_engine, Column, String, Integer
from sqlalchemy.orm import DeclarativeBase, Session

DATABASE_URL = os.environ.get("DATABASE_URL", "postgresql://noderegistry:noderegistry@db:5432/noderegistry")

engine = create_engine(DATABASE_URL)


class Base(DeclarativeBase):
    pass


class NodeModel(Base):
    __tablename__ = "nodes"
    id = Column(String, primary_key=True)
    name = Column(String, nullable=False)
    host = Column(String, nullable=False)
    port = Column(Integer, nullable=False)


Base.metadata.create_all(engine)


class NodeRegistryServicer(node_registry_pb2_grpc.NodeRegistryServicer):
    def Register(self, request, context):
        node_id = str(uuid.uuid4())
        with Session(engine) as session:
            node = NodeModel(id=node_id, name=request.name, host=request.host, port=request.port)
            session.add(node)
            session.commit()
            return node_registry_pb2.NodeResponse(
                node=node_registry_pb2.Node(id=node.id, name=node.name, host=node.host, port=node.port)
            )

    def List(self, request, context):
        with Session(engine) as session:
            nodes = session.query(NodeModel).all()
            return node_registry_pb2.NodeList(
                nodes=[node_registry_pb2.Node(id=n.id, name=n.name, host=n.host, port=n.port) for n in nodes]
            )

    def Get(self, request, context):
        with Session(engine) as session:
            node = session.get(NodeModel, request.id)
            if node is None:
                context.abort(grpc.StatusCode.NOT_FOUND, "Node not found")
                return node_registry_pb2.NodeResponse()
            return node_registry_pb2.NodeResponse(
                node=node_registry_pb2.Node(id=node.id, name=node.name, host=node.host, port=node.port)
            )

    def Delete(self, request, context):
        with Session(engine) as session:
            node = session.get(NodeModel, request.id)
            if node is None:
                context.abort(grpc.StatusCode.NOT_FOUND, "Node not found")
                return node_registry_pb2.Empty()
            session.delete(node)
            session.commit()
            return node_registry_pb2.Empty()


def serve():
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    node_registry_pb2_grpc.add_NodeRegistryServicer_to_server(NodeRegistryServicer(), server)
    server.add_insecure_port("[::]:50051")
    server.start()
    server.wait_for_termination()


if __name__ == "__main__":
    serve()
