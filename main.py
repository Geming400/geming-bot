import asyncio
from pathlib import Path
import tempfile
from typing import Final, Optional, cast
import dotenv
import discord
import os
from ollama import AsyncClient
import ollama
import random
import utils
import psutil

import logging.handlers
from config import Config

dotenv.load_dotenv(".env")
CONFIG: Final[Config] = Config("./config.jsonc")

aiHandler = utils.Ai(systemPrompt=CONFIG.getSystemPrompt())

tempfile.tempdir = "./tempdir/"
Path(os.path.dirname(tempfile.tempdir)).mkdir(parents=True, exist_ok=True)

logger: Final[logging.Logger] = utils.getLogger(CONFIG.getLogPath(), logging.DEBUG, "mainbot")
aiLogger: Final[logging.Logger] = utils.getLogger(CONFIG.getLogPath(), logging.DEBUG, "AI")

aiPingReply = discord.AllowedMentions.none()
isModelPreloaded = False

Context = discord.ApplicationContext
AutocompleteContext = discord.AutocompleteContext

bot = discord.Bot()
bot.debug_guilds = [1316947105796984842]

current_model: str = CONFIG.getDefaultModel() or "hermes3"

async def getModels(ctx: AutocompleteContext):
    models: list[str] = [model["model"] for model in ollama.list().model_dump()["models"]]
    return models


# BOT COMMANDS

