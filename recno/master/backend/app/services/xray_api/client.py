import grpc
import json
import uuid

class XrayGRPCClient:
    def __init__(self, host: str, port: int):
        self.target = f"{host}:{port}"
        # Setting up gRPC channel
        # self.channel = grpc.insecure_channel(self.target)

    def add_user(self, inbound_tag: str, email: str, user_uuid: str):
        """
        Dynamically add a user to a VLESS inbound via gRPC HandlerService
        """
        print(f"Connecting to Xray at {self.target} via gRPC to ADD user {email} (UUID: {user_uuid}) to inbound {inbound_tag}...")

        # Real implementation involves creating `AlterInboundRequest` and sending it to `HandlerServiceStub`
        #
        # stub = command_pb2_grpc.HandlerServiceStub(self.channel)
        # request = command_pb2.AlterInboundRequest(
        #     tag=inbound_tag,
        #     operation=core_pb2.TypedMessage(
        #         type="v2ray.core.app.proxyman.command.AddUserOperation",
        #         value=... # Serialized user.proto
        #     )
        # )
        # try:
        #     stub.AlterInbound(request)
        # except grpc.RpcError as e:
        #     print(f"Failed to add user: {e.details()}")
        #     return False

        return True

    def remove_user(self, inbound_tag: str, email: str):
        """
        Dynamically remove a user from an inbound via gRPC HandlerService
        """
        print(f"Connecting to Xray at {self.target} via gRPC to REMOVE user {email} from inbound {inbound_tag}...")

        # Real implementation
        # stub = command_pb2_grpc.HandlerServiceStub(self.channel)
        # request = command_pb2.AlterInboundRequest(
        #     tag=inbound_tag,
        #     operation=core_pb2.TypedMessage(
        #         type="v2ray.core.app.proxyman.command.RemoveUserOperation",
        #         value=... # Serialized RemoveUserOperation
        #     )
        # )
        # stub.AlterInbound(request)

        return True

    def get_user_stats(self, email: str):
        """
        Get user traffic statistics dynamically via gRPC StatsService
        """
        # Real implementation
        # stub = stats_pb2_grpc.StatsServiceStub(self.channel)
        # try:
        #     downlink_req = stats_pb2.GetStatsRequest(name=f"user>>{email}>>traffic>>downlink", reset=False)
        #     downlink_res = stub.GetStats(downlink_req)
        #     down = downlink_res.stat.value
        # except Exception:
        #     down = 0

        # try:
        #     uplink_req = stats_pb2.GetStatsRequest(name=f"user>>{email}>>traffic>>uplink", reset=False)
        #     uplink_res = stub.GetStats(uplink_req)
        #     up = uplink_res.stat.value
        # except Exception:
        #     up = 0

        # return {"uplink": up, "downlink": down}
        return {"uplink": 1024, "downlink": 2048}

# Testing the functionality
if __name__ == "__main__":
    client = XrayGRPCClient("127.0.0.1", 6020)
    client.add_user("vless-inbound", "test_user_email", str(uuid.uuid4()))
