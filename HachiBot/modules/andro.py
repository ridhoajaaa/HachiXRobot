#    HachiBot (A telegram bot project)

#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.

#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.

#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <https://www.gnu.org/licenses/>.

import re

import rapidjson as json
from bs4 import BeautifulSoup
from HachiBot import pbot
from HachiBot.modules.tr_engine.strings import tld
from HachiBot.mwt import MWT
from hurry.filesize import size as sizee
from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup, Update
from requests import get
from yaml import Loader, load

# Greeting all bot owners that is using this module,
# v1 - RealAkito (used to be peaktogoo) [Original module Maker]
# have spent so much time of their life into making this module better, stable, and well more supports.
#
# v2 - Hitalo (@HitaloSama on GitHub) [Pyrogram Adapt]
# This module was entirely re-written in pyrogram for the HachiBot bot
# Some commands have been ported/adapted from other bots.
#
# Important credits:
# * The ofox command was originally developed by MrYacha.
# * The /twrp, /specs, /whatis, /variants, /samcheck and /samget
# commands were originally developed by KassemSYR.
#
# This module was inspired by Android Helper Bot by Vachounet.
# None of the code is taken from the bot itself, to avoid confusion.
# Please don't remove these comment, show respect to module contributors.

MIUI_FIRM = "https://raw.githubusercontent.com/XiaomiFirmwareUpdater/miui-updates-tracker/master/data/latest.yml"
REALME_FIRM = "https://raw.githubusercontent.com/RealmeUpdater/realme-updates-tracker/master/data/latest.yml"

fw_links = {"SAMMOBILE": "https://www.sammobile.com/samsung/firmware/{}/{}/",
            "SAMFW": "https://samfw.com/firmware/{}/{}/",
            "SAMFREW": "https://samfrew.com/model/{}/region/{}/",
            }.items()


@MWT(timeout=60 * 10)
class GetDevice:
    def __init__(self, device):
        """Get device info by codename or model!"""
        self.device = device

    def get(self):
        if self.device.lower().startswith('sm-'):
            data = get(
                'https://raw.githubusercontent.com/androidtrackers/certified-android-devices/master/by_model.json').content
            db = json.loads(data)
            try:
                name = db[self.device.upper()][0]['name']
                device = db[self.device.upper()][0]['device']
                brand = db[self.device.upper()][0]['brand']
                model = self.device.lower()
                return {'name': name,
                        'device': device,
                        'model': model,
                        'brand': brand
                        }
            except KeyError:
                return False
        else:
            data = get(
                'https://raw.githubusercontent.com/androidtrackers/certified-android-devices/master/by_device.json').content
            db = json.loads(data)
            newdevice = self.device.strip('lte').lower() if self.device.startswith(
                'beyond') else self.device.lower()
            try:
                name = db[newdevice][0]['name']
                model = db[newdevice][0]['model']
                brand = db[newdevice][0]['brand']
                device = self.device.lower()
                return {'name': name,
                        'device': device,
                        'model': model,
                        'brand': brand
                        }
            except KeyError:
                return False


@pbot.on_message(filters.command("miui"))
async def miui(c: Client, update: Update):
    if len(update.command) != 2:
        message = "Please write a codename, example: `/miui whyred`"
        await update.reply_text(message)
        return

    codename = update.command[1]

    yaml_data = load(get(MIUI_FIRM).content, Loader=Loader)
    data = [i for i in yaml_data if codename in i['codename']]

    if len(data) < 1:
        await update.reply_text("Provide a valid codename!")
        return

    for fw in data:
        av = fw['android']
        branch = fw['branch']
        method = fw['method']
        link = fw['link']
        fname = fw['name']
        version = fw['version']
        size = fw['size']
        date = fw['date']
        md5 = fw['md5']
        codename = fw['codename']

        btn = branch + ' | ' + method + ' | ' + version

        keyboard = [[InlineKeyboardButton(text=btn, url=link)]]

    text = f"**MIUI - Last build for {codename}:**"
    text += f"\n\n**Name:** `{fname}`"
    text += f"\n**Android:** `{av}`"
    text += f"\n**Size:** `{size}`"
    text += f"\n**Date:** `{date}`"
    text += f"\n**MD5:** `{md5}`"

    await update.reply_text(text,
                            reply_markup=InlineKeyboardMarkup(keyboard),
                            parse_mode="markdown")


