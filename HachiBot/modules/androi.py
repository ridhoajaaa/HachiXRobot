# Copyright (C) 2022 HitaloSama.
# Copyright (C) 2019 Aiogram.
#
# This file is part of Hitsuki (Telegram Bot)
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
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from pyrogram import filters
from babel.dates import format_datetime
from bs4 import BeautifulSoup
from httpx import TimeoutException

from HachiBot import pbot

from .math import convert_size
from HachiBot.utils.http import http
from HachiBot.utils.message import get_arg, get_cmd


@pbot.on_message(filters.command(["pixel", "pe"]))
async def pixel_experience(message, strings):

    try:
        args = message.text.split()
        device = args[1]
    except IndexError:
        device = ""

    try:
        atype = args[2].lower()
    except IndexError:
        atype = "twelve"

    if device == "":
        text = strings["Please type your device <b>codename</b>!\nFor example, <code>/pe whyred</code>"]
        await message.reply(text)
        return

    fetch = await http.get(
        f"https://download.pixelexperience.org/ota_v5/{device}/{atype}"
    )
    if fetch.status_code == 200:
        response = json.loads(fetch.content)
        if response["error"]:
            await message.reply(strings["err_query"])
            return
        filename = response["filename"]
        url = response["url"]
        buildsize_a = response["size"]
        buildsize_b = convert_size(int(buildsize_a))
        version = response["version"]
        build_time = response["datetime"]

        text = (strings["download"]).format(url=url, filename=filename)
        text += (strings["build_size"]).format(size=buildsize_b)
        text += (strings["version"]).format(version=version)
        text += (strings["release_time"]).format(date=format_datetime(build_time))

        btn = strings["dl_btn"]
        keyboard = InlineKeyboardMarkup().add(InlineKeyboardButton(text=btn, url=url))
        await message.reply(text, reply_markup=keyboard)
        return
    text = strings["err_query"]
    await message.reply(text)


@pbot.on_message(filters.command(["statix", "sxos"]))
async def statix(message, strings):

    try:
        device = get_arg(message)
    except IndexError:
        device = ""

    if device == "":
        text = strings["cmd_example"].format(cmd=get_cmd(message))
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

        text = (strings["download"]).format(url=url, filename=filename)
        text += (strings["build_type"]).format(type=romtype)
        text += (strings["build_size"]).format(size=buildsize_b)
        text += (strings["version"]).format(version=version)
        text += (strings["release_time"]).format(date=format_datetime(build_time))

        btn = strings["dl_btn"]
        keyboard = InlineKeyboardMarkup().add(InlineKeyboardButton(text=btn, url=url))
        await message.reply(text, reply_markup=keyboard, disable_web_page_preview=True)
        return
    text = strings["err_query"]
    await message.reply(text)


@pbot.on_message(filters.command(["crdroid", "crd"]))
async def crdroid(message, strings):

    try:
        device = get_arg(message)
    except IndexError:
        device = ""

    if device == "x00t":
        device = "X00T"

    if device == "x01bd":
        device = "X01BD"

    if device == "":
        text = strings["cmd_example"].format(cmd=get_cmd(message))
        await message.reply(text)
        return

    fetch = await http.get(
        f"https://raw.githubusercontent.com/crdroidandroid/android_vendor_crDroidOTA/11.0/{device}.json"
    )

    if fetch.status_code in [500, 504, 505]:
        await message.reply(strings["err_github"])
        return

    if fetch.status_code == 200:
        try:
            usr = json.loads(fetch.content)
            response = usr["response"]
            filename = response[0]["filename"]
            url = response[0]["download"]
            version = response[0]["version"]
            maintainer = response[0]["maintainer"]
            size_a = response[0]["size"]
            size_b = convert_size(int(size_a))
            build_time = response[0]["timestamp"]
            romtype = response[0]["buildtype"]

            text = (strings["download"]).format(url=url, filename=filename)
            text += (strings["build_type"]).format(type=romtype)
            text += (strings["build_size"]).format(size=size_b)
            text += (strings["version"]).format(version=version)
            text += (strings["release_time"]).format(date=format_datetime(build_time))
            text += (strings["maintainer"]).format(name=maintainer)

            btn = strings["dl_btn"]
            keyboard = InlineKeyboardMarkup().add(
                InlineKeyboardButton(text=btn, url=url)
            )
            await message.reply(
                text, reply_markup=keyboard, disable_web_page_preview=True
            )
            return

        except ValueError:
            text = strings["err_ota"]
            await message.reply(text)
            return

    elif fetch.status_code == 404:
        text = strings["err_query"]
        await message.reply(text)
        return
        