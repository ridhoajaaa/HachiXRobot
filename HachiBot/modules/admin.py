import html
import os
import re
from typing import Optional
from HachiBot.events import callbackquery

from telegram import ParseMode, Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.error import BadRequest
from telegram.ext import CallbackContext, CommandHandler, Filters, run_async
from telegram.utils.helpers import mention_html

from HachiBot import DRAGONS, dispatcher
from HachiBot.modules.disable import DisableAbleCommandHandler
from HachiBot.modules.helper_funcs.chat_status import (
    bot_admin,
    can_pin,
    can_promote,
    connection_status,
    user_admin,
    ADMIN_CACHE,
)

from HachiBot.modules.helper_funcs.admin_rights import (
    user_can_changeinfo,
    user_can_promote,
)
from HachiBot.modules.helper_funcs.extraction import (
    extract_user,
    extract_user_and_text,
)
from HachiBot.modules.log_channel import loggable
from HachiBot.modules.helper_funcs.alternate import send_message


@bot_admin
@user_admin
def set_sticker(update: Update, context: CallbackContext):
    msg = update.effective_message
    chat = update.effective_chat
    user = update.effective_user

    if user_can_changeinfo(chat, user, context.bot.id) is False:
        return msg.reply_text("You're missing rights to change chat info!")

    if msg.reply_to_message:
        if not msg.reply_to_message.sticker:
            return msg.reply_text(
        f"<u><b>Sticker Not Found</b></u>\n"
        f"You need to reply to some sticker to set chat sticker set!",
        parse_mode=ParseMode.HTML,
        )
        stkr = msg.reply_to_message.sticker.set_name
        try:
            context.bot.set_chat_sticker_set(chat.id, stkr)
            msg.reply_text(f"Successfully set new group stickers in <b>{chat.title}</b>!")
        except BadRequest as excp:
            if excp.message == "Participants_too_few":
                return msg.reply_text(
                    "Sorry, due to telegram restrictions chat needs to have minimum 100 members before they can have group stickers!"
                )
            msg.reply_text(f"Error! {excp.message}.")
    else:
        msg.reply_text(
        f"<u><b>Sticker Not Found</b></u>\n"
        f"You need to reply to some sticker to set chat sticker set!",
        parse_mode=ParseMode.HTML,
        )


@bot_admin
@user_admin
def setchatpic(update: Update, context: CallbackContext):
    chat = update.effective_chat
    msg = update.effective_message
    user = update.effective_user

    if user_can_changeinfo(chat, user, context.bot.id) is False:
        msg.reply_text("You are missing right to change group info!")
        return

    if msg.reply_to_message:
        if msg.reply_to_message.photo:
            pic_id = msg.reply_to_message.photo[-1].file_id
        elif msg.reply_to_message.document:
            pic_id = msg.reply_to_message.document.file_id
        else:
            msg.reply_text("You can only set some photo as chat pic!")
            return
        dlmsg = msg.reply_text("Just a sec...")
        tpic = context.bot.get_file(pic_id)
        tpic.download("gpic.png")
        try:
            with open("gpic.png", "rb") as chatp:
                context.bot.set_chat_photo(int(chat.id), photo=chatp)
                msg.reply_text("Successfully set new chatpic!")
        except BadRequest as excp:
            msg.reply_text(f"Error! {excp.message}")
        finally:
            dlmsg.delete()
            if os.path.isfile("gpic.png"):
                os.remove("gpic.png")
    else:
        msg.reply_text("Reply to some photo or file to set new chat pic!")


@bot_admin
@user_admin
def rmchatpic(update: Update, context: CallbackContext):
    chat = update.effective_chat
    msg = update.effective_message
    user = update.effective_user

    if user_can_changeinfo(chat, user, context.bot.id) is False:
        msg.reply_text("You don't have enough rights to delete group photo")
        return
    try:
        context.bot.delete_chat_photo(int(chat.id))
        msg.reply_text("Successfully deleted chat's profile photo!")
    except BadRequest as excp:
        msg.reply_text(f"Error! {excp.message}.")
        return


@bot_admin
@user_admin
def set_desc(update: Update, context: CallbackContext):
    msg = update.effective_message
    chat = update.effective_chat
    user = update.effective_user

    if user_can_changeinfo(chat, user, context.bot.id) is False:
        return msg.reply_text("You're missing rights to change chat info!")

    tesc = msg.text.split(None, 1)
    if len(tesc) >= 2:
        desc = tesc[1]
    else:
        return msg.reply_text("Setting empty description won't do anything!")
    try:
        if len(desc) > 255:
            return msg.reply_text("Description must needs to be under 255 characters!")
        context.bot.set_chat_description(chat.id, desc)
        msg.reply_text(
            f"Successfully updated chat description in <b>{chat.title}</b>!",
            parse_mode=ParseMode.HTML,
        )
    except BadRequest as excp:
        msg.reply_text(f"Error! {excp.message}.")


