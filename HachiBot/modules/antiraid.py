# MODUL FROM https://github.com/aryazakaria01/Natsunagi-Nagisa

import html
from typing import Optional
from datetime import timedelta
from pytimeparse.timeparse import timeparse

from telegram import InlineKeyboardButton, InlineKeyboardMarkup, ParseMode, Update
from telegram.ext import CallbackContext
from telegram.utils.helpers import mention_html

from HachiBot import LOGGER as log
from HachiBot.modules.log_channel import loggable
from HachiBot.modules.helper_funcs.anonymous import user_admin as u_admin, AdminPerms, resolve_user as res_user
from HachiBot.modules.helper_funcs.chat_status import connection_status, user_admin_no_reply
from HachiBot.modules.helper_funcs.decorators import ddocmd, ddocallback
from HachiBot.modules.cron_jobs import j

import HachiBot.modules.sql.welcome_sql as sql


def get_time(time: str) -> int:
    try:
        return timeparse(time)
    except:
        return 0


def get_readable_time(time: int) -> str:
    t = f"{timedelta(seconds=time)}".split(":")
    if time == 86400:
        return "1 day"
    return "{} hour(s)".format(t[0]) if time>=3600 else "{} minutes".format(t[1])


@ddocmd(command="raid", pass_args=True)
@connection_status
@loggable
@u_admin(AdminPerms.CAN_CHANGE_INFO)
def setRaid(update: Update, context: CallbackContext) -> Optional[str]:
    args = context.args
    chat = update.effective_chat
    msg = update.effective_message
    u = update.effective_user
    user = res_user(u, msg.message_id, chat)
    if chat.type == "private":
        context.bot.sendMessage(chat.id, "This command is not available in PMs.")
        return
    stat, time, acttime = sql.getDefenseStatus(chat.id)
    readable_time = get_readable_time(time)
    if len(args) == 0:
        if stat:
            text = 'Raid mode is currently <code>Enabled</code>\nWould you like to <code>Disable</code> raid?'
            keyboard = [[
                InlineKeyboardButton("Disable Raid",callback_data="disable_raid={}={}".format(chat.id, time)), 
                InlineKeyboardButton("Cancel",callback_data="cancel_raid=1"), 
                ]]
        else:
            text = f"Raid mode is currently <code>Disabled</code>\nWould you like to <code>Enable</code> raid for {readable_time}?"
            keyboard = [[
                InlineKeyboardButton("Enable Raid",callback_data="enable_raid={}={}".format(chat.id, time)), 
                InlineKeyboardButton("Cancel",callback_data="cancel_raid=0"), 
                ]] 
        reply_markup = InlineKeyboardMarkup(keyboard)
        msg.reply_text(text, parse_mode=ParseMode.HTML, reply_markup=reply_markup)

    elif args[0] == "off":
        if stat:
            sql.setDefenseStatus(chat.id, False, time, acttime)
            text = "Raid mode has been <code>Disabled</code>, members that join will no longer be kicked."
            msg.reply_text(text, parse_mode=ParseMode.HTML)
            logmsg = (
            f"<b>{html.escape(chat.title)}:</b>\n"
            f"#RAID\n"
            f"Disabled\n"
            f"<b>Admin:</b> {mention_html(user.id, user.first_name)}\n"
        )
            return logmsg

    else:
        args_time = args[0].lower()
        time = get_time(args_time)
        if time:
            readable_time = get_readable_time(time)
            if time >= 300 and time < 86400:
                text = f"Raid mode is currently <code>Disabled</code>\nWould you like to <code>Enable</code> raid for {readable_time}?"
                keyboard = [[
                    InlineKeyboardButton("Enable Raid",callback_data="enable_raid={}={}".format(chat.id, time)), 
                    InlineKeyboardButton("Cancel",callback_data="cancel_raid=0"), 
                    ]]
                reply_markup = InlineKeyboardMarkup(keyboard)
                msg.reply_text(text, parse_mode=ParseMode.HTML, reply_markup=reply_markup)
            else:
                msg.reply_text("You can only set time between 5 minutes and 1 day", parse_mode=ParseMode.HTML)

        else:
            msg.reply_text("Unknown time given, give me something like 5m or 1h", parse_mode=ParseMode.HTML)


@ddocallback(pattern="enable_raid=")
@connection_status
@user_admin_no_reply
@loggable
def enable_raid_cb(update: Update, _: CallbackContext) -> Optional[str]:
    args = update.callback_query.data.replace("enable_raid=","").split("=")
    chat = update.effective_chat
    user = update.effective_user
    chat_id = args[0]
    time = int(args[1])
    readable_time = get_readable_time(time)
    _, t, acttime = sql.getDefenseStatus(chat_id)
    sql.setDefenseStatus(chat_id, True, time, acttime)
    update.effective_message.edit_text(f"Raid mode has been <code>Enabled</code> for {readable_time}.", parse_mode=ParseMode.HTML)
    log.info("enabled raid mode in {} for {}".format(chat_id, readable_time))
    def disable_raid(_):
        sql.setDefenseStatus(chat_id, False, t, acttime)
        log.info("disbled raid mode in {}".format(chat_id))
        logmsg = (
            f"<b>{html.escape(chat.title)}:</b>\n"
            f"#RAID\n"
            f"Automatically Disabled\n"
        )
        return logmsg
    j.run_once(disable_raid, time)
    logmsg = (
        f"<b>{html.escape(chat.title)}:</b>\n"
        f"#RAID\n"
        f"Enablbed for {readable_time}\n"
        f"<b>Admin:</b> {mention_html(user.id, user.first_name)}\n"
    )
    return logmsg


