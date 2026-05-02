import grpc
import sys
import os

# Добавляем путь к сгенерированным протобаф файлам, чтобы импорты внутри работали корректно
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), 'proto')))

from app.proxyman.command import command_pb2
from app.proxyman.command import command_pb2_grpc
from app.stats.command import command_pb2 as stats_pb2
from app.stats.command import command_pb2_grpc as stats_pb2_grpc
from common.serial import typed_message_pb2
from common.protocol import user_pb2
from proxy.vless import account_pb2

class XrayGRPCClient:
    def __init__(self, host: str, port: int):
        self.target = f"{host}:{port}"
        self.channel = grpc.insecure_channel(self.target)

    def add_user(self, inbound_tag: str, email: str, uuid_str: str):
        stub = command_pb2_grpc.HandlerServiceStub(self.channel)

        # Создаем аккаунт VLESS
        vless_account = account_pb2.Account(id=uuid_str)

        account_typed = typed_message_pb2.TypedMessage(
            type="xray.proxy.vless.Account",
            value=vless_account.SerializeToString()
        )

        user = user_pb2.User(
            level=0,
            email=email,
            account=account_typed
        )

        add_user_op = command_pb2.AddUserOperation(user=user)

        op_typed = typed_message_pb2.TypedMessage(
            type="xray.app.proxyman.command.AddUserOperation",
            value=add_user_op.SerializeToString()
        )

        request = command_pb2.AlterInboundRequest(
            tag=inbound_tag,
            operation=op_typed
        )

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

        request = command_pb2.AlterInboundRequest(
            tag=inbound_tag,
            operation=op_typed
        )

        try:
            stub.AlterInbound(request)
            return True
        except grpc.RpcError as e:
            print(f"Ошибка gRPC при удалении пользователя: {e.details()}")
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