@pbot.on_message(filters.command("realmeui"))
async def realmeui(c: Client, update: Update):
    if len(update.command) != 2:
        message = "Please write a codename, example: `/realmeui RMX2061`"
        await update.reply_text(message)
        return

    codename = update.command[1]

    yaml_data = load(get(REALME_FIRM).content, Loader=Loader)
    data = [i for i in yaml_data if codename in i['codename']]

    if len(data) < 1:
        await update.reply_text("Provide a valid codename!")
        return

    for fw in data:
        reg = fw['region']
        link = fw['download']
        device = fw['device']
        version = fw['version']
        cdn = fw['codename']
        sys = fw['system']
        size = fw['size']
        date = fw['date']
        md5 = fw['md5']

        btn = reg + ' | ' + version

        keyboard = [[InlineKeyboardButton(text=btn, url=link)]]

    text = f"**RealmeUI - Last build for {codename}:**"
    text += f"\n\n**Device:** `{device}`"
    text += f"\n**System:** `{sys}`"
    text += f"\n**Size:** `{size}`"
    text += f"\n**Date:** `{date}`"
    text += f"\n**MD5:** `{md5}`"

    await update.reply_text(text,
                            reply_markup=InlineKeyboardMarkup(keyboard),
                            parse_mode="markdown")


@pbot.on_message(filters.command("samspec"))
async def samspecs(c: Client, update: Update):
    if len(update.command) != 2:
        message = (
            "Please write your codename or model into it,\ni.e <code>/specs herolte</code> or <code>/specs sm-g610f</code>")
        await c.send_message(
            chat_id=update.chat.id,
            text=message)
        return
    device = update.command[1]
    data = GetDevice(device).get()
    if data:
        name = data['name']
        model = data['model']
        device = name.lower().replace(' ', '-')
    else:
        message = "coudn't find your device, chack device & try!"
        await c.send_message(
            chat_id=update.chat.id,
            text=message)
        return
    sfw = get(f'https://sfirmware.com/samsung-{model.lower()}/')
    if sfw.status_code == 200:
        page = BeautifulSoup(sfw.content, 'lxml')
        message = '<b>Device:</b> Samsung {}\n'.format(name)
        res = page.find_all('tr', {'class': 'mdata-group-val'})
        res = res[2:]
        for info in res:
            title = re.findall(r'<td>.*?</td>', str(info)
                               )[0].strip().replace('td', 'b')
            data = re.findall(r'<td>.*?</td>', str(info)
                              )[-1].strip().replace('td', 'code')
            message += "× {}: <code>{}</code>\n".format(title, data)

    else:
        message = "Device specs not found in bot database, make sure this is a Samsung device!"
        await c.send_message(
            chat_id=update.chat.id,
            text=message)
        return

    await c.send_message(
        chat_id=update.chat.id,
        text=message)


@pbot.on_message(filters.command(["whatis", "codename"]))
async def models(c: Client, update: Update):
    if len(update.command) != 2:
        message = "Please write your codename into it, i.e <code>/whatis herolte</code>"
        await c.send_message(
            chat_id=update.chat.id,
            text=message,
            disable_web_page_preview=True)
        return

    device = update.command[1]
    data = GetDevice(device).get()
    if data:
        name = data['name']
        device = data['device']
        brand = data['brand']
        model = data['model']
    else:
        message = "coudn't find your device, chack device & try!"
        await c.send_message(
            chat_id=update.chat.id,
            text=message)
        return

    message = f'<b>{device}/{model.upper()}</b> is <code>{brand} {name}</code>\n'
    await c.send_message(
        chat_id=update.chat.id,
        text=message,
        disable_web_page_preview=True)


