import os
from getpass import getpass
from telethon.sync import TelegramClient
from telethon.sessions import StringSession


def prompt(label: str, default: str = "") -> str:
    value = input(f"{label}{' [' + default + ']' if default else ''}: ").strip()
    return value or default


def main():
    api_id = int(prompt("API_ID", os.getenv("API_ID", "")))
    api_hash = prompt("API_HASH", os.getenv("API_HASH", ""))
    phone = prompt("PHONE (e.g. +15551234567)")

    with TelegramClient(StringSession(), api_id, api_hash) as client:
        client.start(phone=phone, password=getpass("2FA Password (if any, else leave blank): "))
        session = client.session.save()
        print("\nCopy this string session into your .env as ACCOUNT_N_SESSION=...\n")
        print(session)


if __name__ == "__main__":
    main()

