import uuid

import sqlalchemy
from app.pool import Pool
from datetime import datetime
import json
from app import crud, models
from typing import Dict
from sqlalchemy.orm.session import Session
from app.database import SessionLocal


class ServiceHandler:
    def __init__(self, pool: Pool):
        self.pool = pool

    async def handle(self, topic: str, payload: Dict):
        db = SessionLocal()

        try:
            parts = topic.split("/")

            if len(parts) < 2 or parts[0] != "moca":
                return

            # moca/...

            if parts[1] == "via" and len(parts) >= 5:
                # data from a service (e.g. moca-service-telegram)
                # example: moca/via/telegram/4/contacts --> add or update contact(s)

                service: str = parts[2]
                connector_id: int = int(parts[3])
                command: str = parts[4]

                connector = crud.get_connector_by_connector_id(
                    db, service, connector_id
                )

                if not connector:
                    print("No connector configured.")
                    return

                if command == "contacts":
                    for contact_data in payload:
                        internal_contact_id = contact_data.get("contact_id")

                        maybe_contact = crud.get_contact_from_connector(
                            db, connector.user_id, connector.connector_id, internal_contact_id
                        )
                        if maybe_contact:
                            new_contact = models.Contact(
                                contact_id=maybe_contact.contact_id,
                                internal_id=internal_contact_id,
                                service_id=service,
                                name=contact_data.get("name"),
                                username=contact_data.get("username"),
                                phone=contact_data.get("phone"),
                                avatar=None,
                                connector_id=connector.connector_id,
                            )
                            db.merge(new_contact)
                            db.commit()
                        else:
                            new_contact = models.Contact(
                                internal_id=internal_contact_id,
                                service_id=service,
                                name=contact_data.get("name"),
                                username=contact_data.get("username"),
                                phone=contact_data.get("phone"),
                                avatar=None,
                                connector_id=connector.connector_id,
                            )
                            db.add(new_contact)
                            db.commit()
                elif command == "chats":
                    for chat_data in payload:
                        internal_chat_id = chat_data.get("chat_id")

                        # TODO this should just merge the chats, because deleting a chat would
                        # hurt the primary key constraints
                        chat = db.query(models.Chat).filter(
                            models.Chat.internal_id == internal_chat_id,
                            models.Chat.connector_id == connector.connector_id,
                        ).first()

                        if not chat:
                            chat = models.Chat(
                                connector_id=connector.connector_id,
                                internal_id=internal_chat_id,
                                name=chat_data.get("name"),
                                is_muted=False,
                                is_archived=False,
                            )

                            db.add(chat)
                            db.commit()
                        else:
                            chat = models.Chat(
                                chat_id = chat.chat_id,
                                connector_id=connector.connector_id,
                                internal_id=internal_chat_id,
                                name=chat_data.get("name"),
                                is_muted=False,
                                is_archived=False,
                            )

                            db.update(chat)
                            db.commit()
                        

                        chat_id = chat.chat_id

                        last_message = chat_data.get("last_message")

                        if last_message:

                            # Get contact of the sender, else ask for it
                            internal_contact_id = last_message.get("contact_id")

                            # check if contact exists, else request contact
                            maybe_contact = crud.get_contact_from_connector(
                                db,
                                connector.user_id,
                                connector.connector_id,
                                internal_contact_id,
                            )

                            if not maybe_contact:
                                contact = await self.get_contact(
                                    connector.connector_type, connector.connector_id, internal_contact_id
                                )
                                print(f"Got contact from service: {contact.get('name')}")
                                new_contact = models.Contact(
                                    internal_id=internal_contact_id,
                                    service_id=connector.connector_type,
                                    connector_id=connector.connector_id,
                                    name=contact.get("name"),
                                    username=contact.get("username"),
                                    phone=contact.get("phone"),
                                    avatar=contact.get("avatar"),
                                    is_self=False,
                                )
                                db.add(new_contact)
                                db.commit()

                                contact_id = new_contact.contact_id
                            else:
                                contact_id = maybe_contact.contact_id

                            # TODO: Reimplement last message
                            # new_last_message = models.Message(
                            #     message_id=last_message.get("message_id"),
                            #     contact_id=contact_id,
                            #     internal_id=chat_id,
                            #     message=json.dumps(last_message.get("message")),
                            #     sent_datetime=datetime.fromisoformat(last_message.get("sent_datetime"))
                            # )

                            # db.merge(new_last_message)
                            # db.commit()

                        participants = chat_data.get("participants")
                        if participants:
                            for participant in participants:
                                c = crud.get_contact_from_connector(
                                    db,
                                    connector.user_id,
                                    connector.connector_id,
                                    participant,
                                )
                                if not c:
                                    contact = await self.get_contact(
                                        connector.connector_type, connector.connector_id, participant
                                    )
                                    print(f"Got contact from service: {contact.get('name')}")
                                    c = models.Contact(
                                        internal_id=participant,
                                        service_id=connector.connector_type,
                                        connector_id=connector.connector_id,
                                        name=contact.get("name"),
                                        username=contact.get("username"),
                                        phone=contact.get("phone"),
                                        avatar=contact.get("avatar"),
                                        is_self=False,
                                    )
                                    db.add(c)
                                    db.commit()

                                db.add(
                                    models.ContactsChatsRelationship(
                                        contact_id=c.contact_id, chat_id=chat_id
                                    )
                                )
                                try:
                                    db.commit()
                                except sqlalchemy.exc.IntegrityError:
                                    db.rollback()

                elif command == "messages":
                    for message_data in payload:

                        # Get contact of the sender, else ask for it
                        internal_contact_id = message_data.get("contact_id")

                        # check if contact exists, else request contact
                        c = crud.get_contact_from_connector(
                            db,
                            connector.user_id,
                            connector.connector_id,
                            internal_contact_id,
                        )
                        if not c:
                            contact = await self.get_contact(
                                connector.connector_type, connector.connector_id, internal_contact_id
                            )
                            print(f"Got contact from service: {contact.get('name')}")
                            c = models.Contact(
                                internal_id=internal_contact_id,
                                service_id=connector.connector_type,
                                connector_id=connector.connector_id,
                                name=contact.get("name"),
                                username=contact.get("username"),
                                phone=contact.get("phone"),
                                avatar=contact.get("avatar"),
                                is_self=False,
                            )
                            db.add(c)
                            db.commit()
                        else:
                            # print(f"Contact {c.name} already exists. Skipping...")
                            pass

                        chat = (
                            db.query(models.Chat)
                            .filter(
                                models.Chat.connector_id == connector_id,
                                models.Chat.internal_id == message_data.get("chat_id"),
                            )
                            .first()
                        )

                        if not chat:
                            chat = models.Chat(
                                connector_id=connector_id,
                                internal_id=message_data.get("chat_id"),
                                name="Loading...",
                                is_muted=False,
                                is_archived=False,
                            )

                            db.add(chat)
                            db.commit()

                        new_last_message = models.Message(
                            internal_id=message_data.get("message_id"),
                            contact_id=c.contact_id,
                            chat_id=chat.chat_id,
                            message=json.dumps(message_data.get("message")),
                            sent_datetime=datetime.fromisoformat(
                                message_data.get("sent_datetime")
                            ),
                        )

                        crud.add_or_update_message(db, connector_id, new_last_message)
                        



        finally:
            db.close()

    async def get_contact(self, connector_type, connector_id, contact_id):
        return await self.pool.get(
            f"{connector_type}/{connector_id}/{str(uuid.uuid4())}/get_contact/{contact_id}", {}
        )
