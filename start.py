#!/usr/bin/env python
# coding=utf-8
"""
Gipsy start functions
"""

import pkg_resources

# check python version
import sys
py_version = sys.version_info
if py_version.major != 3 or py_version.minor < 9:
    log.error("⚠️ Gipsy require Python 3.10 or more.", file=sys.stderr)
    sys.exit(1)

# Check modules
def check_libs():
    """Check if the required libraries are installed and can be imported"""
    with open("requirements.txt", 'r') as file:
        packages = pkg_resources.parse_requirements(file.readlines())
    try:
        pkg_resources.working_set.resolve(packages)
    except Exception as e:
        print(f"\n⛔ \u001b[41m\u001b[37;1m{type(e).__name__}\033[0m: \033[31m{e}\033[0m")
        print("\n⚠️ \033[33mPlease install all the required modules with the folliwing command:\033[1m\n\n      \u001b[47m\033[30mpip3 install -r requirements.txt\033[0m\n ")
        exit(1)
check_libs()


import os
import asyncio
import time
import setup
from utils import Gunibot
import argparse
import logging
import yaml
import discord
from LRFutils.color import Color
from LRFutils import log



# Check and dispatch the config to all plugins
from core import config
config.check()

# Getting global system list
global_systems = []
for system in os.listdir("./bot/utils/"):
    if os.path.isfile("./bot/utils/" + system) and system[-3:] == ".py":
        global_systems.append("bot.utils." + system[0:-3])

# Getting plugin list
plugins = []
for plugin in os.listdir("./plugins/"):
    if plugin[0] != "_":
        if os.path.isdir("./plugins/" + plugin):
            plugins.append(f"plugins.{plugin}.{plugin}")

def print_ascii_art():
    """
    Print GIPSY 2.0 ascii art
    """
    # Disable some pylints warning violations in this function
    # pylint: disable=anomalous-backslash-in-string
    # pylint: disable=trailing-whitespace
    print(
        f"""{Color.Blue}
      ___  ____  ____  ___  _  _        ___     ___  
     / __)(_  _)(  _ \/ __)( \/ )      (__ \   / _ \\ 
    ( (_-. _)(_  )___/\__ \ \  /        / _/  ( (_) )
     \___/(____)(__)  (___/ (__)       (____)()\___/ 

        {Color.NC}"""
    )


# ---------------#
#    M A I N    #
# ---------------#
def main():
    """
    Main function
    """

    # Creating client
    client = Gunibot(
        case_insensitive=True, status=discord.Status("online"), beta=False
    )

    # Writing logs + welcome message
    if not os.path.isdir("logs"):
        os.makedirs("logs")
    
    print(" ")
    log.info("▶️ Starting Gipsy...")

    # pylint: disable-next=anomalous-backslash-in-string
    print_ascii_art()

    # Loading extensions (global system + plugins)
    async def load(bot_client, global_system_list, plugin_list):
        loaded = 0
        failed = 0
        notloaded = ""
        for extension in global_system_list + plugin_list:
            try:
                await bot_client.load_extension(extension)
                loaded += 1
            except Exception:  # pylint: disable=broad-except
                log.error(f"Failed to load extension: {extension}")
                notloaded += "\n - " + extension
                failed += 1
        return loaded, failed

    # Printing info when the bot is started
    async def on_ready():
        """Called when the bot is connected to Discord API"""
        log.info(f"{Color.Green}✅ Bot connected")
        log.info("Nom : " + client.user.name)
        log.info("ID : " + str(client.user.id))
        if len(client.guilds) < 200:
            serveurs = [x.name for x in client.guilds]
            log.info("Connected on " + str(len(client.guilds)) + " servers:\n - " + "\n - ".join(serveurs))
        else:
            log.info("Connected on " + str(len(client.guilds)) + " servers")
        loaded, failed = await load(client, global_systems, plugins)
        log.info(f"{loaded} plugins loaded, {failed} plugins failed")
        print("--------------------------------------------------------------------------------")
        await asyncio.sleep(2)

    client.add_listener(on_ready)

    # Check if the bot must run in beta
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "-b", "--beta", help="Run with the beta bot token", action="store_true"
    )
    args = parser.parse_args()

    # Launch bot
    try: client.run(config.get("bot.token"))
    except discord.errors.LoginFailure:
        log.error("⚠️ Invalid token")
        setup.token_set(force_set=True)
        os.system("python3 start.py")
        exit()

if __name__ == "__main__":
    main()
