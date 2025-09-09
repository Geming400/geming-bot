import asyncio
from pathlib import Path
import tempfile
from typing import cast
import dotenv
import discord
import os
import random
import utils.utils as utils
from utils.utils import CONFIG
from utils.Loggers import Loggers

dotenv.load_dotenv(".env")

aiHandler = CONFIG.storage.aiHandler

tempfile.tempdir = "./tempdir/"
Path(os.path.dirname(tempfile.tempdir)).mkdir(parents=True, exist_ok=True)

Context = discord.ApplicationContext

bot = discord.Bot()
bot.debug_guilds = [
    1316947105796984842
]

current_model: str = CONFIG.getDefaultModel() or "hermes3"
    
@bot.slash_command(name="dyrs", description="Get dyrs' personnal infos ! (for free)")
async def dyrsInfos(ctx: Context):
    responses: tuple[str, ...] = (
        "Dyrs' real name is `Dylan`",
        "Dyrs is homosexual",
        "Dyrs is danish",
        "Dyrs is straight",
        "Dyrs is lesbian",
        "Dyrs is trans",
        "Dyrs is non-binary",
        "Dyrs is not a femboy",
        "Dyrs is not a furry",
        "Dyrs is geming's alt",
        "Dyrs real name is dyris",
        "Dyrs was taken by a silly furry catboy gay femboy called zazu :3 Mmmreeow >w<",
        "Dyris, she's real I think",
        "hello",
        "hello, I am here to speak the truth, geming is actually a gay furry femboy, he's just trying to hide from you all, share the truth...",
        "Dyrs is actually geming: proof, she's geming",
        "Dyrs' pronouns are `Any` so she can be called with any pronouns :trol:",
        "Dyrs... I remember yrou'er kissing boys",
        "Dyrs... I remember you're kissing boys",
        "Dyrs is a flowey", # idk what that means
        "Dyrs is homopho- oh wait, wrong person. sowwy dyrs 3:\nI'm really sowwy 33:\nHere's a hug >w< *hugs you*",
        "Dyrs hates being called nice person",
        "Dyrs hates being blushed",
        "Dyrs never wore thigh highs",
        "Dyrs did wear thigh highs with a trans flag on it"
    )
    
    if ctx.author.id == 1388940934598627372: # dyrs
        await ctx.respond(random.choice(responses) + "\n-# Hii dyrs :3333 Mrreeeow >w<")
    else:
        await ctx.respond(random.choice(responses))

@bot.slash_command(description="Why.")
@discord.option(
    "user",
    discord.User,
    description="Why..."
)
async def sex(ctx: Context, user: discord.User):
    await ctx.respond("https://cdn.discordapp.com/attachments/1268366668384440352/1372330251757027389/2025_23_49_53.gif?ex=68a98ee4&is=68a83d64&hm=85b8d19ac042233ff7ee14ced7e7abeed292cef893a58fa284a5624e7081f7aa&")

@bot.slash_command(name="linux-icbm", description="Linus torvalds' own ICBM, that's it")
@discord.option(
    "user",
    discord.User,
    description="The user to send the icmb to"
)
async def linux_icbm(ctx: Context, user: discord.User):
    await ctx.respond(f"Finding {user.mention}'s location...")
    await asyncio.sleep(5)
    await ctx.edit(content="Done! Sending linus torvalds ICBM...")
    await asyncio.sleep(3)
    await ctx.edit(content="https://cdn.discordapp.com/attachments/1268366668384440352/1372330251757027389/2025_23_49_53.gif?ex=68a98ee4&is=68a83d64&hm=85b8d19ac042233ff7ee14ced7e7abeed292cef893a58fa284a5624e7081f7aa&")

@bot.slash_command(name="reload-configs", description="Reload the config files")
async def reloadConfigs(ctx: Context):
    if not CONFIG.isOwner(ctx.author.id):
        utils.logNoAuthorization(ctx, Loggers.logger, name="/reloadConfigs", reason="Isn't trusted")
        await ctx.respond("No :3", ephemeral=True)
        return
    
    Loggers.logger.info(f"Reloading configs for user {ctx.author.name} ({ctx.author.id})")
    CONFIG.reloadConfigs()
    aiHandler.systemPrompt = CONFIG.getSystemPrompt()
    await ctx.respond("Reloaded configs !", ephemeral=True)

@bot.listen(once=True)
async def on_ready():
    Loggers.logger.info(f"Launched bot '{cast(discord.ClientUser, bot.user).name}'")

cogs_list = [
    'ai'
]

for cog in cogs_list:
    Loggers.logger.debug(f"Loaded cog '{cog}'")
    bot.load_extension(f'cogs.{cog}')

bot.run(os.getenv("TOKEN"))

