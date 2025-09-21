from typing import Optional, cast
import discord
from discord.ext import commands

from utils import utils
from utils.Loggers import Loggers
from utils.db.Profiles import GuildProfile, UserProfile


Context = discord.ApplicationContext


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
        
        if user.id == ctx.author.id:
            await ctx.respond("You cannot ban yourself !", ephemeral=True)
            return
        
        requestedBy = f", requested by {ctx.author.name} ({ctx.author.id})"
        Loggers.modLogger.info(f"Banning user {user.name} ({user.id}) from using gemingbot's ai" + requestedBy)
        await ctx.respond(f"Banning user <@{user.id}> ...", ephemeral=True)

        
        
        guildProfile = await GuildProfile.createOrGet(ctx.guild_id)
        if user.id in guildProfile.bannedAiUsers:
            Loggers.modLogger.info(f"Tried banning user {user.id} ({user.name}) but they are already banned")
            await ctx.edit(content=f"Cannot ban user <@{user.id}> because they are already banned")
            return
            
        guildProfile.bannedAiUsers.append(user.id)
        await guildProfile.save()
        
        if ctx.author.can_send():
            await ctx.author.send(embed=discord.Embed(
                title="Gemingbot's AI",
                description=f"You got banned from Gemingbot's ai in the server `{ctx.guild.name}` !",
                color=discord.Color.red()
            ))
        Loggers.modLogger.info(f"Banned user {user.id} ({user.name}) from using gemingbot's ai")
        await ctx.edit(content=f"Banned user <@{user.id}> !")

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
    
        if user.id == ctx.author.id:
            await ctx.respond("You cannot unban yourself (as you cannot ban yourself) !", ephemeral=True)
            return
        
        await ctx.respond(f"Unbanning user <@{user.id}> ...", ephemeral=True)
        
        requestedBy = f", requested by {ctx.author.name} ({ctx.author.id})"
        Loggers.modLogger.info(f"Unbanning user {user.name} ({user.id}) from using gemingbot's ai" + requestedBy)
            
            
            
        guildProfile = await GuildProfile.createOrGet(ctx.guild_id)
        if not user.id in guildProfile.bannedAiUsers:
            Loggers.modLogger.info(f"Tried unbanning user {user.id} but they are not banned")
            await ctx.edit(content=f"Cannot unban user <@{user.id}> because they are not banned")
            return
        
        guildProfile.bannedAiUsers.remove(user.id)
        await guildProfile.save()
        
        if ctx.author.can_send():
            await ctx.author.send(embed=discord.Embed(
                title="Gemingbot's AI",
                description=f"You got unbanned from Gemingbot's ai in the server `{ctx.guild.name}` !",
                color=discord.Color.green()
            ))
        Loggers.modLogger.info(f"Unbanned user {user.id} ({user.name}) from using gemingbot's ai" + requestedBy)
        await ctx.edit(content=f"Unbanned user <@{user.id}> !")
    

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
    
        if user.id == ctx.author.id:
            await ctx.respond("You cannot ban yourself !", ephemeral=True)
            return
        
        requestedBy = f", requested by {ctx.author.name} ({ctx.author.id})"
        Loggers.modLogger.info(f"Banning user {user.name} ({user.id}) from using gemingbot's ai (globally)" + requestedBy)
        await ctx.respond(f"Banning user <@{user.id}> ...", ephemeral=True)
        
        
        
        userProfile = await UserProfile.createOrGet(user.id)
        if not userProfile.aiBanned:
            ctx.edit(content=f"Cannot ban globally <@{user.id}> because they are already banned")
            Loggers.modLogger.info(f"Tried banning user {user.id} but they are already banned globally")
            return
        
        userProfile.aiBanned = True
        await userProfile.save()
        
        Loggers.modLogger.info(f"Banned user {user.id} ({user.name}) from using gemingbot's ai (globally)" + requestedBy)
        if ctx.author.can_send():
            await ctx.author.send(embed=discord.Embed(
                title="Gemingbot's AI",
                description="You got globally banned from Gemingbot's ai !",
                color=discord.Color.red()
            ))
        await ctx.edit(content=f"Banned user <@{user.id}> !")

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
        
        if user.id == ctx.author.id:
            await ctx.respond("You cannot unban yourself (as you cannot ban yourself) !", ephemeral=True)
            return
        
        await ctx.respond(f"Unbanning user <@{user.id}> ...", ephemeral=True)
        
        requestedBy = f", requested by {ctx.author.name} ({ctx.author.id})"
        Loggers.modLogger.info(f"Unbanning user {user.name} ({user.id}) from using gemingbot's ai" + requestedBy)
        

        userProfile = await UserProfile.createOrGet(user.id)
        if userProfile.aiBanned:
            ctx.edit(content=f"Cannot unban globally <@{user.id}> because they are not banned")
            Loggers.modLogger.info(f"Tried unbanning user {user.id} but they are not banned globally")
            return
            
        userProfile.aiBanned = False
        await userProfile.save()
        
        if ctx.author.can_send():
            await ctx.author.send(embed=discord.Embed(
                title="Gemingbot's AI",
                description="You got globally banned from Gemingbot's ai !",
                color=discord.Color.green()
            ))
        Loggers.modLogger.info(f"Unbanned user {user.id} ({user.name}) from using gemingbot's ai" + requestedBy)
        await ctx.edit(content=f"Unbanned user <@{user.id}> !")
        

def setup(bot: discord.Bot):
    bot.add_cog(Moderation(bot))
    bot.add_cog(GlobalModeration(bot))
    