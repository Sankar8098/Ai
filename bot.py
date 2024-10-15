# Don't Remove Credit @VJ_Botz
# Subscribe YouTube Channel For Amazing Bot @Tech_VJ
# Ask Doubt on telegram @KingVJ01

import sys
import glob
import importlib.util
import logging
import logging.config
import pytz
import asyncio
from pathlib import Path
from datetime import date, datetime
from aiohttp import web
from pyrogram import Client, idle 
from pyromod import listen
from database.ia_filterdb import Media
from database.users_chats_db import db
from info import *
from utils import temp
from typing import Union, Optional, AsyncGenerator
from Script import script
from plugins import web_server
from TechVJ.bot import TechVJBot
from TechVJ.util.keepalive import ping_server
from TechVJ.bot.clients import initialize_clients

# Get logging configurations
logging.config.fileConfig('logging.conf')
logging.getLogger().setLevel(logging.INFO)
logging.getLogger("pyrogram").setLevel(logging.ERROR)
logging.getLogger("imdbpy").setLevel(logging.ERROR)
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logging.getLogger("aiohttp").setLevel(logging.ERROR)
logging.getLogger("aiohttp.web").setLevel(logging.ERROR)

# Define the path to plugins and start the bot
ppath = "plugins/*.py"
files = glob.glob(ppath)
TechVJBot.start()
loop = asyncio.get_event_loop()

async def start():
    print('\nInitializing Your Bot\n')
    bot_info = await TechVJBot.get_me()
    await initialize_clients()

    # Load plugins dynamically
    for name in files:
        with open(name) as a:
            patt = Path(a.name)
            plugin_name = patt.stem  # Using stem will remove .py automatically
            plugins_dir = Path(f"plugins/{plugin_name}.py")
            import_path = f"plugins.{plugin_name}"
            spec = importlib.util.spec_from_file_location(import_path, plugins_dir)
            load = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(load)
            sys.modules[import_path] = load
            print(f"Tech VJ Imported => {plugin_name}")

    # Start background tasks if running on Heroku
    if ON_HEROKU:
        asyncio.create_task(ping_server())

    # Fetch banned users and chats from the database
    b_users, b_chats = await db.get_banned()
    temp.BANNED_USERS = b_users
    temp.BANNED_CHATS = b_chats
    await Media.ensure_indexes()

    # Set bot details in temp
    me = await TechVJBot.get_me()
    temp.ME = me.id
    temp.U_NAME = me.username
    temp.B_NAME = me.first_name

    # Log the startup messages and bot info
    logging.info(LOG_STR)
    logging.info(script.LOGO)

    # Timezone and logging
    tz = pytz.timezone('Asia/Kolkata')
    today = date.today()
    now = datetime.now(tz)
    time = now.strftime("%H:%M:%S %p")

    # Notify about the restart in the log channel
    await TechVJBot.send_message(
        chat_id=LOG_CHANNEL, 
        text=script.RESTART_TXT.format(today, time)
    )

    # Start the web server
    app = web.AppRunner(await web_server())
    await app.setup()
    bind_address = "0.0.0.0"
    await web.TCPSite(app, bind_address, PORT).start()
    await idle()

if __name__ == '__main__':
    try:
        loop.run_until_complete(start())
    except KeyboardInterrupt:
        logging.info('Service Stopped Bye 👋')
            
