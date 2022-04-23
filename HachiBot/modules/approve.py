import html
import re

from telegram import ParseMode, InlineKeyboardMarkup, InlineKeyboardButton, Update
from telegram.error import BadRequest
from telegram.ext import CallbackContext, Filters
from telegram.utils.helpers import mention_html

import HachiBot.modules.sql.approve_sql as sql
from HachiBot import DRAGONS as SUDO_USERS
from HachiBot.modules.helper_funcs.chat_status import user_admin as u_admin
from HachiBot.modules.helper_funcs.decorators import ddocmd, ddocallback
from HachiBot.modules.helper_funcs.extraction import extract_user
from HachiBot.modules.log_channel import loggable
from HachiBot.modules.helper_funcs.anonymous import user_admin, AdminPerms


@ddocmd(command='free', filters=Filters.chat_type.groups)
@loggable
@user_admin(AdminPerms.CAN_CHANGE_INFO)
def free(update: Update, context: CallbackContext):
    message = update.effective_message
    chat_title = message.chat.title
    chat = update.effective_chat
    args = context.args
    user = update.effective_user
    user_id = extract_user(message, args)
    if not user_id:
        message.reply_text(
        f"<u><b>User Not Found</b></u>\n"
        f"The command /free must be used specifying user <b>username/id/mention</b> or <b>replying</b> to one of his messages.",
        parse_mode=ParseMode.HTML,
        )
        return ""
    try:
        member = chat.get_member(user_id)
        user_member = chat.get_member(user_id)
    except BadRequest:
        return ""
    if member.status == "administrator" or member.status == "creator":
        message.reply_text(
        f"<u><b>User Has Admin</b></u>\n"
        f"You can't make {mention_html(user_member.user.id, user_member.user.first_name)} [<code>{user_member.user.id}</code>] Free.",
        parse_mode=ParseMode.HTML,
        )
        return ""
    if sql.is_approved(message.chat_id, user_id):
        message.reply_text(
            f"{mention_html(user_member.user.id, user_member.user.first_name)} [<code>{user_member.user.id}</code>] is already approved in <b>{chat_title}</b>.",
            parse_mode=ParseMode.HTML,
        )
        return ""
    if sql.approve(message.chat_id, user_id):
        message.reply_text(
        f"@{html.escape(user_member.username)} [<code>{user_member.user.id}</code>] is now longer 🧙‍♂ approved in <b>{chat_title}!</b>",
        parse_mode=ParseMode.HTML,
    )
    else:
        f"{mention_html(user_member.user.id, user_member.user.first_name)} [<code>{user_member.user.id}</code>] is now longer 🧙‍♂ approved in <b>{chat_title}!</b>",
        parse_mode=ParseMode.HTML,
        
    log_message = (
        f"<b>{html.escape(chat.title)}:</b>\n"
        f"#APPROVED\n"
        f"<b>Admin:</b> {mention_html(user.id, user.first_name)}\n"
        f"<b>User:</b> {mention_html(member.user.id, member.user.first_name)}")

    return log_message


@ddocmd(command='unfree', filters=Filters.chat_type.groups)
@loggable
@user_admin(AdminPerms.CAN_CHANGE_INFO)
def unfree(update: Update, context: CallbackContext):
    message = update.effective_message
    chat_title = message.chat.title
    chat = update.effective_chat
    args = context.args
    user = update.effective_user
    user_id = extract_user(message, args)
    if not user_id:
        message.reply_text(
        f"<u><b>User Not Found</b></u>\n"
        f"The command /unfree must be used specifying user <b>username/id/mention</b> or <b>replying</b> to one of his messages.",
        parse_mode=ParseMode.HTML,
        )
        return ""
    try:
        member = chat.get_member(user_id)
        user_member = chat.get_member(user_id)
    except BadRequest:
        return ""
    if member.status == "administrator" or member.status == "creator":
        message.reply_text(
        f"<u><b>User Has Admin</b></u>\n"
        f"You can't remove {mention_html(user_member.user.id, user_member.user.first_name)} [<code>{user_member.user.id}</code>] From 🔓 Free.",
        parse_mode=ParseMode.HTML,
        )
        return ""
    if not sql.is_approved(message.chat_id, user_id):
        message.reply_text(
        f"<u><b>User Doesn't Have This Role</b></u>\n"
        f"You can't remove {mention_html(user_member.user.id, user_member.user.first_name)} [<code>{user_member.user.id}</code>] From 🔓 Free.",
        parse_mode=ParseMode.HTML,
        )
        return ""
    sql.disapprove(message.chat_id, user_id)
    message.reply_text(
        f"{mention_html(user_member.user.id, user_member.user.first_name)} [<code>{user_member.user.id}</code>] is no longer approved in <b>{chat_title}</b>.",
        parse_mode=ParseMode.HTML,
        )
    log_message = (
        f"<b>{html.escape(chat.title)}:</b>\n"
        f"#UNAPPROVED\n"
        f"<b>Admin:</b> {mention_html(user.id, user.first_name)}\n"
        f"<b>User:</b> {mention_html(member.user.id, member.user.first_name)}")

    return log_message


