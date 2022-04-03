# ⚠️ © @greyyvbss 

# ⚠️ Don't Remove Credits for /asupan

import requests
import os
import urllib
import random

import aiohttp
import requests
from telegram import ParseMode, InlineKeyboardButton, InlineKeyboardMarkup
from telethon.tl.types import InputMessagesFilterVideo
from telegram.utils.helpers import mention_html
from pyrogram import filters
from HachiBot.events import register
from HachiBot import telethn as tbot, ubot2
from HachiBot import TEMP_DOWNLOAD_DIRECTORY, pbot
            

@register(pattern="^/asupan ?(.*)")

async def _(event):

    memeks = await event.reply("**Mencari Video Asupan...🔍**") 

    try:

        asupannya = [

            asupan

            async for asupan in ubot2.iter_messages(

            "@Database_TonicUbot", filter=InputMessagesFilterVideo

            )

        ]

        kontols = random.choice(asupannya)

        pantek = await ubot2.download_media(kontols)

        await tbot.send_file(

            event.chat.id, 

            file=pantek,

            caption=f"Asupan Founded\nRequested by: {event.sender.first_name}",
        )

        await tbot.reply_file(eply_markup=InlineKeyboardMarkup(
            [
            [
                InlineKeyboardButton(text="Support Chat", url="https://t.me/demonszxx"),
            ]
            ]
            )
        )

        await memeks.delete()

    except Exception:

        await memeks.edit("Asupannya gaada komsol")


@register(pattern="^/bokep ?(.*)")

async def _(event):

    memeks = await event.reply("**Mencari Video Asupan...🔍**") 

    try:

        asupannya = [

            asupan

            async for asupan in ubot2.iter_messages(

            "@TonicPorn", filter=InputMessagesFilterVideo

            )

        ]

        kontols = random.choice(asupannya)

        pantek = await ubot2.download_media(kontols)

        await tbot.send_file(

            event.chat.id, 

            file=pantek,

            caption=f"Bokepp Founded\nRequested by: {event.sender.first_name}",
            reply_markup=InlineKeyboardMarkup(
            [
            [
                InlineKeyboardButton(text="Support Chat", url="https://t.me/demonszxx"),
            ]
            ]
            )
            )

        await memeks.delete()

    except Exception:

        await memeks.edit("Bokep nya abiss sygg")


@register(pattern="^/chika ?(.*)")
async def chika(event):
    try:
        resp = requests.get("https://api-tede.herokuapp.com/api/chika").json()
        chikanya = f"{resp['url']}"
        return await tbot.send_file(event.chat_id, chikanya)
    except Exception:
        await event.reply("`Error 404 not found...`")


@register(pattern="^/hilih ?(.*)")
async def _(hilih):
    kuntul = hilih.pattern_match.group(1)
    if not kuntul:
        await hilih.reply("Usage: /hilih <text>")
        return
    try:
        resp = requests.get(f"https://tede-api.herokuapp.com/api/hilih?kata={kuntul}").json()
        hilihnya = f"{resp['result']}"
        return await hilih.reply(hilihnya)
    except Exception:
        await hilih.reply("Something went wrong LOL...")

@pbot.on_message(filters.command("bugil"))
async def boobs(client, message):
    if not os.path.isdir(TEMP_DOWNLOAD_DIRECTORY):
        os.makedirs(TEMP_DOWNLOAD_DIRECTORY)
    pic_loc = os.path.join(TEMP_DOWNLOAD_DIRECTORY, "bobs.jpg")
    a = await message.reply_text("**Mencari Gambar Ipeh Lagi Bugil**")
    await a.edit("`Mengirim...`")
    nsfw = requests.get("http://api.oboobs.ru/noise/1").json()[0]["preview"]
    urllib.request.urlretrieve("http://media.oboobs.ru/{}".format(nsfw), pic_loc)
    await client.send_photo(
        message.chat.id, pic_loc, caption="**Sange boleh, Goblok jangan**"
    )
    os.remove(pic_loc)
    await a.delete()


@pbot.on_message(filters.command("meme"))
async def memes(client, message):
    async with aiohttp.ClientSession() as ses:
        async with ses.get(
            "https://meme-api.herokuapp.com/gimme/wholesomememes"
        ) as resp:
            r = await resp.json()
            await message.reply_photo(r["url"], caption=r["title"])