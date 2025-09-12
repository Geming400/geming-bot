from pathlib import Path
import tempfile
from typing import cast
import dotenv
import discord
import os
from utils import utils
from utils.Loggers import Loggers
from utils.utils import CONFIG
import sys

def exceptHook(excT: type[BaseException], exc: BaseException, traceback):
    Loggers.logger.exception(exc)
    
sys.excepthook = exceptHook

dotenv.load_dotenv(".env")

tempfile.tempdir = "./tempdir/"
Path(os.path.dirname(tempfile.tempdir)).mkdir(parents=True, exist_ok=True)

bot = discord.Bot()
"""bot.debug_guilds = [
    1316947105796984842
]"""

cogs_list: list[str] = [
    "mainBot",
    "ai"
]

@bot.slash_command(name="reload-cogs", description="Reload all cogs.")
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

for cog in cogs_list:
    bot.load_extension(f'cogs.{cog}')
    Loggers.logger.debug(f"Loaded cog '{cog}'")

bot.activity = discord.Activity(type=discord.ActivityType.watching, name="geming turning into a transbian furry")
bot.run(os.getenv("TOKEN"))

