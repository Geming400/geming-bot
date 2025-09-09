import functools
import os
from typing import Any, Optional
from jsonc_parser.parser import JsoncParser
import dotenv
import discord

from utils import SharedStorage


dotenv.load_dotenv(".env")

__all__ = [
    "Config"
]

Context = discord.ApplicationContext

class Singleton(type):
    _instances = {}
    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super(Singleton, cls).__call__(*args, **kwargs)
        return cls._instances[cls]

# TODO: make the singleton work across different modules
class Config(metaclass=Singleton):
    file: str
    content: dict[str, Any]
    
    def __init__(self) -> None:
        self.file = os.getenv("CONFIG-PATH") or "config.json"
        self.content = {}
        
        self.loadConfigFile()
        
        self._storage = SharedStorage.SharedStorage(self)
        
    @property
    def storage(self): return self._storage
    
    def loadConfigFile(self):
        self.content = JsoncParser.parse_file(self.file)
    
    def reloadConfigs(self):
        self.loadConfigFile()
        self.getSystemPrompt.cache_clear()
    
    def getLogPath(self) -> str:
        return self.content["log-path"]
    
    def getDefaultModel(self) -> Optional[str]:
        return self.content.get("default-model")
    
    def getKeepAlive(self) -> int:
        return self.content.get("keep-alive", 60*5) # default ollama value
    
    @functools.lru_cache
    def getSystemPrompt(self) -> str:
        if self.content.get("is-system-prompt-file", False):
            with open(self.content["ai-system-prompt"]) as f:
                return f.read()
        else:
            return self.content.get("ai-system-prompt", "")
        
    def getOwner(self) -> int:
        return self.content["owner-userID"]
    
    def getTrustedUsers(self) -> list[int]:
        users: list[int] = self.content.get("trusted-userIDs", [])
        users.append(self.getOwner())
        return users

    def isOwner(self, userID: int) -> bool:
        return userID == self.getOwner()
    
    def isTrusted(self, userID: int) -> bool:
        return userID in self.getTrustedUsers()
