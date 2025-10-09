import asyncio
import functools
import random
import re
from typing import Optional, Type, cast
import discord
from discord.ext import commands, tasks
import httpx

from utils import utils
from utils.Loggers import Loggers
from utils.utils import CONFIG, INTEGRATION_TYPES


Context = discord.ApplicationContext


aiHandler = CONFIG.storage.aiHandler


@functools.lru_cache
async def getTjcsIp():
    Loggers.logger.debug("Cached tjc's ip")
    
    tjcsIp = await httpx.AsyncClient().get("https://tjcsucht.net/api/ip")
    return tjcsIp.text

class MainBot(commands.Cog):
    def __init__(self, bot: discord.Bot):
        self.bot = bot
        
    
    """
    @discord.slash_command(
        name="dyrs",
        description="Get dyrs' personnal infos ! (for free)",
        integration_type=INTEGRATION_TYPES
    )
    async def dyrsInfos(self, ctx: Context):
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
    """

    @discord.slash_command(
        name="linux-icbm",
        description="Linus torvalds' own ICBM, that's it",
        integration_type=INTEGRATION_TYPES
    )
    @discord.option(
        name="user",
        input_type=discord.User,
        description="The user to send the icmb to"
    )
    async def linux_icbm(self, ctx: Context, user: discord.User):
        await ctx.respond(f"Finding {user.mention}'s location...")
        
        try:
            await asyncio.sleep(5)
            await ctx.edit(content=f"Done! User's ip is `{await getTjcsIp()}`. Sending linus torvalds ICBM...")
        except:
            await ctx.respond(f"Finding {user.mention}'s location...")
            await asyncio.sleep(5)
            await ctx.edit(content="Done! Sending linus torvalds ICBM...")
        await asyncio.sleep(3)
        await ctx.edit(content="https://cdn.discordapp.com/attachments/1268366668384440352/1372330251757027389/2025_23_49_53.gif?ex=68a98ee4&is=68a83d64&hm=85b8d19ac042233ff7ee14ced7e7abeed292cef893a58fa284a5624e7081f7aa&")

    # NOTE: If "activities" weren't set before, but then were to be added
    # they won't be registered
    # also, changes to the `frequency` arg also won't be affected
    @discord.slash_command(
        name="reload-configs",
        description="Reload the config files",
        integration_type=INTEGRATION_TYPES
    )
    async def reloadConfigs(self, ctx: Context):
        if not CONFIG.isOwner(ctx.author.id):
            utils.logNoAuthorization(ctx, Loggers.logger, cmdname="/reload-configs", reason="Isn't owner")
            await ctx.respond("No :3", ephemeral=True)
            return
        
        Loggers.logger.info(f"Reloading configs for user {ctx.author.name} ({ctx.author.id})")
        try:
            CONFIG.reloadConfigs()
            aiHandler.systemPrompt = CONFIG.getSystemPrompt()
            await ctx.respond("Reloaded configs !", ephemeral=True)
        except Exception as e:
            Loggers.logger.exception(f"Caught error while trying to reload configs: {e}")
            await ctx.respond(embed=utils.createErrorEmbed(f"Error while trying to reload configs: ({e.__class__.__name__}) {e}"), ephemeral=True)
        
    @discord.slash_command(
        name="help",
        description="Get every commands you can access",
        integration_type=INTEGRATION_TYPES
    )
    @discord.option(
        name="user",
        description="If not specified, it'll default to you",
        input_type=discord.User,
        required=False
    )
    async def helpCmd(self, ctx: Context, user: Optional[discord.User]):
        cmds = []
        ret = ""
        
        _user: discord.User | discord.Member = user or ctx.author
        
        if _user.bot:
            ctx.respond("It's literally a bot bro", ephemeral=True)
            return
        
        if isinstance(_user, discord.Member):
            if _user.guild_permissions.administrator or CONFIG.isOwner(_user.id):
                cmds += [
                    "Admin commands (server specific):",
                    "/permissions enable-ai",
                    "/permissions enable-ai-per-channel",
                    "/moderation ban-ai",
                    "/moderation unban-ai",
                    "/moderation ai-banned-users"
                ]
            
        if CONFIG.isOwner(_user.id):
            cmds += [
                "Owner commands:",
                "/reload-cogs",
                "/reload-configs",
                "/ai-set-ping-reply",
                "/global-flush",
                "/ai-kill",
                "/global-moderation ban-ai",
                "/global-moderation unban-ai",
                "/global-moderation ai-banned-users"
            ]
        if CONFIG.isTrusted(_user.id):
            cmds += [
                "Trusted commands:",
                "/set-model",
                "/ai-system-prompt",
                "/get-memory",
                "/force-change-status"
            ]
        
        cmds += [
            "User commands:",
            "/help",
            "/ai",
            # "/dyrs",
            "/linux-icbm",
            "/getUserRole",
            "/cattify",
            "/true-or-false"
        ]
        
        s: str
        for s in cmds:
            if s.startswith("/"): # is a command
                ret += f"- `{s}`\n"
            else:
                ret += f"## {s}\n"
            
        await ctx.respond(embed=discord.Embed(
            title="Help",
            description=ret,
            footer=None if user == ctx.author else discord.EmbedFooter(f"As {_user.display_name}", _user.display_avatar.url)
            ), ephemeral=not ctx.can_send())
    
    @discord.slash_command(
        name="get-role",
        description="Get's the role of someone (gemingbot role)",
        integration_type=INTEGRATION_TYPES
    )
    @discord.option(
        name="user",
        input_type=discord.User,
        required=False
    )
    async def getUserRole(self, ctx: Context, user: Optional[discord.User]):
        if user == None: user = cast(discord.User, ctx.author)
        
        usrRole = "user"
        
        if CONFIG.isOwner(user.id):
            usrRole = "owner"
        elif CONFIG.isTrusted(user.id):
            usrRole = "trusted"
        
        if user.id == 729671931359395940: # geming
            usrRole = f"Your local furry transfem lesbian ({usrRole})"
        if user.id == 1204083604636827688: # cao
            usrRole = f"cao :333 Mrreow >w< ({usrRole})"
        elif user.id == 782022246284656680: # popcorn
            usrRole = f"Popcorn? He's literally food :3 ({usrRole})"
        elif user.id == 1159650088038170635: # lynar
            usrRole = f"Lynar :333333 mrprp >w< ({usrRole})"
        elif user.id == 1072494833777782805 or user.id == 1237908486638276802: # bonzai / silly billy (aka gay dudes)
            usrRole = f"gay role ({usrRole})"
        elif user.id == 1045761412489809975 or user.id == 940959889126219856: # tjc / bonzai
            usrRole = f"trans role :333 ({usrRole})"
        elif user.bot:
            if user.id == cast(discord.ClientUser, self.bot.user).id:
                usrRole = f"gay af bot"
            else:
                usrRole = f"It's literally a bot, what did you expect {ctx.author.display_name} ?"
            
        
        await ctx.respond(embed=discord.Embed(
            title=f"{user.name}'s role",
            description=f"{user.mention}'s role is **`{usrRole}`**",
            footer=discord.EmbedFooter(user.display_name, user.display_avatar.url)
        ), allowed_mentions = discord.AllowedMentions.none())
        
    
    @commands.Cog.listener(once=True)
    async def on_ready(self):
        if CONFIG.getStatuses():
            Loggers.logger.debug("Starting task 'changeStatusTask'")
            self.changeStatusTask.start()
    
    async def changeStatus(self):
        Loggers.logger.debug("Changing status")
    
        statuses = CONFIG.getStatuses()
        if statuses:
            await statuses.setRandomStatus(self.bot)
    
    @tasks.loop(seconds=CONFIG.getStatuses().frequency) # pyright: ignore[reportOptionalMemberAccess]
    async def changeStatusTask(self):
        if not self.bot.is_ready():
            Loggers.logger.debug("Cannot change status due to the bot still not being logged in")
            return
        
        await self.changeStatus()
    
    if CONFIG.getStatuses():
        @discord.slash_command(name="force-change-status", description="Force changes the status of gemingbot")
        @discord.option(
            name="safe",
            input_type=bool,
            default=False,
            description="If set to `True`, it'll not restart the `MainBot.changeStatusTask`. Instead it'll just change it"
        )
        # @discord.option(
        #     name="status",
        #     input_type=str,
        #     required=False,
        #     autocomplete=discord.utils.basic_autocomplete(CONFIG.getStatuses().getFormattedStatusesAsStrList()) # pyright: ignore[reportOptionalMemberAccess]
        # )
        async def forceChangeStatus(self, ctx: Context, safe: bool):
            if not CONFIG.isTrusted(ctx.author.id):
                utils.logNoAuthorization(ctx, Loggers.logger, cmdname="/force-change-status", reason="Isn't trusted")
                await ctx.respond("No :3", ephemeral=True)
                return

            if safe:
                await self.changeStatus()
                await ctx.respond("Changed status !", ephemeral=True)
            else:
                try:
                    Loggers.logger.debug("Restarted 'changeStatusTask' task because of the command '/force-change-status'")
                    self.changeStatusTask.restart()
                    
                    await ctx.respond("Changed status !", ephemeral=True)
                except Exception as e:
                    Loggers.logger.exception(f"Caught an exception while trying to restart the task `MainBot.changeStatusTask` in command '/force-change-status': {e}")
                    await ctx.respond(embed=utils.createErrorEmbed(str(e)), ephemeral=True)
                
