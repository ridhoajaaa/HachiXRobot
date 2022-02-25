import re

from jikanpy import Jikan
from jikanpy.exceptions import APIException
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, ParseMode, Update
from telegram.ext import CallbackContext, CallbackQueryHandler

from HachiBot import REDIS, dispatcher
from HachiBot.modules.disable import DisableAbleCommandHandler

jikan = Jikan()


def anime(update: Update, context: CallbackContext):
    msg = update.effective_message
    args = context.args
    query = " ".join(args)
    res = ""
    try:
        res = jikan.search("anime", query)
    except APIException:
        msg.reply_text("Error connecting to the API. Please try again!")
        return ""
    try:
        res = res.get("results")[0].get("mal_id")  # Grab first result
    except APIException:
        msg.reply_text("Error connecting to the API. Please try again!")
        return ""
    if res:
        anime = jikan.anime(res)
        title = anime.get("title")
        japanese = anime.get("title_japanese")
        type = anime.get("type")
        duration = anime.get("duration")
        synopsis = anime.get("synopsis")
        source = anime.get("source")
        status = anime.get("status")
        episodes = anime.get("episodes")
        score = anime.get("score")
        rating = anime.get("rating")
        genre_lst = anime.get("genres")
        genres = "".join(genre.get("name") + ", " for genre in genre_lst)
        genres = genres[:-2]
        studio_lst = anime.get("studios")
        studios = "".join(studio.get("name") + ", " for studio in studio_lst)
        studios = studios[:-2]
        duration = anime.get("duration")
        premiered = anime.get("premiered")
        image_url = anime.get("image_url")
        url = anime.get("url")
        trailer = anime.get("trailer_url")
    else:
        msg.reply_text("No results found!")
        return
    rep = f"<b>{title} ({japanese})</b>\n"
    rep += f"<b>Type:</b> <code>{type}</code>\n"
    rep += f"<b>Source:</b> <code>{source}</code>\n"
    rep += f"<b>Status:</b> <code>{status}</code>\n"
    rep += f"<b>Genres:</b> <code>{genres}</code>\n"
    rep += f"<b>Episodes:</b> <code>{episodes}</code>\n"
    rep += f"<b>Duration:</b> <code>{duration}</code>\n"
    rep += f"<b>Score:</b> <code>{score}</code>\n"
    rep += f"<b>Studio(s):</b> <code>{studios}</code>\n"
    rep += f"<b>Premiered:</b> <code>{premiered}</code>\n"
    rep += f"<b>Rating:</b> <code>{rating}</code>\n\n"
    rep += f"<a href='{image_url}'>\u200c</a>"
    rep += f"<i>{synopsis}</i>\n"
    if trailer:
        keyb = [
            [
                InlineKeyboardButton("More Information", url=url),
                InlineKeyboardButton("Trailer", url=trailer),
                InlineKeyboardButton(
                    "Add to Watchlist", callback_data=f"xanime_watchlist={title}"
                ),
            ]
        ]
    else:
        keyb = [
            [
                InlineKeyboardButton("More Information", url=url),
                InlineKeyboardButton(
                    "Add to Watchlist", callback_data=f"xanime_watchlist={title}"
                ),
            ]
        ]

    msg.reply_text(
        rep, parse_mode=ParseMode.HTML, reply_markup=InlineKeyboardMarkup(keyb)
    )


def character(update: Update, context: CallbackContext):
    msg = update.effective_message
    res = ""
    args = context.args
    query = " ".join(args)
    try:
        search = jikan.search("character", query).get("results")[0].get("mal_id")
    except APIException:
        msg.reply_text("No results found!")
        return ""
    if search:
        try:
            res = jikan.character(search)
        except APIException:
            msg.reply_text("Error connecting to the API. Please try again!")
            return ""
    if res:
        name = res.get("name")
        kanji = res.get("name_kanji")
        about = res.get("about")
        about = re.sub(r"\\n", r"\n", about)
        about = re.sub(r"\r\n", r"", about)
        if len(about) > 4096:
            about = about[:4000] + "..."
        image = res.get("image_url")
        url = res.get("url")
        rep = f"<b>{name} ({kanji})</b>\n\n"
        rep += f"<a href='{image}'>\u200c</a>"
        rep += f"<i>{about}</i>"
        keyb = [
            [
                InlineKeyboardButton("More Information", url=url),
                InlineKeyboardButton(
                    "Add to favorite character", callback_data=f"xanime_fvrtchar={name}"
                ),
            ]
        ]

        msg.reply_text(
            rep, parse_mode=ParseMode.HTML, reply_markup=InlineKeyboardMarkup(keyb)
        )


def upcoming(update: Update, context: CallbackContext):
    msg = update.effective_message
    rep = "<b>Upcoming anime</b>\n"
    later = jikan.season_later()
    anime = later.get("anime")
    for new in anime:
        name = new.get("title")
        url = new.get("url")
        rep += f"× <a href='{url}'>{name}</a>\n"
        if len(rep) > 2000:
            break
    msg.reply_text(rep, parse_mode=ParseMode.HTML, disable_web_page_preview=True)


