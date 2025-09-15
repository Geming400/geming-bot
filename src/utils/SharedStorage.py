import functools
import os
from pathlib import Path
from typing import TYPE_CHECKING, Optional, Type, TypeVar, cast
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
    _connection: Optional[sqlite3.Connection]
    
    def __init__(self, dbPath: str) -> None:
        self.dbPath = dbPath
        self._connection = None
        
        print(f"Creating path {os.path.dirname(dbPath)} if it doesn't exist")
        Path(os.path.dirname(dbPath)).mkdir(parents=True, exist_ok=True)
    
    @property
    def connection(self) -> sqlite3.Connection:
        if self._connection: return self._connection
        
        try:
            self._connection = sqlite3.connect(self.dbPath)
            return self._connection
        except sqlite3.OperationalError as e:
            print(f"Failed to open db: {e}")
            print("If the db wasn't created yet, you might need to relaunch the bot")
            raise e

    @functools.cached_property
    def cursor(self) -> sqlite3.Cursor:
        return self.connection.cursor()
    
    def checkIfDbExists(self):
        try:
            self.connection
            return True
        except:
            return False
    

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
        self.aiHandler.systemPrompt = self.config.getSystemPrompt()