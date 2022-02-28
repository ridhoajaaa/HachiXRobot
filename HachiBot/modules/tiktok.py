# Copyright (C) 2020 Frizzy.
# All rights reserved.
#
# Licensed under the Raphielscape Public License, Version 1.d (the "License");
# you may not use this file except in compliance with the License.
# Lord UserBot

from telethon.errors.rpcerrorlist import YouBlockedUserError
from telethon.tl.functions.contacts import UnblockRequest
from telethon import TelegramClient

from HachiBot.utils.tools import edit_delete, edit_or_reply
from HachiBot.events import register
from HachiBot import ubot
from HachiBot.services.telethon import tbot

# Alvin Gans


@register(pattern="/tiktok(?: |$)(.*)")
async def _(event):
    xxnx = event.pattern_match.group(1)
    if xxnx:
        d_link = xxnx
    elif event.is_reply:
        d_link = await event.get_reply_message()
    else:
        return await edit_delete(
            event,
            "**Berikan Link Tiktok Pesan atau Reply Link Tiktok Untuk di Download**",
        )
    xx = await edit_or_reply(event, "`Video Sedang Diproses...`")
    chat = "@thisvidbot"
    async with tbot.client.conversation(chat) as conv:
        try:
            msg_start = await conv.send_message("/start")
            r = await conv.get_response()
            msg = await conv.send_message(d_link)
            details = await conv.get_response()
            video = await conv.get_response()
            text = await conv.get_response()
            await ubot.client.send_read_acknowledge(conv.chat_id)
        except YouBlockedUserError:
            await msg.edit("Boss! Please Unblock @thisvidbot ")
            return
        await event.client.send_file(event.chat_id, video)
        await ubot.client.delete_messages(
            conv.chat_id, [msg_start.id, r.id, msg.id, details.id, video.id, text.id]
        )
        await xx.delete()
