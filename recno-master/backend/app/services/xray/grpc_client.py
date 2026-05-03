
import grpc
from app.services.xray.proto.app.proxyman.command import command_pb2
from app.services.xray.proto.app.proxyman.command import command_pb2_grpc
from app.services.xray.proto.app.stats.command import command_pb2 as stats_pb2
from app.services.xray.proto.app.stats.command import command_pb2_grpc as stats_pb2_grpc
from app.services.xray.proto.common.serial import typed_message_pb2
from app.services.xray.proto.common.protocol import user_pb2
from app.services.xray.proto.proxy.vless import account_pb2 as vless_account_pb2
from app.services.xray.proto.proxy.vmess import account_pb2 as vmess_account_pb2
from app.services.xray.proto.proxy.trojan import config_pb2 as trojan_account_pb2

class XrayGRPCClient:


    def __init__(self, host: str, port: int):
        self.target = f"{host}:{port}"
        self.channel = grpc.insecure_channel(self.target)
        except Exception:
            self.channel = grpc.insecure_channel(self.target)



    def add_user(self, inbound_tag: str, email: str, uuid_str: str, protocol: str = "vless"):

        stub = command_pb2_grpc.HandlerServiceStub(self.channel)

        if protocol == "vless":
            account = vless_account_pb2.Account(id=uuid_str)
            account_typed = typed_message_pb2.TypedMessage(
                type="xray.proxy.vless.Account",
                value=account.SerializeToString()
            )
        elif protocol == "vmess":
            account = vmess_account_pb2.Account(id=uuid_str)
            account_typed = typed_message_pb2.TypedMessage(
                type="xray.proxy.vmess.Account",
                value=account.SerializeToString()
            )
        elif protocol == "trojan":
            account = trojan_account_pb2.Account(password=uuid_str)
            account_typed = typed_message_pb2.TypedMessage(
                type="xray.proxy.trojan.Account",
                value=account.SerializeToString()
            )
        elif protocol == "hysteria2":
            account_typed = typed_message_pb2.TypedMessage(
                type="xray.proxy.hysteria2.Account",
                value=b''
            )
        else:
            return False

        user = user_pb2.User(level=0, email=email, account=account_typed)
        add_user_op = command_pb2.AddUserOperation(user=user)
        op_typed = typed_message_pb2.TypedMessage(
            type="xray.app.proxyman.command.AddUserOperation",
            value=add_user_op.SerializeToString()
        )

        request = command_pb2.AlterInboundRequest(tag=inbound_tag, operation=op_typed)

        try:
            stub.AlterInbound(request)
            return True
        except grpc.RpcError as e:
            print(f"Ошибка gRPC при добавлении пользователя: {e.details()}")
            return False

    def remove_user(self, inbound_tag: str, email: str):

        stub = command_pb2_grpc.HandlerServiceStub(self.channel)
        rm_user_op = command_pb2.RemoveUserOperation(email=email)
        op_typed = typed_message_pb2.TypedMessage(
            type="xray.app.proxyman.command.RemoveUserOperation",
            value=rm_user_op.SerializeToString()
        )
        request = command_pb2.AlterInboundRequest(tag=inbound_tag, operation=op_typed)
        try:
            stub.AlterInbound(request)
            return True
        except grpc.RpcError:
            return False

    def get_stats(self, email: str):

        stub = stats_pb2_grpc.StatsServiceStub(self.channel)
        downlink = 0
        uplink = 0
        try:
            req_down = stats_pb2.GetStatsRequest(name=f"user>>{email}>>traffic>>downlink", reset=True)
            res_down = stub.GetStats(req_down)
            if res_down.stat:
                downlink = res_down.stat.value
        except grpc.RpcError:
            pass

        try:
            req_up = stats_pb2.GetStatsRequest(name=f"user>>{email}>>traffic>>uplink", reset=True)
            res_up = stub.GetStats(req_up)
            if res_up.stat:
                uplink = res_up.stat.value
        except grpc.RpcError:
            pass

        return {"uplink": uplink, "downlink": downlink}
