import math
from typing import Callable, Optional, TypeVar, cast
import discord
from discord.ext import commands
from discord.ui.item import Item

from utils import utils
from utils.Loggers import Loggers
from utils.db.Profiles import GuildProfile, UserProfile
from utils.utils import CONFIG


Context = discord.ApplicationContext

T = TypeVar('T')

class BannedUsersView(discord.ui.View):
    class ChangePageButton(discord.ui.Button):
        currentPage: int
        action: Callable[[int], int]
        interactionOwner: discord.Member | discord.User
        bannedUsers: list[int]
        
        def __init__(self, *,
                     style: discord.ButtonStyle = discord.ButtonStyle.secondary,
                     label: Optional[str] = None,
                     disabled: bool = False,
                     custom_id: Optional[str] = None,
                     url: Optional[str] = None,
                     emoji: str | discord.Emoji | discord.PartialEmoji | None = None,
                     sku_id: Optional[int] = None,
                     row: Optional[int] = None,
                     currentPage: int,
                     action: Callable[[int], int],
                     interactionOwner: discord.Member | discord.User,
                     bannedUsers: list[int]
                     ):
            super().__init__(style=style, label=label, disabled=disabled, custom_id=custom_id, url=url, emoji=emoji, sku_id=sku_id, row=row)
            
            self.currentPage = currentPage
            self.action = action
            self.interactionOwner = interactionOwner
            self.bannedUsers = bannedUsers
        
        def checkIsOwner(self, interaction: discord.Interaction) -> bool:
            if interaction.user:
                return interaction.user.id == self.interactionOwner.id
            return False
        
        async def callback(self, interaction: discord.Interaction):
            if self.checkIsOwner(interaction):
                await cast(discord.Message, interaction.message).edit(view=BannedUsersView(
                    numPage=self.action(self.currentPage),
                    bannedUsers=self.bannedUsers,
                    interactionOwner=self.interactionOwner
                ), embed=BannedUsersView.createEmbed(self.bannedUsers, self.currentPage))
            else:
                # Should never happen, but just in case
                await interaction.respond("You cannot interact with this since it is not your interaction", ephemeral=True)
                
    
    userPerPages = 10
    
    numPage: int
    interactionOwner: discord.Member | discord.User
    bannedUsers: list[int]
    
    def __init__(self, *items: Item, timeout: Optional[float] = 180, disable_on_timeout: bool = False,
                 numPage: int,
                 bannedUsers: list[int],
                 interactionOwner: discord.Member | discord.User
                 ):
        super().__init__(*items, timeout=timeout, disable_on_timeout=disable_on_timeout)
        
        self.numPage = numPage
        self.interactionOwner = interactionOwner
        self.bannedUsers = bannedUsers
        self.lastPage = math.ceil(len(bannedUsers) / BannedUsersView.userPerPages) - 1
        if self.lastPage < 0:
            self.lastPage = 0
        
        self.add_item(BannedUsersView.ChangePageButton(
            label="<<",
            disabled=numPage <= 0,
            
            currentPage=numPage,
            action=lambda x: x-1,
            interactionOwner=self.interactionOwner,
            bannedUsers=self.bannedUsers
        ))
        for i in range(1, 4):
            if numPage + i >= self.lastPage: break
            
            self.add_item(BannedUsersView.ChangePageButton(
                label=str(numPage + i),
                
                currentPage=numPage,
                action=lambda x: numPage + i,
                interactionOwner=self.interactionOwner,
                bannedUsers=self.bannedUsers
            ))
        self.add_item(BannedUsersView.ChangePageButton(
            label=">>",
            disabled=numPage >= self.lastPage,
            
            currentPage=numPage,
            action=lambda x: x+1,
            interactionOwner=self.interactionOwner,
            bannedUsers=self.bannedUsers
        ))
    
    
    @staticmethod
    def createEmbed(bannedUsersIDs: list[int], page: int) -> discord.Embed:
        bannedUsersText = ""
        for userID in BannedUsersView.splitList(bannedUsersIDs, BannedUsersView.userPerPages, page):
            bannedUsersText += f"- <@{userID}>\n"
        
        embed = discord.Embed(
            title="Banned users",
            description=bannedUsersText.removesuffix("\n"),
            footer=discord.EmbedFooter(text=f"Page {page + 1}")
        )
        
        return embed
    
    @staticmethod
    def splitList(l: list[T], n: int, index: int) -> list[T]:
        """Splits a list in members of `n` and returns the index `index`

        Args:
            l: The list to split
            n: The numbers of sub-list to make
            index: The index of the sublist to get
            
        Returns:
            The sublist of index `index`
        """
        
        finalLists: list[list[T]] = []
        currentSubList: list[T] = []
        
        for i, v in enumerate(l, start=1):
            currentSubList.append(v)
            
            if i % n == 0:
                finalLists.append(currentSubList.copy())
                currentSubList.clear()
        
        if currentSubList != []:
            finalLists.append(currentSubList.copy())
            currentSubList.clear()
        
        try:
            return finalLists[index]
        except:
            return []
        

