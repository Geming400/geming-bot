import logging
import os
from typing import Final, Optional
import discord
import ollama

from utils.config import Config

__all__ = [
    "preloadModel",
    "preloadModelAsync",
    "logNoAuthorization",
    "formatAiMessages",
    "removeThinkTag",
    "createErrorEmbed",
    "CONFIG"
]

CONFIG: Final[Config] = Config()

def preloadModel(model: str):
    ollama.generate(model)
    
async def preloadModelAsync(model: str):
    await ollama.AsyncClient().generate(model)
    
def logNoAuthorization(ctx: discord.ApplicationContext, logger: logging.Logger, name: Optional[str] = None, reason: Optional[str] = None):
    logger.warning(f"User {ctx.author.name} ({ctx.author.id}) tried running command {name or '[no name provided]'} but doesn't have the permissions, reason: {reason or 'No reason provided'}")

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
    
    username = os.getenv("USERNAME")
    if username and description:
        description = description.replace(username, "")
    
    return discord.Embed(
        title="Error !",
        description=description,
        colour=discord.Colour.red()
        )


    