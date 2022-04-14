import time
import uvloop
import asyncio
import importlib

from pytgcalls import idle
from pyrogram import Client

from .N4Utilities.tgcallsrun import run
from N4 import BOT_NAME, ASSNAME, app, chacha, aiohttpsession
from N4.N4Utilities.database.functions import clean_restart_stage
from N4.N4Utilities.database.queue import (get_active_chats, remove_active_chat)
from .config import API_ID, API_HASH, BOT_TOKEN, MONGO_DB_URI, SUDO_USERS, LOG_GROUP_ID


Client(
    ':n4:',
    API_ID,
    API_HASH,
    bot_token=BOT_TOKEN,
    plugins={'root': 'N4.Plugins'},
).start()


print(f"[ INFO ] BOT STARTED AS {BOT_NAME} !")
print(f"[ INFO ] USERBOT STARTED AS {ASSNAME} !")


async def load_start():
    restart_data = await clean_restart_stage()
    if restart_data:
        print("[ INFO ] SENDING RESTART STATUS")
        try:
            await app.edit_message_text(
                restart_data["chat_id"],
                restart_data["message_id"],
                "✅ Bot restarted successfully",
            )
        except Exception:
            pass
    served_chats = []
    try:
        chats = await get_active_chats()
        for chat in chats:
            served_chats.append(int(chat["chat_id"]))
    except Exception:
        print("error came while clearing db")
        pass
    for served_chat in served_chats:
        try:
            await remove_active_chat(served_chat)                                         
        except Exception:
            print("error came while clearing db")
            pass     
    await app.send_message(LOG_GROUP_ID, "✅ bot client started")
    await chacha.send_message(LOG_GROUP_ID, "✅ userbot client started")
    print("[ INFO ] BOT & USERBOT CLIENT STARTED")
    
   
loop = asyncio.get_event_loop_policy().get_event_loop()
loop.run_until_complete(load_start())
run()
idle()

loop.close()
print("[ INFO ] BOT & USERBOT STOPPED")
