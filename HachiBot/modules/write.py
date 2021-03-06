# from ultroid
# © @greyyvbss
# ⚠️ Don't Remove Credits

import os

from PIL import Image, ImageDraw, ImageFont
from HachiBot.events import register
from HachiBot.utils.tools import edit_delete, edit_or_reply, text_set

@register(pattern="/write(?: |$)(.*)")
async def writer(event):
    if event.reply_to:
        reply = await event.get_reply_message()
        text = reply.message
    elif event.pattern_match.group(1).strip():
        text = event.text.split(maxsplit=1)[1]
    else:
        return await edit_delete(event, "Give some text")
    k = await edit_or_reply(event, "Processing ..")
    img = Image.open("HachiBot/resources/kertas.jpg")
    draw = ImageDraw.Draw(img)
    font = ImageFont.truetype("HachiBot/resources/assfont.ttf", 30)
    x, y = 150, 140
    lines = text_set(text)
    line_height = font.getsize("hg")[1]
    for line in lines:
        draw.text((x, y), line, fill=(1, 22, 55), font=font)
        y = y + line_height - 5
    file = "hachi.jpg"
    img.save(file)
    await event.reply(file=file)
    os.remove(file)
    await k.delete()
