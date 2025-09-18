from telethon import TelegramClient
from telethon.sessions import StringSession
import os
import logging

class AccountManager:
    def __init__(self, accounts):
        self.accounts = accounts
        self.clients = []
        os.makedirs("sessions", exist_ok=True)

    async def init_clients(self):
        self.clients = []
        for acc in self.accounts:
            session_name = os.path.join("sessions", acc['phone'].replace("+", ""))
            # Prefer provided string session for non-interactive auth; fallback to local session file
            string_session = (acc.get('session') or '').strip()
            if string_session:
                client = TelegramClient(StringSession(string_session), acc['api_id'], acc['api_hash'])
                await client.connect()
                if not await client.is_user_authorized():
                    # If provided session is invalid, fallback to interactive start
                    logging.warning(f"Session string invalid for {acc['phone']}, falling back to interactive login")
                    client = TelegramClient(session_name, acc['api_id'], acc['api_hash'])
                    await client.start(phone=acc['phone'])
            else:
                client = TelegramClient(session_name, acc['api_id'], acc['api_hash'])
                await client.start(phone=acc['phone'])
            self.clients.append({"client": client, "phone": acc['phone']})
            logging.info(f"✅ Logged in: {acc['phone']}")
        return self.clients

    async def close_clients(self):
        for item in self.clients:
            client = item["client"] if isinstance(item, dict) else item
            await client.disconnect()
