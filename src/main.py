import asyncio
from pathlib import Path
import tempfile
from types import FrameType
from typing import Optional, cast
import dotenv
import discord
import os
from utils import utils
from utils.Loggers import Loggers
from utils.utils import CONFIG, INTEGRATION_TYPES
import sys
import signal


dotenv.load_dotenv(".env")

# hooks

def exceptHook(excT: type[BaseException], exc: BaseException, traceback):
    Loggers.logger.exception(f"Exception catched in 'exceptHook' {exc}")

async def asyncSigIntHandler(sig: int, frame: Optional[FrameType]):
    Loggers.logger.info("--- Now exiting ---")
    
    try:
        Loggers.logger.info("Closing db connection")
        await CONFIG.storage.db.close()
        
        Loggers.logger.info("Closing discord connection")
        await bot.close() # we cannot use `asyncio.run(bot.close())` here,
                          # since "This event loop is already running"
    except Exception as e:
        Loggers.logger.exception(f"Caught an error while trying to exit: {e}")
        Loggers.logger.info("(async) Ignoring exception and now exiting")
    
    Loggers.logger.info("Exiting")
    sys.exit(0)

def sigIntHandler(sig: int, frame: Optional[FrameType]):
    Loggers.logger.debug("Entered `signal.SIGINT` hook")
    asyncio.set_event_loop(asyncio.new_event_loop())
    try:
        asyncio.create_task(asyncSigIntHandler(sig, frame))
    except Exception as e:
        Loggers.logger.exception(f"Error catched in 'sigIntHandler()' (sync): {e}")
        Loggers.logger.info("(sync) Ignoring exception and now exiting")
        sys.exit(0)
    

sys.excepthook = exceptHook
signal.signal(signal.SIGINT, sigIntHandler)



tempfile.tempdir = "../tempdir/"
Path(os.path.dirname(tempfile.tempdir)).mkdir(parents=True, exist_ok=True)


# bot

bot = discord.Bot()
"""bot.debug_guilds = [
    1316947105796984842
]"""

cogs_list: list[str] = [
    "mainBot",
    "permissions",
    "ai"
]

@bot.slash_command(
    name="reload-cogs",
    description="Reload all cogs.",
    integration_type=INTEGRATION_TYPES
)
async def reloadCogs(ctx: discord.ApplicationContext):
    if not CONFIG.isOwner(ctx.author.id):
        utils.logNoAuthorization(ctx, Loggers.logger, cmdname="/reload-cogs", reason="Isn't owner")
        await ctx.respond("No :3", ephemeral=True)
        return
    
    await ctx.respond("Reloading cogs", ephemeral=True)
    
    reloadedCogs: list[str] = []
    numCogsError = 0
    
    for cog in cogs_list:
        try:
            bot.reload_extension(f'cogs.{cog}')
            Loggers.logger.debug(f"Reloaded cog '{cog}'")
            
            reloadedCogs.append(cog)
        except Exception as e:
            numCogsError += 1
            Loggers.logger.exception(f"Error while trying to load cog {cog}: {e}")
            
            reloadedCogs.append(cog + " **(failed)**")
        
        if len(reloadedCogs) == len(cogs_list):
            if numCogsError:
                embedColour = discord.Colour.red()
            else:
                embedColour = discord.Colour.green()
            embedFooter = discord.EmbedFooter(f"Reloaded {len(reloadedCogs)} cogs ! {numCogsError} cogs failed to load !")
        else:
            embedColour = discord.Colour.orange()
            embedFooter = None
        
        embedDescription = "- " + "\n- ".join(reloadedCogs)
        
        await ctx.edit(embed=discord.Embed(
            title="Reloaded cogs :",
            description=embedDescription,
            colour=embedColour,
            footer=embedFooter
            ))

@bot.listen(once=True)
async def on_ready():
    Loggers.logger.info(f"Launched bot '{cast(discord.ClientUser, bot.user).name}'")

@bot.event
async def on_application_command_error(ctx: discord.ApplicationContext, error: discord.DiscordException):
    #await ctx.respond(embed=utils.createErrorEmbed(str(error)), ephemeral=True)
    Loggers.logger.exception(f"Handling exception from 'on_application_command_error' {error}")
    raise error

for cog in cogs_list:
    bot.load_extension(f'cogs.{cog}')
    Loggers.logger.debug(f"Loaded cog '{cog}'")


Loggers.logger.info("Checking if DB exists")
if CONFIG.storage.db.exists:
    Loggers.logger.info("Db exists !")
else:
    Loggers.logger.info("Db doesn't exists, it'll now get created")
    Loggers.logger.info("Initializing db")
    try:
        asyncio.run(CONFIG.storage.db.initDB())
    except Exception as e:
        Loggers.logger.exception(f"Error while trying to initialize db: {e}")
        Loggers.logger.info("Not continuing, exiting")
        sys.exit(1)
        

bot.activity = discord.Activity(type=discord.ActivityType.watching, name="geming turning into a transbian furry")
bot.run(os.getenv("TOKEN"))
