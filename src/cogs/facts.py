from datetime import datetime
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
        
        if datetime.now().month == 12:
            return [
                "🎄",
                "Geming is still cis and straight, but now jolly !!",
                "I'm still trans no matter what",
                "mincecraft", # yeah this is going to be a christmas exclusive fact, deal with it
                "Furries are still hella gay in christmas >w<",
                "I accept christmas cuddles !!!",
                "jolly",
                "jolly simulator 2025",
                "Error! You are **not jolly enough** to execute this command.",
                "Error! You **must be** jolly to execute this command.",
                f"Haii {slashCommandCtx.author.name} :333 I hope you're jolly !!",
                "You've been a bad girl this year 3: No cuddles for you !",
                "Fun fact: geming is a jolly furry", # oh god I hope no one gets this fact
                # let's just hope we don't get epic embed fails
                "https://tenor.com/view/cat-the-voices-jolly-christmas-gif-5774532700081404887",
                "https://cdn.discordapp.com/attachments/1368719810623438943/1444941953127944354/image0.gif?ex=692e8a8f&is=692d390f&hm=7a1ce697824e9bc1e43641c0d10ba694f37c509176c2456c29f0c6bed7990cd8&",
                "https://tenor.com/view/rage-consumes-me-christmas-santa-gif-4593896469233522859",
                "https://tenor.com/view/jiggy-jolly-get-jiggy-get-jolly-get-jolly-with-it-gif-13651478034157223092",
                "https://tenor.com/view/my-jolly-reaction-jolly-my-honest-reaction-gif-5490890317762380451",
                "https://tenor.com/view/fellow-jolly-gif-15469421991206860581",
                "https://tenor.com/view/jolly-christmas-posting-jolly-cat-christmas-this-cat-looks-at-jolly-people-gif-4925436984769801382",
                "https://tenor.com/view/black-panther-christmas-christmas-gif-version-you-are-a-jolly-fellow-you-are-a-king-gg-blackpanther-holiday-gif-4868310304434186622",
                "https://tenor.com/th/view/bnuy-caption-gif-5014866802185976204",
                "How to be jolly in 3 simple steps!\n\- Step 1: ask geming\n\- Step 2: become jolly with their permission\n\- Step 3: if they said yes, congrats !!!", # pyright: ignore[reportInvalidStringEscapeSequence]
                "Christmas\nHoliday originating in Christianity, usually December 25\nChristmas is an annual festival commemorating the birth of Jesus Christ, observed primarily on December 25 as a religious and cultural celebration among billions of people around the world. A liturgical feast central to Christianity, Christmas preparation begins on the First Sunday of Advent and it is followed by Christmastide, which historically in the West lasts twelve days and culminates on Twelfth Night... [Continued in Wikipedia](https://en.wikipedia.org/wiki/Christmas)",
                "Jolly geming !!!",
                "Listen to the voices... Spread the jolly...",
                "I will obey and spread the jolly around me",
                "I will obey and spread the ~~wokeness~~ jolly around me",
                "Stop spreading y'all wokeness, it's christmas 3:\n-# So sad I know...",
                f"Epic unjollyness fail !! Laught at {slashCommandCtx.author.mention} !! (They are {random.randint(0, 3)}/10 jolly)",
                "Silly billy has been very mean this year (they have been calling geming a transbian furry !!) and will NOT get any present this year...",
                "Have you been a good girl this year :333 Mrppprr >w<",
                "jolly meow",
                "jolly purr",
                "jolly gay",
                "jolly gemingbot",
                """
Dashing through the snow
In a one-horse open sleigh
O'er the fields we go
Laughing all the way
Bells on bob tail* ring
Making spirits bright
What fun it is to ride and sing
A sleighing song tonight!

Chorus:
Jingle bells, jingle bells,
Jingle all the way.
Oh! what fun it is to ride
In a one-horse open sleigh.
Jingle bells, jingle bells,
Jingle all the way.
Oh! what fun it is to ride
In a one-horse open sleigh.

A day or two ago,
I thought I'd take a ride
And soon, Miss Fanny Bright
Was seated by my side,
The horse was lean and lank
Misfortune seemed his lot
He got into a drifted bank
And then we got upsot*.
[Chorus]

A day or two ago,
The story I must tell
I went out on the snow,
And on my back I fell;
A gent was riding by
In a one-horse open sleigh,
He laughed as there I sprawling lie,
But quickly drove away.
[Chorus]
Now the ground is white
Go it while you're young,
Take the girls tonight
and sing this sleighing song;
Just get a bobtailed* bay
Two forty* as his speed
Hitch him to an open sleigh
And crack! you'll take the lead.
[Chorus]
"""
            ]
        else:
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
                "I'm a silly kitty >w<",
                "I'm was born in 2025",
                "Geming, coming out as trans, coming soon in your local theater...",
                "I hate silly billy because they don't think my creator is cis... 3:\n-# spoiler: they aren't mreeoow :33",
                "h",
                "Cao doing anything except admitting she's trans smh",
                "Thank you [Veiquisha](https://cdn.discordapp.com/attachments/1416099087710949386/1445523545429115163/x1cuXlI.png?ex=6930a835&is=692f56b5&hm=7dfd6e370f9324fc597afee4027df75b4dbec847d96eb91f323556b0ed157ccb&), I love you :3"
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
            await ctx.respond(
                "There has been an error while trying to remove a fact!",
                embed=utils.createErrorEmbed(f"({e.__class__.__name__}) {e}"),
                ephemeral=True
            )
            
            raise e
    
    # TODO: unbreak this command
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
            await ctx.respond(
                "There has been an error while trying to add a fact! (This command is very broken, contact geming to warn him about it)",
                embed=utils.createErrorEmbed(f"({e.__class__.__name__}) {e}"),
                ephemeral=True
            )
            
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
            christmasStuff = "\n-# Geming bot facts, now in jolly edition !" if datetime.now().month == 12 else ""
            
            for dbFact in facts:
                if choosenFact == dbFact[1]: # if the fact exists in the db (aka not hardcoded)
                    _fact = await Profiles.FactProfile.createOrGet(choosenFact)
                    if _fact.addedBy:
                        factBy = f"\n-# Fact added by {_fact.addedByName} (<@{_fact.addedBy}>)"
                    else:
                        factBy = f"\n-# Fact added by an unknown user"
                    christmasStuff = "\n-# (Not a jolly fact because it's custom fact) !" if datetime.now().month == 12 else ""
        
            
            await ctx.respond(choosenFact + factBy + christmasStuff, allowed_mentions=discord.AllowedMentions.none())
        except Exception as e:
            Loggers.factsLogger.exception(f"Caught exception while trying to get a random fact: {e}")
            await ctx.respond("There has been an error while trying to get a random fact!", embed=utils.createErrorEmbed(f"({e.__class__.__name__}) {e}"), ephemeral=True)
            
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
            await ctx.respond("There has been an error while trying to get every facts!", embed=utils.createErrorEmbed(f"({e.__class__.__name__}) {e}"), ephemeral=True)
            
            raise e

    
def setup(bot: discord.Bot):
    bot.add_cog(FactStuff(bot))
    