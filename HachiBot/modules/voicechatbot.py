# Voics Chatbot Module Credits Pranav Ajay 🐰Github = Red-Aura 🐹 Telegram= @madepranav
# @lyciachatbot support Now
import os
import aiofiles
import aiohttp
from random import randint
from pyrogram import filters
from HachiBot import pbot as ewex


async def fetch(url):
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as resp:
            try:
                data = await resp.json()
            except:
                data = await resp.text()
    return data


async def ai_Hachi(url):
    ai_name = "HachiXBot.mp3"
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as resp:
            if resp.status == 200:
                f = await aiofiles.open(ai_name, mode="wb")
                await f.write(await resp.read())
                await f.close()
    return ai_name


@ewex.on_message(filters.command("voice"))
async def ewex(_, message):
    if len(message.command) < 2:
        await message.reply_text("Hachi AI Voice Chatbot")
        return
    text = message.text.split(None, 1)[1]
    ewex = text.replace(" ", "%20")
    m = await message.reply_text("Hachi Is Best...")
    try:
        L = await fetch(
            f"https://api.affiliateplus.xyz/api/chatbot?message={lycia}&botname=@idzeroid_bot&ownername=@IdzXartez&user=1"
        )
        chatbot = L["message"]
        VoiceAi = f"https://lyciavoice.herokuapp.com/lycia?text={chatbot}&lang=id"
        name = "HachiXBot"
    except Exception as e:
        await m.edit(str(e))
        return
    await m.edit("Made By @yxdodd...")
    HachiVoice = await ai_Hachi(VoiceAi)
    await m.edit("Appling...")
    await message.reply_audio(audio=HachiVoice, title=chatbot, performer=name)
    os.remove(HachiVoice)
    await m.delete()
