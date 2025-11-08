import os
from typing import Optional, cast
import discord
from discord.ext import commands
import tempfile

from ollama import AsyncClient
import psutil
from utils.db import Profiles
import utils.utils as utils
from utils.Loggers import Loggers
from utils.AiHandler import AiHandler
from utils.utils import CONFIG, INTEGRATION_TYPES


Context = discord.ApplicationContext

aiHandler = CONFIG.storage.aiHandler


# HOST: Final[Optional[str]] = CONFIG.getAiHost()

class AiUtils(commands.Cog):
    def __init__(self, bot: discord.Bot):
        self.bot = bot
    
    async def getModels(self, ctx: discord.AutocompleteContext) -> list[str]:
        if await CONFIG.storage.aiHandler.isOllamaRunningAsync(CONFIG.getAiHost()):
            return await CONFIG.storage.aiHandler.getModelsAsync(CONFIG.getAiHost())
        return ["❌ OLLAMA ISN'T UP, NO MODELS AVAILABLE"]

    @discord.slash_command(
        name="ai-set-ping-reply",
        description="Enables or disables ping reply for the ai",
        integration_type=INTEGRATION_TYPES
    )
    @discord.option(
        name="ping-reply",
        input_type=bool
    )
    async def aiSetPingReply(self, ctx: Context, ping_reply: bool):
        if not CONFIG.isOwner(ctx.author.id):
            utils.logNoAuthorization(ctx, Loggers.logger, cmdname="/ai-set-ping-reply", reason="Isn't owner")
            await ctx.respond("No :3", ephemeral=True)
            return
        
        oldAiPingReply = CONFIG.storage.aiPingReply == discord.AllowedMentions.all()
        Loggers.aiLogger.info(f"Set ping reply to from `{oldAiPingReply}` to `{ping_reply}` for user {ctx.author.name} ({ctx.author.id})")
        
        if ping_reply:
            CONFIG.storage.aiPingReply = discord.AllowedMentions.all()
        else:
            CONFIG.storage.aiPingReply = discord.AllowedMentions.none()
        
        await ctx.respond(f"Set `ping-reply` from `{oldAiPingReply}` to `{ping_reply}`", ephemeral=True)
    
    @discord.slash_command(
        name="set-model",
        description="Sets the current model to use for the ai",
        integration_type=INTEGRATION_TYPES
    )
    @discord.option(
        name="model",
        input_type=str,
        autocomplete=getModels
    )
    async def setModel(self, ctx: Context, model: str):
        if not CONFIG.isTrusted(ctx.author.id):
            utils.logNoAuthorization(ctx, Loggers.logger, cmdname="/set-model", reason="Isn't trusted")
            await ctx.respond("No :3", ephemeral=True)
            return
        
        if not model in await CONFIG.storage.aiHandler.getModelsAsync(CONFIG.getAiHost()):
            await ctx.respond(f"`{model}` model is not a valid model !", ephemeral=True)
            return 
        
        if model == CONFIG.storage.currentModel:
            await ctx.respond(f"`{model}` model is already in use !", ephemeral=True)
            return
        
        old_model = CONFIG.storage.currentModel
        CONFIG.storage.currentModel = model
        
        if await aiHandler.isModelPreloaded(model, CONFIG.getAiHost()):
            await ctx.respond(f"Sucessfully changed model from `{old_model}` to `{CONFIG.storage.currentModel}`")
            return
            
        await ctx.respond(f"Sucessfully changed model from `{old_model}` to `{CONFIG.storage.currentModel}`\n-# Preloading model...")
        await utils.preloadModelAsync(model, CONFIG.getAiHost())
        
        await ctx.edit(content=f"Sucessfully changed model from `{old_model}` to `{CONFIG.storage.currentModel}`\n-# Preloaded model !")
    
    @discord.slash_command(
        name="ai-system-prompt",
        description="Get the system prompt of geming bot",
        integration_type=INTEGRATION_TYPES
    )
    async def fetchSystemPrompt(self, ctx: Context):
        if not CONFIG.isTrusted(ctx.author.id):
            utils.logNoAuthorization(ctx, Loggers.logger, cmdname="/ai-system-prompt", reason="Isn't trusted")
            await ctx.respond("No :3", ephemeral=True)
            return
        
        Loggers.aiLogger.info(f"Getting system prompt for user {ctx.author.name} ({ctx.author.id})")
        
        file = discord.File(
            fp=CONFIG.getSystemPromptPath(),
            filename="output.txt",
            description=f"The system prompt of geming bot"
        )
        
        await ctx.respond(
            content=f"The system prompt of {cast(discord.ClientUser, self.bot.user).mention} is:",
            file=file,
            ephemeral=True,
            allowed_mentions=discord.AllowedMentions.none()
        )
    
    @discord.slash_command(
        name="get-memory",
        description="Gets the ai's memory, if no channel is provided, we'll get the memory if this channel",
        integration_type=INTEGRATION_TYPES
        )
    @discord.option(
        name="channel",
        input_type=discord.TextChannel,
        description="The channel to check for",
        required=False
    )
    @discord.option(
        name="channel-id",
        input_type=str,
        description="The channel ID to check for",
        required=False
    )
    async def getAiMemory(self, ctx: Context, channel: Optional[discord.TextChannel], channel_id: Optional[str]):
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
                Loggers.aiLogger.info(f"Sent ai memory for channelID `{channelID}` in channelID `{ctx.channel_id}` for user {ctx.author.name} ({ctx.author.id})")
                
                tmpfile._closer.cleanup()
            else:
                Loggers.aiLogger.info(f"User {ctx.author.name} ({ctx.author.id}) tried getting ai memory for channelID `{channelID}` in channelID `{ctx.channel_id}`")
                await ctx.respond(f"AI memory for `{channelID}` (<#{channelID}>) is empty !", ephemeral=True)
        
        
        if not CONFIG.isTrusted(ctx.author.id):
            utils.logNoAuthorization(ctx, Loggers.logger, cmdname="/get-memory", reason="Isn't trusted")
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
        

    @discord.slash_command(
        name="flush",
        description="Flushes tjc's smart toilet :3   (Clears the ai's memory)",
        integration_type=INTEGRATION_TYPES
    )
    async def flushAI(self, ctx: Context):
        # if not CONFIG.isTrusted(ctx.author.id):
        #     utils.logNoAuthorization(ctx, Loggers.logger, name="/flushAI", reason="Isn't trusted")
        #     await ctx.respond("No :3", ephemeral=True)
        #     return
        
        userProfile = await Profiles.UserProfile.createOrGet(ctx.author.id)
        if userProfile.aiBanned:
            Loggers.aiLogger.info(f"User {ctx.author.name} ({ctx.author.id}) is banned from using the AI, not continuing (from `/flush`)")
            await ctx.respond("You are banned from using `gemingbot`'s ai, therefore, you **cannot use this command** !", ephemeral=True)
            
            return
        
        aiHandler.clearMemory(ctx.channel_id)
        Loggers.aiLogger.info(f"Flushed ai's memory for channel ID {ctx.channel_id} for user {ctx.author.name} ({ctx.author.id})")
        await ctx.respond("Flushed tjc's smart toilet !")
        
    @discord.slash_command(
        name="global-flush",
        description="Flushes every human's smart toilet :3   (Clears the ai's memory on every channels)",
        integration_type=INTEGRATION_TYPES
    )
    async def flushAIGlobally(self, ctx: Context):
        if not CONFIG.isOwner(ctx.author.id):
            utils.logNoAuthorization(ctx, Loggers.logger, cmdname="/global-flush", reason="Isn't owner")
            await ctx.respond("No :3", ephemeral=True)
            return
        
        aiHandler.clearMemory()
        Loggers.aiLogger.info(f"Flushed ai's globally memory for user {ctx.author.name} ({ctx.author.id})")
        await ctx.respond("Flushed every human's smart toilet !")

    @discord.slash_command(
        name="ai-kill",
        description="Kill the AI processes",
        integration_type=INTEGRATION_TYPES
    )
    async def killAI(self, ctx: Context):
        if not CONFIG.isOwner(ctx.author.id):
            utils.logNoAuthorization(ctx, Loggers.logger, cmdname="/ai-kill", reason="Isn't owner")
            await ctx.respond("No :3", ephemeral=True)
            return

        Loggers.aiLogger.info(f"Killing ai process for user {ctx.author.name} ({ctx.author.id})")

        for proc in psutil.process_iter():
            if proc.name() == "ollama.exe":
                if os.name == "posix":
                    os.system("pkill ollama")
                else:
                    os.system("taskkill /F /IM ollama.exe") # for some reason, it only kills the running ai, not `ollama.exe`
                
                await ctx.respond("Killed `ollama` process (if it was running)", ephemeral=True)
                return
        await ctx.respond("The `ollama` process wasn't running", ephemeral=True)
        
