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

import time

import rapidjson as json
from telegram import Update
from telegram.ext import CallbackContext
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from pyrogram import filters
from babel.dates import format_datetime
from bs4 import BeautifulSoup
from httpx import TimeoutException

from HachiBot import pbot

from .math import convert_size
from HachiBot.utils.http import http


@pbot.on_message(filters.command(["pixel", "pe"]))
async def pixel_experience(update: Update, context: CallbackContext):

    try:
        message = update.effective_message
        args = context.args
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

        text = ("<b>Download:</b> <a href='{}'>{}</a>\n").format(url=url, filename=filename)
        text += ("<b>Build Size:</b> <code>{}</code>\n").format(size=buildsize_b)
        text += ("<b>Version:</b> <code>{}</code>\n").format(version=version)
        text += ("<b>Date:</b> <code>{}</code>\n").format(date=format_datetime(build_time))

        btn = ("Click here to download!")
        keyboard = InlineKeyboardMarkup().add(InlineKeyboardButton(text=btn, url=url))
        await message.reply(text, reply_markup=keyboard)
        return
    text = ("Couldn't find any results matching your query.")
    await message.reply(text)


@pbot.on_message(filters.command(["statix", "sxos"]))
async def statix(message, update: Update, context: CallbackContext):

    try:
        message = update.effective_message
        args = context.args
        device = args[1]
    except IndexError:
        device = ""

    if device == "":
        text = ("Please type your device <b>codename</b>!\nFor example, <code>/pe whyred</code>")
        await message.reply(text)
        return

    fetch = await http.get(f"https://downloads.statixos.com/json/{device}.json")
    if fetch.status_code == 200 and len(fetch.json()["response"]) != 0:
        usr = json.loads(fetch.content)
        response = usr["response"]
        filename = response[0]["filename"]
        url = response[0]["url"]
        buildsize_a = response[0]["size"]
        buildsize_b = convert_size(int(buildsize_a))
        version = response[0]["version"]
        build_time = response[0]["datetime"]
        romtype = response[0]["romtype"]

        text = ("<b>Download:</b> <a href='{}'>{}</a>\n").format(url=url, filename=filename)
        text += ("<b>Type:</b> {}\n").format(type=romtype)
        text += ("<b>Build Size:</b> <code>{}</code>\n").format(size=buildsize_b)
        text += ("<b>Version:</b> <code>{}</code>\n").format(version=version)
        text += ("<b>Date:</b> <code>{date}</code>\n").format(date=format_datetime(build_time))

        btn = ("Click here to download!")
        keyboard = InlineKeyboardMarkup().add(InlineKeyboardButton(text=btn, url=url))
        await message.reply(text, reply_markup=keyboard, disable_web_page_preview=True)
        return
    text = ("Couldn't find any results matching your query.")
    await message.reply(text)


@pbot.on_message(filters.command(["crdroid", "crd"]))
async def crdroid(message, update: Update, context: CallbackContext):

    try:
        message = update.effective_message
        args = context.args
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

            text = ("<b>Download:</b> <a href='{}'>{}</a>\n").format(url=url, filename=filename)
            text += ("<b>Type:</b> {}\n").format(type=romtype)
            text += ("<b>Build Size:</b> <code>{}</code>\n").format(size=size_b)
            text += ("<b>Version:</b> <code>{}</code>\n").format(version=version)
            text += ("<b>Date:</b> <code>{}</code>\n").format(date=format_datetime(build_time))
            text += ("maintainer").format(name=maintainer)

            btn = ("Click here to download!")
            keyboard = InlineKeyboardMarkup().add(
                InlineKeyboardButton(text=btn, url=url)
            )
            await message.reply(
                text, reply_markup=keyboard, disable_web_page_preview=True
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
        