from telethon import events
from os import getenv
from dotenv import load_dotenv
from telethon.sync import TelegramClient
import os
import asyncio
import ffmpeg
from FastTelethonhelper import fast_download, fast_upload
import logging
import subprocess
from HachiBot import telethn as bot

def subp(cmd):
  result = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
  f = open('log.txt', 'w')
  f.write(str(result))
  f.close()
  return result

def generate_thumbnail(in_filename):
    probe = ffmpeg.probe(in_filename)
    out_filename = f'{in_filename[:-3]}.jpg'
    cmd = ["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "default=noprint_wrappers=1:nokey=1", in_filename]
    time = float(subp(cmd).stdout.decode())
    time = time // 2
    width = probe['streams'][0]['width']
    try:
        (
          ffmpeg
          .input(in_filename, ss=time)
          .filter('scale', width, -1)
          .output(out_filename, vframes=1)
          .overwrite_output()
          .run(capture_stdout=True, capture_stderr=True)
        )
    except ffmpeg.Error as e:
        print(e.stderr.decode())
    return out_filename

def vidsticker(in_filename):
  out_filename =f'{in_filename[:-3]}_processed.webm'
  try:
    (
      ffmpeg.
      input(in_filename)
      .output(out_filename, vcodec='libvpx-vp9', crf=40, pix_fmt='yuva420p', vf='scale=512:-1')
      .global_args('-report')
      .run()
    )
  except ffmpeg.Error as e:
     print(e.stderr.decode())
  return out_filename
  
@bot.on(events.NewMessage(pattern=r'/convert'))
async def stickervid(event):
  video = await event.get_reply_message()
  if not video:
    return await event.reply("**Please reply to gift or video media!**")
  if video.file.duration > 500:
    return await event.reply('Should be smaller than 3 secs as per Telegram video-sticker guideline.')
  m = await event.reply('Downloading...')
  dl = await fast_download(bot, video)
  await m.edit('Encoding....')
  hek = vidsticker(dl)
  await m.edit('Uploading...')
  fu = await fast_upload(bot, hek)
  await bot.send_message(event.chat_id, file = fu, force_document=True)
  await m.delete()
  os.remove(dl)
  os.remove(hek)  

@bot.on(events.NewMessage(pattern=r'ffmpeg'))
async def ffmpegr(event):
  try:
    stcmd = event.text.split(' ')
  except IndexError:
    return await event.reply('Use as ffmpeg <cmd>')
  video = await event.get_reply_message()
  m = await event.reply('Downloading...')
  dl = await fast_download(bot, video)
  out = f'{dl[:-4]}_ffmpeg.{stcmd[-1]}'
  await m.edit('Encoding....')
  #cmd = f'ffmpeg -i {dl} {stcmd} {out}'
  stcmd.pop(0)
  stcmd.pop(-1)
  cmd = ['ffmpeg', '-i', dl]
  cmd.extend(stcmd)
  cmd.append('-y')
  cmd.append(f'{out}')
  await event.reply(" ".join(cmd))
  h = subp(cmd)
  #await event.reply(str(h))
  await m.edit('Uploading.....')
  await bot.send_message(event.chat_id, file=out, thumb=generate_thumbnail(dl))
  await m.delete()