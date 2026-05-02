class XrayGRPCClient:
    """Клиент для управления Xray через gRPC порт (обычно 6020)"""
    def __init__(self, host: str, port: int):
        self.target = f"{host}:{port}"
        # В реальном приложении здесь инициализируется grpc канал
        # self.channel = grpc.insecure_channel(self.target)

    def add_user(self, inbound_tag: str, email: str, uuid_str: str):
        """Добавление пользователя на лету"""
        print(f"[gRPC] Добавление юзера {email} ({uuid_str}) в {inbound_tag} на {self.target}...")
        # Реализация:
        # stub = command_pb2_grpc.HandlerServiceStub(self.channel)
        # request = ...
        # stub.AlterInbound(request)
        return True

    def remove_user(self, inbound_tag: str, email: str):
        """Удаление пользователя на лету"""
        print(f"[gRPC] Удаление юзера {email} из {inbound_tag} на {self.target}...")
        return True

    def get_stats(self, email: str):
        """Получение статистики (uplink/downlink)"""
        print(f"[gRPC] Запрос статистики для {email} на {self.target}...")
        return {"uplink": 1024000, "downlink": 2048000}
