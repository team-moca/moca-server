from app import crud, models
from typing import Dict
from sqlalchemy.orm.session import Session


class ServiceHandler:
    def __init__(self, db):
        self._db = db

    @property
    def db(self):
        return self._db()

    async def handle(self, topic: str, payload: Dict):
        
        parts = topic.split("/")

        if len(parts) < 2 or parts[0] != "moca":
            return

        # moca/...

        if parts[1] == "via" and len(parts) >= 5:
            # data from a service (e.g. moca-service-telegram)
            # example: moca/via/telegram/4/contacts --> add or update contact(s)

            service: str = parts[2]
            service_id: int = int(parts[3])
            command: str = parts[4]

            connector = crud.get_connector_by_service_id(self.db, service, service_id)

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
                    self.db.merge(new_contact)
                    self.db.commit()
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
                    self.db.merge(new_chat)
                    self.db.commit()


        
