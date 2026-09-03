"""SQLAlchemy Database Models for Transactions, Wallets, Alerts, Audit Logs, and Users."""

import datetime
from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime, Text, JSON
from backend.database.session import Base


class DBUser(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(64), unique=True, index=True, nullable=False)
    email = Column(String(128), unique=True, index=True, nullable=False)
    hashed_password = Column(String(256), nullable=False)
    role = Column(String(32), default="investigator")  # admin, investigator, auditor, api_user
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)


class DBTransaction(Base):
    __tablename__ = "transactions"

    id = Column(Integer, primary_key=True, index=True)
    tx_hash = Column(String(128), unique=True, index=True, nullable=False)
    chain = Column(String(32), index=True, default="ethereum")
    sender = Column(String(128), index=True, nullable=False)
    receiver = Column(String(128), index=True, nullable=False)
    amount = Column(Float, nullable=False)
    fee = Column(Float, default=0.0)
    timestamp = Column(DateTime, default=datetime.datetime.utcnow, index=True)
    block_number = Column(Integer, index=True)
    risk_score = Column(Float, default=0.0, index=True)
    risk_tier = Column(String(32), default="LOW")
    is_flagged = Column(Boolean, default=False)
    explainability = Column(JSON, nullable=True)


class DBWallet(Base):
    __tablename__ = "wallets"

    id = Column(Integer, primary_key=True, index=True)
    address = Column(String(128), unique=True, index=True, nullable=False)
    chain = Column(String(32), index=True, default="ethereum")
    risk_score = Column(Float, default=0.0)
    risk_tier = Column(String(32), default="LOW")
    is_sanctioned = Column(Boolean, default=False)
    tag = Column(String(64), default="unlabeled")  # exchange, mixer, darknet, whale, normal
    total_received = Column(Float, default=0.0)
    total_sent = Column(Float, default=0.0)
    last_seen = Column(DateTime, default=datetime.datetime.utcnow)


class DBAlert(Base):
    __tablename__ = "alerts"

    id = Column(Integer, primary_key=True, index=True)
    alert_id = Column(String(64), unique=True, index=True, nullable=False)
    tx_hash = Column(String(128), index=True, nullable=False)
    severity = Column(String(32), default="HIGH")  # CRITICAL, HIGH, MEDIUM, LOW
    alert_type = Column(String(64), nullable=False)  # PEELING_CHAIN, SANCTION_HIT, VELOCITY_SPIKE, MIXER_HOP
    description = Column(Text, nullable=False)
    status = Column(String(32), default="OPEN")  # OPEN, INVESTIGATING, RESOLVED, DISMISSED
    created_at = Column(DateTime, default=datetime.datetime.utcnow)


class DBAuditLog(Base):
    __tablename__ = "audit_logs"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, nullable=True)
    action = Column(String(64), nullable=False)
    entity_type = Column(String(32), nullable=False)  # TRANSACTION, WALLET, ALERT
    entity_id = Column(String(128), nullable=False)
    details = Column(JSON, nullable=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
