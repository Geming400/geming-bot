import json
from sqlite3 import Row
from typing import Optional, overload, override

from utils.db.Profile import Profile, SqlParseType
from utils.utils import CONFIG

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
    
    def __init__(self, row: Row, gotCreated: bool) -> None:
        self.guildID = row[0]
        self.ai = bool(row[1])
        self.aiChannels = json.loads(row[2])
        super().__init__(row, gotCreated)
    
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
    
    def __init__(self, row: Row, gotCreated: bool) -> None:
        self.id = row[0]
        self.guildID = row[1]
        self.bannedAiUsers = json.loads(row[2])
        super().__init__(row, gotCreated)
    
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
    
    def __init__(self, row: Row, gotCreated: bool) -> None:
        self.userID = row[0]
        self.role = row[1]
        self.aiBanned = bool(row[2])
        
        super().__init__(row, gotCreated)
    
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


class FactProfile(Profile[str]):
    _table = "facts"
    
    id: int
    fact: str
    locked: bool
    addedBy: Optional[int]
    """The userID of the one that added the fact
    """
    addedByName: Optional[str]
    """The name of the one that added the fact
    """
    
    def __init__(self, row: Row, gotCreated: bool) -> None:
        self.id = row[0]
        self.fact = row[1]
        self.locked = row[2]
        self.addedBy = row[3]
        self.addedByName = row[4]
        
        super().__init__(row, gotCreated)
    
    @override
    @classmethod
    def default(cls):
        return cls._default(id=None, fact=None, locked=False, addedBy=None, addedByName=None) # ik it breaks typing, but they will get their real value when needed
    
    @classmethod
    async def createOrGet(cls, name: str):
        return await cls._createOrGet(name, nameVar="fact", column="fact")
            
    @override
    def parseToSql(self, type: SqlParseType) -> str:
        return self._parseToSql(type, (
            ("fact", self.fact),
            ("locked", self.locked),
            ("added_by", self.addedBy),
            ("added_by_name", self.addedByName)
        ))
    
    @override
    async def save(self):
        await self._save("id", self.id)
    
    @staticmethod
    async def getFactsWithIDs() -> list[tuple[int, str]]:
        ret: list[tuple[int, str]] = []
        
        
        conn = await CONFIG.storage.db.connect()
        
        query = f"SELECT * FROM {FactProfile._table}"
        async with conn.execute(query) as cur:
            rows = await cur.fetchall()
            for row in rows:
                ret.append((row[0], row[1]))
                
        await conn.close()
        
        return ret
    
    @staticmethod
    async def getFacts() -> list[str]:
        ret: list[str] = []
        
        
        conn = await CONFIG.storage.db.connect()
        
        query = f"SELECT `fact` FROM {FactProfile._table}"
        async with conn.execute(query) as cur:
            rows = await cur.fetchall()
            for row in rows:
                ret.append(row[0])
                
        await conn.close()
        
        return ret
    
    @staticmethod
    async def addFact(fact: str):
        conn = await CONFIG.storage.db.connect()
        
        query = f"INSERT INTO `{FactProfile._table}` (`fact`) VALUES ({FactProfile.sqlObjAsStr(fact)})"
        async with conn.execute(query):
            await conn.commit()
        await conn.close()
    
    @staticmethod
    async def removeFact(fact: str):
        conn = await CONFIG.storage.db.connect()
        
        query = f"DELETE FROM `{FactProfile._table}` WHERE `fact` = {FactProfile.sqlObjAsStr(fact)}"
        async with conn.execute(query):
            await conn.commit()
        await conn.close()
        
    @staticmethod
    async def removeFactFromID(factID: int):
        conn = await CONFIG.storage.db.connect()
        
        query = f"DELETE FROM `{FactProfile._table}` WHERE `id` = {factID}"
        async with conn.execute(query):
            await conn.commit()
        await conn.close()