@bot_admin
@user_admin
def setchat_title(update: Update, context: CallbackContext):
    chat = update.effective_chat
    msg = update.effective_message
    user = update.effective_user
    args = context.args

    if user_can_changeinfo(chat, user, context.bot.id) is False:
        msg.reply_text("You don't have enough rights to change chat info!")
        return

    title = " ".join(args)
    if not title:
        msg.reply_text("Enter some text to set new title in your chat!")
        return

    try:
        context.bot.set_chat_title(int(chat.id), str(title))
        msg.reply_text(
            f"Successfully set <b>{title}</b> as new chat title!",
            parse_mode=ParseMode.HTML,
        )
    except BadRequest as excp:
        msg.reply_text(f"Error! {excp.message}.")
        return


@connection_status
@bot_admin
@can_promote
@user_admin
@loggable
def admin(update: Update, context: CallbackContext) -> str:
    bot = context.bot
    args = context.args

    message = update.effective_message
    chat = update.effective_chat
    user = update.effective_user

    promoter = chat.get_member(user.id)

    if (
        not (promoter.can_promote_members or promoter.status == "creator")
        and user.id not in DRAGONS
    ):
        message.reply_text(
        f"<u><b>Permission Not Set</b></u>\n"
        f"You are missing one permission to do that, CAN_PROMOTE_MEMBER",
        parse_mode=ParseMode.HTML,
        )
        return

    user_id = extract_user(message, args)

    if not user_id:
        message.reply_text(
        f"<u><b>User Not Found</b></u>\n"
        f"The command /admin must be used specifying user <b>username/id/mention</b> or <b>replying</b> to one of his messages.",
        parse_mode=ParseMode.HTML,
        )
        return

    try:
        user_member = chat.get_member(user_id)
    except:
        return

    if user_member.status in ("administrator", "creator"):
        message.reply_text(
        f"<u><b>User Already Has Admin</b></u>\n"
        f"You can't make {mention_html(user_member.user.id, user_member.user.first_name)} [<code>{user_member.user.id}</code>] 👮🏻‍♂️ Admin.",
        parse_mode=ParseMode.HTML,
        )
        return

    if user_id == bot.id:
        message.reply_text(
        f"<u><b>This Is My Self</b></u>\n"
        f"I can't promote myself! Get an admin to do it for me.",
        parse_mode=ParseMode.HTML,
        )
        return

    # set same perms as bot - bot can't assign higher perms than itself!
    bot_member = chat.get_member(bot.id)

    bot.promoteChatMember(
            chat.id,
            user_id,
            can_change_info=bot_member.can_change_info,
            can_post_messages=bot_member.can_post_messages,
            can_edit_messages=bot_member.can_edit_messages,
            can_delete_messages=bot_member.can_delete_messages,
            can_invite_users=bot_member.can_invite_users,
            # can_promote_members=bot_member.can_promote_members,
            can_restrict_members=bot_member.can_restrict_members,
            can_pin_messages=bot_member.can_pin_messages,
    )
    
    title = "babu"
    if " " in message.text:
        title = message.text.split(" ", 1)[1]
        if len(title) > 16:
            message.reply_text(
                "The title length is longer than 16 characters.\nTruncating it to 16 characters."
            )

        try:
            bot.setChatAdministratorCustomTitle(chat.id, user_id, title)

        except BadRequest:
            message.reply_text(
        f"<u><b>Invalid Admin</b></u>\n"
        f"I can't set custom title for admins that I didn't promote!",
        parse_mode=ParseMode.HTML,
        )

    bot.sendMessage(
        chat.id,
        f"Promoting a user in <b>{chat.title}</b>\n\n<b>User: {mention_html(user_member.user.id, user_member.user.first_name)}</b>\n<b>Admin: {mention_html(user.id, user.first_name)}</b>\n\n<b>With Title: {title[:16]}</b>",
        parse_mode=ParseMode.HTML,
    )
    button = InlineKeyboardMarkup(
        [
            [
                InlineKeyboardButton(text="Reload 🔃", callback_data="reload_")
            ]
        ]
    )

    log_message = (
        f"<b>{html.escape(chat.title)}:</b>\n"
        f"#PROMOTED\n"
        f"<b>Admin:</b> {mention_html(user.id, user.first_name)}\n"
        f"<b>User:</b> {mention_html(user_member.user.id, user_member.user.first_name)}"
    )

    return log_message


