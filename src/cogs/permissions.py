from typing import Optional, cast
import discord
from discord.ext import commands

from utils import utils
from utils.db import Profiles
from utils.utils import CONFIG


Context = discord.ApplicationContext


class BotPermissionHandler(commands.Cog):
    permissions = discord.SlashCommandGroup("permissions", description="Commands related to", guild_only=True)
    
    def __init__(self, bot: discord.Bot):
        self.bot = bot
        bot.add_application_command(BotPermissionHandler.permissions)
    
    @staticmethod
    async def isAllowed(ctx: Context):
        """Returns wethever or not a given user is authorized to change the bot's server permissions or not

        Args:
            ctx: The context

        Returns:
            If the user is allowed to change the bot's server permissions
        """
        
        isBotOwner = ctx.author.id == CONFIG.getOwner()
        #isServerOwner = cast(discord.Guild, ctx.guild).owner == ctx.author
        isAdmin = cast(discord.Member, ctx.author).guild_permissions.administrator
        
        return isBotOwner or isAdmin
        #return isBotOwner or isServerOwner or isAdmin
    
    @staticmethod
    async def sendErrorMsg(ctx: Context):
        """Replies with a error message saying the user doesn't have permission to execute this command

        Args:
            ctx: The context
        """
        await ctx.respond(embed=utils.createErrorEmbed("You do not have access to this command !"), ephemeral=True)

    
    @permissions.command(name="enable-ai", description="Wethever or not to enable ai globally in this server")
    @discord.option(
        name="enable",
        description="Wethever or not the ai should be enabled globally on this server",
        input_type=bool
    )
    async def enableAi(self, ctx: Context, enableAI: bool):
        if await BotPermissionHandler.isAllowed(ctx):
            await ctx.respond("Applying changes...", ephemeral=True)
            
            guildPerms = await Profiles.getGuildPermissionProfile(cast(int, ctx.guild_id))
            oldAiVal = guildPerms.ai
            guildPerms.ai = enableAI
            await guildPerms.save()
            
            await ctx.edit(content=f"Changed value from `enableAI({oldAiVal})` to `enableAI({enableAI})` !")
        else:
            await BotPermissionHandler.sendErrorMsg(ctx)
    
    @permissions.command(name="enable-ai-per-channel", description="Wethever or not to enable ai globally in this server")
    @discord.option(
        name="channel",
        description="Wethever or not the ai should be enabled globally on this server. If not provided, it'll use this channel",
        input_type=discord.TextChannel,
        required=False
    )
    @discord.option(
        name="remove",
        description="If set to `true`, it'll remove this channel from the list of channels with ai enabled",
        input_type=bool,
        default=False
    )
    async def enableAiPerChannel(self, ctx: Context, channel: Optional[discord.TextChannel], remove: bool):
        channel = channel or cast(discord.TextChannel, ctx.channel)
        
        if await BotPermissionHandler.isAllowed(ctx):
            await ctx.respond("Applying changes...", ephemeral=True)
            
            guildPerms = await Profiles.getGuildPermissionProfile(cast(int, ctx.guild_id))
            if remove:
                if channel.id in guildPerms.aiChannels:
                    guildPerms.aiChannels.remove(channel.id)
                    await guildPerms.save()
                    
                    ctx.edit(content=f"Removed channel {channel.mention} was removed from list of channels with ai enabled !")
                else:
                    ctx.edit(content=f"The channel {channel.mention} was not found inside the list of channels with ai enabled !")
            else:
                tip = "\n-# **tip: to remove that channel, set the `remove` argument to `true`**"
                
                if channel.id in guildPerms.aiChannels:
                    ctx.edit(content=f"Cannot insert channel {channel.mention} from the list of channels with ai enabled, it is already in it !" + tip)
                else:
                    guildPerms.aiChannels.append(channel.id)
                    ctx.edit(content=f"Inserted channel {channel.mention} from the list of channels with ai enabled !" + tip)
        else:
            await BotPermissionHandler.sendErrorMsg(ctx)
    
    

def setup(bot: discord.Bot):
    bot.add_cog(BotPermissionHandler(bot))