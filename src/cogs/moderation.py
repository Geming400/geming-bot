from typing import Optional, cast
import discord
from discord.ext import commands

from utils import utils
from utils.Loggers import Loggers
from utils.db.Profiles import GuildProfile, UserProfile


Context = discord.ApplicationContext

async def ban(ctx: Context, user: discord.User, *, ban: bool, condition: bool, globally: bool = False) -> bool:
    """"dry" smh

    Args:
        ctx: The context
        user: The user to do the action on
        ban: If set to `True`, we'll ban the user, otherwise, we'll unban it
        condition: A bool value to know if the user is actually bannable or not
        globally: If it's a global ban. Defaults to False.

    Returns:
        If their was an action done on the given user
    """
    
    if user.id == ctx.author.id:
        # await ctx.respond("You cannot ban yourself !", ephemeral=True)
        # return False
        ...

    verb = "ban" if ban else "unban"
    requestedByText = f", requested by {ctx.author.name} ({ctx.author.id})"
    globalBanText = f"(**global {verb}**)" if globally else ""
    
    Loggers.modLogger.info(f"{verb}ning user {user.name} ({user.id}) from using gemingbot's ai" + requestedByText)
    await ctx.respond(f"{verb}ning user <@{user.id}> ...", ephemeral=True)
    
    if not condition:
        Loggers.modLogger.info(f"Tried {verb}ning user {user.id} ({user.name}) but they are already {verb}ned {globalBanText}")
        await ctx.edit(content=f"Cannot {verb} user <@{user.id}> because they are already {verb}ned")
        
        return False
    
    if user.can_send():
        embedColor = discord.Color.red() if ban else discord.Color.green()
        await user.send(embed=discord.Embed(
            title="Gemingbot's AI",
            description=f"You got {verb}ned from Gemingbot's ai in the server `{ctx.guild.name}` ! {globalBanText}",
            color=embedColor
        ))
            
        Loggers.modLogger.info(f"Sent dm to user {user.name} ({user.id})")
    else:
        Loggers.modLogger.info(f"Couldn't send dm to user {user.name} ({user.id}) because their dms are disabled")
    
    Loggers.modLogger.info(f"{verb}ned user {user.id} ({user.name}) from using gemingbot's ai {globalBanText}")
    await ctx.edit(content=f"{verb}ned user <@{user.id}> ! {globalBanText}")
    
    return True

class Moderation(commands.Cog):
    moderationGroup = discord.SlashCommandGroup(
        "moderation",
        "Useful commands to moderate users (only on this server)"
    )
        
    def __init__(self, bot: discord.Bot):
        self.bot = bot

    @moderationGroup.command(name="ban-ai", description="Bans a given user from using gemingbot's ai (in this server)")
    @discord.option(
        name="user",
        input_type=discord.User,
        description="The user to ban"
    )
    async def banAI(self, ctx: Context, user: discord.User):
        if not (cast(discord.Member, ctx.author).guild_permissions.ban_members or ctx.author.id == self.bot.owner_id):
            utils.logNoAuthorization(ctx, Loggers.modLogger, "/moderation ban-ai", "Doesn't have the 'ban members' permissions")
            await ctx.respond("You don't have the permission to execute this !", ephemeral=True)
            return
        
        guildProfile = await GuildProfile.createOrGet(ctx.guild_id)
        if await ban(ctx, user, ban=True, condition=not user.id in guildProfile.bannedAiUsers, globally=False):
            guildProfile.bannedAiUsers.append(user.id)
            await guildProfile.save()

    @moderationGroup.command(name="unban-ai", description="Unbans a given user from using gemingbot's ai (in this server)")
    @discord.option(
        name="user",
        input_type=discord.User,
        description="The user to ban",
        required=False
    )
    async def unbanAI(self, ctx: Context, user: discord.User):
        if not (cast(discord.Member, ctx.author).guild_permissions.ban_members or ctx.author.id == self.bot.owner_id):
            utils.logNoAuthorization(ctx, Loggers.modLogger, "/moderation unban-ai", "Doesn't have the 'ban members' permissions")
            await ctx.respond("You don't have the permission to execute this !", ephemeral=True)
            return
    
        guildProfile = await GuildProfile.createOrGet(ctx.guild_id)
        if await ban(ctx, user, ban=False, condition=user.id in guildProfile.bannedAiUsers, globally=False):
            guildProfile.bannedAiUsers.remove(user.id)
            await guildProfile.save()
    

class GlobalModeration(commands.Cog):
    globalModerationGroup = discord.SlashCommandGroup(
        "global-moderation",
        "Useful commands to moderate users globally",
        checks=[
            commands.is_owner().predicate # pyright: ignore[reportFunctionMemberAccess]
        ],  # Ensures the owner_id user can access this group, and no one else
    )
        
    def __init__(self, bot: discord.Bot):
        self.bot = bot
    
    
    @globalModerationGroup.command(name="ban-ai", description="Bans a given user from using gemingbot's ai (globally)")
    @discord.option(
        name="user",
        input_type=discord.User,
        description="The user to ban",
        required=False
    )
    async def banAI(self, ctx: Context, user: discord.User):
        if not ctx.author.id == self.bot.owner_id:
            utils.logNoAuthorization(ctx, Loggers.modLogger, "/global-moderation ban-ai", "Isn't owner")
            await ctx.respond("You don't have the permission to execute this !", ephemeral=True)
            return
    
        userProfile = await UserProfile.createOrGet(user.id)
        if await ban(ctx, user, ban=True, condition=not userProfile.aiBanned, globally=True):
            userProfile.aiBanned = True
            await userProfile.save()

    @globalModerationGroup.command(name="unban-ai", description="Unbans a given user from using gemingbot's ai (globally)")
    @discord.option(
        name="user",
        input_type=discord.User,
        description="The user to ban",
        required=False
    )
    async def unbanAI(self, ctx: Context, user: discord.User):
        if not ctx.author.id == self.bot.owner_id:
            utils.logNoAuthorization(ctx, Loggers.modLogger, "/global-moderation unban-ai", "Isn't owner")
            await ctx.respond("You don't have the permission to execute this !", ephemeral=True)
            return
        
        userProfile = await UserProfile.createOrGet(user.id)
        if await ban(ctx, user, ban=False, condition=userProfile.aiBanned, globally=True):
            userProfile.aiBanned = False
            await userProfile.save()
        

def setup(bot: discord.Bot):
    bot.add_cog(Moderation(bot))
    bot.add_cog(GlobalModeration(bot))
    