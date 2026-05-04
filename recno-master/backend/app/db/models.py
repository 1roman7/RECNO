from sqlalchemy import Column, Integer, String, Boolean, ForeignKey, DateTime, BigInteger, Text, Table
from sqlalchemy.orm import declarative_base, relationship
from datetime import datetime

Base = declarative_base()

# Association table for targeted CustomKeys to specific Users
user_custom_keys_association = Table(
    'user_custom_keys', Base.metadata,
    Column('user_id', Integer, ForeignKey('users.id', ondelete="CASCADE")),
    Column('custom_key_id', Integer, ForeignKey('custom_keys.id', ondelete="CASCADE"))
)

class Admin(Base):
    """Администраторы панели"""
    __tablename__ = 'admins'
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    sub_id = Column(String, unique=True, index=True, nullable=True)
    hashed_password = Column(String)
    is_superadmin = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)

class Node(Base):
    """Подключенные удаленные серверы (Ноды)"""
    __tablename__ = 'nodes'
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True)
    address = Column(String) # IP или домен
    api_port = Column(Integer, default=6020)
    is_active = Column(Boolean, default=True)
    xray_config = Column(Text, nullable=True) # JSON конфиг Xray ноды
    created_at = Column(DateTime, default=datetime.utcnow)

class User(Base):
    """Пользователи (клиенты)"""
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    sub_id = Column(String, unique=True, index=True, nullable=True)
    status = Column(String, default="active") # active, disabled
    expire_date = Column(DateTime, nullable=True)
    data_limit = Column(BigInteger, default=0) # Общий лимит в байтах, 0 - безлимит
    data_used = Column(BigInteger, default=0)
    ip_limit = Column(Integer, default=0) # 0 = безлимит
    reset_strategy = Column(String, default="none") # none, daily, weekly, monthly, yearly
    created_at = Column(DateTime, default=datetime.utcnow)

    # Ключи пользователя
    keys = relationship("ProxyKey", back_populates="user", cascade="all, delete-orphan")
    custom_keys = relationship("CustomKey", secondary=user_custom_keys_association, back_populates="users")

class ProxyKey(Base):
    """Конкретные сгенерированные ключи/прокси пользователя для Inbounds"""
    __tablename__ = 'proxy_keys'
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey('users.id'))
    node_id = Column(Integer, ForeignKey('nodes.id'), nullable=True)

    private_key = Column(String, nullable=True)
    public_key = Column(String, nullable=True)
    short_id = Column(String, nullable=True)

    remark = Column(String)
    protocol = Column(String)
    link = Column(String)

    uuid = Column(String, index=True, nullable=True)

    data_used = Column(BigInteger, default=0)
    ip_limit = Column(Integer, default=0)
    reset_strategy = Column(String, default="none")

    is_custom = Column(Boolean, default=False)

    user = relationship("User", back_populates="keys")
    node = relationship("Node")

class Inbound(Base):
    """Универсальные Inbounds Xray"""
    __tablename__ = 'inbounds'
    id = Column(Integer, primary_key=True, index=True)
    remark = Column(String, default="Inbound")
    protocol = Column(String, default="vless") # vless, vmess, trojan, hysteria2
    port = Column(Integer, default=443)
    transport = Column(String, default="tcp") # tcp, ws, grpc, xhttp
    security = Column(String, default="none") # none, tls, reality
    sni = Column(String, nullable=True)
    fingerprint = Column(String, default="chrome") # chrome, safari, qq, random
    dest = Column(String, nullable=True) # for reality
    server_names = Column(String, nullable=True) # comma separated for reality
    alpn = Column(String, nullable=True) # h2,http/1.1
    node_id = Column(Integer, ForeignKey('nodes.id'), nullable=True)

    private_key = Column(String, nullable=True)
    public_key = Column(String, nullable=True)
    short_id = Column(String, nullable=True) # None = Master node

    node = relationship("Node")

class CustomKey(Base):
    """Кастомные (сторонние) ключи"""
    __tablename__ = 'custom_keys'
    id = Column(Integer, primary_key=True, index=True)
    remark = Column(String)
    link = Column(String)
    is_global = Column(Boolean, default=False) # Если True - выдается всем

    users = relationship("User", secondary=user_custom_keys_association, back_populates="custom_keys")

class SystemSettings(Base):
    """Настройки панели и подписки (Profile-Title, Update Interval и тд)"""
    __tablename__ = 'system_settings'
    id = Column(Integer, primary_key=True, index=True)
    sub_title = Column(String, default="RECNO PROXY")
    sub_update_interval = Column(Integer, default=24) # in hours
    master_xray_config = Column(Text, nullable=True) # Встроенный Xray Master-сервера