class MainBotButThingIdk(commands.Cog):
    def __init__(self, bot: discord.Bot):
        self.bot = bot
    
    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        if message.author.bot: return
        
        async def doReaction(): # We gotta implement the furry femboy stuff :33
            if ":3" in message.content:
                await message.add_reaction("<:colonthree:1419334742163329034>")
            elif "3:" in message.content:
                await message.add_reaction("<:threecolon:1419343595579637810>")
            elif ">w<" in message.content or ">ω<" in message.content:
                await message.add_reaction("<:regional_indicator_cuteface:1419357811237716170>")
            elif "-w-" in message.content or "-ω-" in message.content:
                await message.add_reaction("<:regional_indicator_eepingface:1419359420386644228>")
            
        if self.bot.user in message.mentions:
            # not funny uber-bot like easter egg
            pattern = r"remind .+ in \d+ ((second(|s))|(hour(|s))|(day(|s))|(month(|s))|(year(|s))) to" # uber bot ahh regex
            if re.findall(pattern, message.content, re.RegexFlag.IGNORECASE):
                await message.reply("I am not uber bot you dumbass")
                return
            
            hasVeryNotFunnyMessage = "ollama isn't running, the ai isn't currently avalaible" in message.content or "`ollama` isn't running, the ai isn't currently avalaible" in message.content
            
            if random.randint(0, 10) == 5 and not (self.bot.user in message.mentions):
                await doReaction()
            elif hasVeryNotFunnyMessage:
                await message.reply("Shut up 3:")
            elif "mreow" in message.content or "meow" in message.content:
                await message.reply("Mrpprpr >w< Mreeow :33")
            elif "purr" in message.content:
                await message.reply("Purrrrr :33")
            elif "rawr" in message.content:
                await message.reply("Meeeow :33 Mpprprp >w<")
            elif "mrrrrrph" in message.content:
                await message.reply("Mrreeow :3 Nya~ ! Purrrr >w<")
    
    # @discord.slash_command(name="sync-command-tree", description="Syncs the command tree")
    # async def syncCommandTree(self, ctx: Context):
    #     if not CONFIG.isOwner(ctx.author.id):
    #         utils.logNoAuthorization(ctx, Loggers.logger, cmdname="/sync-command-tree", reason="Isn't owner")
    #         await ctx.respond("No :3", ephemeral=True)
    #         return
        
    #     await self.bot.sync_commands()
    #     await ctx.respond(f"Synced {len(self.bot.commands)} commands !", ephemeral=True)

def setup(bot: discord.Bot):
    bot.add_cog(MainBot(bot))
    bot.add_cog(MainBotButThingIdk(bot))
    