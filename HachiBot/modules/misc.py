from ast import pattern
import datetime
import platform
import random
import re
import wikipedia
import os

from platform import python_version

import requests as r
from requests import get
from random import randint
from PIL import Image
from telegraph import Telegraph, upload_file, exceptions
from psutil import boot_time, cpu_percent, disk_usage, virtual_memory
from spamwatch import __version__ as __sw__
from telegram import (
    ChatAction,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    ReplyKeyboardRemove,
    ParseMode,
    Update,
    __version__,
)
from telegram.error import BadRequest
from telegram.ext import CallbackContext, CommandHandler, Filters
from telethon import events, Button, types

from HachiBot import OWNER_ID, SUPPORT_CHAT, WALL_API, dispatcher, telethn as Client
from HachiBot.events import register
from HachiBot.__main__ import GDPR
from HachiBot.modules.disable import DisableAbleCommandHandler
from HachiBot.modules.helper_funcs.alternate import send_action, typing_action
from HachiBot.modules.helper_funcs.chat_status import user_admin
from HachiBot.modules.helper_funcs.filters import CustomFilters
from HachiBot.modules.helper_funcs.decorators import ddocmd


MARKDOWN_HELP = f"""
Markdown is a very powerful formatting tool supported by telegram. {dispatcher.bot.first_name} has some enhancements, to make sure that \
saved messages are correctly parsed, and to allow you to create buttons.
 × <code>_italic_</code>: wrapping text with '_' will produce italic text
 × <code>*bold*</code>: wrapping text with '*' will produce bold text
 × <code>`code`</code>: wrapping text with '`' will produce monospaced text, also known as 'code'
 × <code>[sometext](someURL)</code>: this will create a link - the message will just show <code>sometext</code>, \
and tapping on it will open the page at <code>someURL</code>.
<b>Example:</b><code>[test](example.com)</code>
× <code>[buttontext](buttonurl:someURL)</code>: this is a special enhancement to allow users to have telegram \
buttons in their markdown. <code>buttontext</code> will be what is displayed on the button, and <code>someurl</code> \
will be the url which is opened.
<b>Example:</b> <code>[This is a button](buttonurl:example.com)</code>
If you want multiple buttons on the same line, use :same, as such:
<code>[one](buttonurl://example.com)
[two](buttonurl://google.com:same)</code>
This will create two buttons on a single line, instead of one button per line.
Keep in mind that your message <b>MUST</b> contain some text other than just a button!
"""

wibu = "HachiBot"
telegraph = Telegraph()
data = telegraph.create_account(short_name=wibu)
auth_url = data["auth_url"]
TMP_DOWNLOAD_DIRECTORY = "./"


@register(pattern="^/cancel(?: |$)(.*)")
async def cancel_handle(message, state, **kwargs):
    state='*',
    allow_kwargs=True
    await state.finish()
    await message.reply('Cancelled.')


@user_admin
def echo(update, _):
    args = update.effective_message.text.split(None, 1)
    message = update.effective_message

    if message.reply_to_message:
        message.reply_to_message.reply_text(
            args[1], parse_mode=ParseMode.MARKDOWN, disable_web_page_preview=True
        )
    else:
        message.reply_text(
            args[1],
            quote=False,
            parse_mode=ParseMode.MARKDOWN,
            disable_web_page_preview=True,
        )
    message.delete()


def markdown_help_sender(update: Update):
    update.effective_message.reply_text(MARKDOWN_HELP, parse_mode=ParseMode.HTML)
    update.effective_message.reply_text(
        "Try forwarding the following message to me, and you'll see, and Use #test!",
    )
    update.effective_message.reply_text(
        "/save test This is a markdown test. _italics_, *bold*, code, "
        "[URL](example.com) [button](buttonurl:github.com) "
        "[button2](buttonurl://google.com:same)",
    )


def repo(update: Update, context: CallbackContext):
    message = update.effective_message
    text = message.text[len('/repo '):]
    usr = get(f'https://api.github.com/users/{text}/repos?per_page=40').json()
    reply_text = "*Repo*\n"
    for i in range(len(usr)):
        reply_text += f"[{usr[i]['name']}]({usr[i]['html_url']})\n"
    message.reply_text(reply_text,
                       parse_mode=ParseMode.MARKDOWN,
                       disable_web_page_preview=True)


def gdpr(update: Update, context: CallbackContext):
    update.effective_message.reply_text(
        (update.effective_chat.id, "Deleting identifiable data..."))
    for mod in GDPR:
        mod.__gdpr__(update.effective_user.id)

    update.effective_message.reply_text("GDPR is done",
                                        parse_mode=ParseMode.MARKDOWN)


