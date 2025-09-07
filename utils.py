import copy
from enum import Enum
import logging.handlers
import os
from pathlib import Path
from typing import Final, Optional, overload
import discord
import ollama

from config import Config

__all__ = [
    "preloadModel",
    "preloadModelAsync",
    "logNoAuthorization",
    "Ai"
]

CONFIG: Final[Config] = Config("./config.jsonc")

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

def createHandler(handler: logging.Handler, level: int, name: str = __name__):
    handler.setFormatter(logging.Formatter("[%(asctime)s - %(levelname)s - %(name)s] %(message)s"))
    handler.setLevel(level)
    
    return handler

def createTimedRotatingFileHandler(logPath: str, level: int, name: str = __name__):
    handler = logging.handlers.TimedRotatingFileHandler(Path(logPath) / f"{name}.log", "D", backupCount=30*3, encoding="utf-8") # we want to keep the logs for ~3 month
    return createHandler(handler, level, name)
    
def createStreamHandler(level: int, name: str = __name__):
    handler = logging.StreamHandler()
    return createHandler(handler, level, name)

def getLogger(logPath: str, level: int, name: str = __name__) -> logging.Logger:
    Path(os.path.dirname(logPath)).mkdir(parents=True, exist_ok=True)
    
    logger: Final = logging.getLogger(name)
    logger.addHandler(createTimedRotatingFileHandler(logPath, level, name))
    logger.addHandler(createStreamHandler(level, name))
    logger.setLevel(level)
    
    return logger

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

class Ai:
    class Role(str, Enum):
        SYSTEM = "system"
        ASSISTANT = "assistant"
        USER = "user"
        
    systemPrompt: str
    _globalMessages: list[dict[str, str]]
    _messages: dict[int, list[dict[str, str]]]
    
    def __init__(self, systemPrompt: str = "") -> None:
        self.systemPrompt = systemPrompt
        self.clearMemory()
    
    @overload
    def addMessage(self, role: Role, content: str, channelID: int) -> None: ...
    @overload
    def addMessage(self, role: Role, content: str) -> None: ...
    
    def addMessage(self, role: Role, content: str, channelID: Optional[int] = None):
        if channelID == None:
            self._globalMessages.append({
                "role": role.value,
                "content": content
            })
        else:
            if self._messages.get(channelID) == None: self._messages[channelID] = []
            self._messages[channelID].append({
                "role": role.value,
                "content": content
            })
    
    @overload
    def clearMemory(self): ...
    @overload
    def clearMemory(self, channelID: int): ...
    
    def clearMemory(self, channelID: Optional[int] = None):
        if channelID:
            self._messages[channelID] = []
        else:
            self._messages = {}
    
    def clearGlobalMemory(self):
        self._globalMessages

    @overload
    def getMessagesWithPrompt(self) -> list[dict[str, str]]:
        """Gets the global messages and adds the system prompt

        Returns:
            The global messages including the system prompt
        """
        ...
    @overload
    def getMessagesWithPrompt(self, channelID: int) -> list[dict[str, str]]:
        """Gets the channel dependant messages and adds the system prompt
        
        Args:
            channelID: From which channel to get the messages

        Returns:
            The channel dependant messages including the system prompt
        """
        ...
    
    def getMessagesWithPrompt(self, channelID: Optional[int] = None) -> list[dict[str, str]]:
        if channelID:
            msg = copy.deepcopy(self._messages).get(channelID, [])
            
            if self.systemPrompt:
                msg.insert(0, {'role': 'system', 'content': CONFIG.getSystemPrompt()})
            return msg
        else:
            msg = self.globalMessages.copy()
            if self.systemPrompt:
                msg.append({'role': 'system', 'content': CONFIG.getSystemPrompt()})
            return msg
    
    def getUserInfos(self, user: discord.User | discord.Member):
        """Get the user infos

        Args:
            user: The one who sent a prompt to the ai

        Returns:
            The infos that the ai needs to differentiate users
        """
        
        return f"\n(This was sent by `{user.name}` (Discord userID: `{user.id}`, mention: `{user.mention}`)"
    
    @property
    def messages(self):
        """Returns a dict of each 'messages' object inside of each channel IDs
        """
        return self._messages
    
    @property
    def globalMessages(self):
        """Returns a list of "global messages" (not channelID dependant)
        """
        return self._globalMessages
    
    
    