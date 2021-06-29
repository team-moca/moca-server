from sqlalchemy import Column, Table, ForeignKey, Integer, String, Boolean, DateTime
from sqlalchemy.orm import relationship, backref
from .database import Base
from sqlalchemy.sql import func

# many to many relationship
class ContactsChatsRelationship(Base):
    __tablename__ = "contacts_chats_relationship"

    contact_id = Column(Integer, ForeignKey("contacts.contact_id"), primary_key=True)
    chat_id = Column(Integer, ForeignKey("chats.chat_id"), primary_key=True)

    contact = relationship("Contact", back_populates="chats")
    chat = relationship("Chat", back_populates="contacts")


class User(Base):
    __tablename__ = "users"

    user_id = Column(Integer, primary_key=True)
    username = Column(String(255), unique=True)
    mail = Column(String(255))
    hashed_password = Column(String(255))
    is_verified = Column(Boolean())
    verification_code = Column(String(6), nullable=True)
    created_at = Column(DateTime, nullable=False, server_default=func.now())
    updated_at = Column(
        DateTime,
        nullable=False,
        server_default=func.now(),
        server_onupdate=func.now(),
    )

    def __repr__(self):
        return "<User %s>" % self.username


class Contact(Base):
    __tablename__ = "contacts"

    contact_id = Column(Integer, primary_key=True, autoincrement=True)
    internal_id = Column(
        String, comment="ID that the connector uses to refer to this contact.",
        unique=True
    )

    service_id = Column(String(255))
    name = Column(String(255))
    username = Column(String(255))
    phone = Column(String(255), nullable=True)
    avatar = Column(String(255))
    connector_id = Column(
        Integer,
        ForeignKey("connectors.connector_id", ondelete="CASCADE"),
        nullable=True,
    )
    is_self = Column(Boolean, nullable=False, default=False)
    messages = relationship("Message", backref="contacts", lazy=True)

    chats = relationship("ContactsChatsRelationship", back_populates="contact")

    def __repr__(self):
        return "<Contact %s@%s>" % (self.name, self.service_id)


class Chat(Base):
    __tablename__ = "chats"

    chat_id = Column(Integer, primary_key=True, autoincrement=True)
    internal_id = Column(
        String, comment="ID that the connector uses to refer to this chat.",
        unique=True
    )
    connector_id = Column(
        Integer, ForeignKey("connectors.connector_id"), nullable=False
    )
    name = Column(String(255))
    # chat_type = Column(String(255))
    is_muted = Column(Boolean())
    is_archived = Column(Boolean())
    pin_position = Column(Integer(), nullable=True)
    contacts = relationship("ContactsChatsRelationship", back_populates="chat")
    messages = relationship("Message", backref="chats", lazy=True)

    def __repr__(self):
        return "<Chat %s>" % self.name


class Message(Base):
    __tablename__ = "messages"

    message_id = Column(Integer, primary_key=True, autoincrement=True)
    internal_id = Column(
        String, comment="ID that the connector uses to refer to this message.",
        unique=True
    )

    contact_id = Column(
        Integer, ForeignKey("contacts.contact_id", ondelete="CASCADE"), nullable=False
    )
    chat_id = Column(
        Integer, ForeignKey("chats.chat_id", ondelete="CASCADE"), nullable=False
    )
    message = Column(String())  # JSON
    sent_datetime = Column(DateTime())

    def __repr__(self):
        return "<Message %s>" % self.message_id


class Connector(Base):
    __tablename__ = "connectors"

    connector_id = Column(Integer, primary_key=True)
    connector_type = Column(String(255))
    user_id = Column(Integer, ForeignKey("users.user_id"))
    connector_user_id = Column(String(255))
    configuration = Column(String())  # JSON
    is_finished = Column(Boolean(), nullable=False, default=False)
    contacts = relationship("Contact", backref="connectors", lazy=True)

    def __repr__(self):
        return "<%s-Connector %s>" % (self.connector_type, self.connector_id)


class Session(Base):
    __tablename__ = "sessions"

    session_id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.user_id"))
    name = Column(String(255))
    valid_until = Column(DateTime())

    def __repr__(self):
        return "<Session %s (%s)>" % (self.session_id, self.name)
