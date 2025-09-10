import asyncio
import functools
import random
from typing import Optional, cast
import discord
from discord.ext import commands
import httpx

from utils import utils
from utils.Loggers import Loggers
from utils.utils import CONFIG


Context = discord.ApplicationContext


aiHandler = CONFIG.storage.aiHandler


@functools.lru_cache
def getTjcsIp():
    Loggers.logger.debug("Cached tjc's ip")
    
    tjcsIp = httpx.Client().get("https://tjcsucht.net/api/ip")
    return tjcsIp.text

class MainBot(commands.Cog):
    def __init__(self, bot: discord.Bot):
        self.bot = bot
    
    @discord.slash_command(name="dyrs", description="Get dyrs' personnal infos ! (for free)")
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

    @discord.slash_command(name="anton", description="idk what this means, ask dyrs")
    async def anton(self, ctx: Context):
        if random.randint(0, 100) == 10:
            ctx.respond("https://tenor.com/view/anton-alert-r74n-gif-7263058800090359550")
        else:
            ctx.respond("anton.")

    @discord.slash_command(name="sex", description="Why.")
    @discord.option(
        "user",
        discord.User,
        description="Why..."
    )
    async def sex(ctx: Context, user: discord.User):
        await ctx.respond("https://cdn.discordapp.com/attachments/1268366668384440352/1372330251757027389/2025_23_49_53.gif?ex=68a98ee4&is=68a83d64&hm=85b8d19ac042233ff7ee14ced7e7abeed292cef893a58fa284a5624e7081f7aa&")


    @discord.slash_command(name="linux-icbm", description="Linus torvalds' own ICBM, that's it")
    @discord.option(
        "user",
        discord.User,
        description="The user to send the icmb to"
    )
    async def linux_icbm(self, ctx: Context, user: discord.User):
        await ctx.respond(f"Finding {user.mention}'s location...")
        
        try:
            await asyncio.sleep(5)
            await ctx.edit(content=f"Done! User's ip is `{getTjcsIp()}`. Sending linus torvalds ICBM...")
        except:
            await ctx.respond(f"Finding {user.mention}'s location...")
            await asyncio.sleep(5)
            await ctx.edit(content="Done! Sending linus torvalds ICBM...")
        await asyncio.sleep(3)
        await ctx.edit(content="https://cdn.discordapp.com/attachments/1268366668384440352/1372330251757027389/2025_23_49_53.gif?ex=68a98ee4&is=68a83d64&hm=85b8d19ac042233ff7ee14ced7e7abeed292cef893a58fa284a5624e7081f7aa&")

    @discord.slash_command(name="reload-configs", description="Reload the config files")
    async def reloadConfigs(self, ctx: Context):
        if not CONFIG.isOwner(ctx.author.id):
            utils.logNoAuthorization(ctx, Loggers.logger, cmdname="/reload-configs", reason="Isn't owner")
            await ctx.respond("No :3", ephemeral=True)
            return
        
        Loggers.logger.info(f"Reloading configs for user {ctx.author.name} ({ctx.author.id})")
        CONFIG.reloadConfigs()
        aiHandler.systemPrompt = CONFIG.getSystemPrompt()
        await ctx.respond("Reloaded configs !", ephemeral=True)
        
    @discord.slash_command(name="help", description="Get every commands you can access")
    async def helpCmd(self, ctx: Context):
        cmds = []
        ret = ""
        
        if CONFIG.isOwner(ctx.author.id):
            cmds += [
                "Owner commands:",
                "/reload-cogs",
                "/reload-configs",
                "/ai-set-ping-reply",
                "/global-flush",
                "/ai-kill"
            ]
        if CONFIG.isTrusted(ctx.author.id):
            cmds += [
                "Trusted commands:",
                "/set-model",
                "/ai-system-prompt",
                "/get-memory"
            ]
        
        cmds += [
            "User commands:",
            "/ai",
            "/dyrs",
            "/anton",
            "/linux-icbm",
            "/help"
        ]
        
        s: str
        for s in cmds:
            if s.startswith("/"): # is a command
                ret += f"- {s}\n"
            else:
                ret += f"## {s}\n"
            
        await ctx.respond(embed=discord.Embed(
            title="Help",
            description=ret
            ))
    
    @discord.slash_command(name="get-role", description="Get's the role of someone (gemingbot role)")
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
        elif user.id == 1204083604636827688:
            usrRole = "cao :333 Mrreow >w<"
        elif user.bot:
            usrRole = f"It's literally a bot, what did you expect {ctx.author.display_name} ?"
        
        await ctx.respond(embed=discord.Embed(
            title=f"{user.display_name}'s role",
            description=f"{user.mention}'s role is **`{usrRole}`**",
            footer=discord.EmbedFooter(user.display_name, user.display_avatar.url)
        ), allowed_mentions = discord.AllowedMentions.none())
        
        

def setup(bot: discord.Bot):
    bot.add_cog(MainBot(bot))
    