@connection_status
@bot_admin
@can_promote
@user_admin
@loggable
def lowpromote(update: Update, context: CallbackContext) -> str:
    bot = context.bot
    args = context.args

    message = update.effective_message
    chat = update.effective_chat
    user = update.effective_user

    promoter = chat.get_member(user.id)

    if (
        not (promoter.can_promote_members or promoter.status == "creator")
        and user.id not in DRAGONS
    ):
        message.reply_text(
        f"<u><b>Permission Not Set</b></u>\n"
        f"You are missing one permission to do that, CAN_PROMOTE_MEMBER",
        parse_mode=ParseMode.HTML,
        )
        return

    user_id = extract_user(message, args)

    if not user_id:
        message.reply_text(
        f"<u><b>User Not Found</b></u>\n"
        f"The command /etmin must be used specifying user <b>username/id/mention</b> or <b>replying</b> to one of his messages.",
        parse_mode=ParseMode.HTML,
        )
        return
    
    try:
        user_member = chat.get_member(user_id)
    except:
        return

    if user_member.status in ("administrator", "creator"):
        message.reply_text(
        f"<u><b>User Already Has Admin</b></u>\n"
        f"You can't make {mention_html(user_member.user.id, user_member.user.first_name)} [<code>{user_member.user.id}</code>] 👮🏻‍♂️ Etmin.",
        parse_mode=ParseMode.HTML,
        )
        return

    if user_id == bot.id:
        message.reply_text(
        f"<u><b>This Is My Self</b></u>\n"
        f"I can't promote myself! Get an admin to do it for me.",
        parse_mode=ParseMode.HTML,
        )
        return

    # set same perms as bot - bot can't assign higher perms than itself!
    bot_member = chat.get_member(bot.id)

    try:
        bot.promoteChatMember(
            chat.id,
            user_id,
            can_delete_messages=bot_member.can_delete_messages,
            can_invite_users=bot_member.can_invite_users,
            can_pin_messages=bot_member.can_pin_messages,
        )
    except BadRequest as err:
        if err.message == "User_not_mutual_contact":
            message.reply_text(
        f"<u><b>The User Not In The Group</b></u>\n"
        f"You can't add {mention_html(user_member.user.id, user_member.user.first_name)} [<code>{user_member.user.id}</code>] as 👮🏻‍♂️ etmin because he is not a member of the group.",
        parse_mode=ParseMode.HTML,
        )
        else:
            message.reply_text("An error occured while promoting.")
        return

    bot.sendMessage(
        chat.id,
        f"Lowpromoting a user in <b>{chat.title}<b>\n\nUser: {mention_html(user_member.user.id, user_member.user.first_name)}\nAdmin: {mention_html(user.id, user.first_name)}",
        parse_mode=ParseMode.HTML,
    )

    log_message = (
        f"<b>{html.escape(chat.title)}:</b>\n"
        f"#LOWPROMOTED\n"
        f"<b>Admin:</b> {mention_html(user.id, user.first_name)}\n"
        f"<b>User:</b> {mention_html(user_member.user.id, user_member.user.first_name)}"
    )

    return log_message


@connection_status
@bot_admin
@can_promote
@user_admin
@loggable
def coadmin(update: Update, context: CallbackContext) -> str:
    bot = context.bot
    args = context.args

    message = update.effective_message
    chat = update.effective_chat
    user = update.effective_user

    promoter = chat.get_member(user.id)

    if (
        not (promoter.can_promote_members or promoter.status == "creator")
        and user.id not in DRAGONS
    ):
        message.reply_text(
        f"<u><b>Permission Not Set</b></u>\n"
        f"You are missing one permission to do that, CAN_PROMOTE_MEMBER",
        parse_mode=ParseMode.HTML,
        )
        return

    user_id = extract_user(message, args)

    if not user_id:
        message.reply_text(
        f"<u><b>User Not Found</b></u>\n"
        f"The command /coadmin must be used specifying user <b>username/id/mention</b> or <b>replying</b> to one of his messages.",
        parse_mode=ParseMode.HTML,
        )
        return

    try:
        user_member = chat.get_member(user_id)
    except:
        return

    if user_member.status in ("administrator", "creator"):
        message.reply_text(
        f"<u><b>User Already Has CoAdmin</b></u>\n"
        f"You can't make {mention_html(user_member.user.id, user_member.user.first_name)} [<code>{user_member.user.id}</code>] 👮🏻‍♂️ CoAdmin.",
        parse_mode=ParseMode.HTML,
        )
        return

    if user_id == bot.id:
        message.reply_text(
        f"<u><b>This Is My Self</b></u>\n"
        f"I can't promote myself! Get an admin to do it for me.",
        parse_mode=ParseMode.HTML,
        )
        return

    # set same perms as bot - bot can't assign higher perms than itself!
    bot_member = chat.get_member(bot.id)

    try:
        bot.promoteChatMember(
            chat.id,
            user_id,
            can_change_info=bot_member.can_change_info,
            can_post_messages=bot_member.can_post_messages,
            can_edit_messages=bot_member.can_edit_messages,
            can_delete_messages=bot_member.can_delete_messages,
            can_invite_users=bot_member.can_invite_users,
            can_promote_members=bot_member.can_promote_members,
            can_restrict_members=bot_member.can_restrict_members,
            can_pin_messages=bot_member.can_pin_messages,
            can_manage_voice_chats=bot_member.can_manage_voice_chats,
        )
    except BadRequest as err:
        if err.message == "User_not_mutual_contact":
            message.reply_text(
        f"<u><b>The User Not In The Group</b></u>\n"
        f"You can't add {mention_html(user_member.user.id, user_member.user.first_name)} [<code>{user_member.user.id}</code>] as 👮🏻‍♂️ CoAdmin because he is not a member of the group.",
        parse_mode=ParseMode.HTML,
        )
        else:
            message.reply_text("An error occured while promoting.")
        return

    keyboard = InlineKeyboardMarkup(
        [
            [
                InlineKeyboardButton(
                    "Demote", callback_data="demote_({})".format(user_member.user.id)
                )
            ]
        ]
    )

    bot.sendMessage(
        chat.id,
        f"Fullpromoting a user in <b>{chat.title}</b>\n\n<b>User: {mention_html(user_member.user.id, user_member.user.first_name)}</b>\n<b>Promoter: {mention_html(user.id, user.first_name)}</b>",
        parse_mode=ParseMode.HTML,
    )

    log_message = (
        f"<b>{html.escape(chat.title)}:</b>\n"
        f"#COADMIND\n"
        f"<b>Admin:</b> {mention_html(user.id, user.first_name)}\n"
        f"<b>User:</b> {mention_html(user_member.user.id, user_member.user.first_name)}"
    )

    return log_message