@bot.event
async def on_message(message: discord.Message):
    if bot.user in message.mentions:
        global isModelPreloaded, current_model
        
        async with message.channel.typing():
            try:
                if not isModelPreloaded:
                    utils.preloadModel(current_model)
                    isModelPreloaded = True
            
                aiLogger.debug("Adding user's prompt to memory")
                
                prompt = message.content.replace(cast(discord.ClientUser, bot.user).mention, "")
                
                aiHandler.addMessage(utils.Ai.Role.USER, prompt + aiHandler.getUserInfos(message.author), message.channel.id)
                
                aiLogger.info(f"Asking prompt for user {message.author.name} ({message.author.id}):\n{prompt}")
                response = await AsyncClient().chat(current_model, messages=aiHandler.getMessagesWithPrompt(message.channel.id), keep_alive=CONFIG.getKeepAlive())
                content = utils.removeThinkTag(response.message.content or "")
                
                aiLogger.info(f"Got an answer for {message.author.name}'s prompt ({message.author.id}) (prompt: '{message.content}'):\n{content}")
                
                if len(content or "") >= 2000:
                    tmpfile = tempfile.TemporaryFile(delete_on_close=False)
                    tmpfile.write(content.encode())
                    tmpfile.close()
                    
                    file = discord.File(
                        fp=tmpfile.name,
                        filename="output.txt",
                        description=f"The output of the AI ({current_model})"
                        )
                    await message.reply(content="", file=file)
                    
                    tmpfile._closer.cleanup()
                else:
                    await message.reply(content=content or "**[no response]**", allowed_mentions=aiPingReply)
                    
                if content:
                    aiLogger.debug("Adding ai's response to memory")
                    aiHandler.addMessage(utils.Ai.Role.ASSISTANT, content, message.channel.id)
            except ConnectionError:
                await message.reply(content="`ollama` isn't running, the ai isn't currently avalaible")
            except Exception as e:
                await message.reply(content="", embed=utils.createErrorEmbed(f"({e.__class__.__name__}) {e}"), allowed_mentions=discord.AllowedMentions.none())
                await message.add_reaction("⚠️")
                logger.exception(e)
                
                raise e
        
    
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
    global current_model, isModelPreloaded
    
    if not CONFIG.isTrusted(ctx.author.id):
        utils.logNoAuthorization(ctx, logger, name="/set-model", reason="Isn't trusted")
        await ctx.respond("No :3", ephemeral=True)
        return
    
    if model == current_model:
        await ctx.respond(f"`{model}` model is already in use !", ephemeral=True)
        return
    
    old_model = current_model
    current_model = model
    
    await ctx.respond(f"Sucessfully changed model from `{old_model}` to `{current_model}`\n-# Preloading model...")
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
    # if not CONFIG.isTrusted(ctx.author.id):
    #     utils.logNoAuthorization(ctx, logger, name="/ai", reason="Isn't trusted")
    #     await ctx.respond("No (not for the moment at least) :3", ephemeral=True)
    #     return
    
    if model == None: model = current_model
    
    await ctx.respond(f"Asking ai...\n-# using model `{model}`")
    
    global isModelPreloaded
    try:
        if not isModelPreloaded:
            utils.preloadModel(model)
            await ctx.edit(content=f"Asking ai...\n-# using preloaded model `{model}`")
            isModelPreloaded = True
    
        aiLogger.debug("Adding user's prompt to memory")
        
        aiHandler.addMessage(utils.Ai.Role.USER, prompt + aiHandler.getUserInfos(ctx.author), ctx.channel_id)
        
        aiLogger.info(f"Asking prompt for user {ctx.author.name} ({ctx.author.id}):\n{prompt}")
        response = await AsyncClient().chat(model, messages=aiHandler.getMessagesWithPrompt(ctx.channel_id), keep_alive=CONFIG.getKeepAlive())
        content = utils.removeThinkTag(response.message.content or "")
        aiLogger.info(f"Got an answer for {ctx.author.name}'s prompt ({ctx.author.id}) (prompt {prompt}):\n{content}")
        if len(content or "") >= 2000:
            tmpfile = tempfile.TemporaryFile(delete_on_close=False)
            tmpfile.write(content.encode())
            tmpfile.close()
            
            file = discord.File(
                fp=tmpfile.name,
                filename="output.txt",
                description=f"The output of the AI ({model})"
                )
            await ctx.edit(content="", file=file)
            
            tmpfile._closer.cleanup()
        else:
            await ctx.edit(content=content or "**[no response]**", allowed_mentions=aiPingReply)
            
        if content:
            aiLogger.debug("Adding ai's response to memory")
            aiHandler.addMessage(utils.Ai.Role.ASSISTANT, content, ctx.channel_id)
    except ConnectionError:
        ctx.edit(content="`ollama` isn't running, the ai isn't currently avalaible", ephemeral=True)
    except Exception as e:
        await ctx.edit(content="", embed=utils.createErrorEmbed(f"({e.__class__.__name__}) {e}"), allowed_mentions=discord.AllowedMentions.none())
        logger.exception(e)
        raise e

@bot.slash_command(name="reload-configs", description="Reload the config files")
async def reloadConfigs(ctx: Context):
    if not CONFIG.isOwner(ctx.author.id):
        utils.logNoAuthorization(ctx, logger, name="/reloadConfigs", reason="Isn't trusted")
        await ctx.respond("No :3", ephemeral=True)
        return
    
    logger.info(f"Reloading configs for user {ctx.author.name} ({ctx.author.id})")
    CONFIG.reloadConfigs()
    aiHandler.systemPrompt = CONFIG.getSystemPrompt()
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
            aiLogger.info(f"Sent ai memory for channelID `{channelID}` in channelID `{ctx.channel_id}` for user {ctx.author.name} ({ctx.author.id})")
            
            tmpfile._closer.cleanup()
        else:
            aiLogger.info(f"User {ctx.author.name} ({ctx.author.id}) tried getting ai memory for channelID `{channelID}` in channelID `{ctx.channel_id}`")
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

