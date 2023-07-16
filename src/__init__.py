import logging
import datetime
from .utils.database import BaseDatabase

startup = datetime.datetime.now()
logger = logging.getLogger("disnake")
logger.setLevel(logging.DEBUG)
handler = logging.FileHandler(
    filename=f"logs\\synth-{startup.timestamp()}.log", encoding="utf-8", mode="w"
)
handler.setFormatter(
    logging.Formatter("[%(asctime)s] %(levelname)s:%(name)s: %(message)s")
)
logger.addHandler(handler)

testdb = BaseDatabase("test")