@connection_status
@bot_admin
@can_promote
@user_admin
@loggable
def unadmin(update: Update, context: CallbackContext) -> str:
    bot = context.bot
    args = context.args

    chat = update.effective_chat
    message = update.effective_message
    user = update.effective_user

    user_id = extract_user(message, args)
    if not user_id:
        message.reply_text(
        f"<u><b>User Not Found</b></u>\n"
        f"The command /unadmin must be used specifying user <b>username/id/mention</b> or <b>replying</b> to one of his messages.",
        parse_mode=ParseMode.HTML,
        )
        return

    try:
        user_member = chat.get_member(user_id)
    except:
        return

    if user_member.status == "creator":
        message.reply_text(
        f"<u><b>This Is Creator Group</b></u>\n"
        f"I can't demote the creator! don't make fun of yourself!",
        parse_mode=ParseMode.HTML,
        )
        return

    if not user_member.status == "administrator":
        message.reply_text(
        f"<u><b>User Doesn't Have This Role</b></u>\n"
        f"You can't remove {mention_html(user_member.user.id, user_member.user.first_name)} [<code>{user_member.user.id}</code>] From 👮🏻‍♂️ Admin.",
        parse_mode=ParseMode.HTML,
        )
        return

    if user_id == bot.id:
        message.reply_text(
        f"<u><b>This Is My Self</b></u>\n"
        f"I can't demote myself! Get an admin to do it manually for me.",
        parse_mode=ParseMode.HTML,
        )
        return

    try:
        bot.promoteChatMember(
            chat.id,
            user_id,
            can_change_info=False,
            can_post_messages=False,
            can_edit_messages=False,
            can_delete_messages=False,
            can_invite_users=False,
            can_restrict_members=False,
            can_pin_messages=False,
            can_promote_members=False,
            can_manage_voice_chats=False,
        )

        bot.sendMessage(
            chat.id,
            f"Sucessfully demoted a admins in <b>{chat.title}</b>\n\n<b>Admin: {mention_html(user_member.user.id, user_member.user.first_name)}</b>\n<b>Demoter: {mention_html(user.id, user.first_name)}</b>",
            parse_mode=ParseMode.HTML,
        )

        log_message = (
            f"<b>{html.escape(chat.title)}:</b>\n"
            f"#DEMOTED\n"
            f"<b>Admin:</b> {mention_html(user.id, user.first_name)}\n"
            f"<b>User:</b> {mention_html(user_member.user.id, user_member.user.first_name)}"
        )

        return log_message
    except BadRequest:
        message.reply_text(
        f"<u><b>Admin Not Promoted By The Bot</b></u>\n"
        f"The Administrator you have selected has not been promoted by this Bot and therefore cannot be removed with the command.",
        parse_mode=ParseMode.HTML,
        )
        return


@user_admin
def reload(update, _):
    try:
        ADMIN_CACHE.pop(update.effective_chat.id)
    except KeyError:
        pass

    update.effective_message.reply_text("✅ Admins cache refreshed!\n✅ Admin list updated!")


