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
                        new_chat = models.Chat(
                            user_id=connector.user_id,
                            chat_id=chat_id,
                            name=chat_data.get("name"),
                            is_muted=False,
                            is_archived=False,
                            contacts=[],
                        )
                        db.merge(new_chat)
                        db.commit()

                        last_message = chat_data.get("last_message")

                        if last_message:

                            # Get contact of the sender, else ask for it
                            contact_id = last_message.get("contact_id")

                            # check if contact exists, else request contact
                            if not crud.get_contact(db, connector.user_id, contact_id):
                                await self.get_contact(connector.connector_id, contact_id)

                            new_last_message = models.Message(
                                message_id=last_message.get("message_id"),
                                contact_id=contact_id,
                                chat_id=chat_id,
                                message=json.dumps(last_message.get("message")),
                                sent_datetime=datetime.fromisoformat(last_message.get("sent_datetime"))
                            )

                            db.merge(new_last_message)
        finally:
            db.close()


    async def get_contact(self, connector_id, contact_id):
        return await self.pool.get(f"telegram/users/{connector_id}/get_contact/{contact_id}", {})