@pbot.on_message(filters.command(["variants", "models"]))
async def variants(c: Client, update: Update):
    if len(update.command) != 2:
        message = "Please write your codename into it, i.e <code>/specs herolte</code>"
        await c.send_message(
            chat_id=update.chat.id,
            text=message)
        return

    device = update.command[1]
    data = GetDevice(device).get()
    if data:
        name = data['name']
        device = data['device']
    else:
        message = "coudn't find your device, chack device & try!"
        await c.send_message(
            chat_id=update.chat.id,
            text=message)
        return

    data = get(
        'https://raw.githubusercontent.com/androidtrackers/certified-android-devices/master/by_device.json').content
    db = json.loads(data)
    device = db[device]
    message = f'<b>{name}</b> variants:\n\n'

    for i in device:
        name = i['name']
        model = i['model']
        message += '<b>Model</b>: <code>{}</code> \n<b>Name:</b> <code>{}</code>\n\n'.format(
            model, name)

    await c.send_message(
        chat_id=update.chat.id,
        text=message)


@pbot.on_message(filters.command(["samget", "samcheck"]))
async def check(c: Client, update: Update):
    if len(update.command) != 3:
        message = "Please type your device <b>MODEL</b> and <b>CSC</b> into it!\ni.e <code>/fw SM-G975F XSG!</code>"
        await c.send_message(
            chat_id=update.chat.id,
            text=message)
        return

    cmd, temp, csc = update.command
    model = 'sm-' + temp if not temp.upper().startswith('SM-') else temp
    fota = get(
        f'http://fota-cloud-dn.ospserver.net/firmware/{csc.upper()}/{model.upper()}/version.xml')
    test = get(
        f'http://fota-cloud-dn.ospserver.net/firmware/{csc.upper()}/{model.upper()}/version.test.xml')
    if test.status_code != 200:
        message = f"Couldn't find any firmwares for {temp.upper()} - {csc.upper()}, please refine your search or try again later!"
        await c.send_message(
            chat_id=update.chat.id,
            text=message)
        return

    page1 = BeautifulSoup(fota.content, 'lxml')
    page2 = BeautifulSoup(test.content, 'lxml')
    os1 = page1.find("latest").get("o")
    os2 = page2.find("latest").get("o")
    if page1.find("latest").text.strip():
        pda1, csc1, phone1 = page1.find("latest").text.strip().split('/')
        message = f'<b>MODEL:</b> <code>{model.upper()}</code>\n<b>CSC:</b> <code>{csc.upper()}</code>\n\n'
        message += '<b>Latest Avaliable Firmware:</b>\n'
        message += f'× PDA: <code>{pda1}</code>\n× CSC: <code>{csc1}</code>\n'
        if phone1:
            message += f'× Phone: <code>{phone1}</code>\n'
        if os1:
            message += f'× Android: <code>{os1}</code>\n'
        message += '\n'
    else:
        message = f'<b>No public release found for {model.upper()} and {csc.upper()}.</b>\n\n'
    message += '<b>Latest Test Firmware:</b>\n'
    if len(page2.find("latest").text.strip().split('/')) == 3:
        pda2, csc2, phone2 = page2.find("latest").text.strip().split('/')
        message += f'× PDA: <code>{pda2}</code>\n× CSC: <code>{csc2}</code>\n'
        if phone2:
            message += f'× Phone: <code>{phone2}</code>\n'
        if os2:
            message += f'× Android: <code>{os2}</code>\n'
    else:
        md5 = page2.find("latest").text.strip()
        message += f'× Hash: <code>{md5}</code>\n× Android: <code>{os2}</code>\n\n'
    cmd.split()
    if cmd in ("samcheck"):
        await c.send_message(
            chat_id=update.chat.id,
            text=message)
    elif cmd in ("samget"):
        message += "\n**Download from below:**\n"
        keyboard = [
            [
                InlineKeyboardButton(
                    site_name, url=fw_link.format(model.upper(), csc.upper())
                )
            ]
            for site_name, fw_link in fw_links
        ]

        await c.send_message(
            chat_id=update.chat.id,
            text=message,
            reply_markup=InlineKeyboardMarkup(keyboard))


