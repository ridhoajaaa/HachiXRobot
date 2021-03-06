from io import BytesIO
import html
from time import sleep
from typing import Optional, List
from pyrogram import filters
from pyrogram.types import Message
from telegram import TelegramError, Chat, Message
from telegram import Update, Bot
from telegram.error import BadRequest
from telegram import ParseMode
from telegram.ext import MessageHandler, Filters, CommandHandler
from telegram.ext.dispatcher import run_async
from telegram.utils.helpers import escape_markdown
from html import escape
from HachiBot.modules.helper_funcs.chat_status import is_user_ban_protected, bot_admin

import HachiBot.modules.sql.users_sql as sql
from HachiBot import app, arq
from HachiBot.utils.filter_groups import autocorrect_group
from HachiBot import dispatcher, OWNER_ID, DEMONS, DRAGONS, LOGGER
from HachiBot.modules.helper_funcs.filters import CustomFilters

USERS_GROUP = 4


@app.on_message(
    filters.command("autocorrect")
    & ~filters.edited
)
async def autocorrect_bot(_, message: Message):
    if not message.reply_to_message:
        return await message.reply_text("Reply to a text message.")
    reply = message.reply_to_message
    text = reply.text or reply.caption
    if not text:
        return await message.reply_text("Reply to a text message.")
    data = await arq.spellcheck(text)
    if not data.ok:
        return await message.reply_text("Something wrong happened.")
    result = data.result
    await message.reply_text(result.corrected if result.corrected else "Empty")


IS_ENABLED = False


def escape_html(word):
    return escape(word)


def quickscope(bot: Bot, update: Update, args: List[int]):
    if args:
        chat_id = str(args[1])
        to_kick = str(args[0])
    else:
        update.effective_message.reply_text("You don't seem to be referring to a chat/user")
    try:
        bot.ban_chat_member(chat_id, to_kick)
        update.effective_message.reply_text("Attempted banning " + to_kick + " from" + chat_id)
    except BadRequest as excp:
        update.effective_message.reply_text(excp.message + " " + to_kick)


def quickunban(bot: Bot, update: Update, args: List[int]):
    if args:
        chat_id = str(args[1])
        to_kick = str(args[0])
    else:
        update.effective_message.reply_text("You don't seem to be referring to a chat/user")
    try:
        bot.unban_chat_member(chat_id, to_kick)
        update.effective_message.reply_text("Attempted unbanning " + to_kick + " from" + chat_id)
    except BadRequest as excp:
        update.effective_message.reply_text(excp.message + " " + to_kick)


def banall(bot: Bot, update: Update, args: List[int]):
    if args:
        chat_id = str(args[0])
        all_mems = sql.get_chat_members(chat_id)
    else:
        chat_id = str(update.effective_chat.id)
        all_mems = sql.get_chat_members(chat_id)
    for mems in all_mems:
        try:
            bot.ban_chat_member(chat_id, mems.user)
            update.effective_message.reply_text("Tried banning " + str(mems.user))
            sleep(0.1)
        except BadRequest as excp:
            update.effective_message.reply_text(excp.message + " " + str(mems.user))
            continue

def slist(bot: Bot, update: Update):
    message = update.effective_message
    text1 = "My Sudo Users are???:"
    text2 = "My Support Users are????:"
    for user_id in DEMONS:
        try:
            user = bot.get_chat(user_id)
            name = "[{}](tg://user?id={})".format(user.first_name + (user.last_name or ""), user.id)
            if user.username:
                name = escape_html("@" + user.username)
            text1 += "\n - `{}`".format(name)
        except BadRequest as excp:
            if excp.message == 'Chat not found':
                text1 += "\n - ({}) - not found".format(user_id)
    for user_id in DRAGONS:
        try:
            user = bot.get_chat(user_id)
            name = "[{}](tg://user?id={})".format(user.first_name + (user.last_name or ""), user.id)
            if user.username:
                name = escape_html("@" + user.username)
            text2 += "\n - `{}`".format(name)
        except BadRequest as excp:
            if excp.message == 'Chat not found':
                text2 += "\n - ({}) - not found".format(user_id)
    message.reply_text(text1 + "\n", parse_mode=ParseMode.MARKDOWN)
    message.reply_text(text2 + "\n", parse_mode=ParseMode.MARKDOWN)

###
###__help__ = """
#**Owner only:**
#- /getlink **chatid**: Get the invite link for a specific chat.
#- /banall: Ban all members from a chat
#- /snipe **chatid** **string**: Make me send a message to a specific chat.
#- /getchats: Get comman chats with a user
#- /leavechat or /leave **chatid** : leave a chat
#**Sudo/owner only:**
#- /quickscope **userid** **chatid**: Ban user from chat.
#- /quickunban **userid** **chatid**: Unban user from chat.
#- /Stats: check bot's stats
#- /chatlist: get chatlist
#- /gbanlist: get gbanned users list
#- Chat bans via /restrict chat_id and /unrestrict chat_id commands
#**Support user:**
#- /Gban : Global ban a user
#- /Ungban : Ungban a user
#Sudo/owner can use these commands too.
#**Users:**
#- /slist Gives a list of sudo and support users
###"""

#__mod_name__ = "SPECIAL COMMANDS"


BANALL_HANDLER = CommandHandler("banall", banall, pass_args=True, run_async=True, filters=Filters.user(OWNER_ID))
QUICKSCOPE_HANDLER = CommandHandler("quickscope", quickscope, pass_args=True, run_async=True, filters=CustomFilters.sudo_filter)
QUICKUNBAN_HANDLER = CommandHandler("quickunban", quickunban, pass_args=True, run_async=True, filters=CustomFilters.sudo_filter)
SLIST_HANDLER = CommandHandler("slist", slist, run_async=True,
                           filters=CustomFilters.sudo_filter | CustomFilters.support_filter)

dispatcher.add_handler(BANALL_HANDLER)
dispatcher.add_handler(QUICKSCOPE_HANDLER)
dispatcher.add_handler(QUICKUNBAN_HANDLER)
dispatcher.add_handler(SLIST_HANDLER)