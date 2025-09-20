import json
from sqlite3 import Row
from typing import Optional, override
from utils.db.Profile import Profile, SqlParseType

__all__ = [
    "getServerPermissionProfile",
    "ServerProfile"
]

class ServerPermissionsProfile(Profile[int]):
    _table = "server_permissions"
    
    serverID: int
    ai: bool
    aiChannels: list[int]
    
    def __init__(self, row: Row) -> None:
        self.serverID = row[0]
        self.ai = bool(row[1])
        self.aiChannels = json.loads(row[2])
    
    @override
    @classmethod
    def default(cls):
        return cls._default(ai=True, aiChannels=[])
    
    @override
    @classmethod
    async def createOrGet(cls, name: int):
        return await cls._createOrGet(name, nameVar="serverID", column="serverid")

    @override
    def parseToSql(self, type: SqlParseType) -> str:
        return self._parseToSql(type, (
            ("serverid", self.serverID),
            ("ai", self.ai),
            ("ai_channels", self.aiChannels)
        ))
    
    @override
    async def save(self):
        await self._save("serverid", self.serverID)

class ServerProfile(Profile[int]):
    _table = "servers"
    
    id: int
    serverID: int
    
    def __init__(self, row: Row) -> None:
        self.id, self.serverID = row
    
    @override
    @classmethod
    def default(cls):
        return cls._default(id=None, serverID=None) # ik it breaks typing, but they will get their real value when needed
    
    @classmethod
    async def createOrGet(cls, name: int):
        return await cls._createOrGet(name, nameVar="serverID", column="serverid")
            
    @override
    def parseToSql(self, type: SqlParseType) -> str:
        return self._parseToSql(type, (("serverID", self.serverID), ))
    
    @override
    async def save(self):
        await self._save("serverid", self.serverID)
    
    async def getPermissions(self) -> ServerPermissionsProfile:
        """Gets the permissions of this server.

        Returns:
            The server permissions contained in a `ServerPermissionsProfile` instance
        """
        
        return await ServerPermissionsProfile.createOrGet(self.serverID)


async def getServerPermissionProfile(serverID: int) -> ServerPermissionsProfile:
    """Helper method to get a `ServerPermissionsProfile` instance

    Args:
        serverID: The server ID

    Returns:
        The server permissions contained in a `ServerPermissionsProfile` instance
    """
    
    server = await ServerProfile.createOrGet(serverID)
    return await server.getPermissions()