@ddocallback(pattern="disable_raid=")
@connection_status
@user_admin_no_reply
@loggable
def disable_raid_cb(update: Update, _: CallbackContext) -> Optional[str]:
    args = update.callback_query.data.replace("disable_raid=","").split("=")
    chat = update.effective_chat
    user = update.effective_user
    chat_id = args[0]
    time = args[1]
    _, t, acttime = sql.getDefenseStatus(chat_id)
    sql.setDefenseStatus(chat_id, False, time, acttime)
    update.effective_message.edit_text(
        'Raid mode has been <code>Disabled</code>, joinig members will no longer be kicked.',
        parse_mode=ParseMode.HTML,
    )
    logmsg = (
        f"<b>{html.escape(chat.title)}:</b>\n"
        f"#RAID\n"
        f"Disabled\n"
        f"<b>Admin:</b> {mention_html(user.id, user.first_name)}\n"
    )
    return logmsg


@ddocallback(pattern="cancel_raid=")
@connection_status
@user_admin_no_reply
def disable_raid_cb(update: Update, context: CallbackContext):
    args = update.callback_query.data.split("=")
    what = args[0]
    update.effective_message.edit_text(f"Action cancelled, Raid mode will stay <code>{'Enabled' if what ==1 else 'Disabled'}</code>.", parse_mode=ParseMode.HTML)


@ddocmd(command="raidtime")
@connection_status
@loggable
@u_admin(AdminPerms.CAN_CHANGE_INFO)
def raidtime(update: Update, context: CallbackContext) -> Optional[str]:
    what, time, acttime = sql.getDefenseStatus(update.effective_chat.id)
    args = context.args
    msg = update.effective_message
    u = update.effective_user
    chat = update.effective_chat
    user = res_user(u, msg.message_id, chat)
    if not args:
        msg.reply_text(f"Raid mode is currently set to {get_readable_time(time)}\nWhen toggled, the raid mode will last for {get_readable_time(time)} then turn off automatically", parse_mode=ParseMode.HTML)
        return
    args_time = args[0].lower()
    time = get_time(args_time)
    if time:
        readable_time = get_readable_time(time)
        if time >= 300 and time < 86400:
            text = f"Raid mode is currently set to {readable_time}\nWhen toggled, the raid mode will last for {readable_time} then turn off automatically"
            msg.reply_text(text, parse_mode=ParseMode.HTML)
            sql.setDefenseStatus(chat.id, what, time, acttime)
            logmsg = (
            f"<b>{html.escape(chat.title)}:</b>\n"
            f"#RAID\n"
            f"Set Raid mode time to {readable_time}\n"
            f"<b>Admin:</b> {mention_html(user.id, user.first_name)}\n"
            )
            return logmsg
        else:
            msg.reply_text("You can only set time between 5 minutes and 1 day", parse_mode=ParseMode.HTML)
    else:
        msg.reply_text("Unknown time given, give me something like 5m or 1h", parse_mode=ParseMode.HTML)


@ddocmd(command="raidactiontime", pass_args=True)
@connection_status
@u_admin(AdminPerms.CAN_CHANGE_INFO)
@loggable
def raidtime(update: Update, context: CallbackContext) -> Optional[str]:
    what, t, time = sql.getDefenseStatus(update.effective_chat.id)
    args = context.args
    msg = update.effective_message
    u = update.effective_user
    chat = update.effective_chat
    user = res_user(u, msg.message_id, chat)
    if not args:
        msg.reply_text(f"Raid actoin time is currently set to {get_readable_time(time)}\nWhen toggled, the members that join will be temp banned for {get_readable_time(time)}", parse_mode=ParseMode.HTML)
        return
    args_time = args[0].lower()
    time = get_time(args_time)
    if time:
        readable_time = get_readable_time(time)
        if time >= 300 and time < 86400:
            text = f"Raid actoin time is currently set to {get_readable_time(time)}\nWhen toggled, the members that join will be temp banned for {readable_time}"
            msg.reply_text(text, parse_mode=ParseMode.HTML)
            sql.setDefenseStatus(chat.id, what, t, time)
            logmsg = (
            f"<b>{html.escape(chat.title)}:</b>\n"
            f"#RAID\n"
            f"Set Raid mode action time to {readable_time}\n"
            f"<b>Admin:</b> {mention_html(user.id, user.first_name)}\n"
            )
            return logmsg
        else:
            msg.reply_text("You can only set time between 5 minutes and 1 day", parse_mode=ParseMode.HTML)
    else:
        msg.reply_text("Unknown time given, give me something like 5m or 1h", parse_mode=ParseMode.HTML)


__mod_name__ = "AntiRaid"

__help__ = """
Ever had your group raided by spammers or bots?
This module allows you to quickly stop the raiders
By enabling *raid mode* I will automatically kick every user that tries to join
When the raid is done you can toggle back lockgroup and everything will be back to normal.
  
*Admins only!* 
× /raid `(off/time optional)` : toggle the raid mode (on/off)
if no time is given it will default to 2 hours then turn off automatically
By enabling *raid mode* I will kick every user on joining the group.
× /raidtime `(time optional)` : view or set the default duration for raid mode, after that time from toggling the raid mode will turn off automatically
Default is 6 hours
× /raidactiontime `(time optional)` : view or set the default duration that the raid mode will tempban
Default is 1 hour
"""