def manga(update: Update, context: CallbackContext):
    msg = update.effective_message
    args = context.args
    query = " ".join(args)
    res = ""
    manga = ""
    try:
        res = jikan.search("manga", query).get("results")[0].get("mal_id")
    except APIException:
        msg.reply_text("Error connecting to the API. Please try again!")
        return ""
    if res:
        try:
            manga = jikan.manga(res)
        except APIException:
            msg.reply_text("Error connecting to the API. Please try again!")
            return ""
        title = manga.get("title")
        japanese = manga.get("title_japanese")
        type = manga.get("type")
        status = manga.get("status")
        score = manga.get("score")
        volumes = manga.get("volumes")
        chapters = manga.get("chapters")
        genre_lst = manga.get("genres")
        genres = "".join(genre.get("name") + ", " for genre in genre_lst)
        genres = genres[:-2]
        synopsis = manga.get("synopsis")
        image = manga.get("image_url")
        url = manga.get("url")
        rep = f"<b>{title} ({japanese})</b>\n"
        rep += f"<b>Type:</b> <code>{type}</code>\n"
        rep += f"<b>Status:</b> <code>{status}</code>\n"
        rep += f"<b>Genres:</b> <code>{genres}</code>\n"
        rep += f"<b>Score:</b> <code>{score}</code>\n"
        rep += f"<b>Volumes:</b> <code>{volumes}</code>\n"
        rep += f"<b>Chapters:</b> <code>{chapters}</code>\n\n"
        rep += f"<a href='{image}'>\u200c</a>"
        rep += f"<i>{synopsis}</i>"
        keyb = [
            [
                InlineKeyboardButton("More Information", url=url),
                InlineKeyboardButton(
                    "Add to Read list", callback_data=f"xanime_manga={title}"
                ),
            ]
        ]

        msg.reply_text(
            rep, parse_mode=ParseMode.HTML, reply_markup=InlineKeyboardMarkup(keyb)
        )


def animestuffs(update, context):
    query = update.callback_query
    user = update.effective_user
    splitter = query.data.split("=")
    query_match = splitter[0]
    callback_anime_data = splitter[1]
    if query_match == "xanime_watchlist":
        watchlist = list(REDIS.sunion(f"anime_watch_list{user.id}"))
        if callback_anime_data not in watchlist:
            REDIS.sadd(f"anime_watch_list{user.id}", callback_anime_data)
            context.bot.answer_callback_query(
                query.id,
                text=f"{callback_anime_data} is successfully added to your watch list.",
                show_alert=True,
            )
        else:
            context.bot.answer_callback_query(
                query.id,
                text=f"{callback_anime_data} already exists in your watch list!",
                show_alert=True,
            )

    elif query_match == "xanime_fvrtchar":
        fvrt_char = list(REDIS.sunion(f"anime_fvrtchar{user.id}"))
        if callback_anime_data not in fvrt_char:
            REDIS.sadd(f"anime_fvrtchar{user.id}", callback_anime_data)
            context.bot.answer_callback_query(
                query.id,
                text=f"{callback_anime_data} is successfully added to your favorite character.",
                show_alert=True,
            )
        else:
            context.bot.answer_callback_query(
                query.id,
                text=f"{callback_anime_data} already exists in your favorite characters list!",
                show_alert=True,
            )
    elif query_match == "xanime_manga":
        fvrt_char = list(REDIS.sunion(f"anime_mangaread{user.id}"))
        if callback_anime_data not in fvrt_char:
            REDIS.sadd(f"anime_mangaread{user.id}", callback_anime_data)
            context.bot.answer_callback_query(
                query.id,
                text=f"{callback_anime_data} is successfully added to your read list.",
                show_alert=True,
            )
        else:
            context.bot.answer_callback_query(
                query.id,
                text=f"{callback_anime_data} already exists in your favorite read list!",
                show_alert=True,
            )


ANIME_STUFFS_HANDLER = CallbackQueryHandler(
    animestuffs, pattern="xanime_.*", run_async=True
)
ANIME_HANDLER = DisableAbleCommandHandler(
    "manime", anime, pass_args=True, run_async=True
)
CHARACTER_HANDLER = DisableAbleCommandHandler(
    "mcharacter", character, pass_args=True, run_async=True
)
UPCOMING_HANDLER = DisableAbleCommandHandler("mupcoming", upcoming, run_async=True)
MANGA_HANDLER = DisableAbleCommandHandler(
    "mmanga", manga, pass_args=True, run_async=True
)

dispatcher.add_handler(ANIME_STUFFS_HANDLER)
dispatcher.add_handler(ANIME_HANDLER)
dispatcher.add_handler(CHARACTER_HANDLER)
dispatcher.add_handler(UPCOMING_HANDLER)
dispatcher.add_handler(MANGA_HANDLER)