@ddocmd(command='listfree', filters=Filters.chat_type.groups)
@user_admin(AdminPerms.CAN_CHANGE_INFO)
def listfree(update: Update, _: CallbackContext):
    message = update.effective_message
    chat_title = message.chat.title
    chat = update.effective_chat
    msg = "The following users are approved in this chats.\n"
    approved_users = sql.list_approved(message.chat_id)
    for i in approved_users:
        member = chat.get_member(int(i.user_id))
        msg += f"- `{i.user_id}`: {member.user['first_name']}\n"
    if msg.endswith("approved.\n"):
        message.reply_text(f"No users are approved in {chat_title}.")
        return ""
    else:
        message.reply_text(msg, parse_mode=ParseMode.MARKDOWN)


@ddocmd(command='freeas', filters=Filters.chat_type.groups)
@user_admin(AdminPerms.CAN_CHANGE_INFO)
def freeas(update, context):
    message = update.effective_message
    chat = update.effective_chat
    args = context.args
    user_id = extract_user(message, args)
    if not user_id:
        message.reply_text(
        f"<u><b>User Not Found</b></u>\n"
        f"The command /freeas must be used specifying user <b>username/id/mention</b> or <b>replying</b> to one of his messages.",
        parse_mode=ParseMode.HTML,
        )
        return ""
    member = chat.get_member(int(user_id))

    if sql.is_approved(message.chat_id, user_id):
        message.reply_text(
            f"{member.user['first_name']} is an approved user. Locks, antiflood, and blocklists won't apply to them."
        )
    else:
        message.reply_text(
            f"{member.user['first_name']} is not an approved user. They are affected by normal commands."
        )


@ddocmd(command='unfreeall', filters=Filters.chat_type.groups)
def unfreeall(update: Update, _: CallbackContext):
    chat = update.effective_chat
    user = update.effective_user
    member = chat.get_member(user.id)
    if member.status != "creator" and user.id not in SUDO_USERS:
        update.effective_message.reply_text(
            "Only the chat owner can unapprove all users at once.")
    else:
        buttons = InlineKeyboardMarkup([
            [
                InlineKeyboardButton(
                    text="Unapprove all users",
                    callback_data="unapproveall_user")
            ],
            [
                InlineKeyboardButton(
                    text="Cancel", callback_data="unapproveall_cancel")
            ],
        ])
        update.effective_message.reply_text(
            f"Are you sure you would like to unapprove ALL users in {chat.title}? This action cannot be undone.",
            reply_markup=buttons,
            parse_mode=ParseMode.MARKDOWN,
        )


@ddocallback(pattern=r"unapproveall_.*")
def unapproveall_btn(update: Update, _: CallbackContext):
    query = update.callback_query
    chat = update.effective_chat
    message = update.effective_message
    member = chat.get_member(query.from_user.id)
    if query.data == "unapproveall_user":
        if member.status == "creator" or query.from_user.id in SUDO_USERS:
            approved_users = sql.list_approved(chat.id)
            users = [int(i.user_id) for i in approved_users]
            for user_id in users:
                sql.disapprove(chat.id, user_id)

        if member.status == "administrator":
            query.answer("Only owner of the chat can do this.")

        if member.status == "member":
            query.answer("You need to be admin to do this.")
    elif query.data == "unapproveall_cancel":
        if member.status == "creator" or query.from_user.id in SUDO_USERS:
            message.edit_text(
                "Removing of all approved users has been cancelled.")
            return ""
        if member.status == "administrator":
            query.answer("Only owner of the chat can do this.")
        if member.status == "member":
            query.answer("You need to be admin to do this.")


__mod_name__ = "Approvals"

__help__ = """
Sometimes, you might trust a user not to send unwanted content.
Maybe not enough to make them admin, but you might be ok with locks, blacklists, and antiflood not applying to them.
That's what approvals are for - approve of trustworthy users to allow them to send
*Admin commands:*

× /freeas*:* Check a user's approval status in this chat.
× /free*:* Approve of a user. Locks, blacklists, and antiflood won't apply to them anymore.
× /unfree*:* Unapprove of a user. They will now be subject to locks, blacklists, and antiflood again.
× /listfree*:* List all approved users.
× /unfreeall*:* Unapprove *ALL* users in a chat. This cannot be undone.
"""