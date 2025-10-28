import logging
import os
from typing import Final, Optional
import discord
import ollama

from utils.Loggers import Loggers
from utils.config import Config

__all__ = [
    "preloadModel",
    "preloadModelAsync",
    "logNoAuthorization",
    "formatAiMessages",
    "removeThinkTag",
    "createErrorEmbed",
    "CONFIG",
    "INTEGRATION_TYPES"
]

CONFIG: Final[Config] = Config()

INTEGRATION_TYPES: Final[set[discord.IntegrationType]] = {
    discord.IntegrationType.guild_install,
    discord.IntegrationType.user_install,
}

def preloadModel(model: str, host: Optional[str] = None):
    Loggers.aiLogger.info(f"Preloading model {model}")
    ollama.Client(host).generate(model, keep_alive=CONFIG.getKeepAlive())
    Loggers.aiLogger.info(f"Preloaded model {model}")
    
async def preloadModelAsync(model: str, host: Optional[str] = None):
    Loggers.aiLogger.info(f"Preloading model {model} (async)")
    await ollama.AsyncClient(host).generate(model, keep_alive=CONFIG.getKeepAlive())
    Loggers.aiLogger.info(f"Preloaded model {model} (async)")
    
def logNoAuthorization(ctx: discord.ApplicationContext, logger: logging.Logger, cmdname: Optional[str] = None, reason: Optional[str] = None, stacklevel = 2):
    funcName = logger.findCaller(stacklevel=stacklevel)[2]
    logger.warning(f"User {ctx.author.name} ({ctx.author.id}) tried running command {"" if cmdname else "(from function)"} `{cmdname or funcName}` but doesn't have the permissions, reason: {reason or 'No reason provided'}")

def formatAiMessages(messages: list[dict[str, str]]) -> str:
    ret: list[str] = []
    
    for message in messages:
        ret.append(f"- ({message["role"]}) {message["content"]}")
        
    return "AI memory:\n" + "\n\n".join(ret)

def removeThinkTag(s: str) -> str:
    print(f"Removing think tags from response {s}")
    try:
        ret = s.split("</think>", 1)[1]
        return ret
    except:
        return s

def createErrorEmbed(description: Optional[str] = None):
    """Creates an error embed
    """
    
    username = os.getenv("USERNAME") # Just in case
    if username and description:
        description = description.replace(username, "")
    
    return discord.Embed(
        title="Error !",
        description=description,
        colour=discord.Colour.red()
        )

# from:
# https://stackoverflow.com/questions/18854620/whats-the-best-way-to-split-a-string-into-fixed-length-chunks-and-work-with-the
def chunkString(string: str, size: int):
    return (string[0+i : size+i] for i in range(0, len(string), size))
