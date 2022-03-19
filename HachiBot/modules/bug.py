# Copyright (c) 2022 Shiinobu Project

from datetime import datetime

from pyrogram import filters
from pyrogram.types import (
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    CallbackQuery,
    Message,
)
from telegram import ParseMode

from HachiBot import pbot as Client
from HachiBot import (
    OWNER_ID as owner,
    SUPPORT_CHAT as log,
)
from HachiBot.utils.errors import capture_err


def content(msg: Message) -> [None, str]:
    text_to_return = msg.text

    if msg.text is None:
        return None
    if " " in text_to_return:
        try:
            return msg.text.split(None, 1)[1]
        except IndexError:
            return None
    else:
        return None


@Client.on_message(filters.command("bug"))
@capture_err
async def bug(_, msg: Message):
    if msg.chat.username:
        chat_username = (f"@{msg.chat.username}")
    else:
        chat_username = (f"Private Group")

    bugs = content(msg)
    user_id = msg.from_user.id
    mention = msg.from_user.mention
    datetimes_fmt = "%d-%m-%Y"
    datetimes = datetime.utcnow().strftime(datetimes_fmt)
    
    bug_report = f"""
📣 **New bug reported.**

**Chat:** {chat_username}
**Name:** `{mention}`
**User ID:** `{user_id}`
**Chat ID:** `{msg.chat.id}`

**Content Bug Reports:**
`{bugs}`
"""

    
    if msg.chat.type == "private":
        await msg.reply_text("❎ <b>This command only works in groups.</b>")
        return
    
    elif user_id:
        if bugs:
            await msg.reply_text(
                f"<b>Bug Report:</b> <code>{bugs}</code>\n\n"
                "✅ <b>The bug was successfully reported to the support group!</b>",
                reply_markup=InlineKeyboardMarkup(
                    [
                        [
                            InlineKeyboardButton(
                                "Close", callback_data=f"close_reply")
                        ]
                    ]
                )
            )
            await Client.send_message(
                log,
                f"{bug_report}",
                reply_markup=InlineKeyboardMarkup(
                    [
                        [
                            InlineKeyboardButton(
                                "Go To Message", url=f"{msg.link}")
                        ],
                        [
                            InlineKeyboardButton(
                                "Close", callback_data=f"close_send_photo")
                        ]
                    ]
                )
            )
        else:
            await msg.reply_text(
        f"<u><b>Bug Not Found</b></u>\n"
        f"The command /bug <b><Reason></b> must be used specifying, <b>Example:</b> /bug Music Lag .",
        parse_mode=ParseMode.HTML,
        )
        
    

@Client.on_callback_query(filters.regex("close_reply"))
async def close_reply(msg, CallbackQuery):
    await CallbackQuery.message.delete()

@Client.on_callback_query(filters.regex("close_send_photo"))
async def close_send_photo(Client, CallbackQuery):
    await CallbackQuery.message.delete()


__mod_name__ = "Bug"
