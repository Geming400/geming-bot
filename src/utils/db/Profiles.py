import json
from sqlite3 import Row
from typing import override

from utils.db.Profile import Profile, SqlParseType

__all__ = [
    "GuildProfile",
    "getGuildPermissionProfile",
    "UserProfile"
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
    bannedAiUsers: list[int]
    
    def __init__(self, row: Row) -> None:
        self.id = row[0]
        self.guildID = row[1]
        self.bannedAiUsers = json.loads(row[2])
        super().__init__(row)
    
    @override
    @classmethod
    def default(cls):
        return cls._default(id=None, guildID=None, bannedAiUsers=[]) # ik it breaks typing, but they will get their real value when needed
    
    @classmethod
    async def createOrGet(cls, name: int):
        return await cls._createOrGet(name, nameVar="guildID", column="guildid")
            
    @override
    def parseToSql(self, type: SqlParseType) -> str:
        return self._parseToSql(type, (
            ("guildID", self.guildID),
            ("banned_users", self.bannedAiUsers)
        ))
    
    @override
    async def save(self):
        await self._save("guildid", self.guildID)
    
    async def getPermissions(self) -> GuildPermissionsProfile:
        """Gets the permissions of this server.

        Returns:
            The server permissions contained in a `ServerPermissionsProfile` instance
        """
        
        return await GuildPermissionsProfile.createOrGet(self.guildID)
    
    
class UserProfile(Profile[int]):
    _table = "users"
    
    userID: int
    role: str
    aiBanned: bool
    
    def __init__(self, row: Row) -> None:
        self.userID = row[0]
        self.role = row[1]
        self.aiBanned = bool(row[2])
        
        super().__init__(row)
    
    @override
    @classmethod
    def default(cls):
        return cls._default(userID=None, role="user", aiBanned=False)
    
    @override
    @classmethod
    async def createOrGet(cls, name: int):
        return await cls._createOrGet(name, nameVar="userID", column="userid")
            
    @override
    def parseToSql(self, type: SqlParseType) -> str:
        return self._parseToSql(type, (
            ("userid", self.userID),
            ("role", self.role),
            ("ai_banned", self.aiBanned)
        ))
    
    @override
    async def save(self):
        await self._save("userid", self.userID)
    


async def getGuildPermissionProfile(guildID: int) -> GuildPermissionsProfile:
    """Helper method to get a `ServerPermissionsProfile` instance

    Args:
        guildID: The server ID

    Returns:
        The server permissions contained in a `ServerPermissionsProfile` instance
    """
    
    server = await GuildProfile.createOrGet(guildID)
    return await server.getPermissions()
