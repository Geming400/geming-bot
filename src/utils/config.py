from enum import Enum
import functools
import os
import random
from typing import Any, Literal, Optional
from jsonc_parser.parser import JsoncParser
import dotenv
import discord

from utils.SharedStorage import SharedStorage


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

class Activites:
    class ActivityState(str, Enum):
        STATUS = "status"
        PLAYING = "playing"
        STREAMING = "streaming"
        LISTENING = "listening"
        WATCHING = "watching"
        COMPETING = "competing"
    
        @staticmethod
        def getStateFromVal(val: str) -> "Activites.ActivityState":
            match val.lower():
                case "status": return Activites.ActivityState.STATUS
                case "playing": return Activites.ActivityState.PLAYING
                case "streaming": return Activites.ActivityState.STREAMING
                case "listening": return Activites.ActivityState.LISTENING
                case "watching": return Activites.ActivityState.WATCHING
                case "competing": return Activites.ActivityState.COMPETING
                
            raise ValueError(f"{val} is not a valid value for this enum")
        
        @staticmethod
        def toDiscordActivity(activityType: "Activites.ActivityState", text: str) -> discord.Activity | discord.CustomActivity:
                match activityType:
                    case Activites.ActivityState.STATUS: return discord.CustomActivity(name=text)
                    case Activites.ActivityState.PLAYING: return discord.Activity(type=discord.ActivityType.playing, name=text)
                    case Activites.ActivityState.STREAMING: return discord.Activity(type=discord.ActivityType.streaming, name=text)
                    case Activites.ActivityState.LISTENING: return discord.Activity(type=discord.ActivityType.listening, name=text)
                    case Activites.ActivityState.WATCHING: return discord.Activity(type=discord.ActivityType.watching, name=text)
                    case Activites.ActivityState.COMPETING: return discord.Activity(type=discord.ActivityType.competing, name=text)
    
    class Status:
        state: "Activites.ActivityState"
        """The state of the status
        """
        
        text: str
        """The text of the status
        """
        
        def __init__(self, state: "Activites.ActivityState", text: str) -> None:
            self.state = state
            self.text = text
        
        def __repr__(self) -> str:
            return f"Status( state = ActivityState.{self.state.name}, test = {self.text} )"
    

    frequency: int
    """How frequent in seconds will the status change
    """
    
    statuses: list[Status]
    """A set containing all of the activites
    """
    
    def __init__(self, frequency: int, statuses: list["Status"]) -> None:
        self.frequency = frequency
        self.statuses = statuses
    
    def getRandomStatus(self) -> Status:
        return random.choice(self.statuses)
    
    async def setRandomStatus(self, bot: discord.Bot):
        if self.statuses == []: return
        
        status = self.getRandomStatus()
        
        activity = Activites.ActivityState.toDiscordActivity(status.state, status.text)
        await bot.change_presence(activity=activity)
    
    def getFormattedStatusesAsStrList(self) -> list[str]:
        ret = []
        
        for status in self.statuses:
            ret.append(f"({status.state.value}) {status.text}")
        
        return ret
    
    def __repr__(self) -> str:
        return f"Activities( frequency = {self.frequency}, status = {self.statuses} )"
    
    def __iter__(self):
        return self.statuses

class Config(metaclass=Singleton):
    file: str
    content: dict[str, Any]
    
    def __init__(self) -> None:
        self.file = os.getenv("CONFIG-PATH") or "config.jsonc"
        self.content = {}
        
        self.loadConfigFile()
        
        self._storage = SharedStorage(self)
        
    @property
    def storage(self): return self._storage
    
    def loadConfigFile(self):
        self.content = JsoncParser.parse_file(self.file)
    
    def reloadConfigs(self):
        self.loadConfigFile()
        
        self.getSystemPrompt.cache_clear()
        self.getStatuses.cache_clear()
    
    def getLogPath(self) -> str:
        return self.content["log-path"]
    
    def getDefaultModel(self) -> Optional[str]:
        return self.content["ai"].get("default-model")
    
    def getKeepAlive(self) -> int:
        return self.content["ai"].get("keep-alive", 60*5) # default ollama value
    
    @functools.lru_cache
    def getSystemPrompt(self) -> str:
        if self.content["ai"].get("is-system-prompt-file", False):
            with open(self.content["ai"]["system-prompt"]) as f:
                return f.read()
        else:
            return self.content.get("system-prompt", "")
        
    def getOwner(self) -> int:
        return self.content["permissions"]["owner-userID"]
    
    def getTrustedUsers(self) -> list[int]:
        users: list[int] = self.content["permissions"].get("trusted-userIDs", [])
        users.append(self.getOwner())
        return users
    
    def getFactPermissionsUsers(self) -> list[int]:
        users: list[int] = self.content["permissions"].get("facts-add-remove-userIDs", [])
        users.append(self.getOwner())
        return users

    def isOwner(self, userID: int) -> bool:
        return userID == self.getOwner()
    
    def isTrusted(self, userID: int) -> bool:
        return userID in self.getTrustedUsers()
    
    def canEditFacts(self, userID: int) -> bool:
        return userID in self.getFactPermissionsUsers()
    
    def getDbPath(self) -> str:
        return self.content["db"]["path"]
    
    def getAiHost(self) -> str | Literal["127.0.0.1"]:
        return os.getenv("AI-HOST") or "127.0.0.1"
    
    @functools.lru_cache
    def getStatuses(self) -> Optional[Activites]:
        if not self.content.get("activities"): return None
        
        frequency: int = self.content["activities"]["frequency"]
        statuses: list[dict[str, str]] = self.content["activities"]["statuses"]
        statusesAsObj: list[Activites.Status] = []
        
        for status in statuses:
            statusesAsObj.append(
                Activites.Status(
                    state=Activites.ActivityState.getStateFromVal(status["state"]),
                    text=status["text"]
                )
            )
        
        return Activites(frequency, statusesAsObj)