@connection_status
@bot_admin
@can_promote
@user_admin
def set_title(update: Update, context: CallbackContext):
    bot = context.bot
    args = context.args

    chat = update.effective_chat
    message = update.effective_message

    user_id, title = extract_user_and_text(message, args)
    try:
        user_member = chat.get_member(user_id)
    except:
        return

    if not user_id:
        message.reply_text(
            "You don't seem to be referring to a user or the ID specified is incorrect..",
        )
        return

    if user_member.status == "creator":
        message.reply_text(
            "This person CREATED the chat, how can i set custom title for him?",
        )
        return

    if user_member.status != "administrator":
        message.reply_text(
            "Can't set title for non-admins!\nPromote them first to set custom title!",
        )
        return

    if user_id == bot.id:
        message.reply_text(
            "I can't set my own title myself! Get the one who made me admin to do it for me.",
        )
        return

    if not title:
        message.reply_text("Setting blank title doesn't do anything!")
        return

    if len(title) > 16:
        message.reply_text(
            "The title length is longer than 16 characters.\nTruncating it to 16 characters.",
        )

    try:
        bot.setChatAdministratorCustomTitle(chat.id, user_id, title)
    except BadRequest:
        message.reply_text(
            "Either they aren't promoted by me or you set a title text that is impossible to set."
        )
        return

    bot.sendMessage(
        chat.id,
        f"Sucessfully set title for <code>{user_member.user.first_name or user_id}</code> "
        f"to <code>{html.escape(title[:16])}</code>!",
        parse_mode=ParseMode.HTML,
    )


@bot_admin
@can_pin
@user_admin
@loggable
def pin(update: Update, context: CallbackContext) -> str:
    bot, args = context.bot, context.args
    user = update.effective_user
    chat = update.effective_chat
    msg = update.effective_message
    msg_id = msg.reply_to_message.message_id if msg.reply_to_message else msg.message_id

    if msg.chat.username:
        # If chat has a username, use this format
        link_chat_id = msg.chat.username
        message_link = f"https://t.me/{link_chat_id}/{msg_id}"
    elif (str(msg.chat.id)).startswith("-100"):
        # If chat does not have a username, use this
        link_chat_id = (str(msg.chat.id)).replace("-100", "")
        message_link = f"https://t.me/c/{link_chat_id}/{msg_id}"

    is_group = chat.type not in ("private", "channel")
    prev_message = update.effective_message.reply_to_message

    if prev_message is None:
        msg.reply_text(
        f"<u><b>Chat Not Found</b></u>\n"
        f"The command /pin must be used specifying chat <b>replying</b> to one of his messages.",
        parse_mode=ParseMode.HTML,
        )
        return

    is_silent = True
    if len(args) >= 1:
        is_silent = (
            args[0].lower() != "notify"
            or args[0].lower() == "loud"
            or args[0].lower() == "violent"
        )

    if prev_message and is_group:
        try:
            bot.pinChatMessage(
                chat.id, prev_message.message_id, disable_notification=is_silent
            )
            msg.reply_text(
                f"Succsesfully pinned a message In Group <b>{chat.title}</b>.",
                reply_markup=InlineKeyboardMarkup(
                    [[InlineKeyboardButton("Go To Message", url=f"{message_link}")]]
                ),
                parse_mode=ParseMode.HTML,
                disable_web_page_preview=True,
            )
        except BadRequest as excp:
            if excp.message != "Chat_not_modified":
                raise

        log_message = (
            f"<b>{html.escape(chat.title)}:</b>\n"
            f"MESSAGE-PINNED-SUCCESSFULLY\n"
            f"<b>Admin:</b> {mention_html(user.id, html.escape(user.first_name))}"
        )

        return log_message