async def doBanAction(ctx: Context, user: discord.User, *, ban: bool, condition: bool, globally: bool = False, silent: bool = False) -> bool:
    """"dry" smh

    Args:
        ctx: The context
        user: The user to do the action on
        ban: If set to `True`, we'll ban the user, otherwise, we'll unban it
        condition: A bool value to know if the user is actually bannable or not
        globally: If it's a global ban. Defaults to False.
        silent: If a message will be sent to the user

    Returns:
        If their was an action done on the given user
    """
    


    verb = "ban" if ban else "unban"
    requestedByText = f", requested by {ctx.author.name} ({ctx.author.id})"
    globalBanText = f"(**global {verb}**)" if globally else ""
    inServerText = "" if globally else f"in the server `{ctx.guild.name}`"
    
    if user.id == ctx.author.id:
        await ctx.respond(f"You cannot {verb} yourself !", ephemeral=True)
        return False
    
    Loggers.modLogger.info(f"{verb}ning user {user.name} ({user.id}) from using gemingbot's ai" + requestedByText)
    await ctx.respond(f"{verb}ning user <@{user.id}> ...", ephemeral=True)
    
    if not condition:
        Loggers.modLogger.info(f"Tried {verb}ning user {user.id} ({user.name}) but they are already {verb}ned {globalBanText}")
        await ctx.edit(content=f"Cannot {verb} user <@{user.id}> because they are already {verb}ned")
        
        return False
    
    if not silent:
        try:
            if user.can_send():
                embedColor = discord.Color.red() if ban else discord.Color.green()
                await user.send(embed=discord.Embed(
                    title="Gemingbot's AI",
                    description=f"You got {verb}ned from Gemingbot's ai {inServerText} ! {globalBanText}",
                    color=embedColor
                ))
                    
                Loggers.modLogger.info(f"Sent dm to user {user.name} ({user.id})")
            else:
                Loggers.modLogger.info(f"Couldn't send dm to user {user.name} ({user.id}) because their dms are disabled")
        except Exception as e:
            Loggers.modLogger.exception(f"Caught error while trying to {"globally" if globally else ""} {verb} user {user.name}: {e}")
    else:
        Loggers.modLogger.info(f"Will not send a dm to the user {user.name} ({user.id}) because they got {verb}ned silently")
    
    Loggers.modLogger.info(f"{verb}ned user {user.id} ({user.name}) from using gemingbot's ai {globalBanText}")
    await ctx.edit(content=f"{verb}ned user <@{user.id}> ! {globalBanText}")
    
    return True



class Moderation(commands.Cog):
    moderationGroup = discord.SlashCommandGroup(
        "moderation",
        "Useful commands to moderate users (only on this server)",
        checks=[
            commands.has_permissions(ban_members=True).predicate # pyright: ignore[reportFunctionMemberAccess]
        ]  # Ensures the owner_id user can access this group, and no one else
    )
        
    def __init__(self, bot: discord.Bot):
        self.bot = bot

    @moderationGroup.command(name="ban-ai", description="Bans a given user from using gemingbot's ai (in this server)")
    @discord.option(
        name="user",
        input_type=discord.User,
        description="The user to ban"
    )
    @discord.option(
        name="silent",
        input_type=bool,
        default=False,
        description="If a DM will be sent to the user or not (defaults to false)"
    )
    async def banAI(self, ctx: Context, user: discord.User, silent: bool):
        if not (cast(discord.Member, ctx.author).guild_permissions.ban_members or ctx.author.id == self.bot.owner_id):
            utils.logNoAuthorization(ctx, Loggers.modLogger, "/moderation ban-ai", "Doesn't have the 'ban members' permissions")
            await ctx.respond("You don't have the permission to execute this !", ephemeral=True)
            return
        
        guildProfile = await GuildProfile.createOrGet(ctx.guild_id)
        if await doBanAction(ctx, user, ban=True, condition=not user.id in guildProfile.bannedAiUsers, globally=False, silent=silent):
            guildProfile.bannedAiUsers.append(user.id)
            await guildProfile.save()

    @moderationGroup.command(name="unban-ai", description="Unbans a given user from using gemingbot's ai (in this server)")
    @discord.option(
        name="user",
        input_type=discord.User,
        description="The user to ban",
        required=False
    )
    @discord.option(
        name="silent",
        input_type=bool,
        default=False,
        description="If a DM will be sent to the user or not (defaults to false)"
    )
    async def unbanAI(self, ctx: Context, user: discord.User, silent: bool):
        if not (cast(discord.Member, ctx.author).guild_permissions.ban_members or ctx.author.id == self.bot.owner_id):
            utils.logNoAuthorization(ctx, Loggers.modLogger, "/moderation unban-ai", "Doesn't have the 'ban members' permissions")
            await ctx.respond("You don't have the permission to execute this !", ephemeral=True)
            return
    
        guildProfile = await GuildProfile.createOrGet(ctx.guild_id)
        if await doBanAction(ctx, user, ban=False, condition=user.id in guildProfile.bannedAiUsers, globally=False, silent=silent):
            guildProfile.bannedAiUsers.remove(user.id)
            await guildProfile.save()
    
    @moderationGroup.command(name="ai-banned-users", description="Gets the banned users of gemingbot's ai in this server")
    async def getBannedUsers(self, ctx: Context):
        if isinstance(ctx.author, discord.User):
            await ctx.respond("Cannot do this in a non-server context !")
            return
        
        if (ctx.author.guild_permissions.ban_members) or (not ctx.author.id == self.bot.owner_id):
            utils.logNoAuthorization(ctx, Loggers.modLogger, "/oderation ai-banned-users", "Doesn't have the required permissions (banning members)")
            await ctx.respond("You don't have the permission to execute this !", ephemeral=True)
            return
        
        guildProfile = await GuildProfile.createOrGet(ctx.guild_id)
        
        view = BannedUsersView(numPage=0, interactionOwner=ctx.author, bannedUsers=guildProfile.bannedAiUsers)
        await ctx.respond(view=view, embed=BannedUsersView.createEmbed(guildProfile.bannedAiUsers, page=0))
    

