# Copyright (C) 2020 Frizzy.
# All rights reserved.
#
# Licensed under the Raphielscape Public License, Version 1.d (the "License");
# you may not use this file except in compliance with the License.
# Lord UserBot

from telethon.errors.rpcerrorlist import YouBlockedUserError
from telethon.tl.functions.contacts import UnblockRequest
from telethon import TelegramClient
from telethon import events

from HachiBot.utils.tools import edit_delete, edit_or_reply
from HachiBot.events import register
from HachiBot import ubot
from HachiBot.services.telethon import tbot

# Alvin Gans


@register(pattern="/tiktok(?: |$)(.*)")
async def _(event):
    if event.fwd_from:
        return
    d_link = event.pattern_match.group(1)
    if ".com" not in d_link:
        await event.edit(
            "`Mohon Maaf, Saya Membutuhkan Link Video Tiktok Untuk Mendownload Nya`"
        )
    else:
        await event.edit("```Video Sedang Diproses.....```")
    chat = "@ttsavebot"
    async with tbot.conversation(chat) as conv:
        try:
            msg_start = await conv.send_message("/start")
            r = await conv.get_response()
            msg = await conv.send_message(d_link)
            details = await conv.get_response()
            video = await conv.get_response()
            """ - don't spam notif - """
            await tbot.send_read_acknowledge(conv.chat_id)
        except YouBlockedUserError:
            await event.edit(
                "**Kesalahan:** `Mohon Buka Blokir` @ttsavebot `Dan Coba Lagi !`"
            )
            return
        await tbot.send_file(event.chat_id, video)
        await event.client.delete_messages(
            conv.chat_id, [msg_start.id, r.id, msg.id, details.id, video.id]
        )
        await event.delete()