@bot_admin
@can_pin
@user_admin
@loggable
def unpin(update: Update, context: CallbackContext):
    chat = update.effective_chat
    user = update.effective_user
    msg = update.effective_message
    msg_id = msg.reply_to_message.message_id if msg.reply_to_message else msg.message_id
    unpinner = chat.get_member(user.id)

    if (
        not (unpinner.can_pin_messages or unpinner.status == "creator")
        and user.id not in DRAGONS
    ):
        msg.reply_text("You don't have the necessary rights to do that!")
        return

    if msg.chat.username:
        # If chat has a username, use this format
        link_chat_id = msg.chat.username
        message_link = f"https://t.me/{link_chat_id}/{msg_id}"
    elif (str(msg.chat.id)).startswith("-100"):
        # If chat does not have a username, use this
        link_chat_id = (str(msg.chat.id)).replace("-100", "")
        message_link = f"https://t.me/c/{link_chat_id}/{msg_id}"

    is_group = chat.type not in ("private", "channel")
    prev_message = update.effective_message.reply_to_message

    if prev_message and is_group:
        try:
            context.bot.unpinChatMessage(chat.id, prev_message.message_id)
            msg.reply_text(
                f"i removed the <a href='{message_link}'>pinned message</a>.",
                parse_mode=ParseMode.HTML,
                disable_web_page_preview=True,
            )
        except BadRequest as excp:
            if excp.message != "Chat_not_modified":
                raise

    if not prev_message and is_group:
        try:
            context.bot.unpinChatMessage(chat.id)
            msg.reply_text("Unpinned the last pinned message.")
        except BadRequest as excp:
            if excp.message == "Message to unpin not found":
                msg.reply_text(
                    "I can't see pinned message, Maybe already unpined, or pin Message to old 🙂"
                )
            else:
                raise

    log_message = (
        f"<b>{html.escape(chat.title)}:</b>\n"
        f"MESSAGE-UNPINNED-SUCCESSFULLY\n"
        f"<b>Admin:</b> {mention_html(user.id, html.escape(user.first_name))}"
    )

    return log_message


@bot_admin
def pinned(update: Update, context: CallbackContext) -> str:
    bot = context.bot
    msg = update.effective_message
    msg_id = (
        update.effective_message.reply_to_message.message_id
        if update.effective_message.reply_to_message
        else update.effective_message.message_id
    )

    chat = bot.getChat(chat_id=msg.chat.id)
    if chat.pinned_message:
        pinned_id = chat.pinned_message.message_id
        if msg.chat.username:
            link_chat_id = msg.chat.username
            message_link = f"https://t.me/{link_chat_id}/{pinned_id}"
        elif (str(msg.chat.id)).startswith("-100"):
            link_chat_id = (str(msg.chat.id)).replace("-100", "")
            message_link = f"https://t.me/c/{link_chat_id}/{pinned_id}"

        msg.reply_text(
            f"Chat Pinned In <b>{html.escape(chat.title)}.</b>",
            reply_to_message_id=msg_id,
            parse_mode=ParseMode.HTML,
            disable_web_page_preview=True,
            reply_markup=InlineKeyboardMarkup(
                [
                    [
                        InlineKeyboardButton(
                            text="Go To Message",
                            url=f"https://t.me/{link_chat_id}/{pinned_id}",
                        )
                    ]
                ]
            ),
        )

    else:
        msg.reply_text(
            f"There is no pinned message in <b>{html.escape(chat.title)}!</b>",
            parse_mode=ParseMode.HTML,
        )


@bot_admin
@user_admin
@connection_status
def invite(update: Update, context: CallbackContext):
    bot = context.bot
    chat = update.effective_chat

    if chat.username:
        update.effective_message.reply_text(f"https://t.me/{chat.username}")
    elif chat.type in [chat.SUPERGROUP, chat.CHANNEL]:
        bot_member = chat.get_member(bot.id)
        if bot_member.can_invite_users:
            invitelink = bot.exportChatInviteLink(chat.id)
            update.effective_message.reply_text(invitelink)
        else:
            update.effective_message.reply_text(
                "I don't have access to the invite link, try changing my permissions!",
            )
    else:
        update.effective_message.reply_text(
            "I can only give you invite links for supergroups and channels, sorry!",
        )


@connection_status
def adminlist(update, context):
    chat = update.effective_chat
    user = update.effective_user
    args = context.args
    bot = context.bot

    if update.effective_message.chat.type == "private":
        send_message(update.effective_message, "This command only works in Groups.")
        return

    chat = update.effective_chat
    chat_id = update.effective_chat.id
    chat_name = update.effective_message.chat.title

    try:
        msg = update.effective_message.reply_text(
            "Fetching group admins...",
            parse_mode=ParseMode.HTML,
        )
    except BadRequest:
        msg = update.effective_message.reply_text(
            "Fetching group admins...",
            quote=False,
            parse_mode=ParseMode.HTML,
        )

    administrators = bot.getChatAdministrators(chat_id)
    text = "Admins in <b>{}</b>:".format(html.escape(update.effective_chat.title))

    for admin in administrators:
        user = admin.user
        status = admin.status
        custom_title = admin.custom_title

        if user.first_name == "":
            name = "☠ Deleted Account"
        else:
            name = "{}".format(
                mention_html(
                    user.id,
                    html.escape(user.first_name + " " + (user.last_name or "")),
                ),
            )

        if user.is_bot:
            administrators.remove(admin)
            continue

        # if user.username:
        #    name = escape_markdown("@" + user.username)
        if status == "creator":
            text += "\n 🌏 Creator:"
            text += "\n<code> × </code>{}\n".format(name)

            if custom_title:
                text += f"<code> ┗━ {html.escape(custom_title)}</code>\n"

    text += "\n🌟 Admins:"

    custom_admin_list = {}
    normal_admin_list = []

    for admin in administrators:
        user = admin.user
        status = admin.status
        custom_title = admin.custom_title

        if user.first_name == "":
            name = "☠ Deleted Account"
        else:
            name = "{}".format(
                mention_html(
                    user.id,
                    html.escape(user.first_name + " " + (user.last_name or "")),
                ),
            )
        # if user.username:
        #    name = escape_markdown("@" + user.username)
        if status == "administrator":
            if custom_title:
                try:
                    custom_admin_list[custom_title].append(name)
                except KeyError:
                    custom_admin_list.update({custom_title: [name]})
            else:
                normal_admin_list.append(name)

    for admin in normal_admin_list:
        text += "\n<code> × </code>{}".format(admin)

    for admin_group in custom_admin_list.copy():
        if len(custom_admin_list[admin_group]) == 1:
            text += "\n<code> × </code>{} | <code>{}</code>".format(
                custom_admin_list[admin_group][0],
                html.escape(admin_group),
            )
            custom_admin_list.pop(admin_group)

    text += "\n"
    for admin_group, value in custom_admin_list.items():
        text += "\n🚨 <code>{}</code>".format(admin_group)
        for admin in value:
            text += "\n<code> × </code>{}".format(admin)
        text += "\n"

    try:
        msg.edit_text(text, parse_mode=ParseMode.HTML)
    except BadRequest:  # if original message is deleted
        return


