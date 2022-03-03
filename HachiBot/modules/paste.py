import codecs
import os
import requests

from telegram.ext import CallbackContext
from telegram import (
    InlineKeyboardMarkup,
    InlineKeyboardButton,
    ParseMode,
    Update,
)

from HachiBot import aiohttpsession as session
from HachiBot import pbot as app
from HachiBot.utils.errors import capture_err
from HachiBot.utils.pastebin import paste

def paste(update: Update, context: CallbackContext):
    msg = update.effective_message

    if msg.reply_to_message and msg.reply_to_message.document:
        file = context.bot.get_file(msg.reply_to_message.document)
        file.download("file.txt")
        text = codecs.open("file.txt", "r+", encoding="utf-8")
        paste_text = text.read()
        url = "https://www.toptal.com/developers/hastebin/documents"
        key = requests.post(url, data=paste_text.encode("UTF-8")).json().get("key")
        text = "**Pasted to Hastebin!!!**"
        buttons = [
            [
                InlineKeyboardButton(
                    text="View Link",
                    url=f"https://www.toptal.com/developers/hastebin/{key}",
                ),
                InlineKeyboardButton(
                    text="View Raw",
                    url=f"https://www.toptal.com/developers/hastebin/raw/{key}",
                ),
            ]
        ]
        msg.reply_text(
            text,
            reply_markup=InlineKeyboardMarkup(buttons),
            parse_mode=ParseMode.MARKDOWN,
            disable_web_page_preview=True,
        )
        os.remove("file.txt")
    else:
        msg.reply_text("Give me a text file to paste on hastebin")
        return
