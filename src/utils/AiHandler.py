import copy
from enum import Enum
from typing import Optional, cast, overload

import discord
import httpcore
import httpx
import ollama

from utils.utils import CONFIG
from utils.Loggers import Loggers

__all__ = [
    "AiHandler"
]

class AiHandler:
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
    
    def isOllamaRunning(self, host: str) -> bool:
        with httpx.Client() as client:
            try:
                client.get(f"http://{host}:11434", timeout=1.5)
                return True
            except (httpx.ConnectError, httpx.TimeoutException):
                return False
            
    async def isOllamaRunningAsync(self, host: str) -> bool:
        async with httpx.AsyncClient() as client:
            try:
                await client.get(f"http://{host}:11434", timeout=1.5)
                return True
            except (httpx.ConnectError, httpx.TimeoutException):
                return False
    
    async def isModelPreloaded(self, modelName: str, host: Optional[str] = None) -> bool:        
        for processes in await ollama.AsyncClient(host).ps():
            for model in processes[1]:
                Loggers.aiLogger.debug(f"Checking if model {model.name} is preloaded")
                if cast(ollama.ProcessResponse.Model, model).name == modelName:
                    Loggers.aiLogger.debug(f"Model {modelName} is preloaded")
                    return True
        return False
    
    def getModels(self, host: Optional[str] = None) -> list[str]:
        try:
            _models = ollama.Client(host).list()
            models: list[str] = [model["model"] for model in _models.model_dump()["models"]]
            return models
        except ConnectionError:
            return []

    async def getModelsAsync(self, host: Optional[str] = None) -> list[str]:
        try:
            _models = await ollama.AsyncClient(host).list()
            models: list[str] = [model["model"] for model in _models.model_dump()["models"]]
            return models
        except ConnectionError:
            return []
            