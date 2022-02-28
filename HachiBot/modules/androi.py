# Copyright (C) 2022 HitaloSama.
# Copyright (C) 2019 Aiogram.
#
# This file is part of Hachi (Telegram Bot)
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as
# published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version.

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.

# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

import asyncio
import time

import rapidjson as json
from pyrogram import Client, filters
from telegram.ext import CallbackContext
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, ParseMode, Bot, Update
from pyrogram import filters
from babel.dates import format_datetime
from bs4 import BeautifulSoup
from hurry.filesize import size as sizee
from requests import get

from HachiBot import pbot

from .math import convert_size
from HachiBot.utils.http import http
from HachiBot.modules.helper_funcs.alternate import typing_action
from HachiBot.modules.helper_funcs.decorators import ddocmd


@pbot.on_message(filters.command("pe"))
async def pixel_experience(c: Client, update: Update):

    chat_id = update.chat.id,
    try:
        device = update.command[1]
    except Exception:
        device = ''

    try:
        atype = update.command[1]
    except Exception:
        atype = "twelve"

    if device == '':
        reply_text = ("Please type your device **codename**!\nFor example, `/pe tissot`")
        await update.reply_text(reply_text, disable_web_page_preview=True)
        return

    fetch = get(
        f"https://download.pixelexperience.org/ota_v5/{device}/{atype}"
    )
    if fetch.status_code == 200:
        response = json.loads(fetch.content)
        if response["error"]:
            update.reply_text("Couldn't find any results matching your query.")
            return
        filename = response["filename"]
        url = response["url"]
        buildsize_a = response["size"]
        buildsize_b = convert_size(int(buildsize_a))
        version = response["version"]
        build_time = response["datetime"]

        reply_text = ("<b>Download:</b> <a href='{}'>{}</a>\n").format(url, filename)
        reply_text += ("<b>Build Size:</b> <code>{}</code>\n").format(buildsize_b)
        reply_text += ("<b>Version:</b> <code>{}</code>\n").format(version)
        reply_text += ("<b>Date:</b> <code>{date}</code>\n").format(date=format_datetime(build_time))


        keyboard = [[
            InlineKeyboardButton(text=("Click here to Download"), url=f"{url}")
        ]]
        await update.reply_text(reply_text,
                                reply_markup=InlineKeyboardMarkup(keyboard),
                                parse_mode="markdown",
                                disable_web_page_preview=True)
        return

    elif fetch.status_code == 404:
        reply_text = ("Couldn't find any results matching your query.")
    await update.reply_text(reply_text,
                            parse_mode="markdown",
                            disable_web_page_preview=True)


@pbot.on_message(filters.command(["sxos", "statix"]))
async def statix(c: Client, update: Update):
    
    try:
        device = update.command[1]
    except Exception:
        device = ''

    if device == '':
        reply_text = ("Please type your device **codename**!\nFor example, `/sxos tissot`")
        await update.reply_text(reply_text, disable_web_page_preview=True)
        return

    fetch = get(
        f"https://downloads.statixos.com/json/{device}.json"
        )
    if fetch.status_code == 200 and len(fetch.json()["response"]) != 0:
        usr = json.loads(fetch.content)
        response = usr["response"][0]
        filename = response["filename"]
        url = response["url"]
        buildsize_a = response["size"]
        buildsize_b = sizee(int(buildsize_a))
        version = response["version"]
        build_time = response["datetime"]
        romtype = response["romtype"]

        reply_text = ("<b>Download:</b> <a href='{}'>{}</a>\n").format(url, filename)
        reply_text += ("<b>Type:</b> {}\n").format(type=romtype)
        reply_text += ("<b>Build Size:</b> <code>{}</code>\n").format(buildsize_b)
        reply_text += ("<b>Version:</b> <code>{}</code>\n").format(version)
        reply_text += ("<b>Date:</b> <code>{date}</code>\n").format(date=format_datetime(build_time))

        keyboard = [
            [InlineKeyboardButton(text="Click Here To Downloads", url=f"{url}")]
        ]
        await update.reply_text(reply_text,
                                reply_markup=InlineKeyboardMarkup(keyboard),
                                parse_mode="markdown",
                                disable_web_page_preview=True)
        return

    elif fetch.status_code == 404:
        reply_text = ("Couldn't find any results matching your query.")
    await update.reply_text(reply_text,
                            parse_mode="markdown",
                            disable_web_page_preview=True)


@pbot.on_message(filters.command(["crdroid", "crd"]))
async def crdroid(c: Client, update: Update):

    chat_id = update.chat.id,
    try:
        device = update.command[1]
    except Exception:
        device = ''

    if device == "x00t":
        device = "X00T"

    if device == "x01bd":
        device = "X01BD"

    if device == '':
        reply_text = ("Please type your device **codename**!\nFor example, `/crd tissot`")
        await update.reply_text(reply_text, disable_web_page_preview=True)
        return

    fetch = await http.get(
        f"https://raw.githubusercontent.com/crdroidandroid/android_vendor_crDroidOTA/11.0/{device}.json"
    )

    if fetch.status_code in [500, 504, 505]:
        await update.reply_text(
            "HachiBot have been trying to connect to Github User Content, It seem like Github User Content is down"
        )
        return

    if fetch.status_code == 200:
        try:
            usr = json.loads(fetch.content)
            response = usr["response"]
            filename = response["filename"]
            url = response["download"]
            version = response["version"]
            maintainer = response['maintainer']
            maintainer_url = response['telegram_username']
            size_a = response["size"]
            size_b = sizee(int(size_a))
            build_time = response["timestamp"]
            romtype = response["buildtype"]

            reply_text = ("<b>Download:</b> <a href='{}'>{}</a>\n").format(url=url, filename=filename)
            reply_text += ("<b>Type:</b> {}\n").format(type=romtype)
            reply_text += ("<b>Build Size:</b> <code>{}</code>\n").format(size=size_b)
            reply_text += ("<b>Version:</b> <code>{}</code>\n").format(version=version)
            reply_text += ("<b>Date:</b> <code>{}</code>\n").format(date=format_datetime(build_time))
            reply_text += ("**Maintainer:** {}\n").format(
                f"[{maintainer}](https://t.me/{maintainer_url})")

            btn = ("Click here to Download")
            keyboard = [[InlineKeyboardButton(
                text=btn, url=url)]]
            await update.reply_text(reply_text, reply_markup=InlineKeyboardMarkup(keyboard), disable_web_page_preview=True)
            return

        except ValueError:
            reply_text = ("Tell the rom maintainer to fix their OTA json. I'm sure this won't work with OTA and it won't work with this bot too :P")
            await update.reply_text(reply_text, disable_web_page_preview=True)
            return

    elif fetch.status_code == 404:
        reply_text = ("Couldn't find any results matching your query.")
        await update.reply_text(reply_text, disable_web_page_preview=True)
        return
        