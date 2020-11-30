import enum

from flask_restx import fields


class ChatType(enum.Enum):
    single = "single"
    multi = "multi"
    group = "group"

def get_contact_schema(api):
    return api.model(
        "Contact",
        {
            "contact_id": fields.String,
            "service_id": fields.String,
            "username": fields.String,
            "phone": fields.String,
            "name": fields.String,
            "avatar": fields.String,
        },
    )


def get_chat_schema(api):

    return api.model(
        "Chat",
        {
            "chat_id": fields.String,
            "name": fields.String,
            "chat_type": fields.String(
                description="Type of chat. single for a normal one to one chat, multi for a chat that combines the chat with one person via multiple services, group for groups (via exactly one service).",
                example="single",
                enum=ChatType._member_names_,
            ),
            "contacts": fields.List(fields.Nested(get_contact_schema(api))),
            "last_message": fields.Nested(get_message_schema(api)),
        },
    )


def get_message_schema(api):
    return api.model(
        "Message",
        {
            "message_id": fields.Integer(
                description="Unique id identifying this message.", example=56183044
            ),
            "contact_id": fields.Integer(
                description="Sender's contact id. If sending a message, this field will be ignored.",
                example=100,
            ),
            "message": fields.Raw(
                description="A JSON object representing the message. You can get the type by looking at the type property in this json."
            ),
            "sent_datetime": fields.DateTime(
                description="Datetime this message was sent by the sender.",
                example="2020-11-11T09:02:30",
            ),
        },
    )
