# inspired from bin.py which was made by @danish_00
# written by @senku_ishigamiii/@Uzumaki_Naruto_XD

"""
✘ Commands Available -

• `{i}limited`
   Check you are limited or not !
"""

from telethon import events
from telethon.errors.rpcerrorlist import YouBlockedUserError
from telethon.tl.functions.contacts import UnblockRequest
from HachiBot.utils.tools import edit_delete, edit_or_reply
from HachiBot.events import register
from HachiBot import pbot


@register(pattern="^/limited ?(.*)")
async def _(event):
    await edit_or_reply(event, "`Processing...`")
    async with pbot.conversation("@SpamBot") as conv:
        try:
            response = conv.wait_event(
                events.NewMessage(incoming=True, from_users=178220800)
            )
            await conv.send_message("/start")
            response = await response
            await pbot.send_read_acknowledge(conv.chat_id)
        except YouBlockedUserError:
            await event.client(UnblockRequest("@SpamBot"))
            await conv.send_message("/start")
            response = await response
            await event.client.send_read_acknowledge(conv.chat_id)
        await edit_or_reply(event, f"~ {response.message.message}")