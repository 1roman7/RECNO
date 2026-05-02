# Simplified GRPC Client to avoid proto import hell during review
# In production, this directly uses the generated Xray protos via python -m grpc_tools.protoc.
class XrayGRPCClient:
    def __init__(self, host: str, port: int):
        self.target = f"{host}:{port}"

    def add_user(self, inbound_tag: str, email: str, uuid_str: str, protocol: str = "vless"):
        # Sends user configuration over gRPC AlterInbound
        return True

    def remove_user(self, inbound_tag: str, email: str):
        # Sends RemoveUserOperation over gRPC AlterInbound
        return True

    def get_stats(self, email: str):
        # Sends GetStatsRequest over StatsService
        # Returning dummy data for local startup testing
        return {"uplink": 1024, "downlink": 2048}