def reply_keyboard_remove(update: Update, context: CallbackContext):
    reply_keyboard = []
    reply_keyboard.append([ReplyKeyboardRemove(remove_keyboard=True)])
    reply_markup = ReplyKeyboardRemove(remove_keyboard=True)
    old_message = context.bot.send_message(
        chat_id=update.message.chat_id,
        text='trying',  # This text will not get translated
        reply_markup=reply_markup,
        reply_to_message_id=update.message.message_id)
    context.bot.delete_message(chat_id=update.message.chat_id,
                               message_id=old_message.message_id)


@send_action(ChatAction.UPLOAD_PHOTO)
def rmemes(update, context):
    msg = update.effective_message
    chat = update.effective_chat

    SUBREDS = [
        "meirl",
        "dankmemes",
        "AdviceAnimals",
        "memes",
        "meme",
        "memes_of_the_dank",
        "PornhubComments",
        "teenagers",
        "memesIRL",
        "insanepeoplefacebook",
        "terriblefacebookmemes",
    ]

    subreddit = random.choice(SUBREDS)
    res = r.get(f"https://meme-api.herokuapp.com/gimme/{subreddit}")

    if res.status_code != 200:  # Like if api is down?
        msg.reply_text("Sorry some error occurred :(")
        return
    res = res.json()

    rpage = res.get(str("subreddit"))  # Subreddit
    title = res.get(str("title"))  # Post title
    memeu = res.get(str("url"))  # meme pic url
    plink = res.get(str("postLink"))

    caps = f"× <b>Title</b>: {title}\n"
    caps += f"× <b>Subreddit:</b> <pre>r/{rpage}</pre>"

    keyb = [[InlineKeyboardButton(text="Subreddit Postlink 🔗", url=plink)]]
    try:
        context.bot.send_photo(
            chat.id,
            photo=memeu,
            caption=caps,
            reply_markup=InlineKeyboardMarkup(keyb),
            timeout=60,
            parse_mode=ParseMode.HTML,
        )

    except BadRequest as excp:
        return msg.reply_text(f"Error! {excp.message}")


def markdown_help(update: Update, context: CallbackContext):
    if update.effective_chat.type != "private":
        update.effective_message.reply_text(
            "Contact me in pm",
            reply_markup=InlineKeyboardMarkup(
                [
                    [
                        InlineKeyboardButton(
                            "Markdown help",
                            url=f"t.me/{context.bot.username}?start=markdownhelp",
                        ),
                    ],
                ],
            ),
        )
        return
    markdown_help_sender(update)


@typing_action
def get_bot_ip(update, context):
    """Sends the bot's IP address, so as to be able to ssh in if necessary.
    OWNER ONLY.
    """
    res = requests.get("http://ipinfo.io/ip")
    update.message.reply_text(res.text)


@typing_action
def system_status(update, context):
    uptime = datetime.datetime.fromtimestamp(boot_time()).strftime("%Y-%m-%d %H:%M:%S")
    status = "<b>======[ SYSTEM INFO ]======</b>\n\n"
    status += "<b>System uptime:</b> <code>" + str(uptime) + "</code>\n"

    uname = platform.uname()
    status += "<b>System:</b> <code>" + str(uname.system) + "</code>\n"
    status += "<b>Node name:</b> <code>" + str(uname.node) + "</code>\n"
    status += "<b>Release:</b> <code>" + str(uname.release) + "</code>\n"
    status += "<b>Version:</b> <code>" + str(uname.version) + "</code>\n"
    status += "<b>Machine:</b> <code>" + str(uname.machine) + "</code>\n"
    status += "<b>Processor:</b> <code>" + str(uname.processor) + "</code>\n\n"

    mem = virtual_memory()
    cpu = cpu_percent()
    disk = disk_usage("/")
    status += "<b>CPU usage:</b> <code>" + str(cpu) + " %</code>\n"
    status += "<b>Ram usage:</b> <code>" + str(mem[2]) + " %</code>\n"
    status += "<b>Storage used:</b> <code>" + str(disk[3]) + " %</code>\n\n"
    status += "<b>Python version:</b> <code>" + python_version() + "</code>\n"
    status += "<b>Library version:</b> <code>" + str(__version__) + "</code>\n"
    status += "<b>Spamwatch API:</b> <code>" + str(__sw__) + "</code>\n"
    context.bot.sendMessage(update.effective_chat.id, status, parse_mode=ParseMode.HTML)


