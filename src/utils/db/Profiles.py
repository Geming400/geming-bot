import json
from sqlite3 import Row
from typing import Optional, override

from utils.db.Profile import Profile, SqlParseType

__all__ = [
    "getGuildPermissionProfile",
    "GuildProfile"
]

class GuildPermissionsProfile(Profile[int]):
    _table = "guild_permissions"
    
    guildID: int
    ai: bool
    aiChannels: list[int]
    """The channels where ai is enabled.
    
    Note: if `self.aiChannels == []`, then ai will be enabled in **every** channels
    """
    
    def __init__(self, row: Row) -> None:
        self.guildID = row[0]
        self.ai = bool(row[1])
        self.aiChannels = json.loads(row[2])
        super().__init__(row)
    
    @override
    @classmethod
    def default(cls):
        return cls._default(ai=True, aiChannels=[])
    
    @override
    @classmethod
    async def createOrGet(cls, name: int):
        return await cls._createOrGet(name, nameVar="guildID", column="guildid")

    @override
    def parseToSql(self, type: SqlParseType) -> str:
        return self._parseToSql(type, (
            ("guildid", self.guildID),
            ("ai", self.ai),
            ("ai_channels", self.aiChannels)
        ))
    
    @override
    async def save(self):
        await self._save("guildid", self.guildID)
        
    def isChannelAuthorized(self, channelID: int) -> bool:
        """Checks if a given channel ID is marked as "authorized' (aka: ai is enabled in it)

        Args:
            channelID: The channel ID to check for

        Returns:
            If the channel is marked as authorized
        """
        
        if self.aiChannels == []: return True
        return channelID in self.aiChannels

    def isAiEnabledGlobally(self) -> bool:
        return self.ai

class GuildProfile(Profile[int]):
    _table = "guilds"
    
    id: int
    guildID: int
    
    def __init__(self, row: Row) -> None:
        self.id, self.guildID = row
        super().__init__(row)
    
    @override
    @classmethod
    def default(cls):
        return cls._default(id=None, guildID=None) # ik it breaks typing, but they will get their real value when needed
    
    @classmethod
    async def createOrGet(cls, name: int):
        return await cls._createOrGet(name, nameVar="guildID", column="guildid")
            
    @override
    def parseToSql(self, type: SqlParseType) -> str:
        return self._parseToSql(type, (("guildID", self.guildID), ))
    
    @override
    async def save(self):
        await self._save("guildid", self.guildID)
    
    async def getPermissions(self) -> GuildPermissionsProfile:
        """Gets the permissions of this server.

        Returns:
            The server permissions contained in a `ServerPermissionsProfile` instance
        """
        
        return await GuildPermissionsProfile.createOrGet(self.guildID)


async def getGuildPermissionProfile(guildID: int) -> GuildPermissionsProfile:
    """Helper method to get a `ServerPermissionsProfile` instance

    Args:
        guildID: The server ID

    Returns:
        The server permissions contained in a `ServerPermissionsProfile` instance
    """
    
    server = await GuildProfile.createOrGet(guildID)
    return await server.getPermissions()