@bot.slash_command(name="ai-set-ping-reply", description="Enables or disables ping reply for the ai")
@discord.option(
    name="ping-reply",
    input_type=bool
)
async def aiSetPingReply(ctx: Context, ping_reply: bool):
    if not CONFIG.isOwner(ctx.author.id):
        utils.logNoAuthorization(ctx, logger, name="/reloadConfigs", reason="Isn't trusted")
        await ctx.respond("No :3", ephemeral=True)
        return
    
    global aiPingReply
    
    oldAiPingReply = aiPingReply
    aiLogger.info(f"Set ping reply to from `{oldAiPingReply}` to `{ping_reply}` for user {ctx.author.name} ({ctx.author.id})")
    
    if ping_reply:
        aiPingReply = discord.AllowedMentions.all()
    else:
        aiPingReply = discord.AllowedMentions.none()
    
    await ctx.respond(f"Set `ping-reply` from `{oldAiPingReply}` to `{ping_reply}`", ephemeral=True)
    

@bot.slash_command(name="flush", description="Flushes tjc's smart toilet :3")
async def flushAI(ctx: Context):
    # if not CONFIG.isTrusted(ctx.author.id):
    #     utils.logNoAuthorization(ctx, logger, name="/flushAI", reason="Isn't trusted")
    #     await ctx.respond("No :3", ephemeral=True)
    #     return
    
    aiHandler.clearMemory(ctx.channel_id)
    aiLogger.info(f"Flushed ai's memory for channel ID {ctx.channel_id} for user {ctx.author.name} ({ctx.author.id})")
    await ctx.respond("Flushed tjc's smart toilet !")
    
@bot.slash_command(name="global-flush", description="Flushes every human's smart toilet :3")
async def flushAIGlobally(ctx: Context):
    if not CONFIG.isOwner(ctx.author.id):
        utils.logNoAuthorization(ctx, logger, name="/flushAI", reason="Isn't trusted")
        await ctx.respond("No :3", ephemeral=True)
        return
    
    aiHandler.clearMemory()
    aiLogger.info(f"Flushed ai's globally memory for user {ctx.author.name} ({ctx.author.id})")
    await ctx.respond("Flushed every human's smart toilet !")

@bot.slash_command(name="ai-kill", description="Kill the AI processes")
async def killAI(ctx: Context):
    if not CONFIG.isOwner(ctx.author.id):
        utils.logNoAuthorization(ctx, logger, name="/ai-kill", reason="Isn't trusted")
        await ctx.respond("No :3", ephemeral=True)
        return

    aiLogger.info(f"Killing ai process for user {ctx.author.name} ({ctx.author.id})")

    for proc in psutil.process_iter():
        if proc.name() == "ollama.exe":
            if os.name == "posix":
                os.system("pkill ollama")
            else:
                os.system("taskkill /F /IM ollama.exe")
            
            await ctx.respond("Killed `ollama` process (if it was running)", ephemeral=True)
            return

@bot.slash_command(name="ai-system-prompt", description="Get the system prompt of geming bot")
async def fetchSystemPrompt(ctx: Context):
    if not CONFIG.isTrusted(ctx.author.id):
        utils.logNoAuthorization(ctx, logger, name="/ai-system-prompt", reason="Isn't trusted")
        await ctx.respond("No :3", ephemeral=True)
        return
    
    tmpfile = tempfile.TemporaryFile(delete_on_close=False)
    tmpfile.write(aiHandler.systemPrompt.encode())
    tmpfile.close()
    
    aiLogger.info(f"Getting system prompt for user {ctx.author.name} ({ctx.author.id})")
    
    file = discord.File(
        fp=tmpfile.name,
        filename="output.txt",
        description=f"The output of the AI ({current_model})"
        )
    
    await ctx.respond(
        content=f"The system prompt of {cast(discord.ClientUser, bot.user).mention} is:",
        file=file,
        ephemeral=True,
        allowed_mentions=discord.AllowedMentions.none()
        )

@bot.listen(once=True)
async def on_ready():
    logger.info(f"Launched bot '{cast(discord.ClientUser, bot.user).name}'")

bot.run(os.getenv("TOKEN"))

