import os
import time

import psutil

import HachiBot.modules.no_sql.users_db as users_db
from HachiBot import StartTime
from HachiBot.modules.helper_funcs import formatter

# Stats Module


async def bot_sys_stats():
    bot_uptime = int(time.time() - StartTime)
    cpu = psutil.cpu_percent()
    mem = psutil.virtual_memory().percent
    disk = psutil.disk_usage("/").percent
    process = psutil.Process(os.getpid())
    stats = f"""
ddox@yxdodd:~$ HachiBot:
------------------
HachiBot Pro Uptime: {formatter.get_readable_time((bot_uptime))}
Bot Capasity: {round(process.memory_info()[0] / 1024 ** 2)} MB
CPU Usage: {cpu}%
RAM Usage: {mem}%
Disk Usage: {disk}%
Users: {users_db.num_users()} users.
Groups: {users_db.num_chats()} groups.
"""

    return stats