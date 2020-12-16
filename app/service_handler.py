import uuid
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

                connector = crud.get_connector_by_connector_id(db, service, connector_id)

                if not connector:
                    print("No connector configured.")
                    return

                if command == "contacts":
                    for contact_data in payload:
                        contact_id = int(contact_data.get("contact_id"))
                        new_contact = models.Contact(
                            contact_id=contact_id,
                            service_id=service,
                            name=contact_data.get("name"),
                            username=contact_data.get("username"),
                            phone=contact_data.get("phone"),
                            avatar=None,
                            connector_id=connector.connector_id
                        )
                        db.merge(new_contact)
                        db.commit()
                elif command == "chats":
                    for chat_data in payload:
                        chat_id = int(chat_data.get("chat_id"))
                        
                        last_message = chat_data.get("last_message")

                        if last_message:

                            # Get contact of the sender, else ask for it
                            contact_id = last_message.get("contact_id")

                            # check if contact exists, else request contact
                            if not crud.get_contact(db, connector.user_id, contact_id):
                                contact = await self.get_contact(connector.connector_id, contact_id)
                                print(f"Got contact from service: {contact}")
                                new_contact = models.Contact(
                                    contact_id = contact_id,
                                    service_id = connector.connector_type,
                                    connector_id=connector.connector_id,
                                    name=contact.get("name"),
                                    username=contact.get("username"),
                                    phone=contact.get("phone"),
                                    avatar=contact.get("avatar"),
                                    is_self=False
                                )
                                db.merge(new_contact)
                                db.commit()

                            new_last_message = models.Message(
                                message_id=last_message.get("message_id"),
                                contact_id=contact_id,
                                chat_id=chat_id,
                                message=json.dumps(last_message.get("message")),
                                sent_datetime=datetime.fromisoformat(last_message.get("sent_datetime"))
                            )

                            db.merge(new_last_message)
                            db.commit()

                        participants = chat_data.get("participants")
                        chat_contacts = []
                        if participants:
                            print(participants)
                            for participant in participants:
                                c = crud.get_contact(db, connector.user_id, participant)
                                if not c:
                                    contact = await self.get_contact(connector.connector_id, participant)
                                    print(f"Got contact from service: {contact}")
                                    c = models.Contact(
                                        contact_id = participant,
                                        service_id = connector.connector_type,
                                        connector_id=connector.connector_id,
                                        name=contact.get("name"),
                                        username=contact.get("username"),
                                        phone=contact.get("phone"),
                                        avatar=contact.get("avatar"),
                                        is_self=False
                                    )
                                    db.merge(c)
                                    db.commit()

                                chat_contacts.append(c)

                                db.add(models.ContactsChatsRelationship(contact_id=participant, chat_id=chat_id))

                        db.query(models.Chat).filter(models.Chat.chat_id == chat_id).delete()
                        db.commit()

                        new_chat = models.Chat(
                            user_id=connector.user_id,
                            chat_id=chat_id,
                            name=chat_data.get("name"),
                            is_muted=False,
                            is_archived=False,
                        )

                        db.add(new_chat)
                        db.commit()


                elif command == "messages":
                    for message_data in payload:

                        # Get contact of the sender, else ask for it
                        contact_id = message_data.get("contact_id")

                        # check if contact exists, else request contact
                        if not crud.get_contact(db, connector.user_id, contact_id):
                            contact = await self.get_contact(connector.connector_id, contact_id)
                            print(f"Got contact from service: {contact}")
                            new_contact = models.Contact(
                                contact_id = contact_id,
                                service_id = connector.connector_type,
                                connector_id=connector.connector_id,
                                name=contact.get("name"),
                                username=contact.get("username"),
                                phone=contact.get("phone"),
                                avatar=contact.get("avatar"),
                                is_self=False
                            )
                            db.merge(new_contact)
                            db.commit()

                        new_last_message = models.Message(
                            message_id=message_data.get("message_id"),
                            contact_id=contact_id,
                            chat_id=message_data.get("chat_id"),
                            message=json.dumps(message_data.get("message")),
                            sent_datetime=datetime.fromisoformat(message_data.get("sent_datetime"))
                        )

                        db.merge(new_last_message)
                        db.commit()


        finally:
            db.close()


    async def get_contact(self, connector_id, contact_id):
        return await self.pool.get(f"telegram/{connector_id}/{str(uuid.uuid4())}/get_contact/{contact_id}", {})
