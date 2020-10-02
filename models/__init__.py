from core.extensions import db

# many to many relationship
contacts_chats_relationship = db.Table('contacts_chats_relationship',
    db.Column('contact_id', db.Integer, db.ForeignKey('contact.contact_id'), primary_key=True),
    db.Column('chat_id', db.Integer, db.ForeignKey('chat.chat_id'), primary_key=True)
)

class User(db.Model):
    user_id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(255), unique=True)
    mail = db.Column(db.String(255))
    password_hash = db.Column(db.String(255))
    is_verified = db.Column(db.Boolean())
    verification_code = db.Column(db.String(6), nullable=True)
    created_at = db.Column(db.DateTime, nullable=False, server_default=db.func.now())
    updated_at = db.Column(db.DateTime, nullable=False, server_default=db.func.now(), server_onupdate=db.func.now())
    contacts = db.relationship('Contact', backref='user', lazy=True)

    def __repr__(self):
        return '<User %s>' % self.username

class Contact(db.Model):
    contact_id = db.Column(db.Integer, primary_key=True)
    service_id = db.Column(db.String(255))
    name = db.Column(db.String(255))
    username = db.Column(db.String(255))
    phone = db.Column(db.String(255), nullable=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.user_id'),
        nullable=True)
    chats = db.relationship('Chat', secondary=contacts_chats_relationship, lazy=True,
        backref=db.backref('contacts', lazy='subquery'))
    messages = db.relationship('Message', backref='contact', lazy=True)

    def __repr__(self):
        return '<Contact %s@%s>' % (self.name, self.service_id)

class Chat(db.Model):
    chat_id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255))
    #chat_type = db.Column(db.String(255))
    is_muted = db.Column(db.Boolean())
    is_archived = db.Column(db.Boolean())
    pin_position = db.Column(db.Integer(), nullable=True)
    messages = db.relationship('Message', backref='chat', lazy=True)

    def __repr__(self):
        return '<Chat %s>' % self.name

class Message(db.Model):
    message_id = db.Column(db.Integer, primary_key=True)
    contact_id = db.Column(db.Integer, db.ForeignKey('contact.contact_id'),
        nullable=False)
    chat_id = db.Column(db.Integer, db.ForeignKey('chat.chat_id'),
        nullable=False)
    message = db.Column(db.String()) # JSON

class Connector(db.Model):
    connector_id = db.Column(db.Integer, primary_key=True)
    connector_type = db.Column(db.String(255))
    user_id = db.Column(db.Integer, db.ForeignKey('user.user_id'))
    configuration = db.Column(db.String()) # JSON

    def __repr__(self):
        return '<%s-Connector %s>' % (self.connector_type, self.connector_id)