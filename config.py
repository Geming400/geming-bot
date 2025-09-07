import functools
from typing import Any, Optional
from jsonc_parser.parser import JsoncParser

import discord

__all__ = [
    "Config"
]

Context = discord.ApplicationContext

class Config:
    file: str
    content: dict[str, Any]
    
    def __init__(self, file: str) -> None:
        self.file = file
        self.loadConfigFile()
    
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
