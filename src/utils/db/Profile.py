import abc
import asyncio
from enum import Enum
import sqlite3
from typing import Any, Generic, Optional, Self, Type, TypeVar, overload
import json

import aiosqlite

from utils.utils import CONFIG


__all__ = [
    "Profile"
]

T = TypeVar('T')

class SqlParseType(Enum):
    SET = 0
    """Example: `SET foo = 'hi', foo2 = 'hii but cooler'`
    """
    VALUES = 1
    """Example: `VALUES('val 1', 'val 2')`
    """
    VALUES_COLUMNS = 2
    """Example: `(row1, row2) VALUES('val 1', 'val 2')`
    """

class Profile(Generic[T]):
    """A profile linked to the db, needs to be subclasses and can be anything.
    It's used to easily parse data from the sqlite database and parse the data of `self` to the sqlite database.
    
    Note: When subclassing, `_table`, `__init__`, `createOrGet()`, `default()`, `save()` and `parseToSql()` must be **overriden**.
    
    Note: Each functions (except `__init__`) will have a helper method associated to it (eg: `createOrGet()` -> `_createOrGet()`)
    """
    
    _table: str # to be overriden
    
    @abc.abstractmethod
    def __init__(self, row: sqlite3.Row) -> None:
        """The init function, must **NOT** be called, use `.createOrGet()` instead.
        Also, if you are subclassing this class and implementing `.__init__()`, do not call `super().__init__()`, as it will do nothing

        Note:
            When overriding, you **must parse the `row` arg** according to the **db's table**

        Args:
            row: The row
        """
        ...
    
    @classmethod
    def _default(cls, **kwargs) -> Self:
        """An helper for `.default()`

        Args:
            obj: the object to set the attributes
        """
        
        inst = cls.__new__(cls)
        for name, val in kwargs.items():
            setattr(inst, name, val)
        
        return inst
        
    
    @classmethod
    @abc.abstractmethod
    def default(cls) -> Self:
        """Gets the default object of `Self`.
        Note: This is basically `.__init__`'s implementation except it **just creates the member**.

        Returns:
            An object of type `Self` with the default values
        """
        
        return cls.__new__(cls) # default implementation
        
    
    @staticmethod
    def sqlObjAsStr(obj: Any) -> str:
        """Turns a given object into one readable by SQL

        Args:
            obj: the obj

        Returns:
            The object but readable to the SQL language (eg: `"test"` -> `"'test'"`)
        """
        
        if isinstance(obj, str): return f"'{obj}'"
        if isinstance(obj, (dict, list)): return f"'{json.dumps(obj)}'"
        if isinstance(obj, (set)): return f"'{json.dumps(list(obj))}'"
        if isinstance(obj, bool): return str(int(obj))
        
        return str(obj)
    
    async def _createToDb(self):
        """Creates the current object into the db
        """
        
        conn = await CONFIG.storage.db.connect()
        
        query = f"INSERT INTO `{self._table}` " + self.parseToSql(SqlParseType.VALUES_COLUMNS)
        async with conn.execute(query):
            await conn.commit()
    
    @classmethod
    async def _createOrGet(cls, name: T, nameVar: str, column: str = "id") -> Self:
        """Helper for the `.createOrGet()` function

        Args:
            name: the name of what to fetch, eg: A server ID (most of the time the primary key)
            nameVar: the var in `Self` that contains the value of `name`
            column: the sql column used to know where to fetch (`WHERE {column} = {var}`)

        Returns:
            An object of type `Self`
        """
        
        conn = await CONFIG.storage.db.connect()
        
        query = f"SELECT * FROM `{cls._table}` WHERE `{column}` = {Profile.sqlObjAsStr(name)}"
        async with conn.execute(query) as cur:
            fetchedRow = await cur.fetchone()
            if fetchedRow:
                return cls(row=fetchedRow)
        
        inst = cls.default()
        setattr(inst, nameVar, name)
        
        await inst._createToDb()
        
        # redoing a request because of default values
        async with conn.execute(query) as cur:
            fetchedRow = await cur.fetchone()
            if fetchedRow:
                return cls(row=fetchedRow)
            
        raise Exception(f"Fetched row didn't return anything (query: {query})")
    
    @classmethod
    @abc.abstractmethod
    async def createOrGet(cls, name: T) -> Self:
        """Creates or get a profile from the local DB

        Args:
            name: the name of what to fetch, eg: A server ID

        Returns:
            An object of type `Self`
        """
        ...
    
    async def _save(self, whereColumn: str, whereColumnVal: Any):
        """Helper for the `.save()` function

        Args:
            whereColumn: the column to update (`WHERE = {whereColumn} = {whereColumnVal}`)
            whereColumnVal: the value of the column
        """
        
        lock = asyncio.Lock()
        async with lock:
            conn = await CONFIG.storage.db.connect()
            
            query = f"UPDATE `{self._table}` {self.parseToSql(SqlParseType.SET)} WHERE `{whereColumn}` = {Profile.sqlObjAsStr(whereColumnVal)}"
            async with conn.execute(query):
                await conn.commit()
    
    async def save(self):
        """Save the infos to the db
        """
        ...
    
    @classmethod
    def parseToObj(cls, response: aiosqlite.Row) -> Self:
        """Parse a sql response to an object of type `Self`

        Args:
            response: the response of a sql query (`cur.fetchone()`)

        Returns:
            A class of type `Self`
        """
        
        return cls(response)
        
    
    def _parseToSql(self, type: SqlParseType, members: tuple[tuple[str, Any], ...], primaryKeyVar: Optional[str] = None) -> str:
        """Helper to parse `self` into a sql query
        
        Args:
            members (tuple[tuple[sqlColumnName, varValue]]): the members of this class to turn into an sql query
            primaryKeyVar: the name of the variable in `Self` that's the primary key. It'll get ignored in the `members` param if it's not equal to `None`
        
        Returns:
            A sql query
        """
        
        asSqlMembersDict: dict[str, str] = {}
        for name, val in members:
            if name == primaryKeyVar and primaryKeyVar: continue
            asSqlMembersDict[f"`{name}`"] = Profile.sqlObjAsStr(val)
        
        if type == SqlParseType.SET:
            ret = "SET "
            for col, val in asSqlMembersDict.items():
                ret += f"{col} = {val}, "
            
            return ret.removesuffix(", ")
            #return "SET " + ", ".join(asSqlMembersDict.values())
        elif type == SqlParseType.VALUES:
            return "VALUES(" + ", ".join(asSqlMembersDict.values()) + ")"
        elif type == SqlParseType.VALUES_COLUMNS:
            columns = "(" + ", ".join(asSqlMembersDict.keys()) + ")"
            values = "VALUES(" + ", ".join(asSqlMembersDict.values()) + ")"
            return f"{columns} {values}"
    
    @abc.abstractmethod
    def parseToSql(self, type: SqlParseType) -> str:
        """Parse the current object into a sql query
        
        Returns:
            A sql query
        """
        ...
    
    @property
    def table(self): return self._table
