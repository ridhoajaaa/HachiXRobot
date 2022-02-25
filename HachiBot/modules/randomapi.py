import requests
import os
import urllib

import aiohttp
import requests
from pyrogram import filters
from HachiBot.events import register
from HachiBot import telethn as tbot
from HachiBot import TEMP_DOWNLOAD_DIRECTORY, pbot


@register(pattern="^/ptl ?(.*)")
async def asupan(event):
    try:
        resp = requests.get("https://api-tede.herokuapp.com/api/asupan/ptl").json()
        asupannya = f"{resp['url']}"
        return await tbot.send_file(event.chat_id, asupannya)
    except Exception:
        await event.reply("`Error 404 not found...`")


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