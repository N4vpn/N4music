import os
import wget
import speedtest

from PIL import Image
from N4 import app, SUDOERS
from N4.N4Utilities.database.onoff import is_on_off
from pyrogram import filters, Client
from pyrogram.types import Message
from strings import get_command

# Commands
SPEEDTEST_COMMAND = get_command("SPEEDTEST_COMMAND")

def testspeed(m):
    try:
        test = speedtest.Speedtest()
        test.get_best_server()
        m = m.edit("Running Download SpeedTest")
        test.download()
        m = m.edit("Running Upload SpeedTest")
        test.upload()
        test.results.share()
        result = test.results.dict()
        m = m.edit("Sharing SpeedTest Results")
    except Exception as e:
        return m.edit(e)
    return result
@Client.on_message(command(["speedtest", f"speedtest@{bname}"]) & ~filters.edited)
@sudo_users_only
async def run_speedtest(_, message: Message):
    m = await message.reply_text("⚡️ running server speedtest")
    try:
        test = speedtest.Speedtest()
        test.get_best_server()
        m = await m.edit("⚡️ running download speedtest..")
        test.download()
        m = await m.edit("⚡️ running upload speedtest...")
        test.upload()
        test.results.share()
        result = test.results.dict()
    except Exception as e:
        await m.edit(e)
        return
    m = await m.edit("🔄 sharing speedtest results")
    path = wget.download(result["share"])

    output = f"""💡 SpeedTest Results
    
<u>Client:</u>
ISP: {result['client']['isp']}
Country: {result['client']['country']}
  
<u>Server:</u>
Name: {result['server']['name']}
Country: {result['server']['country']}, {result['server']['cc']}
Sponsor: {result['server']['sponsor']}
Latency: {result['server']['latency']}

⚡️ Ping: {result['ping']}"""
    msg = await app.send_photo(
        chat_id=message.chat.id, photo=path, caption=output
    )
    os.remove(path)
    await m.delete()