@ddocmd(command="wiki")
@typing_action
def wiki(update, context):
    Shinano = re.split(pattern="wiki", string=update.effective_message.text)
    wikipedia.set_lang("id")
    if len(str(Shinano[1])) == 0:
        update.effective_message.reply_text(
            "Enter the keywords for searching to wikipedia!"
        )
    else:
        try:
            HachiBot = update.effective_message.reply_text(
                "Searching the keywords from wikipedia..."
            )
            keyboard = InlineKeyboardMarkup(
                [
                    [
                        InlineKeyboardButton(
                            text="More Information",
                            url=wikipedia.page(Shinano).url,
                        )
                    ]
                ]
            )
            context.bot.editMessageText(
                chat_id=update.effective_chat.id,
                message_id=HachiBot.message_id,
                text=wikipedia.summary(Shinano, sentences=10),
                reply_markup=keyboard,
            )
        except wikipedia.PageError as e:
            update.effective_message.reply_text(f"⚠ Error Detected: {e}")
        except BadRequest as et:
            update.effective_message.reply_text(f"⚠ Error Detected: {et}")
        except wikipedia.exceptions.DisambiguationError as eet:
            update.effective_message.reply_text(
                f"⚠ Error Detected\n\nThere are too many query! Express it more!\n\nPossible query result:\n\n{eet}"
            )


@ddocmd(command="ud")
@typing_action
def ud(update, context):
    msg = update.effective_message
    args = context.args
    text = " ".join(args).lower()
    if not text:
        msg.reply_text("Please enter keywords to search on ud!")
        return
    if text == "Arya":
        msg.reply_text("Arya is my owner so if you search him on urban dictionary you can't find the meaning because he is my husband and only me who know what's the meaning of Arya!")
        return
    try:
        results = get(f"http://api.urbandictionary.com/v0/define?term={text}").json()
        reply_text = f'Word: {text}\n\nDefinition: \n{results["list"][0]["definition"]}'
        reply_text += f'\n\nExample: \n{results["list"][0]["example"]}'
    except IndexError:
        reply_text = (
            f"Word: {text}\n\nResults: Sorry could not find any matching results!"
        )
    ignore_chars = "[]"
    reply = reply_text
    for chars in ignore_chars:
        reply = reply.replace(chars, "")
    if len(reply) >= 4096:
        reply = reply[:4096]  # max msg lenth of tg.
    try:
        msg.reply_text(reply)
    except BadRequest as err:
        msg.reply_text(f"Error! {err.message}")


@register(pattern="^/t(gm|gt) ?(.*)")
async def telegrap(event):
    optional_title = event.pattern_match.group(2)
    if event.reply_to_msg_id:
        start = datetime.now()
        reply_msg = await event.get_reply_message()
        input_str = event.pattern_match.group(1)
        if input_str == "gm":
            downloaded_file_name = await Client.download_media(
                reply_msg,
                TMP_DOWNLOAD_DIRECTORY
            )
            end = datetime.now()
            ms = (end - start).seconds
            if not downloaded_file_name:
                await Client.send_message(
                    event.chat_id,
                    "Not Supported Format Media!"
                )
                return
            else:
                if downloaded_file_name.endswith((".webp")):
                    resize_image(downloaded_file_name)
                try:
                    start = datetime.now()
                    media_urls = upload_file(downloaded_file_name)
                except exceptions.TelegraphException as exc:
                    await event.reply("ERROR: " + str(exc))
                    os.remove(downloaded_file_name)
                else:
                    end = datetime.now()
                    ms_two = (end - start).seconds
                    os.remove(downloaded_file_name)
                    await Client.send_message(
                        event.chat_id,
                        "Your telegraph link is complete uploaded!",
                        buttons=[
                            [
                                types.KeyboardButtonUrl(
                                    "Here Your Telegra.ph Link", "https://telegra.ph{}".format(media_urls[0], (ms + ms_two))
                                )
                            ]
                        ]
                    )
        elif input_str == "gt":
            user_object = await Client.get_entity(reply_msg.sender_id)
            title_of_page = user_object.first_name # + " " + user_object.last_name
            # apparently, all Users do not have last_name field
            if optional_title:
                title_of_page = optional_title
            page_content = reply_msg.message
            if reply_msg.media:
                if page_content != "":
                    title_of_page = page_content
                downloaded_file_name = await Client.download_media(
                    reply_msg,
                    TMP_DOWNLOAD_DIRECTORY
                )
                m_list = None
                with open(downloaded_file_name, "rb") as fd:
                    m_list = fd.readlines()
                for m in m_list:
                    page_content += m.decode("UTF-8") + "\n"
                os.remove(downloaded_file_name)
            page_content = page_content.replace("\n", "<br>")
            response = telegraph.create_page(
                title_of_page,
                html_content=page_content
            )
            end = datetime.now()
            ms = (end - start).seconds
            await Client.send_message(
                    event.chat_id,
                    "Your telegraph link is complete uploaded!",
                    buttons=[
                        [
                            types.KeyboardButtonUrl(
                                "Here Your Telegra.ph Link", "https://telegra.ph/{}".format(response["path"], ms)
                            )
                        ]
                    ]
                )
    else:
        await event.reply("Reply to a message to get a permanent telegra.ph link.")


