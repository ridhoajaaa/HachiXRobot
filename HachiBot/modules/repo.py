import github
from pyrogram import filters
from HachiBot import pbot as app
from platform import python_version as y
from telegram import __version__ as o
from pyrogram import __version__ as z
from telethon import __version__ as s
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton
from pyrogram import filters


HACHI = "https://telegra.ph/file/6ceb68d63031d9b041c99.jpg"


@app.on_message(filters.command("repo") & ~filters.edited)
async def give_repo(c, m):
    g = github.Github()
    list_of_users = ""
    count = 0
    repo = g.get_repo("ridhoajaaa/HachiXBot")
    for i in repo.get_contributors():
        count += 1
        list_of_users += f"•{count}. [{i.login}](https://github.com/{i.login})\n"
    await m.reply_photo(
        photo=HACHI,
        caption=f"""**Saya HachiXBot**

**✪ Owner repo : [ddodxy](https://t.me/ddodxy)**
**✪ Python Version :** `{y()}`
**✪ Library Version :** `{o}`
**✪ Telethon Version :** `{s}`

```----------------
| Collaborators |
----------------```
{list_of_users}
**Create your own with click button bellow.**
""",
        reply_markup=InlineKeyboardMarkup(
            [
                [
                    InlineKeyboardButton("Repo", url="https://xnxx.com"),
                ],
                [
                    InlineKeyboardButton("Support", url="https://t.me/demonszxx"),
                    InlineKeyboardButton("Update", url="https://t.me/hachixlog"),
                ],
            ]
        ),
    )


__mod_name__ = "REPO"
