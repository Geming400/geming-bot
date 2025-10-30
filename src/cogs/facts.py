import random
import tempfile
from typing import Optional, cast
import discord
from discord.ext import commands

from utils import utils
from utils.Loggers import Loggers
from utils.db import Profiles
from utils.utils import CONFIG

Context = discord.ApplicationContext


class FactStuff(commands.Cog):
    factGroup = discord.SlashCommandGroup(
        "facts",
        description="Facts related commands"
    )
        
    def __init__(self, bot: discord.Bot):
        self.bot = bot
    
    def getCustomFacts(self, slashCommandCtx: Context) -> list[str]:
        # the original facts
        # I'm keeping them harcoded
        return [
            "Geming is cis",
            "I am a bot",
            "I am trans",
            "I am a furry",
            "I was made by geming400\n-# (who could've guessed)",
            f"I am {cast(discord.ClientUser, self.bot.user).mention}",
            f"I have {len(self.bot.commands) + random.randint(-2, 2)} commands I think. I might have gotten the number wrong",
            "help",
            "I, gemingbot, came out as trans when I was born because being cis is lame ass !!!!",
            "I am in geming's basement",
            "I'm in love with the concept",
            "Geming's pronouns are not she/her",
            "Geming's pronouns are not she/they",
            "Geming is not trans smh",
            "Geming is not a furry smh",
            "Geming is not lesbian smh"   ,
            "Geming's github is <https://github.com/Geming400/>",
            "I am self aware actually",
            "Geming is NOT genderfluid, skepper",
            "I play gd idfk",
            "I'm gay",
            "-# Don't tell geming but he's actually gay, he just doesn't know yet",
            f"I'm better than {slashCommandCtx.author.mention}",
            f"You are {slashCommandCtx.author.mention} :333",
            "I'm literally geming but better",
            "I am better that chat-gpt",
            "geming's pronouns are actually `he/any` :3",
            "I'm a silly kitty >w<"
        ]
    
    async def getFactsAutocomplete(self, ctx: discord.AutocompleteContext):
        ret: list[str] = []
        
        facts = await Profiles.FactProfile.getFactsWithIDs()
        if not facts:
            return ["No non harcoded facts found !"]
        
        for fact in facts:
            factID, factContent = fact
            ret.append(f"[{factID}] {factContent}")
        
        return ret

    async def getFactsIDAutocomplete(self, ctx: discord.AutocompleteContext):
        ret: list[str] = []
        
        facts = await Profiles.FactProfile.getFactsWithIDs()
        if not facts:
            return []
        
        for fact in facts:
            factID, factContent = fact
            ret.append(f"{factID}")
        
        return ret
    
    async def getFactFromAutocomplete(self, factFormatted: str) -> Optional[tuple[int, str]]:
        # extra check to not query the database when no facts were found
        if not ("[" in factFormatted): return None
        facts = await Profiles.FactProfile.getFactsWithIDs()
        
        for fact in facts:
            factID, factContent = fact
            if factFormatted == f"[{factID}] {factContent}":
                return fact
        
        return None
    
    async def getFactFromID(self, factID: int) -> Optional[tuple[int, str]]:
        facts = await Profiles.FactProfile.getFactsWithIDs()
        
        for fact in facts:
            _factID, _factContent = fact
            if _factID == factID:
                return fact
        
        return None
    
    @factGroup.command(name="remove", description="Get every gemingbot facts")
    @discord.option(
        name="fact",
        description="The fact's to delete",
        input_type=str,
        autocomplete=getFactsAutocomplete,
        required=False
    )
    @discord.option(
        name="fact_id",
        description="The fact's ID to delete (see '/fact get-facts')",
        input_type=int,
        autocomplete=getFactsIDAutocomplete,
        required=False
    )
    async def removeFact(self, ctx: Context, fact: Optional[str], fact_id: Optional[int]):
        if not CONFIG.canEditFacts(ctx.author.id):
            utils.logNoAuthorization(ctx, Loggers.logger, cmdname="/fact remove", reason="Cannot edit facts")
            await ctx.respond("No :3", ephemeral=True)
            return
        
        if fact == None and fact_id == None:
            await ctx.respond("You must set a value for either the parameter `fact` or `fact_id` !", ephemeral=True)
            return
        elif fact != None and fact_id != None:
            await ctx.respond("You cannot set a value for both parameter `fact` and `fact_id` !", ephemeral=True)
            return
        
        try:
            _fact: tuple[int, str]
            if fact:
                foundFact = await self.getFactFromAutocomplete(fact)
                if foundFact:
                    _fact = foundFact
                else:
                    Loggers.factsLogger.info(f"Tried getting fact from autocomplete ('{fact}') but failed")
                    await ctx.respond(f"Tried getting fact from autocomplete (`{fact}`) but failed, **does the fact exist** ?", ephemeral=True)
                    return
            else:
                foundFact = await self.getFactFromID(cast(int, fact_id))
                if foundFact:
                    _fact = foundFact
                else:
                    Loggers.factsLogger.info(f"Tried getting fact from the fact ID ('{fact_id}') but failed")
                    await ctx.respond(f"Tried getting fact from the fact ID (`{fact_id}`) but failed, **does the fact exist** ?", ephemeral=True)
                    return
            
            Loggers.factsLogger.info(f"Removing fact '{_fact[1]}' with ID '{_fact[0]}' for user {ctx.author.name} ({ctx.author.id})")
            await Profiles.FactProfile.removeFactFromID(_fact[0])
            
            await ctx.respond(f"Sucessfully removed fact `{_fact[1]}` with ID `{_fact[0]}` !", ephemeral=True)
        except Exception as e:
            Loggers.factsLogger.exception(f"Caught exception while trying to remove a fact: {e}")
            await ctx.respond("There has been an error while trying to remove a fact!", embed=utils.createErrorEmbed(f"({e.__class__.__name__}) {e}"))
            
            raise e
    
    @factGroup.command(name="add", description="Add a fact to gemingbot")
    @discord.option(
        name="fact",
        description="The fact to add",
        input_type=str
    )
    async def addFact(self, ctx: Context, fact: str):
        if not CONFIG.canEditFacts(ctx.author.id):
            utils.logNoAuthorization(ctx, Loggers.logger, cmdname="/fact add", reason="Cannot edit facts")
            await ctx.respond("No :3", ephemeral=True)
            return
        
        Loggers.factsLogger.info(f"Adding fact '{fact}' for user {ctx.author.name} ({ctx.author.id})")
        
        try:
            facts = await Profiles.FactProfile.getFacts()
            
            if len(fact) >= 250:
                await ctx.respond("Your fact has too much characters (exceeded limit of **250 characters**)", ephemeral=True)
                return
            
            if fact == "":
                await ctx.respond("You cannot create an empty fact !", ephemeral=True)
                return
            
            if fact.lower() in [_fact.lower() for _fact in facts]:
                await ctx.respond("This fact is already in gemingbot !", ephemeral=True)
                return
            
            dbFact = await Profiles.FactProfile.createOrGet(fact)
            dbFact.fact = fact # useless but just for clarity
            
            dbFact.addedBy = ctx.author.id
            dbFact.addedByName = ctx.author.name
            
            await dbFact.save()
            
            await ctx.respond(f"sucessfully added fact `{fact}` !", ephemeral=True)
        except Exception as e:
            Loggers.factsLogger.exception(f"Caught exception while trying to add fact: {e}")
            await ctx.respond("There has been an error while trying to add a fact!", embed=utils.createErrorEmbed(f"({e.__class__.__name__}) {e}"))
            
            raise e
        
    @factGroup.command(name="get", description="Gets a random gemingbot fact !")
    async def getFact(self, ctx: Context):
        Loggers.factsLogger.info(f"Getting random fact for user {ctx.author.name} ({ctx.author.id})")
        
        try:
            customFacts = self.getCustomFacts(ctx)
            facts = await Profiles.FactProfile.getFactsWithIDs()
            factsContent: list[str] = [fact[1] for fact in facts]
            if not factsContent and not customFacts:
                await ctx.respond("Geming bot has no fact 3:", ephemeral=True)
                return
            
            factsContent += customFacts
            
            choosenFact = random.choice(factsContent)
            
            factBy = ""
            
            for dbFact in facts:
                if choosenFact == dbFact[1]: # if the fact exists in the db (aka not hardcoded)
                    _fact = await Profiles.FactProfile.createOrGet(choosenFact)
                    if _fact.addedBy:
                        factBy = f"\n-# Fact added by {_fact.addedByName} (<@{_fact.addedBy}>)"
                    else:
                        factBy = f"\n-# Fact added by an unknown user"
            
            await ctx.respond(choosenFact + factBy, allowed_mentions=discord.AllowedMentions.none())
        except Exception as e:
            Loggers.factsLogger.exception(f"Caught exception while trying to get a random fact: {e}")
            await ctx.respond("There has been an error while trying to get a random fact!", embed=utils.createErrorEmbed(f"({e.__class__.__name__}) {e}"))
            
            raise e

    @discord.slash_command(name="fact", description="Gets a random gemingbot fact !")
    async def oldGetFact(self, ctx: Context):
        await self.getFact(ctx)
        
    @factGroup.command(name="get-facts", description="Get every gemingbot facts")
    @discord.option(
        name="as_file",
        description="If there's too much facts to be send on discord, send the facts as messages or as a file ?",
        input_type=bool,
        default=True
    )
    @discord.option(
        name="no_hardcoded_facts",
        description="If set to `True`, only manually added facts will be outputted",
        input_type=bool,
        default=False
    )
    async def getFacts(self, ctx: Context, as_file: bool, no_hardcoded_facts: bool):
        Loggers.factsLogger.info(f"Getting facts for user {ctx.author.name} ({ctx.author.id})")
        
        try:
            customFacts = self.getCustomFacts(ctx)
            facts = await Profiles.FactProfile.getFactsWithIDs()
            if no_hardcoded_facts:
                if not facts:
                    await ctx.respond("Geming bot has no manually added fact 3:", ephemeral=True)
                    return
            else:
                if not facts and not customFacts:
                    await ctx.respond("Geming bot has no fact 3:", ephemeral=True)
                    return
            
            ret = "Here are gemingbot's facts:\n```"
            
            facts.reverse()
            for fact in facts:
                factID, factContent = fact
                ret += f"- [{factID}] {factContent}\n"
            if not no_hardcoded_facts:
                for customFact in customFacts:
                    ret += f"- [HARDCODED] {customFact}\n"
            ret += "```"
            
            if len(ret) > 2000:
                if as_file: # send as a file
                    tmpfile = tempfile.TemporaryFile(delete_on_close=False)
                    tmpfile.write(ret.encode())
                    tmpfile.close()
                    
                    file = discord.File(
                        fp=tmpfile.name,
                        filename="output.txt",
                        description=f"The system prompt of geming bot"
                    )
                    
                    await ctx.respond(
                        content=f"Here are gemingbot's facts:",
                        file=file,
                        ephemeral=True
                    )
                    
                    tmpfile._closer.cleanup()
                else: # send messages in chunks
                    for s in utils.chunkString(ret, 2000):
                        await ctx.respond(s, ephemeral=True)
            else:
                await ctx.respond(ret, ephemeral=True)
        except Exception as e:
            Loggers.factsLogger.exception(f"Caught exception while trying to get every facts: {e}")
            await ctx.respond("There has been an error while trying to get every facts!", embed=utils.createErrorEmbed(f"({e.__class__.__name__}) {e}"))
            
            raise e

    
def setup(bot: discord.Bot):
    bot.add_cog(FactStuff(bot))
    