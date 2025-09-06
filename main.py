import asyncio
from pathlib import Path
import tempfile
from typing import Final, Optional
import dotenv
import discord
import os
from ollama import AsyncClient
import ollama
import random
import utils

import logging.handlers
from config import Config

dotenv.load_dotenv(".env")
CONFIG: Final[Config] = Config("./config.json")

aiHandler = utils.Ai(systemPrompt=CONFIG.getRawSystemPrompt())

tempfile.tempdir = "./tempdir/"
Path(os.path.dirname(tempfile.tempdir)).mkdir(parents=True, exist_ok=True)

def createHandler(logPath: str, level: int, name: str = __name__):
    handler = logging.handlers.TimedRotatingFileHandler(Path(logPath) / f"{name}.log", "D", backupCount=30*3, encoding="utf-8") # we want to keep the logs for ~3 month
    handler.setFormatter(logging.Formatter("[%(asctime)s - %(levelname)s - %(name)s] %(message)s"))
    handler.setLevel(level)
    
    return handler

def getLogger(logPath: str, level: int, name: str = __name__) -> logging.Logger:
    Path(os.path.dirname(logPath)).mkdir(parents=True, exist_ok=True)
    
    logger: Final = logging.getLogger(name)
    logger.addHandler(createHandler(logPath, level, name))
    logger.setLevel(level)
    
    return logger

logger: Final[logging.Logger] = getLogger(CONFIG.getLogPath(), logging.DEBUG, "mainbot")
aiLogger: Final[logging.Logger] = getLogger(CONFIG.getLogPath(), logging.DEBUG, "AI")

isModelPreloaded = False

Context = discord.ApplicationContext
AutocompleteContext = discord.AutocompleteContext

def createErrorEmbed(description: Optional[str] = None):
    """Creates an error embed
    """
    
    username = os.getenv("USERNAME")
    if username and description:
        description = description.replace(username, "")
    
    return discord.Embed(
        title="Error !",
        description=description,
        colour=discord.Colour.red()
        )

bot = discord.Bot()
bot.debug_guilds = [1316947105796984842]

current_model: str = CONFIG.getDefaultModel() or "hermes3"

async def getModels(ctx: AutocompleteContext):
    models: list[str] = [model["model"] for model in ollama.list().model_dump()["models"]]
    return models

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

@bot.slash_command(name="set-model", description="Sets the current model to use for the ai")
@discord.option(
    name="model",
    input_type=str,
    autocomplete=getModels
)
async def setModel(ctx: Context, model: str):
    global current_model
    
    if not CONFIG.isTrusted(ctx.author.id):
        utils.logNoAuthorization(ctx, logger, name="/set-model", reason="Isn't trusted")
        await ctx.respond("No :3", ephemeral=True)
        return
    
    if model == current_model:
        await ctx.respond(f"`{model}` model is already in use !", ephemeral=True)
        return
    
    old_model = current_model
    current_model = model
    
    await ctx.respond(f"Sucessfully changed model from `{old_model}` to `{current_model}`")
    await utils.preloadModelAsync(model)
    
    await ctx.edit(content=f"Sucessfully changed model from `{old_model}` to `{current_model}`\n-# Preloaded model !")

