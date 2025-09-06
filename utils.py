import copy
from enum import Enum
import logging
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

CONFIG: Final[Config] = Config("./config.json")

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
        
    return "Ai memory:\n" + "\n".join(ret)

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
    
    def clearMemory(self):
        self._globalMessages = []
        self._messages = {}

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
                msg.insert(0, {'role': 'system', 'content': CONFIG.getRawSystemPrompt()})
            return msg
        else:
            msg = self.globalMessages.copy()
            if self.systemPrompt:
                msg.append({'role': 'system', 'content': CONFIG.getRawSystemPrompt()})
            return msg
    
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
    