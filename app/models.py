from sqlalchemy import Column, Table, ForeignKey, Integer, String, Boolean, DateTime
from sqlalchemy.orm  import relationship, backref
from sqlalchemy.sql.expression import func
from .database import Base


# many to many relationship
contacts_chats_relationship = Table(
    "contacts_chats_relationship",
    Base.metadata,
    Column(
        "contact_id", Integer, ForeignKey("contacts.contact_id"), primary_key=True
    ),
    Column("chat_id", Integer, ForeignKey("chats.chat_id"), primary_key=True),
)


class User(Base):
    __tablename__ = "users"

    user_id = Column(Integer, primary_key=True)
    username = Column(String(255), unique=True)
    mail = Column(String(255))
    password_hash = Column(String(255))
    is_verified = Column(Boolean())
    verification_code = Column(String(6), nullable=True)
    created_at = Column(DateTime, nullable=False, server_default=func.now())
    updated_at = Column(
        DateTime,
        nullable=False,
        server_default=func.now(),
        server_onupdate=func.now(),
    )
    contacts = relationship("Contact", backref="users", lazy=True)

    def __repr__(self):
        return "<User %s>" % self.username


class Contact(Base):
    __tablename__ = "contacts"

    contact_id = Column(Integer, primary_key=True)
    service_id = Column(String(255))
    name = Column(String(255))
    username = Column(String(255))
    phone = Column(String(255), nullable=True)
    avatar = Column(String(255))
    user_id = Column(Integer, ForeignKey("users.user_id"), nullable=True)
    is_moca_user = Column(Boolean, nullable=False, default=False)
    chats = relationship(
        "Chat",
        secondary=contacts_chats_relationship,
        lazy=True,
        backref=backref("contacts", lazy="subquery"),
    )
    messages = relationship("Message", backref="contacts", lazy=True)

    def __repr__(self):
        return "<Contact %s@%s>" % (self.name, self.service_id)


class Chat(Base):
    __tablename__ = "chats"

    user_id = Column(Integer, ForeignKey("users.user_id"), nullable=False)
    chat_id = Column(Integer, primary_key=True)
    name = Column(String(255))
    # chat_type = Column(String(255))
    is_muted = Column(Boolean())
    is_archived = Column(Boolean())
    pin_position = Column(Integer(), nullable=True)
    messages = relationship("Message", backref="chats", lazy=True)

    def __repr__(self):
        return "<Chat %s>" % self.name


class Message(Base):
    __tablename__ = "messages"
    
    message_id = Column(Integer, primary_key=True)
    contact_id = Column(
        Integer, ForeignKey("contacts.contact_id"), nullable=False
    )
    chat_id = Column(Integer, ForeignKey("chats.chat_id"), nullable=False)
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

    def __repr__(self):
        return "<%s-Connector %s>" % (self.connector_type, self.connector_id)
