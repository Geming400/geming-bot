import asyncio
from pathlib import Path
from pprint import pprint
import tempfile
from types import FrameType
from typing import Optional
import aiosqlite
import dotenv
import os
from utils.Loggers import Loggers
from utils.db.Profiles import GuildProfile
from utils.utils import CONFIG
import sys
import signal

dotenv.load_dotenv(".env")

async def test():
    print("In async function")
    async with aiosqlite.connect(CONFIG.storage.db.dbPath) as conn:
        j = await conn.execute("SELECT * FROM guilds")
        await j.close()
            
    h = await GuildProfile.createOrGet(12345)
    perms = await h.getPermissions()
    await asyncio.sleep(1)
    # perms.ai = True
    # await perms.save()
    # print("Saved")

#asyncio.run(test())
pprint(CONFIG.getStatuses())
print("finished")
sys.exit(0)