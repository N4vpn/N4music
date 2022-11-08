import os
import yt_dlp
import random
import asyncio
import shutil
import time as sedtime

from os import path
from time import time
from typing import Union
from asyncio import QueueEmpty

from pyrogram import Client, filters
from pyrogram.errors import UserAlreadyParticipant, UserNotParticipant
from pyrogram.types import (
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    InputMediaPhoto,
    CallbackQuery,
    Message,
    Audio,
    Voice,
)
from pytgcalls.types.input_stream import InputAudioStream, InputStream
from youtubesearchpython import VideosSearch

from N4.N4Utilities.helpers.ytdl import ytdl_opts
from N4.N4Utilities.helpers.decorators import errors
from N4.N4Utilities.helpers.thumbnails import gen_thumb
from N4.N4Utilities.helpers.chattitle import CHAT_TITLE
from N4.N4Utilities.helpers.filters import command, other_filters
from N4.N4Utilities.helpers.gets import (get_url, themes, random_assistant)
from N4 import dbb, app, BOT_USERNAME, BOT_ID, ASSID, ASSNAME, ASSUSERNAME, ASSMENTION
from N4.N4Utilities.tgcallsrun import (yukki, convert, download, clear, get, is_empty, put, task_done, smexy)
from N4.N4Utilities.helpers.inline import (play_keyboard, search_markup, play_markup, playlist_markup, audio_markup)
from N4.N4Utilities.database.queue import (is_active_chat, add_active_chat, remove_active_chat, music_on, is_music_playing, music_off)

flex = {}

async def member_permissions(chat_id: int, user_id: int):
    perms = []
    member = await app.get_chat_member(chat_id, user_id)
    if member.can_manage_voice_chats:
        perms.append("can_manage_voice_chats")
    return perms
from N4.N4Utilities.helpers.administrator import adminsOnly

def convert_seconds(seconds):
    seconds = seconds % (24 * 3600)
    seconds %= 3600
    minutes = seconds // 60
    seconds %= 60
    return "%02d:%02d" % (minutes, seconds)


@app.on_message(command(["cleandb"]) & other_filters)
async def cleandb_cmd(_, message): # clean database of current chat (used by admin group only)
    chat_id = message.chat.id
    try:
        clear(message.chat.id)
    except QueueEmpty:
        pass                        
    await remove_active_chat(chat_id)
    try:
        await yukki.pytgcalls.leave_group_call(message.chat.id)
    except:
        pass   
    await message.reply_text("🗑 Cleaned database of this chat !")


@app.on_message(command(["pause"]) & other_filters)
async def pause_cmd(_, message): 
    if message.sender_chat:
        return await message.reply_text("you're an __Anonymous__ Admin !\n\n» revert back to user account.") 
    permission = "can_manage_voice_chats"
    m = await adminsOnly(permission, message)
    if m == 1:
        return
    checking = message.from_user.mention
    chat_id = message.chat.id
    if not await is_active_chat(chat_id):
        return await message.reply_text("❌ **no music is currently playing**")
    elif not await is_music_playing(message.chat.id):
        return await message.reply_text("❌ **no music is currently playing**")   
    await music_off(chat_id)
    await yukki.pytgcalls.pause_stream(chat_id)
    await message.reply_text("⏸ **Track paused.**\n\n• **To resume the playback, use the**\n» /resume command.")


@app.on_message(command(["resume"]) & other_filters)
async def resume_cmd(_, message): 
    if message.sender_chat:
        return await message.reply_text("you're an __Anonymous__ Admin !\n\n» revert back to user account.") 
    permission = "can_manage_voice_chats"
    m = await adminsOnly(permission, message)
    if m == 1:
        return
    checking = message.from_user.mention
    chat_id = message.chat.id
    if not await is_active_chat(chat_id):
        return await message.reply_text("❌ **no music is currently playing**")
    elif await is_music_playing(message.chat.id):
        return await message.reply_text("❌ **no music is currently playing**") 
    else:
        await music_on(chat_id)
        await yukki.pytgcalls.resume_stream(message.chat.id)
        await message.reply_text("▶️ **Track resumed.**\n\n• **To pause the playback, use the**\n» /pause command.")


@app.on_message(command(["stop", "end"]) & other_filters)
async def stop_cmd(_, message): 
    if message.sender_chat:
        return await message.reply_text("you're an __Anonymous__ Admin !\n\n» revert back to user account.") 
    permission = "can_manage_voice_chats"
    m = await adminsOnly(permission, message)
    if m == 1:
        return
    checking = message.from_user.mention
    chat_id = message.chat.id
    if await is_active_chat(chat_id):
        try:
            clear(message.chat.id)
        except QueueEmpty:
            pass                        
        await remove_active_chat(chat_id)
        await yukki.pytgcalls.leave_group_call(message.chat.id)
        await message.reply_text("✅ The userbot has disconnected from the video chat.") 
    else:
        return await message.reply_text("❌ **no music is currently playing**")


