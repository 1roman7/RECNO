from sqlalchemy import Column, Integer, String, Boolean, ForeignKey, DateTime, BigInteger, Text
from sqlalchemy.orm import declarative_base, relationship
from datetime import datetime

Base = declarative_base()

class Admin(Base):
    """Администраторы панели"""
    __tablename__ = 'admins'
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    sub_id = Column(String, unique=True, index=True, nullable=True)
    hashed_password = Column(String)
    is_superadmin = Column(Boolean, default=False) # True - полный доступ, False - только создание подписок
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
    reset_strategy = Column(String, default="none") # none, daily, weekly, monthly, yearly  # Общий использованный трафик
    created_at = Column(DateTime, default=datetime.utcnow)

    # Ключи пользователя
    keys = relationship("ProxyKey", back_populates="user", cascade="all, delete-orphan")

class ProxyKey(Base):
    """Конкретные ключи/прокси пользователя"""
    __tablename__ = 'proxy_keys'
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey('users.id'))
    node_id = Column(Integer, ForeignKey('nodes.id'), nullable=True) # Если None - ключ на Master сервере или сторонний

    remark = Column(String) # Название ключа в приложении (VLESS - Германия и тд)
    protocol = Column(String) # vless, hysteria2, custom
    link = Column(String) # Сам ключ (vless://... или сторонний)

    uuid = Column(String, index=True, nullable=True) # Внутренний ID для Xray, чтобы считать трафик

    data_used = Column(BigInteger, default=0)
    ip_limit = Column(Integer, default=0) # 0 = безлимит
    reset_strategy = Column(String, default="none") # none, daily, weekly, monthly, yearly # Статистика конкретного ключа

    is_custom = Column(Boolean, default=False) # True - если это сторонний ключ, трафик по нему не считаем

    user = relationship("User", back_populates="keys")
    node = relationship("Node")

class PanelConfig(Base):
    """Настройки панели и подписки"""
    __tablename__ = 'panel_config'
    id = Column(Integer, primary_key=True, index=True)
    sub_title = Column(String, default="RECNO PROXY")
    sub_description = Column(String, default="Ваша лучшая подписка")
    master_xray_config = Column(Text, nullable=True) # Встроенный Xray Master-сервера