@pbot.on_message(filters.command("twrp"))
async def twrp(c: Client, update: Update):
    if not len(update.command) == 2:
        m = "Type the device codename, example: <code>/twrp j7xelte</code>"
        await c.send_message(
            chat_id=update.chat.id,
            text=m)
        return

    device = update.command[1]
    url = get(f'https://eu.dl.twrp.me/{device}/')
    if url.status_code == 404:
        m = "TWRP is not available for <code>{device}</code>"
        await c.send_message(
            chat_id=update.chat.id,
            text=m)
        return

    else:
        m = f'<b>Latest TWRP for {device}</b>\n'
        page = BeautifulSoup(url.content, 'lxml')
        date = page.find("em").text.strip()
        m += f'📅 <b>Updated:</b> <code>{date}</code>\n'
        trs = page.find('table').find_all('tr')
        row = 2 if trs[0].find('a').text.endswith('tar') else 1

        for i in range(row):
            download = trs[i].find('a')
            dl_link = f"https://dl.twrp.me{download['href']}"
            dl_file = download.text
            size = trs[i].find("span", {"class": "filesize"}).text
        m += f'📥 <b>Size:</b> <code>{size}</code>\n'
        m += f'📦 <b>File:</b> <code>{dl_file.lower()}</code>'
        keyboard = [[InlineKeyboardButton(
            text="Click here to download", url=dl_link)]]
        await c.send_message(
            chat_id=update.chat.id,
            text=m,
            reply_markup=InlineKeyboardMarkup(keyboard))


@pbot.on_message(filters.command(["evo", "evox"]))
async def evo(c: Client, update: Update):

    chat_id = update.chat.id,
    try:
        device = update.command[1]
    except Exception:
        device = ''

    if device == "example":
        reply_text = tld(chat_id, "err_example_device")
        await update.reply_text(reply_text, disable_web_page_preview=True)
        return

    if device == "x00t":
        device = "X00T"

    if device == "x01bd":
        device = "X01BD"

    if device == '':
        reply_text = tld(chat_id, "cmd_example").format("evo")
        await update.reply_text(reply_text, disable_web_page_preview=True)
        return

    fetch = get(
        f'https://raw.githubusercontent.com/Evolution-X-Devices/official_devices/master/builds/{device}.json'
    )

    if fetch.status_code in [500, 504, 505]:
        await update.reply_text(
            "HachiBot have been trying to connect to Github User Content, It seem like Github User Content is down"
        )
        return

    if fetch.status_code == 200:
        try:
            usr = json.loads(fetch.content)
            filename = usr['filename']
            url = usr['url']
            version = usr['version']
            maintainer = usr['maintainer']
            maintainer_url = usr['telegram_username']
            size_a = usr['size']
            size_b = sizee(int(size_a))

            reply_text = tld(chat_id, "download").format(filename, url)
            reply_text += tld(chat_id, "build_size").format(size_b)
            reply_text += tld(chat_id, "android_version").format(version)
            reply_text += tld(chat_id, "maintainer").format(
                f"[{maintainer}](https://t.me/{maintainer_url})")

            btn = tld(chat_id, "btn_dl")
            keyboard = [[InlineKeyboardButton(
                text=btn, url=url)]]
            await update.reply_text(reply_text, reply_markup=InlineKeyboardMarkup(keyboard), disable_web_page_preview=True)
            return

        except ValueError:
            reply_text = tld(chat_id, "err_json")
            await update.reply_text(reply_text, disable_web_page_preview=True)
            return

    elif fetch.status_code == 404:
        reply_text = tld(chat_id, "err_not_found")
        await update.reply_text(reply_text, disable_web_page_preview=True)
        return