@app.on_message(command(["skip", "next"]) & other_filters)
async def next_cmd(_, message): 
    if message.sender_chat:
        return await message.reply_text("you're an __Anonymous__ Admin !\n\n» revert back to user account.") 
    permission = "can_manage_voice_chats"
    m = await adminsOnly(permission, message)
    if m == 1:
        return
    checking = message.from_user.mention
    chat_id = message.chat.id
    chat_title = message.chat.title
    if not await is_active_chat(chat_id):
        await message.reply_text("❌ **no music is currently playing**")
    else:
        await message.delete()
        task_done(chat_id)
        if is_empty(chat_id):
            await remove_active_chat(chat_id)
            await message.reply_text("❌ no more music in queue\n\n» userbot leaving video chat")
            await yukki.pytgcalls.leave_group_call(message.chat.id)
            return  
        else:
            afk = get(chat_id)['file']
            f1 = (afk[0])
            f2 = (afk[1])
            f3 = (afk[2])
            finxx = (f"{f1}{f2}{f3}")
            if str(finxx) != "raw":   
                mystic = await message.reply_text("📥 downloading next music from playlist...")
                url = (f"https://www.youtube.com/watch?v={afk}")
                try:
                    with yt_dlp.YoutubeDL(ytdl_opts) as ytdl:
                        x = ytdl.extract_info(url, download=False)
                except Exception as e:
                    return await mystic.edit_text(f"failed to download this track.\n\n**reason**: `{e}`") 
                title = (x["title"])
                videoid = afk
                def my_hook(d):
                    if d['status'] == 'downloading':
                        percentage = d['_percent_str']
                        per = (str(percentage)).replace(".","", 1).replace("%","", 1)
                        per = int(per)
                        eta = d['eta']
                        speed = d['_speed_str']
                        size = d['_total_bytes_str']
                        bytesx = d['total_bytes']
                        if str(bytesx) in flex:
                            pass
                        else:
                            flex[str(bytesx)] = 1
                        if flex[str(bytesx)] == 1:
                            flex[str(bytesx)] += 1
                            sedtime.sleep(1)
                            mystic.edit(f"Downloading {title[:50]}\n\n**FileSize:** {size}\n**Downloaded:** {percentage}\n**Speed:** {speed}\n**ETA:** {eta} sec")
                        if per > 500:    
                            if flex[str(bytesx)] == 2:
                                flex[str(bytesx)] += 1
                                sedtime.sleep(0.5)
                                mystic.edit(f"Downloading {title[:50]}...\n\n**FileSize:** {size}\n**Downloaded:** {percentage}\n**Speed:** {speed}\n**ETA:** {eta} sec")
                                print(f"[{videoid}] Downloaded {percentage} at a speed of {speed} in {chat_title} | ETA: {eta} seconds")
                        if per > 800:    
                            if flex[str(bytesx)] == 3:
                                flex[str(bytesx)] += 1
                                sedtime.sleep(0.5)
                                mystic.edit(f"Downloading {title[:50]}....\n\n**FileSize:** {size}\n**Downloaded:** {percentage}\n**Speed:** {speed}\n**ETA:** {eta} sec")
                                print(f"[{videoid}] Downloaded {percentage} at a speed of {speed} in {chat_title} | ETA: {eta} seconds")
                        if per == 1000:    
                            if flex[str(bytesx)] == 4:
                                flex[str(bytesx)] = 1
                                sedtime.sleep(0.5)
                                mystic.edit(f"Downloading {title[:50]}.....\n\n**FileSize:** {size}\n**Downloaded:** {percentage}\n**Speed:** {speed}\n**ETA:** {eta} sec") 
                                print(f"[{videoid}] Downloaded {percentage} at a speed of {speed} in {chat_title} | ETA: {eta} seconds")
                loop = asyncio.get_event_loop()
                xxx = await loop.run_in_executor(None, download, url, my_hook)
                file = await convert(xxx)
                await yukki.pytgcalls.change_stream(
                    chat_id, 
                    InputStream(
                        InputAudioStream(
                            file,
                        ),
                    ),
                )
                thumbnail = (x["thumbnail"])
                duration = convert_seconds(x["duration"] / 60)
                taut = (x["webpage_url"])
                theme = random.choice(themes)
                ctitle = (await app.get_chat(chat_id)).title
                ctitle = await CHAT_TITLE(ctitle)
                f2 = open(f'search/{afk}id.txt', 'r')        
                userid =(f2.read())
                thumb = await gen_thumb(thumbnail, title, userid, theme, ctitle)
                user_id = userid
                buttons = play_markup(videoid, user_id)
                await mystic.delete()
                semx = await app.get_users(userid)
                await app.send_photo(
                    chat_id,
                    photo=thumb,
                    reply_markup=InlineKeyboardMarkup(buttons),    
                    caption=(f"⏭ **Skipped to the next track**\n\n🗂 **Name:** {title[:80]}\n⏱ **Duration:** `{duration}`\n🧸 **Request by:** {semx.mention}"),
                )   
                os.remove(thumb)
            else:      
                await yukki.pytgcalls.change_stream(
                    chat_id, 
                    InputStream(
                        InputAudioStream(
                            afk,
                        ),
                    ),
                )
                _chat_ = ((str(afk)).replace("_","", 1).replace("/","", 1).replace(".","", 1))
                f2 = open(f'search/{_chat_}title.txt', 'r')        
                title =(f2.read())
                f3 = open(f'search/{_chat_}duration.txt', 'r')        
                duration =(f3.read())
                f4 = open(f'search/{_chat_}username.txt', 'r')        
                username =(f4.read())
                f4 = open(f'search/{_chat_}videoid.txt', 'r')        
                videoid =(f4.read())
                user_id = 1
                videoid = str(videoid)
                if videoid == "smex1":
                    buttons = audio_markup(videoid, user_id)
                else:
                    buttons = play_markup(videoid, user_id)
                await app.send_photo(
                    chat_id,
                    photo=f"downloads/{_chat_}final.png",
                    reply_markup=InlineKeyboardMarkup(buttons),
                    caption=(f"⏭ **Skipped to the next track**\n\n🗂 **Name:** {title[:80]}\n⏱ **Duration:** `{duration}`\n🧸 **Request by:** {username}"),
                )
                return