@bot_admin
@can_promote
@user_admin
@loggable
def button(update: Update, context: CallbackContext) -> str:
    query = update.callback_query
    user = update.effective_user
    bot = context.bot
    match = re.match(r"demote_\((.+?)\)", query.data)
    if match:
        user_id = match.group(1)
        chat = update.effective_chat
        member = chat.get_member(user_id)
        bot_member = chat.get_member(bot.id)
        user_member = chat.get_member(user_id)
        bot_permissions = bot.promoteChatMember(
            chat.id,
            user_id,
            can_change_info=bot_member.can_change_info,
            can_post_messages=bot_member.can_post_messages,
            can_edit_messages=bot_member.can_edit_messages,
            can_delete_messages=bot_member.can_delete_messages,
            can_invite_users=bot_member.can_invite_users,
            can_promote_members=bot_member.can_promote_members,
            can_restrict_members=bot_member.can_restrict_members,
            can_pin_messages=bot_member.can_pin_messages,
            can_manage_voice_chats=bot_member.can_manage_voice_chats,
        )
        demoted = bot.promoteChatMember(
            chat.id,
            user_id,
            can_change_info=False,
            can_post_messages=False,
            can_edit_messages=False,
            can_delete_messages=False,
            can_invite_users=False,
            can_restrict_members=False,
            can_pin_messages=False,
            can_promote_members=False,
            can_manage_voice_chats=False,
        )
        if demoted:
            update.effective_message.edit_text(
                f"Sucessfully demoted a admins in <b>{chat.title}</b>\n\n<b>Admin: {mention_html(user_member.user.id, user_member.user.first_name)}</b>\n<b>Demoter: {mention_html(user.id, user.first_name)}</b>",
            parse_mode=ParseMode.HTML,
            )
            query.answer("Demoted!")
            return (
                f"<b>{html.escape(chat.title)}:</b>\n"
                f"#DEMOTE\n"
                f"<b>Admin:</b> {mention_html(user.id, user.first_name)}\n"
                f"<b>User:</b> {mention_html(member.user.id, member.user.first_name)}"
            )
    else:
        update.effective_message.edit_text(
            "This user is not promoted or has left the group!"
        )
        return ""

def button(update: Update, context: CallbackContext) -> str:
    query = update.callback_query
    user = update.effective_user
    bot = context.bot
    match = re.match(r"reload_\((.+?)\)", query.data)
    try:
        ADMIN_CACHE.pop(update.effective_chat.id)
    except KeyError:
        pass

    update.effective_message.reply_text("✅ Admins cache refreshed!\n✅ Admin list updated!")
    query.answer("Reloaded!")


