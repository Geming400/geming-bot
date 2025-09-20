import os
from pathlib import Path
from typing import TYPE_CHECKING, Optional, Type, TypeVar, cast
import aiosqlite
import sqlite3

import discord

__all__ = [
    "SharedStorage"
]

T = TypeVar('T', default=object)

if TYPE_CHECKING:
    import utils.AiHandler as AiHandler
    import utils.config as _config


class _Db:
    """A class to manage the database, it's part of the `SharedStorage`
    """
    
    dbPath: str
    _connection: Optional[aiosqlite.Connection]
    
    def __init__(self, dbPath: str) -> None:
        self.dbPath = dbPath
        self._connection = None
        
        Path(os.path.dirname(dbPath)).mkdir(parents=True, exist_ok=True)
    
    async def connect(self) -> aiosqlite.Connection:
        if self._connection != None: return self._connection
        
        try:
            self._createDbFile()
            self._connection = await aiosqlite.connect(self.dbPath)
            return self._connection
        except aiosqlite.OperationalError as e:
            print(f"Failed to open db: {e}")
            print("If the db wasn't created yet, you might need to relaunch the bot")
            raise e

    async def close(self):
        if self._connection: await self._connection.close()
    
    def _createDbFile(self):
        connection = sqlite3.connect(self.dbPath)
        connection.close()
    
    @property
    def exists(self) -> bool:
        return os.path.exists(self.dbPath)
    
    async def initDB(self):
        """Inits the db, aka, create the tables and stuff
        """
        conn = await self.connect() # creating the db

        currentFolder = Path(__file__).parent.resolve()
        path = currentFolder.parent / "db-init"
        
        items = os.scandir(path.absolute())
        for item in items:
            if item.is_file() and Path(item.path).suffix == ".sql":
                print(f"Executing sql file {item.path}")
                cur = await conn.executescript(open(item.path).read())
                await cur.close()
        
        print(f"Commiting")
        await conn.commit()
    

    

class SharedStorage:
    """A shared storage
    This is not related to the config file, but more to the bot itself
    """
    
    storage: dict[str, object]
    config: "_config.Config"
    
    # -- custom members --
    
    _aiHandler: Optional["AiHandler.AiHandler"]
    currentModel: str
    aiPingReply: discord.AllowedMentions
    db: _Db
    
    # -- custom members --
    
    def __init__(self, config: "_config.Config") -> None:
        self.storage = {}
        self.config = config
        
        # -- custom members --
        
        self._aiHandler = None
        self.currentModel = self.config.getDefaultModel() or "hermes3"
        self.aiPingReply = discord.AllowedMentions.none()
        self.db = _Db(self.config.getDbPath())
        
        # -- custom members --
    
    
    # -- custom members --
    
    @property
    def aiHandler(self):
        if self._aiHandler:
            return self._aiHandler
        else:
            import utils.AiHandler as AiHandler
            
            self._aiHandler = AiHandler.AiHandler(self.config.getSystemPrompt())
            return self._aiHandler
    
    # -- custom members --
    
    def set(self, name: str, val: object):
        self.storage[name] = val
    
    def get(self, name: str, _type: T) -> Optional[T]:
        return cast(T, self.storage.get(name))
    
    def getUnwrap(self, name: str, _type: Type[T]) -> T:
        return cast(T, self.storage[name])
    
    def getUnwrapOr(self, name: str, default: T) -> T:
        return cast(T, self.storage[name] or default)
    
    def getUnwrapOrDefault(self, name: str, _type: Type[T]) -> T:
        return cast(T, self.storage[name] or type(_type)())
    
    def reload(self):
        """Reload the storage, this will get called in `Config.reloadConfigs()`
        """
        self.aiHandler.systemPrompt = self.config.getSystemPrompt()