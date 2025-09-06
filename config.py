from typing import Any, Optional
import json

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
        with open(self.file) as f:
            self.content = json.load(f)
    
    def getLogPath(self) -> str:
        return self.content["log-path"]
    
    def getDefaultModel(self) -> Optional[str]:
        return self.content.get("default-model")
    
    def getOwner(self) -> int:
        return self.content["owner-userid"]
    
    def getTrustedUsers(self) -> list[int]:
        users: list[int] = self.content.get("trusted-userids", [])
        users.append(self.getOwner())
        return users

    def getRawSystemPrompt(self) -> str:
        if self.content.get("is-system-prompt-file", False):
            with open(self.content["ai-system-prompt"]) as f:
                return f.read()
        else:
            return self.content.get("ai-system-prompt", "")

    def getSystemPrompt(self, ctx: Context) -> str:
        return self.getRawSystemPrompt() \
            .replace("{author-name}", ctx.author.name) \
            .replace("{author-id}", str(ctx.author.id))

    def isOwner(self, userID: int) -> bool:
        return userID == self.getOwner()
    
    def isTrusted(self, userID: int) -> bool:
        return userID in self.getTrustedUsers()
