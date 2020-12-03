import json
from datetime import datetime

from sqlalchemy.exc import IntegrityError, InvalidRequestError
from sqlalchemy.orm import joinedload
from werkzeug.exceptions import GatewayTimeout

from core.exceptions import TimeoutException
from core.extensions import db, mqtt, pool
from models import Contact as ContactModel, Chat, Message


def get_chats(user_id: int):

    # Get all contacts where is_moca_user (self contacts)

    contacts = (
        db.session.query(ContactModel)
            .filter(ContactModel.user_id == user_id, ContactModel.is_moca_user)
            .all()
    )

    print(contacts)

    # Ask service (via service_id) for chats

    for contact in contacts:
        if contact.service_id == "DEMO":
            continue

        phone = contact.phone.replace("+", "00")

        print(f"Asking connector for chats for user {phone}")

        mqtt.subscribe(f"telegram/users/{phone}/get_chats/response")
        pool.listen(f"telegram/users/{phone}/get_chats/response")

        mqtt.publish(f"telegram/users/{phone}/get_chats", "")

        try:
            response = pool.get(f"telegram/users/{phone}/get_chats/response")

            # Save new chats in database

            for chat in response:
                chat_id = int(chat.get("chat_id"))
                new_chat = Chat(
                    user_id=user_id,
                    chat_id=chat_id,
                    name=chat.get("name"),
                    is_muted=False,
                    is_archived=False,
                    contacts=[],
                )
                db.session.merge(new_chat)

                last_message = chat.get("last_message")

                if last_message:

                    # Get contact of the sender, else ask for it
                    contact_id = last_message.get("contact_id")

                    get_contact(user_id, phone, contact_id)

                    new_last_message = Message(
                        message_id=last_message.get("message_id"),
                        contact_id=contact_id,
                        chat_id=chat_id,
                        message=json.dumps(last_message.get("message")),
                        sent_datetime=datetime.fromisoformat(last_message.get("sent_datetime"))
                    )

                    db.session.merge(new_last_message)

                db.session.commit()

        except TimeoutException as e:
            e = GatewayTimeout()
            e.data = {"code": "GATEWAY_TIMEOUT"}
            raise e
        finally:
            mqtt.unsubscribe(f"telegram/users/{phone}/get_chats/response")


def get_contact(user_id: int, phone: str, contact_id: int):
    if (
            db.session.query(ContactModel)
                    .filter(ContactModel.contact_id == contact_id)
                    .count()
            == 0
    ):
        mqtt.subscribe(f"telegram/users/{phone}/get_contact/{contact_id}/response")
        pool.listen(f"telegram/users/{phone}/get_contact/{contact_id}/response")

        mqtt.publish(f"telegram/users/{phone}/get_contact/{contact_id}", "")

        try:
            response = pool.get(f"telegram/users/{phone}/get_contact/{contact_id}/response")

            # Save new contact in database
            contact_id = int(response.get("contact_id"))
            new_contact = ContactModel(
                contact_id=contact_id,
                service_id="TELEGRAM",
                name=response.get("name"),
                username=response.get("username"),
                phone=response.get("phone"),
                avatar=None,
                user_id=user_id
            )
            db.session.merge(new_contact)
            db.session.commit()

        except TimeoutException as e:
            e = GatewayTimeout()
            e.data = {"code": "GATEWAY_TIMEOUT"}
            raise e
        finally:
            mqtt.unsubscribe(f"telegram/users/{phone}/get_chats/response")


def get_messages(user_id: int, chat_id: int):

    contacts = (
        db.session.query(ContactModel)
            .filter(ContactModel.user_id == user_id, ContactModel.is_moca_user)
            .all()
    )

    print(contacts)

    # Ask service (via service_id) for chats

    for contact in contacts:
        if contact.service_id == "DEMO":
            continue

        phone = contact.phone.replace("+", "00")

        mqtt.subscribe(f"telegram/users/{phone}/get_messages/{chat_id}/response")
        pool.listen(f"telegram/users/{phone}/get_messages/{chat_id}/response")

        mqtt.publish(f"telegram/users/{phone}/get_messages/{chat_id}", "")

        try:
            response = pool.get(f"telegram/users/{phone}/get_messages/{chat_id}/response")

            # Save new chats in database

            for message in response:

                # Get contact of the sender, else ask for it
                contact_id = message.get("contact_id")

                get_contact(user_id, phone, contact_id)

                new_last_message = Message(
                    message_id=message.get("message_id"),
                    contact_id=contact_id,
                    chat_id=chat_id,
                    message=json.dumps(message.get("message")),
                    sent_datetime=datetime.fromisoformat(message.get("sent_datetime"))
                )

                db.session.merge(new_last_message)

        except TimeoutException as e:
            e = GatewayTimeout()
            e.data = {"code": "GATEWAY_TIMEOUT"}
            raise e
        finally:
            mqtt.unsubscribe(f"telegram/users/{phone}/get_messages/{chat_id}/response")
