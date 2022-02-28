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


@ddocmd(command="pe", can_disable=True)
@typing_action
async def pixel_experience(update: Update, context: CallbackContext):
    message = update.effective_message
    args = context.args

    await asyncio.sleep(2)

    try:
        device = args[1]
    except IndexError:
        device = ""
    try:
        atype = args[2].lower()
    except IndexError:
        atype = "twelve"

    if device == "":
        text = ("Please type your device <b>codename</b>!\nFor example, <code>/pe whyred</code>")
        await message.reply(text)
        return

    asyncio.sleep(delay)

    fetch = await http.get(
        f"https://download.pixelexperience.org/ota_v5/{device}/{atype}"
    )
    if fetch.status_code == 200:
        response = json.loads(fetch.content)
        if response["error"]:
            await message.reply("Couldn't find any results matching your query.")
            return
        filename = response["filename"]
        url = response["url"]
        buildsize_a = response["size"]
        buildsize_b = convert_size(int(buildsize_a))
        version = response["version"]
        build_time = response["datetime"]

        reply_text = ("<b>Download:</b> <a href='{}'>{}</a>\n").format(url=url, filename=filename)
        reply_text += ("<b>Build Size:</b> <code>{}</code>\n").format(size=buildsize_b)
        reply_text += ("<b>Version:</b> <code>{}</code>\n").format(version=version)
        reply_text += ("<b>Date:</b> <code>{}</code>\n").format(date=format_datetime(build_time))

        asyncio.sleep(delay)

        keyboard = [
            [InlineKeyboardButton(text="Click Here To Downloads", url=f"{url}")]
        ]
        message.reply_text(
            reply_text,
            reply_markup=InlineKeyboardMarkup(keyboard),
            parse_mode=ParseMode.MARKDOWN,
            disable_web_page_preview=True,
        )
        return
    message.reply_text(
        "`Couldn't find any results matching your query.`",
        parse_mode=ParseMode.MARKDOWN,
        disable_web_page_preview=True,
    )


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
async def crdroid(message, update: Update, context: CallbackContext):
    message = update.effective_message
    args = context.args

    try:
        device = args[1]
    except IndexError:
        device = ""

    if device == "x00t":
        device = "X00T"

    if device == "x01bd":
        device = "X01BD"

    if device == "":
        text = ("Please type your device <b>codename</b>!\nFor example, <code>/pe whyred</code>")
        await message.reply(text)
        return

    fetch = await http.get(
        f"https://raw.githubusercontent.com/crdroidandroid/android_vendor_crDroidOTA/11.0/{device}.json"
    )

    if fetch.status_code in [500, 504, 505]:
        await message.reply("Hachi have been trying to connect to GitHub User Content, It seem like GitHub User Content is down")
        return

    if fetch.status_code == 200:
        try:
            usr = json.loads(fetch.content)
            response = usr["response"]
            filename = response[0]["filename"]
            url = response[0]["<b>Download:</b> <a href='{url}'>{filename}</a>\n"]
            version = response[0]["version"]
            maintainer = response[0]["maintainer"]
            size_a = response[0]["size"]
            size_b = convert_size(int(size_a))
            build_time = response[0]["timestamp"]
            romtype = response[0]["buildtype"]

            reply_text = ("<b>Download:</b> <a href='{}'>{}</a>\n").format(url=url, filename=filename)
            reply_text += ("<b>Type:</b> {}\n").format(type=romtype)
            reply_text += ("<b>Build Size:</b> <code>{}</code>\n").format(size=size_b)
            reply_text += ("<b>Version:</b> <code>{}</code>\n").format(version=version)
            reply_text += ("<b>Date:</b> <code>{}</code>\n").format(date=format_datetime(build_time))
            reply_text += ("maintainer").format(name=maintainer)

            keyboard = [
            [InlineKeyboardButton(text="Click Here To Downloads", url=f"{url}")]
        ]
            await message.reply_text(
            reply_text,
            reply_markup=InlineKeyboardMarkup(keyboard),
            parse_mode=ParseMode.MARKDOWN,
            disable_web_page_preview=True,
        )
            return

        except ValueError:
            text = ("Tell the rom maintainer to fix their OTA json. I'm sure this won't work with OTA and it won't work with this bot too :P")
            await message.reply(text)
            return

    elif fetch.status_code == 404:
        text = ("Couldn't find any results matching your query.")
        await message.reply(text)
        return
        