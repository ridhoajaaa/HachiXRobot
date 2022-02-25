# Copyright (c) 2021 Man-Userbot
# Created by mrismanaziz
# FROM <https://github.com/mrismanaziz/Man-Userbot>
# t.me/SharingUserbot & t.me/Lunatic0de
#
# Thanks To Ultroid <https://github.com/TeamUltroid/Ultroid>
# Thanks To Geez-UserBot <https://github.com/vckyou/Geez-UserBot>

import os

from telethon import events
from telethon.errors.rpcerrorlist import ChatAdminRequiredError, YouBlockedUserError
from telethon.tl.functions.contacts import UnblockRequest
from telethon.tl.functions.messages import ExportChatInviteRequest
from telethon.tl.types import ChannelParticipantsKicked

from HachiBot import OWNER_ID as owner
from HachiBot.utils.tools import edit_or_reply
from HachiBot.events import register


@register(pattern="/open(?: |$)(.*)")
async def _(event):
    b = await event.client.download_media(await event.get_reply_message())
    with open(b, "r") as a:
        c = a.read()
    await edit_or_reply(event, "**Berhasil Membaca Berkas**")
    if len(c) > 4095:
        await edit_or_reply(
            event, c, deflink=True, linktext="**Berhasil Membaca Berkas**"
        )
    else:
        await event.client.send_message(event.chat_id, f"`{c}`")
        await event.delete()
    os.remove(b)


@register(pattern="/sendbot (.*)")
async def _(event):
    if event.fwd_from:
        return
    chat = str(event.pattern_match.group(1).split(" ", 1)[0])
    link = str(event.pattern_match.group(1).split(" ", 1)[1])
    if not link:
        return await edit_or_reply(event, "**Maaf BOT Tidak Merespond.**")

    botid = await event.client.get_entity(chat)
    await edit_or_reply(event, "`Processing...`")
    async with event.client.conversation(chat) as conv:
        try:
            response = conv.wait_event(
                events.NewMessage(incoming=True, from_users=botid)
            )
            msg = await event.client.send_message(chat, link)
            response = await response
            await event.client.send_read_acknowledge(conv.chat_id)
        except YouBlockedUserError:
            await event.client(UnblockRequest(chat))
            msg = await event.client.send_message(chat, link)
            response = await response
            await event.client.send_read_acknowledge(conv.chat_id)
        except BaseException:
            await message.reply_text(event, "**Tidak dapat menemukan bot itu 🥺**")
        await edit_or_reply(event, f"**Pesan Terkirim:** `{link}`\n**Kepada: {chat}**")
        await event.client.send_message(event.chat_id, response.message)
        await event.client.send_read_acknowledge(event.chat_id)
        await event.client.delete_messages(conv.chat_id, [msg.id, response.id])


@register(pattern="/unbanall$")
async def _(event):
    await edit_or_reply(event, "`Searching Participant Lists...`")
    p = 0
    title = (await event.get_chat()).title
    async for i in event.client.iter_participants(
        event.chat_id,
        filter=ChannelParticipantsKicked,
        aggressive=True,
    ):
        try:
            await event.client.edit_permissions(event.chat_id, i, view_messages=True)
            p += 1
        except BaseException:
            pass
    await edit_or_reply(event, f"**Berhasil unbanned** `{p}` **Orang di Grup {title}**")


@register(pattern="(?:dm)\s?(.*)?")
async def _(event):
    p = event.pattern_match.group(1)
    m = p.split(" ")
    chat_id = m[0]
    try:
        chat_id = int(chat_id)
    except BaseException:
        pass
    mssg = await event.get_reply_message()
    if event.reply_to_msg_id:
        await event.client.send_message(chat_id, mssg)
        await edit_or_reply(event, "**Berhasil Mengirim Pesan Anda.**")
    msg = "".join(i + " " for i in m[1:])
    if msg == "":
        return
    try:
        await event.client.send_message(chat_id, msg)
        await edit_or_reply(event, "**Berhasil Mengirim Pesan Anda.**")
    except BaseException:
        await message.reply_text(event, "**ERROR: Gagal Mengirim Pesan.**", 10)


@register(pattern="/fwdreply ?(.*)")
async def _(e):
    message = e.pattern_match.group(1)
    if not e.reply_to_msg_id:
        return await edit_or_reply(e, "`Mohon Reply ke pesan seseorang.`")
    if not message:
        return await edit_or_reply(e, "`Tidak ditemukan pesan untuk disampaikan`")
    msg = await e.get_reply_message()
    fwd = await msg.forward_to(msg.sender_id)
    await fwd.reply(message)
    await message.reply_text(e, "**Silahkan Check di Private**", 10)


@register(pattern="/getlink(?: |$)(.*)")
async def _(event):
    await edit_or_reply(event, "`Processing...`")
    try:
        e = await event.client(
            ExportChatInviteRequest(event.chat_id),
        )
    except ChatAdminRequiredError:
        return await event.client.send_message(f"**Maaf {owner} Bukan Admin 👮**")
    await edit_or_reply(event, f"**Link Invite GC**: {e.link}")


@register(pattern="/tmsg (.*)")
async def _(event):
    k = await event.get_reply_message()
    if k:
        a = await event.client.get_messages(event.chat_id, 0, from_user=k.sender_id)
        return await event.edit(
            f"**Total ada** `{a.total}` **Chat Yang dikirim Oleh** {u} **di Grup Chat ini**"
        )
    u = event.pattern_match.group(1)
    if not u:
        u = "me"
    a = await event.client.get_messages(event.chat_id, 0, from_user=u)
    await edit_or_reply(
        event, f"**Total ada `{a.total}` Chat Yang dikirim Oleh saya di Grup Chat ini**"
    )


@register(pattern="/view")
async def _(event):
    reply_message = await event.get_reply_message()
    if not reply_message:
        await edit_or_reply(event, "**Mohon Reply ke Link**")
        return
    if not reply_message.text:
        await edit_or_reply(event, "**Mohon Reply ke Link**")
        return
    chat = "@chotamreaderbot"
    xx = await edit_or_reply(event, "`Processing...`")
    async with event.client.conversation(chat) as conv:
        try:
            response = conv.wait_event(
                events.NewMessage(incoming=True, from_users=272572121)
            )
            await event.client.forward_messages(chat, reply_message)
            response = await response
            await event.client.send_read_acknowledge(conv.chat_id)
        except YouBlockedUserError:
            await event.client(UnblockRequest(chat))
            await event.client.forward_messages(chat, reply_message)
            response = await response
            await event.client.send_read_acknowledge(conv.chat_id)
        if response.text.startswith(""):
            await xx.edit("Am I Dumb Or Am I Dumb?")
        else:
            await xx.delete()
            await event.client.send_message(event.chat_id, response.message)