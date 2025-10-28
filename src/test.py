import asyncio
from pathlib import Path
from pprint import pprint
import tempfile
from types import FrameType
from typing import Optional, TypeVar
import aiosqlite
import dotenv
import os
from utils.Loggers import Loggers
from utils.db.Profiles import FactProfile, GuildProfile
from utils.utils import CONFIG
import sys
import signal

dotenv.load_dotenv(".env")

async def test():
    # print("In async function")
    # async with aiosqlite.connect(CONFIG.storage.db.dbPath) as conn:
    #     j = await conn.execute("SELECT * FROM guilds")
    #     await j.close()
            
    # h = await GuildProfile.createOrGet(12345)
    # perms = await h.getPermissions()
    # await asyncio.sleep(1)
    # # perms.ai = True
    # # await perms.save()
    # # print("Saved")
    
    print("facts:")
    pprint(await FactProfile.getFacts())

T = TypeVar('T')

def splitList(l: list[T], n: int, index: int) -> list[T]:
    """Splits a list in members of `n` and returns the index `index`

    Args:
        l: The list to split
        n: The numbers of sub-list to make
        index: The index of the sublist to get
        
    Returns:
        The sublist of index `index`
    """
    
    finalLists: list[list[T]] = []
    currentSubList: list[T] = []
    
    for i, v in enumerate(l, start=1):
        currentSubList.append(v)
        
        if i % n == 0:
            finalLists.append(currentSubList.copy())
            currentSubList.clear()
    
    if currentSubList != []:
        finalLists.append(currentSubList.copy())
        currentSubList.clear()
    
    return finalLists[index]

asyncio.run(test())
# pprint(CONFIG.getStatuses())

# print(splitList([10, 20, 30, 40, 50], 1, 0))

print("finished")
sys.exit(0)