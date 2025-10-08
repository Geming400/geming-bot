import asyncio
from concurrent.futures import ThreadPoolExecutor
from enum import Enum
import functools
import glob
import hashlib
import io
from pathlib import Path
import random
import string
import tempfile
from typing import Final, Optional, cast
import PIL
import discord
from discord.ext import commands
from PIL import Image
import ntpath
import validators

import httpx

from utils import utils
from utils.Loggers import Loggers

Context = discord.ApplicationContext


def checkIfSameSize(images: list[Image.Image]) -> bool:
    sizes = set([img.size for img in images])
    return len(sizes) == 1 # a set removes every duplicates

def getFilename(path: str) -> str:
    head, tail = ntpath.split(path)
    return tail or ntpath.basename(head)

class DICT_LAYER_ENUM(str, Enum):
    CAT_OUTLINE = "cat-outline"
    CAT_FEATURES = "cat-features"
    CAT_EARS = "cat-ears"
    
LAYERS_FOLDER_PATH: Final[str] = "./resources/woke-ass-cat-maker"
PREGENERATED_CATS_FOLDER: Final[str] = f"{LAYERS_FOLDER_PATH}/cats"
LAYERS: Final[dict[DICT_LAYER_ENUM, str]] = {
    DICT_LAYER_ENUM.CAT_OUTLINE: f"{LAYERS_FOLDER_PATH}/cat-outline.png",
    DICT_LAYER_ENUM.CAT_FEATURES: f"{LAYERS_FOLDER_PATH}/cat-features.png",
    DICT_LAYER_ENUM.CAT_EARS: f"{LAYERS_FOLDER_PATH}/cat-ears.png"
}
"""Those are the layers that will be added to the first image
"""