class BotAI(commands.Cog):
    def __init__(self, bot: discord.Bot):
        self.bot = bot
    
    @staticmethod
    async def sendReaction(message: discord.Message, reaction: str):
        try:
            await message.add_reaction(reaction)
        except discord.errors.Forbidden: # cannot react
            ...
    
    @staticmethod
    async def removeReaction(message: discord.Message, reaction: str, user: discord.abc.Snowflake):
        try:
            await message.remove_reaction(reaction, user)
        except discord.errors.Forbidden: # cannot react
            ...
    
    @commands.Cog.listener(name="on_message")
    async def aiOnPing(self, message: discord.Message):
        if self.bot.user in message.mentions:
            channelID = message.channel.id
            
            # If we don't send any messages it's to prevent flooding the current chat
            # as we cannot send ephemeral messages with `discord.Message.reply()`
            if isinstance(message.author, discord.Member):
                guildID = cast(discord.Guild, message.guild).id
                guildPerms = await Profiles.getGuildPermissionProfile(guildID)
                
                guildProfile = await Profiles.GuildProfile.createOrGet(guildID)
                if message.author.id in guildProfile.bannedAiUsers:
                    Loggers.aiLogger.info(f"User {message.author.name} ({message.author.id}) is banned from using the AI in the guild {cast(discord.Guild, message.guild).name} ({guildID}), not continuing (from `/ai`)")
                    await message.reply("You are banned from using `gemingbot`'s ai, therefore, you **cannot use this command** ! (server-specific)")
                    
                    return
                
                # bypass for the bot owner / server administrators
                if not (message.author.guild_permissions.administrator or message.author.id == CONFIG.getOwner()):
                    if not guildPerms.isAiEnabledGlobally():
                        Loggers.aiLogger.info(f"AI is not enabled in server {guildID}, not continuing")
                        # await message.reply(content="Sorry, but geming bot's ai has **been disabled on this server** !", ephemeral=True)
                        # await message.add_reaction("❌")
                        return
                    
                    if not guildPerms.isChannelAuthorized(channelID):
                        Loggers.aiLogger.info(f"AI is not enabled in channel {channelID}, not continuing")
                        # await message.reply("Sorry, but geming bot's ai is **not enabled on this channel** !", ephemeral=True)
                        # await message.add_reaction("❌")
                        return
                    
                userProfile = await Profiles.UserProfile.createOrGet(message.author.id)
                if userProfile.aiBanned:
                    Loggers.aiLogger.info(f"User {message.author.name} ({message.author.id}) is banned from using the AI, not continuing (from pinging gemingbot)")
                    await message.add_reaction("❌")
                    
                    return
            
            Loggers.aiLogger.info("Checking if ollama is up")
            if not await CONFIG.storage.aiHandler.isOllamaRunningAsync(CONFIG.getAiHost()):
                Loggers.aiLogger.info(f"User {message.author.name} ({message.author.id}) tried using the ai, but it is unavailable")
                await message.add_reaction("⚠️")
                # This is really annoying, disabling
                # await message.reply(content="`ollama` isn't running, the ai isn't currently available")
                
                return
            
            async with message.channel.typing():
                try:
                    # if not await aiHandler.isModelPreloaded(CONFIG.storage.currentModel, CONFIG.getAiHost()):
                    #     # await message.add_reaction("<:preloading_model:1419412009212051456>")
                    #     await BotAI.sendReaction(message, "<:preloading_model:1419412009212051456>")
                    #     await utils.preloadModelAsync(CONFIG.storage.currentModel, CONFIG.getAiHost())
                    #     # await message.remove_reaction("<:preloading_model:1419412009212051456>", cast(discord.ClientUser, self.bot.user))
                    #     await BotAI.removeReaction(message, "<:preloading_model:1419412009212051456>", cast(discord.ClientUser, self.bot.user))
                
                    Loggers.aiLogger.debug("Adding user's prompt to memory")
                    
                    prompt = message.content.replace(cast(discord.ClientUser, self.bot.user).mention, "")
                    
                    aiHandler.addMessage(AiHandler.Role.USER, prompt + aiHandler.getUserInfos(message.author), message.channel.id)
                    
                    Loggers.aiLogger.info(f"Asking prompt for user {message.author.name} ({message.author.id}):\n{prompt}")
                    response = await AsyncClient(CONFIG.getAiHost()).chat(CONFIG.storage.currentModel, messages=aiHandler.getMessagesWithPrompt(message.channel.id), keep_alive=CONFIG.getKeepAlive())
                    Loggers.aiLogger.info(f"Got an answer for {message.author.name}'s prompt ({message.author.id}) (prompt: '{message.content}'):\n{response.message.content}")
                    content = utils.removeThinkTag(response.message.content or "")
                    
                    if len(content or "") >= 2000:
                        tmpfile = tempfile.TemporaryFile(delete_on_close=False)
                        tmpfile.write(content.encode())
                        tmpfile.close()
                        
                        file = discord.File(
                            fp=tmpfile.name,
                            filename="output.txt",
                            description=f"The output of the AI ({CONFIG.storage.currentModel})"
                            )
                        await message.reply(content="", file=file)
                        
                        tmpfile._closer.cleanup()
                    else:
                        await message.reply(content=content or "**[no response]**", allowed_mentions=CONFIG.storage.aiPingReply if message.author.bot else None)
                        
                    if content:
                        Loggers.aiLogger.debug("Adding ai's response to memory")
                        aiHandler.addMessage(AiHandler.Role.ASSISTANT, content, message.channel.id)
                except Exception as e:
                    await message.reply(content="", embed=utils.createErrorEmbed(f"({e.__class__.__name__}) {e}"), allowed_mentions=discord.AllowedMentions.none())
                    await message.add_reaction("⚠️")
                    try:
                        await message.remove_reaction("<:preloading_model:1419412009212051456>", cast(discord.ClientUser, self.bot.user))
                    except discord.NotFound: ...
                    Loggers.logger.exception(f"Catched exception in `BotAI.on_message`: {e}")
                    
                    raise e
    
    @discord.slash_command(
        name="ai",
        description="Ask stuff to an ai model and get an answer in probably 7 minutes",
        integration_type=INTEGRATION_TYPES
    )
    @discord.option(
        name="prompt",
        input_type=str,
        description="What to ask to the ai"
    )
    @discord.option(
        name="model",
        input_type=str,
        autocomplete=AiUtils.getModels,
        required=False,
        description="The model to use"
    )
    async def aiCmd(self, ctx: Context, prompt: str, model: Optional[str]):
        # if not CONFIG.isTrusted(ctx.author.id):
        #     utils.logNoAuthorization(ctx, Loggers.logger, name="/ai", reason="Isn't trusted")
        #     await ctx.respond("No (not for the moment at least) :3", ephemeral=True)
        #     return
        
        
        if model and (not model in await CONFIG.storage.aiHandler.getModelsAsync(CONFIG.getAiHost())):
            await ctx.respond(f"`{model}` model is not a valid model !", ephemeral=True)
            return 
        
        if isinstance(ctx.author, discord.Member):
            guildID = cast(discord.Guild, ctx.guild).id
            guildPerms = await Profiles.getGuildPermissionProfile(guildID)
            
            guildProfile = await Profiles.GuildProfile.createOrGet(guildID)
            if ctx.author.id in guildProfile.bannedAiUsers:
                Loggers.aiLogger.info(f"User {ctx.author.name} ({ctx.author.id}) is banned from using the AI in the guild {ctx.guild.name} ({guildID}), not continuing (from `/ai`)")
                await ctx.respond("You are banned from using `gemingbot`'s ai, therefore, you **cannot use this command** ! (server-specific)", ephemeral=True)
                
                return
            
            # bypass for the bot owner / server administrators
            if not (ctx.author.guild_permissions.administrator or ctx.author.id == CONFIG.getOwner()):
                if not guildPerms.isAiEnabledGlobally():
                    await ctx.respond(content="Sorry, but geming bot's ai has **been disabled on this server** !", ephemeral=True)
                    return
                
                if not guildPerms.isChannelAuthorized(ctx.channel_id):
                    await ctx.respond("Sorry, but geming bot's ai is **not enabled on this channel** !", ephemeral=True)
                    return
            
        userProfile = await Profiles.UserProfile.createOrGet(ctx.author.id)
        if userProfile.aiBanned:
            Loggers.aiLogger.info(f"User {ctx.author.name} ({ctx.author.id}) is banned from using the AI, not continuing (from `/ai`)")
            await ctx.respond("You are banned from using `gemingbot`'s ai, therefore, you **cannot use this command** !", ephemeral=True)
            
            return
        
        Loggers.aiLogger.info("Checking if ollama is up")
        if not await CONFIG.storage.aiHandler.isOllamaRunningAsync(CONFIG.getAiHost()):
            Loggers.aiLogger.info(f"User {ctx.author.name} ({ctx.author.id}) tried using the ai, but it is unavailable")
            await ctx.edit(content="`ollama` isn't running, the ai isn't currently available")
            
            return
        
        if model == None: model = CONFIG.storage.currentModel
        
        await ctx.respond(f"Asking ai...\n-# using model `{model}`")
        
        try:
            # if not await aiHandler.isModelPreloaded(CONFIG.storage.currentModel, HOST):
            #     await utils.preloadModelAsync(model, HOST)
            #     await ctx.edit(content=f"Asking ai...\n-# using preloaded model `{model}`")
                
        
            Loggers.aiLogger.debug("Adding user's prompt to memory")
            
            aiHandler.addMessage(AiHandler.Role.USER, prompt + aiHandler.getUserInfos(ctx.author), ctx.channel_id)
            
            Loggers.aiLogger.info(f"Asking prompt for user {ctx.author.name} ({ctx.author.id}):\n{prompt}")
            response = await AsyncClient(CONFIG.getAiHost()).chat(model, messages=aiHandler.getMessagesWithPrompt(ctx.channel_id), keep_alive=CONFIG.getKeepAlive())
            Loggers.aiLogger.info(f"Got an answer for {ctx.author.name}'s prompt ({ctx.author.id}) (prompt {prompt}):\n{response.message.content}")
            content = utils.removeThinkTag(response.message.content or "")
            
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
                tmpfile.close()
            else:
                await ctx.edit(content=content or "**[no response]**", allowed_mentions=CONFIG.storage.aiPingReply if ctx.author.bot else None)
                
            if content:
                Loggers.aiLogger.debug("Adding ai's response to memory")
                aiHandler.addMessage(AiHandler.Role.ASSISTANT, content, ctx.channel_id)
        except Exception as e:
            await ctx.edit(content="", embed=utils.createErrorEmbed(f"({e.__class__.__name__}) {e}"), allowed_mentions=discord.AllowedMentions.none())
            Loggers.logger.exception(f"Catched exception in `BotAI.on_message`: {e}")
            
            raise e

def setup(bot: discord.Bot):
    bot.add_cog(BotAI(bot))
    bot.add_cog(AiUtils(bot))
    