@pbot.on_message(filters.command("pixys"))
async def pixys(c: Client, update: Update):

    chat_id = update.chat.id,
    try:
        device = update.command[1]
    except Exception:
        device = ''

    if device == '':
        reply_text = tld(chat_id, "cmd_example").format("pixys")
        await update.reply_text(reply_text, disable_web_page_preview=True)
        return

    fetch = get(
        f'https://raw.githubusercontent.com/PixysOS-Devices/official_devices/ten/{device}/build.json'
    )
    if fetch.status_code == 200:
        usr = fetch.json()
        response = usr['response'][0]
        filename = response['filename']
        url = response['url']
        buildsize_a = response['size']
        buildsize_b = sizee(int(buildsize_a))
        romtype = response['romtype']
        version = response['version']

        reply_text = tld(chat_id, "download").format(filename, url)
        reply_text += tld(chat_id, "build_size").format(buildsize_b)
        reply_text += tld(chat_id, "version").format(version)
        reply_text += tld(chat_id, "rom_type").format(romtype)

        keyboard = [[
            InlineKeyboardButton(text=tld(chat_id, "btn_dl"), url=f"{url}")
        ]]
        await update.reply_text(reply_text,
                                reply_markup=InlineKeyboardMarkup(keyboard),
                                parse_mode="markdown",
                                disable_web_page_preview=True)
        return

    elif fetch.status_code == 404:
        reply_text = tld(chat_id, "err_not_found")
    await update.reply_text(reply_text,
                            parse_mode="markdown",
                            disable_web_page_preview=True)


@pbot.on_message(filters.command("phhmagisk"))
async def phhmagisk(c: Client, update: Update):

    chat_id = update.chat.id

    fetch = get(
        "https://api.github.com/repos/expressluke/phh-magisk-builder/releases/latest"
    )
    usr = json.loads(fetch.content)
    reply_text = tld(chat_id, "phhmagisk_releases")
    for i in range(len(usr)):
        try:
            name = usr['assets'][i]['name']
            url = usr['assets'][i]['browser_download_url']
            tag = usr['tag_name']
            size_bytes = usr['assets'][i]['size']
            size = float("{:.2f}".format((size_bytes/1024)/1024))
            reply_text += f"**Tag:** `{tag}`\n"
            reply_text += f"**Size**: `{size} MB`\n\n"
            btn = tld(chat_id, "btn_dl")
            keyboard = [[InlineKeyboardButton(
                text=btn, url=url)]]
        except IndexError:
            continue
    await update.reply_text(reply_text,
                            reply_markup=InlineKeyboardMarkup(keyboard),
                            disable_web_page_preview=True)
    return


@pbot.on_message(filters.command("magisk"))
async def magisk(c: Client, update: Update):

    url = 'https://raw.githubusercontent.com/topjohnwu/magisk_files/'
    releases = '**Latest Magisk Releases:**\n'
    variant = ['master/stable', 'master/beta', 'canary/canary']
    for variants in variant:
        fetch = get(url + variants + '.json')
        data = json.loads(fetch.content)
        if variants == "master/stable":
            name = "**Stable**"
            cc = 0
            branch = "master"
        elif variants == "master/beta":
            name = "**Beta**"
            cc = 0
            branch = "master"
        elif variants == "canary/canary":
            name = "**Canary**"
            cc = 1
            branch = "canary"

        if variants == "canary/canary":
            releases += f'{name}: [ZIP v{data["magisk"]["version"]}]({url}{branch}/{data["magisk"]["link"]}) | ' \
                        f'[APK v{data["app"]["version"]}]({url}{branch}/{data["app"]["link"]}) | '
        else:
            releases += f'{name}: [ZIP v{data["magisk"]["version"]}]({data["magisk"]["link"]}) | ' \
                        f'[APK v{data["app"]["version"]}]({data["app"]["link"]}) | '

        if cc == 1:
            releases += f'[Uninstaller]({url}{branch}/{data["uninstaller"]["link"]}) | ' \
                        f'[Changelog]({url}{branch}/notes.md)\n'
        else:
            releases += f'[Uninstaller]({data["uninstaller"]["link"]})\n'

    await update.reply_text(releases, disable_web_page_preview=True)

