import asyncio
import json
import datetime
import html
import os
import tempfile
import time
import textwrap
import re
from io import BytesIO, StringIO
from datetime import timedelta
from decimal import Decimal

import aiohttp
import bs4
import pendulum
import requests
from telethon.errors.rpcerrorlist import FilePartsInvalidError
from telethon.tl.types import (
    DocumentAttributeAnimated,
    DocumentAttributeFilename,
    MessageMediaDocument,
)
from telethon.utils import is_image, is_video

from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup, Message

from HachiBot import dispatcher
from HachiBot.events import register as tomori
from HachiBot.modules.disable import DisableAbleCommandHandler

session = aiohttp.ClientSession()
progress_callback_data = {}


def format_bytes(size):
    size = int(size)
    # 2**10 = 1024
    power = 1024
    n = 0
    power_labels = {0: "", 1: "K", 2: "M", 3: "G", 4: "T"}
    while size > power:
        size /= power
        n += 1
    return f"{size:.2f} {power_labels[n]+'B'}"


def return_progress_string(current, total):
    filled_length = int(30 * current // total)
    return "[" + "=" * filled_length + " " * (30 - filled_length) + "]"


def calculate_eta(current, total, start_time):
    if not current:
        return "00:00:00"
    end_time = time.time()
    elapsed_time = end_time - start_time
    seconds = (elapsed_time * (total / current)) - elapsed_time
    thing = "".join(str(timedelta(seconds=seconds)).split(".")[:-1]).split(", ")
    thing[-1] = thing[-1].rjust(8, "0")
    return ", ".join(thing)


@tomori(pattern="^/whatanime(.*)")
async def whatanime(c: Client, m: Message):
    media = m.photo or m.animation or m.video or m.document
    if not media:
        reply = m.reply_to_message
        if not getattr(reply, "empty", True):
            media = reply.photo or reply.animation or reply.video or reply.document
    if not media:
        await m.reply_text("Please reply it to a Photo or Gif or Video to work")
        return
    with tempfile.TemporaryDirectory() as tempdir:
        reply = await m.reply_text("Downloading media...")
        path = await c.download_media(
            media,
            file_name=os.path.join(tempdir, "0"),
            progress=progress_callback,
            progress_args=(reply,),
        )
        new_path = os.path.join(tempdir, "1.png")
        proc = await asyncio.create_subprocess_exec(
            "ffmpeg", "-i", path, "-frames:v", "1", new_path
        )
        await proc.communicate()
        await reply.edit_text("Uploading media to Trace.moe and finding results...")
        with open(new_path, "rb") as file:
            async with session.post(
                "https://api.trace.moe/search?anilistInfo", data={"image": file}
            ) as resp:
                json = await resp.json()
    if isinstance(json, str):
        await reply.edit_text(html.escape(json))
    else:
        try:
            match = json.get("result")
        except StopIteration:
            await reply.edit_text("No match")
        else:
            match = match[0]
            title_native = match["anilist"]["title"]["native"]
            title_english = match["anilist"]["title"]["english"]
            match["anilist"]["title"]["romaji"]
            anilist_id = match["anilist"]["id"]
            episode = match["episode"]
            similarity = match["similarity"]
            synonyms = match["anilist"]["synonyms"]
            is_adult = match["anilist"]["isAdult"]
            from_time = (
                str(datetime.timedelta(seconds=match["from"]))
                .split(".", 1)[0]
                .rjust(8, "0")
            )
            to_time = (
                str(datetime.timedelta(seconds=match["to"]))
                .split(".", 1)[0]
                .rjust(8, "0")
            )
            text = f"<b>Anime Name:</b> {title_english}"
            if title_native:
                text += f" ({title_native}) \n "
            if synonyms:
                synonyms.sort()
                syn = ", ".join(synonyms)
                text += f"\n<b>Related:</b> {syn}"


async def whatanime(e):
    media = e.media
    if not media:
        r = await e.get_reply_message()
        media = getattr(r, "media", None)
    if not media:
        await e.reply("`Media required`")
        return
    ig = is_gif(media) or is_video(media)
    if not is_image(media) and not ig:
        await e.reply("`Media must be an image or gif or video`")
        return
    filename = "file.jpg"
    if not ig and isinstance(media, MessageMediaDocument):
        attribs = media.document.attributes
        for i in attribs:
            if isinstance(i, DocumentAttributeFilename):
                filename = i.file_name
                break
    cut = await e.reply("`Downloading image..`")
    content = await e.client.download_media(media, bytes, thumb=-1 if ig else None)
    await cut.edit("`Searching for result..`")
    file = memory_file(filename, content)
    async with aiohttp.ClientSession() as session:
        url = "https://api.trace.moe/search?anilistInfo"
        async with session.post(url, data={"image": file}) as raw_resp0:
            resp0 = await raw_resp0.json()
        js0 = resp0.get("result")
        if not js0:
            await cut.edit("`No results found.`")
            return
        js0 = js0[0]
        text = f'<b>{html.escape(js0["anilist"]["title"]["romaji"])}'
        if js0["anilist"]["title"]["native"]:
            text += f' ({html.escape(js0["anilist"]["title"]["native"])})'
        text += "</b>\n"
        if js0["episode"]:
            text += f'<b>Episode:</b> {html.escape(str(js0["episode"]))}\n'
        percent = round(js0["similarity"] * 100, 2)
        text += f"<b>Similarity:</b> {percent}%\n"
        at = re.findall(r"t=(.+)&", js0["video"])[0]
        dt = pendulum.from_timestamp(float(at))
        text += f"<b>At:</b> {html.escape(dt.to_time_string())}"
        await cut.edit(text, parse_mode="html")
        dt0 = pendulum.from_timestamp(js0["from"])
        dt1 = pendulum.from_timestamp(js0["to"])
        ctext = (
            f"{html.escape(dt0.to_time_string())} - {html.escape(dt1.to_time_string())}"
        )
        async with session.get(js0["video"]) as raw_resp1:
            file = memory_file("preview.mp4", await raw_resp1.read())
        try:
            await e.reply(ctext, file=file, parse_mode="html")
        except FilePartsInvalidError:
            await e.reply("`Cannot send preview.`")


async def progress_callback(current, total, reply):
    message_identifier = (reply.chat.id, reply.message_id)
    last_edit_time, prevtext, start_time = progress_callback_data.get(
        message_identifier, (0, None, time.time())
    )
    if current == total:
        try:
            progress_callback_data.pop(message_identifier)
        except KeyError:
            pass
    elif (time.time() - last_edit_time) > 1:
        if last_edit_time:
            download_speed = format_bytes(
                (total - current) / (time.time() - start_time)
            )
        else:
            download_speed = "0 B"
        text = f"""Downloading...
<code>{return_progress_string(current, total)}</code>
<b>Total Size:</b> {format_bytes(total)}
<b>Downladed Size:</b> {format_bytes(current)}
<b>Download Speed:</b> {download_speed}/s
<b>ETA:</b> {calculate_eta(current, total, start_time)}"""
        if prevtext != text:
            await reply.edit_text(text)
            prevtext = text
            last_edit_time = time.time()
            progress_callback_data[message_identifier] = (
                last_edit_time,
                prevtext,
                start_time,
            )


def memory_file(name=None, contents=None, *, _bytes=True):
    if isinstance(contents, str) and _bytes:
        contents = contents.encode()
    file = BytesIO() if _bytes else StringIO()
    if name:
        file.name = name
    if contents:
        file.write(contents)
        file.seek(0)
    return file


def is_gif(file):
    # ngl this should be fixed, telethon.utils.is_gif but working
    # lazy to go to github and make an issue kek
    if not is_video(file):
        return False
    return DocumentAttributeAnimated() in getattr(file, "document", file).attributes