@bot.slash_command(name="ai", description="Ask stuff to an ai model and get an answer in probably 7 minutes")
@discord.option(
    name="prompt",
    input_type=str,
    description="What to ask to the ai"
)
@discord.option(
    name="model",
    input_type=str,
    autocomplete=getModels,
    required=False,
    description="The model to use"
)
async def ai(ctx: Context, prompt: str, model: Optional[str]):
    if not CONFIG.isTrusted(ctx.author.id):
        utils.logNoAuthorization(ctx, logger, name="/ai", reason="Isn't trusted")
        await ctx.respond("No (not for the moment at least) :3", ephemeral=True)
        return
    
    if model == None: model = current_model
    
    await ctx.respond(f"Asking ai...\n-# using model `{model}`")
    
    if not isModelPreloaded:
        await utils.preloadModelAsync(model)
        await ctx.edit(content=f"Asking ai...\n-# using preloaded model `{model}`")
    
    try:
        if ctx.channel_id == None:
            ctx.edit(content="", embed=createErrorEmbed("The channel ID is equal to `None` (for some reason)"))
            return
        
        aiLogger.debug("Adding user's prompt to memory")
        
        userInfos = f"\nYou are talking to {ctx.author.name} (Discord userID: {ctx.author.id}, mention: {ctx.author.mention})"
        aiHandler.addMessage(utils.Ai.Role.USER, prompt + userInfos, ctx.channel_id)
        
        aiLogger.info(f"Asking prompt for user {ctx.author.name} ({ctx.author.id}):\n{prompt}")
        response = await AsyncClient().chat(model, messages=aiHandler.getMessagesWithPrompt(ctx.channel_id))
        content = response.message.content
        aiLogger.info(f"Got an answer for {ctx.author.name}'s prompt ({ctx.author.id}):\n{content}")
        if len(content or "") >= 2000:
            await ctx.edit(content="Output too long for discord 3:")
        else:
            await ctx.edit(content=content or "**[no response]**", allowed_mentions=discord.AllowedMentions.none())
            
        if content:
            aiLogger.debug("Adding ai's response to memory")
            aiHandler.addMessage(utils.Ai.Role.ASSISTANT, content, ctx.channel_id)
    except Exception as e:
        await ctx.edit(content="", embed=createErrorEmbed(f"({e.__class__.__name__}) {e}"))
        logger.exception(e)
        raise e

@bot.slash_command(name="reload-configs", description="Reload the config files")
async def reloadConfigs(ctx: Context):
    if not CONFIG.isOwner(ctx.author.id):
        utils.logNoAuthorization(ctx, logger, name="/reloadConfigs", reason="Isn't trusted")
        await ctx.respond("No :3", ephemeral=True)
        return
    
    logger.info("Reloading configs")
    CONFIG.loadConfigFile()
    await ctx.respond("Reloaded configs !", ephemeral=True)

@bot.slash_command(name="get-memory", description="Gets the ai's memory, if not channel is provided, we will get the memory if this channel")
@discord.option(
    name="channel",
    input_type=discord.abc.GuildChannel,
    description="The channel to check for",
    required=False
)
@discord.option(
    name="channel-id",
    input_type=str,
    description="The channel ID to check for",
    required=False
)
async def getAiMemory(ctx: Context, channel: Optional[discord.abc.GuildChannel], channel_id: Optional[str]):
    async def fromChannel(channelID: int):
        if aiHandler.messages.get(channelID):
            tmpfile = tempfile.TemporaryFile(delete_on_close=False)
            tmpfile.write(utils.formatAiMessages(aiHandler.messages.get(channelID, [])).encode())
            tmpfile.close()
            
            discordFile = discord.File(
                    tmpfile.name,
                    filename=f"output-{channelID}.txt",
                    description=f"The output of the AI's current memory of the channel id {channel_id}"
                    )
        
            await ctx.respond(f"AI memory from channel id `{channelID}` (<#{channelID}>):", file=discordFile, ephemeral=True)
            
            tmpfile._closer.cleanup()
        else:
            await ctx.respond(f"AI memory for `{channelID}` (<#{channelID}>) is empty !", ephemeral=True)
    
    if not CONFIG.isTrusted(ctx.author.id):
        utils.logNoAuthorization(ctx, logger, name="/get-memory", reason="Isn't trusted")
        await ctx.respond("No :3", ephemeral=True)
        return
    
    if channel and channel_id:
        await ctx.respond("Please only select either a channelID or a channel", ephemeral=True)
    
    if channel_id and not channel_id.isdigit():
        await ctx.respond("Please set the value of `channel_id` as an integer\n-# Channel IDs are too long for discord to be accepted as ints", ephemeral=True)
        return
    
    if channel:
        await fromChannel(channel.id)
    elif channel_id:
        await fromChannel(int(channel_id))
    else:
        await fromChannel(ctx.channel_id)

@bot.slash_command(name="flush", description="Flushes tjc's smart toilet :3")
async def flushAI(ctx: Context):
    if not CONFIG.isTrusted(ctx.author.id):
        utils.logNoAuthorization(ctx, logger, name="/flushAI", reason="Isn't trusted")
        await ctx.respond("No :3", ephemeral=True)
        return
    
    aiHandler.clearMemory()
    aiLogger.info("Flushed ai's memory")
    await ctx.respond("Flushed tjc's smart toilet !")
    
print(f"Launched bot !")
logger.info(f"Launched bot")
bot.run(os.getenv("TOKEN"))