__help__ = """
*User Commands*:
× /admins or /staff*:* list of admins in the chat
× /pinned*:* to get the current pinned message.

*The Following Commands are Admins only:* 
× /pin*:* silently pins the message replied to - add `'loud'` or `'notify'` to give notifs to users
× /unpin*:* unpins the currently pinned message
× /invitelink*:* gets invitelink
× /admin*:* promotes the user replied to
× /etmin*:* promotes the user replied to with low right
× /coadmin*:* promotes the user replied to with full rights
× /demote*:* demotes the user replied to
× /title <title here>*:* sets a custom title for an admin that the bot promoted
× /admincache*:* force refresh the admins list
× /del*:* deletes the message you replied to
× /purge*:* deletes all messages between this and the replied to message.
× /purge <integer X>*:* deletes the replied message, and X messages following it if replied to a message.
× /setgtitle <text>*:* set group title
× /setgpic*:* reply to an image to set as group photo
× /setdesc*:* Set group description
× /setsticker*:* Set group sticker

*Anti Channel Mode*:
× /antich or /antichannel <on/off>*:* Bans and deletes anyone who tries to talk as channel and forces them to talk using real account
× /antilinkedchannel <on/off>*:* Makes Hachi automatically delete linked channel posts from groups
× /antichannelpin <on/off>*:* Makes Hachi automatically unpin linked channel posts from chatroom

*Rules*:
× /rules*:* get the rules for this chat.
× /setrules <your rules here>*:* set the rules for this chat.
× /clearrules*:* clear the rules for this chat.
"""

SET_DESC_HANDLER = CommandHandler(
    "setdesc", set_desc, filters=Filters.chat_type.groups, run_async=True
)
SET_STICKER_HANDLER = CommandHandler(
    "setsticker", set_sticker, filters=Filters.chat_type.groups, run_async=True
)
SETCHATPIC_HANDLER = CommandHandler(
    "setgpic", setchatpic, filters=Filters.chat_type.groups, run_async=True
)
RMCHATPIC_HANDLER = CommandHandler(
    "delgpic", rmchatpic, filters=Filters.chat_type.groups, run_async=True
)
SETCHAT_TITLE_HANDLER = CommandHandler(
    "setgtitle", setchat_title, filters=Filters.chat_type.groups, run_async=True
)

ADMINLIST_HANDLER = DisableAbleCommandHandler("admins", adminlist, run_async=True)

PIN_HANDLER = CommandHandler(
    "pin", pin, filters=Filters.chat_type.groups, run_async=True
)
UNPIN_HANDLER = CommandHandler(
    "unpin", unpin, filters=Filters.chat_type.groups, run_async=True
)
PINNED_HANDLER = CommandHandler(
    "pinned", pinned, filters=Filters.chat_type.groups, run_async=True
)

INVITE_HANDLER = DisableAbleCommandHandler("invitelink", invite, run_async=True)

ADMIN_HANDLER = DisableAbleCommandHandler("admin", admin, run_async=True)
COADMIN_HANDLER = DisableAbleCommandHandler(
    "coadmin", coadmin, run_async=True
)
LOW_PROMOTE_HANDLER = DisableAbleCommandHandler(
    "etmin", lowpromote, run_async=True
)
UNADMIN_HANDLER = DisableAbleCommandHandler("unadmin", unadmin, run_async=True)

SET_TITLE_HANDLER = CommandHandler("title", set_title, run_async=True)
RELOAD_HANDLER = CommandHandler(
    "reload", reload, filters=Filters.chat_type.groups, run_async=True
)

dispatcher.add_handler(SET_DESC_HANDLER)
dispatcher.add_handler(SET_STICKER_HANDLER)
dispatcher.add_handler(SETCHATPIC_HANDLER)
dispatcher.add_handler(RMCHATPIC_HANDLER)
dispatcher.add_handler(SETCHAT_TITLE_HANDLER)
dispatcher.add_handler(ADMINLIST_HANDLER)
dispatcher.add_handler(PIN_HANDLER)
dispatcher.add_handler(UNPIN_HANDLER)
dispatcher.add_handler(PINNED_HANDLER)
dispatcher.add_handler(INVITE_HANDLER)
dispatcher.add_handler(ADMIN_HANDLER)
dispatcher.add_handler(COADMIN_HANDLER)
dispatcher.add_handler(LOW_PROMOTE_HANDLER)
dispatcher.add_handler(UNADMIN_HANDLER)
dispatcher.add_handler(SET_TITLE_HANDLER)
dispatcher.add_handler(RELOAD_HANDLER)

__mod_name__ = "Admins"
__command_list__ = [
    "setdesc" "setsticker" "setgpic" "delgpic" "setgtitle" "adminlist",
    "admins",
    "invitelink",
    "admin",
    "coadmin",
    "lowpromote",
    "unadmin",
    "reload",
]
__handlers__ = [
    SET_DESC_HANDLER,
    SET_STICKER_HANDLER,
    SETCHATPIC_HANDLER,
    RMCHATPIC_HANDLER,
    SETCHAT_TITLE_HANDLER,
    ADMINLIST_HANDLER,
    PIN_HANDLER,
    UNPIN_HANDLER,
    PINNED_HANDLER,
    INVITE_HANDLER,
    ADMIN_HANDLER,
    COADMIN_HANDLER,
    LOW_PROMOTE_HANDLER,
    UNADMIN_HANDLER,
    SET_TITLE_HANDLER,
    RELOAD_HANDLER,
]