class SillyStuff(commands.Cog):
    def __init__(self, bot: discord.Bot):
        self.bot = bot
    
    @functools.lru_cache
    @staticmethod
    def getPregeneratedCats(ctx: Optional[discord.AutocompleteContext]): # We've set the `AutocompleteContext` as optional because of `SillyStuff.getCat`
        cats = glob.glob(f"{PREGENERATED_CATS_FOLDER}/*.png")
        ret: list[str] = []
        
        for cat in cats:
            ret.append(
                Path(cat).stem.removesuffix("cat")
            )
            
        return ret
    
    @functools.lru_cache
    @staticmethod
    def getCat(flagName: str) -> Optional[str]:
        """Gets a woke ass cat from a flag

        Args:
            flagName: The name of the flag

        Returns:
            The path of the woke ass cat
        """
        
        for wokecat in SillyStuff.getPregeneratedCats(None):
            if flagName == wokecat:
                return f"{PREGENERATED_CATS_FOLDER}/{wokecat}cat.png"
        
        return None # not needed but it's just for readability
    
    @staticmethod
    def generateCattifyImg(
            img_layers: dict[DICT_LAYER_ENUM, Image.Image],
            # imgName: str,
            imageURL: str,
            req: httpx.Response
        ) -> tuple[Path, bool]:
        
        base_img = Image.open(io.BytesIO(req.content)).convert('RGBA')
        originalBaseImgSize = base_img.size
        
        catImgSize: tuple[int, int] = img_layers[DICT_LAYER_ENUM.CAT_OUTLINE].size
        base_img = base_img.resize(catImgSize)
        
        
        # merging the images
        Loggers.logger.info("Merging the images")

        finalImage = Image.composite(
            Image.new('RGBA', catImgSize, (0, 0, 0, 0)),
            base_img,
            img_layers[DICT_LAYER_ENUM.CAT_OUTLINE]
        ).convert('RGBA')
        finalImage.alpha_composite(img_layers[DICT_LAYER_ENUM.CAT_FEATURES])
        finalImage.alpha_composite(img_layers[DICT_LAYER_ENUM.CAT_EARS])
        
        if tempfile.tempdir:
            dir = Path(tempfile.tempdir)
        else:
            dir = Path("./cattify-tempfile")
            dir.mkdir(parents=True, exist_ok=True)
        
        salt = "".join(random.choices(string.ascii_letters, k=10))
        outputPath = Path(dir) / (hashlib.sha1(imageURL.encode() + salt.encode()).hexdigest() + ".png")
        outputPath.resolve()
        
        Loggers.logger.info(f"Writing image to path {outputPath}")
        finalImage.save(outputPath)
        
        # await ctx.interaction.edit_original_response(
        #     content="Cattified !",
        #     file=discord.File(outputPath, filename=f"{imgName}-cat.png", description="The cattified image")
        # )
        # outputPath.unlink()
        
        return (outputPath, originalBaseImgSize[0] == originalBaseImgSize[1])
    
    @discord.slash_command(name="cattify", description="Cattifies an image")
    @discord.option(
        name="image",
        description="The image to cattify, you can use someone's pfp instead ('user' arg)",
        input_type=discord.Attachment,
        required=False
    )
    @discord.option(
        name="url",
        description="The url of the image to cattify",
        input_type=str,
        required=False
    )
    @discord.option(
        name="user",
        description="The user's pfp to cattify",
        input_type=discord.User,
        required=False
    )
    @discord.option(
        name="flag",
        description="The woke flag to cattify",
        input_type=str,
        autocomplete=getPregeneratedCats,
        required=False
    )
    async def cattify(self, ctx: Context, image: Optional[discord.Attachment], url: Optional[str], user: Optional[discord.User], flag: Optional[str]):
        @functools.lru_cache
        def getImageLayers() -> dict[DICT_LAYER_ENUM, Image.Image]:
            img_layers: dict[DICT_LAYER_ENUM, Image.Image] = {}
            for feature_name, layer in LAYERS.items():
                img_layers[feature_name] = Image.open(layer).convert('RGBA') # Converting a "RBG" image to a "RGBA" image
                
            if not checkIfSameSize(cast(list[Image.Image], img_layers.values())):
                Loggers.logger.warning("Some layers are not of the same size ! Might cause unwanted issues.")
            
            return img_layers
        
        MAX_PARAMS: Final[int] = 4
        if (user, image, flag, url).count(None) < MAX_PARAMS - 1:
            await ctx.respond("You cannot provide values for the `image`, `user` or `flag` arguments at the same time !", ephemeral=True)
            return
        
        if (user, image, flag, url).count(None) == MAX_PARAMS:
            await ctx.respond("You must at least provide a value for the arguments `image`, `user` or `flag` !", ephemeral=True)
            return
        
        imgUrl: str
        if image:
            imgUrl = image.url
        elif user:
            imgUrl = user.display_avatar.url
        elif url:
            _url: Optional[str] = None
            if not validators.url(url):
                Loggers.logger.info(f"Url {url} is not a valid url, fallbacking to appending the 'https' scheme and removing '&' at the end (if possible)")
                
                # fallbacking to 'https' and removing `&`
                _url = url.removesuffix("&")
                if not validators.url(_url):
                    Loggers.logger.info(f"New url {_url} is still not validated after removing the `&` suffix, appending the 'https' scheme")
                    _url = f"https://{url}"
                    
                    if not validators.url(_url):
                        Loggers.logger.info(f"New url {_url} is still not validated after appending the 'https' scheme, removing the `&` suffix")
                        _url = _url.removesuffix("&")
            
            
            if not validators.url(_url or url):
                Loggers.logger.info(f"Url {_url or url} was never sucessfully validated")
                
                await ctx.respond(f"""The given url (`{url}`) is not a valid one !
-# Tried to ignore this by **appending the `https` url scheme** and **removing `&` at the end of the url** (if possible)""", ephemeral=True)
                return
            
            imgUrl = _url or url
        else:
            wokecatPath = SillyStuff.getCat(flag)
            if wokecatPath:
                Loggers.logger.info(f"Getting pregenerated cat with flag {flag} and path {wokecatPath} for user {ctx.author.name} ({ctx.author.id})")
                
                file = discord.File(wokecatPath, description=f"The pre-generated woke cat (flag = {flag})")
                await ctx.respond(f"Cattified !\n-# Cattified `{flag} flag`", file=file)
            else:
                await ctx.respond(f"The given flag (`{flag}`) is not present in the `flags` list !", ephemeral=True)
            
            return
        
        Loggers.logger.info(f"Preparing the images for 'cattification' for user {ctx.author.name} ({ctx.author.id})")
    
        img_layers = getImageLayers()
        
        imgName = Path(imgUrl.split("?", 1)[0]).name # yeah I know i'm using a Path object for an url but shhh
        Loggers.logger.info(f"Downloading image '{imgName}'")
        req = await httpx.AsyncClient().get(imgUrl)
        if req.is_error:
            msg = f"Discord responsded with status code code {req.status_code} while trying to download the {imgName} img"
            Loggers.logger.warning(msg)
            await ctx.respond(emed=utils.createErrorEmbed(msg), ephemeral=True)
            return
        
        await ctx.respond("Processing...")
        
        future = asyncio.get_event_loop().run_in_executor(ThreadPoolExecutor(), SillyStuff.generateCattifyImg,
                                                 img_layers,
                                                 # imgName,
                                                 imgUrl,
                                                 req
                                                 )
        
        def onDone(ft: asyncio.Future[tuple[Path, bool]]):
            async def sendMsg():
                try:
                    outputPath, isImgSquaredShape = ft.result()
                except PIL.UnidentifiedImageError:
                    await ctx.edit(content="", embed=utils.createErrorEmbed(f"The given image (`{imgName}`) is not a valid image !"))
                    return
                except Exception as e:
                    await ctx.edit(content="", embed=utils.createErrorEmbed(f"There was an error while trying to process your image: ({e.__class__.__name__}) {e}"))
                    return
                
                notes = {
                    "" if isImgSquaredShape else "-# The image got resized because it wasn't a square",
                    f"-# Cattified {user.mention}'s pfp" if user else ""
                }
                if "" in notes: notes.remove("")
                
                await ctx.interaction.edit_original_response(
                    content="Cattified !\n" + "\n".join(notes),
                    file=discord.File(outputPath, filename=f"{imgName}-cat.png", description="The cattified image"),
                    allowed_mentions=discord.AllowedMentions.none()
                )
                outputPath.unlink()
            
            asyncio.create_task(sendMsg())
            
        future.add_done_callback(onDone)
    
    @discord.slash_command(name="true-or-false", description="Confirms if a message is true or false !!")
    @discord.option(
        name="msg",
        description="What to confirm",
        input_type=str
    )
    async def trueOfFalse(self, ctx: Context, msg: str):
        if "trans" in msg:
            if "not" in msg or "nt" in msg or "n't" in msg:
                response = "true"
            else:
                response = "false"
        else:
            response = random.Random(msg.lower()).choice(("true", "false"))
        
        await ctx.respond(f"`{msg.replace("`", "\\`")}` is {response} :33")
        
def setup(bot: discord.Bot):
    bot.add_cog(SillyStuff(bot))
    