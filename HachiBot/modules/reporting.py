from multiprocessing.connection import Client
from traceback import format_exc
from HachiBot.modules.helper_funcs.chat_status import user_admin

from pyrogram import filters
from pyrogram.errors import RPCError
from pyrogram.types import CallbackQuery, Message
from telegram.utils.helpers import mention_html
from telegram.ext import CommandHandler, MessageHandler, Filters, CallbackContext

from HachiBot.modules.helper_funcs.decorators import ddocallback
from HachiBot import pbot
from HachiBot import LOGGER, DEMONS
from HachiBot.modules.mongo.reporting_db import Reporting
from HachiBot.services.keyboard import ikb

@user_admin
@pbot.on_message(filters.command("reports") & (filters.private))
async def report_setting(_, m: Message):
    args = m.text.split()
    db = Reporting(m.chat.id)

    if m.chat.type == "private":
        if len(args) >= 2:
            option = args[1].lower()
            if option in ("yes", "on", "true"):
                db.set_settings(True)
                LOGGER.info(f"{m.from_user.id} enabled reports for them")
                await m.reply_text(
                    "Turned on reporting! You'll be notified whenever anyone reports something in groups you are admin.",
                )

            elif option in ("no", "off", "false"):
                db.set_settings(False)
                LOGGER.info(f"{m.from_user.id} disabled reports for them")
                await m.reply_text("Turned off reporting! You wont get any reports.")
        else:
            await m.reply_text(
                f"Your current report preference is: `{(db.get_settings())}`",
            )
    elif len(args) >= 2:
        option = args[1].lower()
        if option in ("yes", "on", "true"):
            db.set_settings(True)
            LOGGER.info(f"{m.from_user.id} enabled reports in {m.chat.id}")
            await m.reply_text(
                "Turned on reporting! Admins who have turned on reports will be notified when /report "
                "or @admin is called.",
                quote=True,
            )

        elif option in ("no", "off", "false"):
            db.set_settings(False)
            LOGGER.info(f"{m.from_user.id} disabled reports in {m.chat.id}")
            await m.reply_text(
                "Turned off reporting! No admins will be notified on /report or @admin.",
                quote=True,
            )
    else:
        await m.reply_text(
            f"This group's current setting is: `{(db.get_settings())}`",
        )


@pbot.on_message(filters.command("report") & filters.group)
async def report_watcher(c: Client, m: Message):
    if m.chat.type != "supergroup":
        return

    if not m.from_user:
        return

    me = await c.get_me()
    db = Reporting(m.chat.id)

    if (m.chat and m.reply_to_message) and (db.get_settings()):
        reported_msg_id = m.reply_to_message.message_id
        reported_user = m.reply_to_message.from_user
        chat_name = m.chat.title or m.chat.username
        admin_list = await c.get_chat_members(m.chat.id, filter="administrators")

        if reported_user.id == me.id:
            await m.reply_text("Nice try.")
            return

        if reported_user.id in DEMONS:
            await m.reply_text("Uh? You reporting my support team?")
            return

        if m.chat.username:
            msg = (
                f"<b>⚠️ Report: </b>{m.chat.title}\n"
                f"<b> • Report by:</b> {(await mention_html(m.from_user.first_name, m.from_user.id))} (<code>{m.from_user.id}</code>)\n"
                f"<b> • Reported user:</b> {(await mention_html(reported_user.first_name, reported_user.id))} (<code>{reported_user.id}</code>)\n"
            )

        else:
            msg = f"{(await mention_html(m.from_user.first_name, m.from_user.id))} is calling for admins in '{chat_name}'!\n"

        link_chat_id = str(m.chat.id).replace("-100", "")
        link = f"https://t.me/c/{link_chat_id}/{reported_msg_id}"  # message link

        reply_markup = ikb(
            [
                [("➡ Message", link, "url")],
                [
                    (
                        "⚠ Kick",
                        f"report_{m.chat.id}=kick={reported_user.id}={reported_msg_id}",
                    ),
                    (
                        "⛔️ Ban",
                        f"report_{m.chat.id}=ban={reported_user.id}={reported_msg_id}",
                    ),
                ],
                [
                    (
                        "❎ Delete Message",
                        f"report_{m.chat.id}=del={reported_user.id}={reported_msg_id}",
                    ),
                ],
            ],
        )

        LOGGER.info(
            f"{m.from_user.id} reported msgid-{m.reply_to_message.message_id} to admins in {m.chat.id}",
        )
        await m.reply_text(
            (
                f"{(await mention_html(m.from_user.first_name, m.from_user.id))} "
                "reported the message to the admins."
            ),
            quote=True,
        )

        for admin in admin_list:
            if (
                admin.user.is_bot or admin.user.is_deleted
            ):  # can't message bots or deleted accounts
                continue
            if Reporting(admin.user.id).get_settings():
                try:
                    await c.send_message(
                        admin.user.id,
                        msg,
                        reply_markup=reply_markup,
                        disable_web_page_preview=True,
                    )
                    try:
                        await m.reply_to_message.forward(admin.user.id)
                        if len(m.text.split()) > 1:
                            await m.forward(admin.user.id)
                    except Exception:
                        pass
                except Exception:
                    pass
                except RPCError as ef:
                    LOGGER.error(ef)
                    LOGGER.error(format_exc())
    return ""


@ddocallback(pattern=r"report_")
async def report_buttons(context: CallbackContext, q: CallbackQuery):
    splitter = (str(q.data).replace("report_", "")).split("=")
    chat_id = int(splitter[0])
    action = str(splitter[1])
    user_id = int(splitter[2])
    message_id = int(splitter[3])
    if action == "kick":
        try:
            await context.bot.ban_chat_member(chat_id, user_id)
            await q.answer("✅ Succesfully kicked")
            await context.bot.unban_chat_member(chat_id, user_id)
            return
        except RPCError as err:
            await q.answer(
                f"🛑 Failed to Kick\n<b>Error:</b>\n</code>{err}</code>",
                show_alert=True,
            )
    elif action == "ban":
        try:
            await context.bot.ban_chat_member(chat_id, user_id)
            await q.answer("✅ Succesfully Banned")
            return
        except RPCError as err:
            await q.answer(f"🛑 Failed to Ban\n<b>Error:</b>\n`{err}`", show_alert=True)
    elif action == "del":
        try:
            await context.bot.delete_messages(chat_id, message_id)
            await q.answer("✅ Message Deleted")
            return
        except RPCError as err:
            await q.answer(
                f"🛑 Failed to delete message!\n<b>Error:</b>\n`{err}`",
                show_alert=True,
            )
    return