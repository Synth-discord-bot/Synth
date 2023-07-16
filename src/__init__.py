import logging
import datetime

startup = datetime.datetime.now()
logger = logging.getLogger("disnake")
logger.setLevel(logging.DEBUG)
handler = logging.FileHandler(
    filename=f"synth-{startup.timestamp()}.log", encoding="utf-8", mode="w"
)
handler.setFormatter(
    logging.Formatter("[%(asctime)s] %(levelname)s:%(name)s: %(message)s")
)
logger.addHandler(handler)
