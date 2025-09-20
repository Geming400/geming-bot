import asyncio
from pathlib import Path
import tempfile
from types import FrameType
from typing import Optional
import dotenv
import os
from utils.Loggers import Loggers
from utils.db.ServerProfile import ServerProfile
from utils.utils import CONFIG
import sys
import signal


# hooks

def exceptHook(excT: type[BaseException], exc: BaseException, traceback):
    Loggers.logger.exception(f"Exception catched in 'exceptHook' {exc}")
    raise exc

async def asyncSigIntHandler(sig: int, frame: Optional[FrameType]):
    Loggers.logger.info("--- Now exiting ---")
    
    try:
        Loggers.logger.info("Closing db connection")
        await CONFIG.storage.db.close()
    except Exception as e:
        Loggers.logger.exception(f"Caught an error while trying to exit: {e}")
        Loggers.logger.info("(async) Ignoring exception and now exiting")
    
    Loggers.logger.info("Exiting")
    sys.exit(0)

def sigIntHandler(sig: int, frame: Optional[FrameType]):
    Loggers.logger.debug("Entered `signal.SIGINT` hook")
    asyncio.set_event_loop(asyncio.new_event_loop())
    try:
        asyncio.create_task(asyncSigIntHandler(sig, frame))
    except Exception as e:
        Loggers.logger.exception(f"Error catched in 'sigIntHandler()' (sync): {e}")
        Loggers.logger.info("(sync) Ignoring exception and now exiting")
        sys.exit(0)
    

sys.excepthook = exceptHook
signal.signal(signal.SIGINT, sigIntHandler)


dotenv.load_dotenv(".env")

tempfile.tempdir = "../tempdir/"
Path(os.path.dirname(tempfile.tempdir)).mkdir(parents=True, exist_ok=True)

Loggers.logger.info("Checking if DB exists")
if CONFIG.storage.db.dbExists():
    Loggers.logger.info("Db exists !")
else:
    Loggers.logger.info("Db doesn't exists, it'll now get created")
    Loggers.logger.info("Initializing db")
    try:
        asyncio.run(CONFIG.storage.db.initDB())
    except Exception as e:
        Loggers.logger.exception(f"Error while trying to initialize db: {e}")
        Loggers.logger.info("Not continuing, exiting")
        sys.exit(1)

async def test():
    h = await ServerProfile.createOrGet(12345)
    perms = await h.getPermissions()
    perms.ai = True
    await perms.save()
    print("Saved")

asyncio.run(test())
sys.exit(0)