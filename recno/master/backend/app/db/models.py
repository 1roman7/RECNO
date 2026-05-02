from sqlalchemy import Column, Integer, String, Boolean, ForeignKey, DateTime, BigInteger
from sqlalchemy.orm import declarative_base, relationship
from datetime import datetime

Base = declarative_base()

class User(Base):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    uuid = Column(String, unique=True, index=True) # Used for Xray Auth
    data_limit = Column(BigInteger, default=0) # 0 means unlimited
    data_used = Column(BigInteger, default=0)
    expire_date = Column(DateTime, nullable=True)
    status = Column(String, default="active") # active, disabled
    created_at = Column(DateTime, default=datetime.utcnow)

class Node(Base):
    __tablename__ = 'nodes'
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String)
    address = Column(String)
    api_port = Column(Integer, default=6020)
    api_tls = Column(Boolean, default=False)

class ProxyKey(Base):
    __tablename__ = 'proxy_keys'
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String)
    link = Column(String) # The actual vless:// or hysteria2:// link
    is_global = Column(Boolean, default=False)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=True) # If null and not global, it's unassigned

    user = relationship("User", back_populates="keys")

User.keys = relationship("ProxyKey", order_by=ProxyKey.id, back_populates="user")

class SubscriptionConfig(Base):
    __tablename__ = 'sub_config'
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, default="RECNO Subscription")
    description = Column(String, default="Welcome to RECNO. Enjoy your proxy.")
