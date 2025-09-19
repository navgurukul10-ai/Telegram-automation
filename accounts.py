# from telethon import TelegramClient
# import os
# import logging

# class AccountManager:
#     def __init__(self, accounts):
#         self.accounts = accounts
#         self.clients = []
#         os.makedirs("sessions", exist_ok=True)

#     async def init_clients(self):
#         self.clients = []
#         for acc in self.accounts:
#             session_name = os.path.join("sessions", acc['phone'].replace("+", ""))
#             client = TelegramClient(session_name, acc['api_id'], acc['api_hash'])
#             await client.start(phone=acc['phone'])
#             self.clients.append({"client": client, "phone": acc['phone']})
#             logging.info(f"✅ Logged in: {acc['phone']}")
#         return self.clients

#     async def close_clients(self):
#         for item in self.clients:
#             client = item["client"] if isinstance(item, dict) else item
#             await client.disconnect()
import os
import logging
from telethon import TelegramClient
from telethon.sessions import StringSession

class AccountManager:
    def __init__(self, accounts):
        self.accounts = accounts
        self.clients = []
        os.makedirs("sessions", exist_ok=True)

    async def init_clients(self):
        self.clients = []
        for acc in self.accounts:
            session_path = os.path.join("sessions", acc['phone'].replace("+", ""))
            session_string = None
            if os.path.exists(session_path):
                with open(session_path, "r") as f:
                    session_string = f.read().strip()

            client = TelegramClient(StringSession(session_string), acc['api_id'], acc['api_hash'])
            await client.start(phone=acc['phone'])

            # Save session string (avoids SQLite locking issue)
            with open(session_path, "w") as f:
                f.write(client.session.save())

            self.clients.append({"client": client, "phone": acc['phone']})
            logging.info(f"✅ Logged in: {acc['phone']}")
        return self.clients

    async def close_clients(self):
        for item in self.clients:
            client = item["client"]
            await client.disconnect()