def resize_image(image):
    im = Image.open(image)
    im.save(image, "PNG")

file_help = os.path.basename(__file__)
file_help = file_help.replace(".py", "")
file_helpo = file_help.replace("_", " ")


__help__ = """
Available commands:
*NOTE*
× /cancel*:* Use this command to stop features not working but still running 

*Markdown*:
× /markdownhelp: quick summary of how markdown works in telegram - can only be called in private chats

*Currency converter*:
× /cash: currency converter
Example:
× /cash 1 USD INR
     OR
× /cash 1 usd inr
» Output: 1.0 USD = 75.505 INR

*Translator*:
× /tr or /tl (language code) as reply to a long message
× /langs : lists all the language codes
Example:
 × /tr en: translates something to english
 × /tr hi-en: translates hindi to english.

*Quotly*:
× /q : To quote a message.
× /q <Number> : To quote more than 1 messages.
× /q r : to quote a message with it's reply

Compress And Decompress: 
× /zip*:* reply to a telegram file to compress it in .zip format
× /unzip*:* reply to a telegram file to decompress it from the .zip format

*Other Commands*:
*Paste*:
× /paste*:* Saves replied content to ezup and replies with a url
× /hpaste*:* Saves replied content to hastebin and replies with a url
× /spaste*:* Saves replied content to spacbin and replies with a url

*React*:
× /react*:* Reacts with a random reaction

*Urban Dictonary*:
× /ud <word>*:* Type the word or expression you want to search use

*Wikipedia*:
× /wiki <query>*:* wikipedia your query

*Wallpapers*:
× /wall <query>*:* get a wallpaper from alphacoders

*Text To Speech*:
× /tts <text>*:* Converts a text message to a voice message.

*Telegraph*:
× tgm*:* Upload media to telegraph
× tgt*:* Upload text to telegraph
"""

ECHO_HANDLER = DisableAbleCommandHandler(
    "echo", echo, filters=Filters.chat_type.groups, run_async=True
)
MD_HELP_HANDLER = CommandHandler("markdownhelp", markdown_help, run_async=True)
REDDIT_MEMES_HANDLER = DisableAbleCommandHandler("rmeme", rmemes, run_async=True)
IP_HANDLER = CommandHandler(
    "ip", get_bot_ip, filters=Filters.chat(OWNER_ID), run_async=True
)
SYS_STATUS_HANDLER = CommandHandler(
    "sysinfo", system_status, filters=CustomFilters.dev_filter, run_async=True
)
REPO_HANDLER = DisableAbleCommandHandler("repos",
                                         repo,
                                         pass_args=True,
                                         run_async=True,
                                         admin_ok=True)

GDPR_HANDLER = CommandHandler("gdpr",
                              gdpr,
                              run_async=True,
                              filters=Filters.chat_type.private)

dispatcher.add_handler(ECHO_HANDLER)
dispatcher.add_handler(MD_HELP_HANDLER)
dispatcher.add_handler(GDPR_HANDLER)
dispatcher.add_handler(REDDIT_MEMES_HANDLER)
dispatcher.add_handler(REPO_HANDLER)
dispatcher.add_handler(SYS_STATUS_HANDLER)
dispatcher.add_handler(IP_HANDLER)
dispatcher.add_handler(
    DisableAbleCommandHandler("removebotkeyboard", reply_keyboard_remove))

__mod_name__ = "Extras"
__command_list__ = ["id", "echo", "rmeme", "ip", "sysinfo", "repos"]
__handlers__ = [
    ECHO_HANDLER,
    MD_HELP_HANDLER,
    REDDIT_MEMES_HANDLER,
    IP_HANDLER,
    SYS_STATUS_HANDLER,
    REPO_HANDLER,
]