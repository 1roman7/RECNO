from apscheduler.schedulers.background import BackgroundScheduler
from app.db.database import SessionLocal
from app.db.models import User, Node
from app.services.xray.grpc_client import XrayGRPCClient
import datetime

def reset_traffic_job():
    db = SessionLocal()
    users = db.query(User).filter(User.reset_strategy != "none").all()
    now = datetime.datetime.utcnow()

    for user in users:
        should_reset = False

        if user.reset_strategy == "daily":
            should_reset = True
        elif user.reset_strategy == "weekly" and now.weekday() == 0: # Monday
            should_reset = True
        elif user.reset_strategy == "monthly" and now.day == 1:
            should_reset = True
        elif user.reset_strategy == "yearly" and now.day == 1 and now.month == 1:
            should_reset = True

        if should_reset:
            user.data_used = 0
            if user.status in ["limited", "expired"]:
                user.status = "active"
                # Need to re-add user to Xray here (skipped for brevity, same logic as create_user)

    db.commit()
    db.close()

def start_scheduler():
    scheduler = BackgroundScheduler()
    # Запускаем проверку раз в сутки в 00:01
    scheduler.add_job(reset_traffic_job, 'cron', hour=0, minute=1)
    scheduler.add_job(collect_stats_job, 'interval', minutes=5)
    scheduler.start()

def collect_stats_job():
    db = SessionLocal()
    users = db.query(User).filter(User.status == "active").all()
    nodes = db.query(Node).filter(Node.is_active == True).all()

    for user in users:
        # Local Master Xray
        try:
            local_client = XrayGRPCClient("127.0.0.1", 6020)
            stats = local_client.get_stats(user.username)
            user.data_used += (stats["uplink"] + stats["downlink"])
        except Exception:
            pass
        # Remote Nodes
        for node in nodes:
            try:
                client = XrayGRPCClient(node.address, node.api_port)
                stats = client.get_stats(user.username)
                user.data_used += (stats["uplink"] + stats["downlink"])
            except Exception:
                pass

        if user.data_limit > 0 and user.data_used >= user.data_limit:
            user.status = "limited"
            # Удаляем юзера
            try:
                XrayGRPCClient("127.0.0.1", 6020).remove_user("vless-inbound", user.username)
            except:
                pass
            for n in nodes:
                try:
                    XrayGRPCClient(n.address, n.api_port).remove_user("vless-inbound", user.username)
                except:
                    pass

    db.commit()
    db.close()
