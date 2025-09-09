from typing import TYPE_CHECKING, Literal, Optional, Type, TypeVar, cast

import discord


T = TypeVar('T', default=object)

if TYPE_CHECKING:
    import utils.AiHandler as AiHandler
    import utils.config as _config

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
    
    # -- custom members --
    
    def __init__(self, config: "_config.Config") -> None:
        self.storage = {}
        self.config = config
        
        # -- custom members --
        
        self._aiHandler = None
        self.currentModel = self.config.getDefaultModel() or "hermes3"
        self.aiPingReply = discord.AllowedMentions.none()
        
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