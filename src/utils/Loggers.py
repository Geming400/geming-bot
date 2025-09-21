import logging.handlers
import os
from pathlib import Path
from typing import Final

from utils.config import Config


__all__ = [
    "Loggers"
]

_config = Config()

def createHandler(handler: logging.Handler, level: int, name: str = __name__):
    handler.setFormatter(logging.Formatter("[%(asctime)s - %(levelname)s - %(name)s] %(message)s"))
    handler.setLevel(level)
    
    return handler

def createTimedRotatingFileHandler(logPath: str, level: int, name: str = __name__):
    handler = logging.handlers.TimedRotatingFileHandler(Path(logPath) / f"{name}.log", "D", backupCount=30*3, encoding="utf-8") # we want to keep the logs for ~3 month
    return createHandler(handler, level, name)
    
def createStreamHandler(level: int, name: str = __name__):
    handler = logging.StreamHandler()
    return createHandler(handler, level, name)

def getLogger(logPath: str, level: int, name: str = __name__) -> logging.Logger:
    Path(os.path.dirname(logPath)).mkdir(parents=True, exist_ok=True)
    
    logger: Final = logging.getLogger(name)
    logger.addHandler(createTimedRotatingFileHandler(logPath, level, name))
    logger.addHandler(createStreamHandler(level, name))
    logger.setLevel(level)
    
    return logger

class Loggers:
    logger: Final[logging.Logger] = getLogger(_config.getLogPath(), logging.DEBUG, "mainbot")
    aiLogger: Final[logging.Logger] = getLogger(_config.getLogPath(), logging.DEBUG, "AI")
    permLogger: Final[logging.Logger] = getLogger(_config.getLogPath(), logging.DEBUG, "permissions")