class GlobalModeration(commands.Cog):
    globalModerationGroup = discord.SlashCommandGroup(
        "global-moderation",
        "Useful commands to moderate users globally",
        checks=[
            commands.is_owner().predicate # pyright: ignore[reportFunctionMemberAccess]
        ]  # Ensures the owner_id user can access this group, and no one else
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
    @discord.option(
        name="silent",
        input_type=bool,
        default=False,
        description="If a DM will be sent to the user or not (defaults to false)"
    )
    async def banAI(self, ctx: Context, user: discord.User, silent: bool):
        if not ctx.author.id == self.bot.owner_id:
            utils.logNoAuthorization(ctx, Loggers.modLogger, "/global-moderation ban-ai", "Isn't owner")
            await ctx.respond("You don't have the permission to execute this !", ephemeral=True)
            return
    
        userProfile = await UserProfile.createOrGet(user.id)
        if await doBanAction(ctx, user, ban=True, condition=not userProfile.aiBanned, globally=True, silent=silent):
            userProfile.aiBanned = True
            await userProfile.save()

    @globalModerationGroup.command(name="unban-ai", description="Unbans a given user from using gemingbot's ai (globally)")
    @discord.option(
        name="user",
        input_type=discord.User,
        description="The user to ban",
        required=False
    )
    @discord.option(
        name="silent",
        input_type=bool,
        default=False,
        description="If a DM will be sent to the user or not (defaults to false)"
    )
    async def unbanAI(self, ctx: Context, user: discord.User, silent: bool):
        if not ctx.author.id == self.bot.owner_id:
            utils.logNoAuthorization(ctx, Loggers.modLogger, "/global-moderation unban-ai", "Isn't owner")
            await ctx.respond("You don't have the permission to execute this !", ephemeral=True)
            return
        
        userProfile = await UserProfile.createOrGet(user.id)
        if await doBanAction(ctx, user, ban=False, condition=userProfile.aiBanned, globally=True, silent=silent):
            userProfile.aiBanned = False
            await userProfile.save()
    
    
    @globalModerationGroup.command(name="ai-banned-users", description="Gets the globally banned users of gemingbot's ai")
    async def getBannedUsers(self, ctx: Context):
        if not ctx.author.id == self.bot.owner_id:
            utils.logNoAuthorization(ctx, Loggers.modLogger, "/global-moderation ai-banned-users", "Isn't owner")
            await ctx.respond("You don't have the permission to execute this !", ephemeral=True)
            return
        
        bannedUsers: list[int] = []
        
        async with CONFIG.storage.db.connect() as conn:
            async with conn.execute("SELECT * FROM `users` WHERE ai_banned = 1") as cur:
                for row in await cur.fetchall():
                    bannedUsers.append(row[0]) # row[0] = userid
        
        view = BannedUsersView(numPage=0, interactionOwner=ctx.author, bannedUsers=bannedUsers)
        await ctx.respond(view=view, embed=BannedUsersView.createEmbed(bannedUsers, page=0))

def setup(bot: discord.Bot):
    bot.add_cog(Moderation(bot))
    bot.add_cog(GlobalModeration(bot))
    