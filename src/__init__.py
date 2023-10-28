import datetime
import logging

import src.bot

startup = datetime.datetime.now()
logger = logging.getLogger()
logger.setLevel(level=logging.INFO)
handler = logging.FileHandler(
    filename=f"logs\\synth-{startup.timestamp()}.log", encoding="utf-8", mode="w"
)
handler.setFormatter(
    logging.Formatter("[%(asctime)s] %(levelname)s:%(name)s: %(message)s")
)
stream_handler = logging.StreamHandler()
stream_handler.setLevel(logging.INFO)
stream_handler.setFormatter(
    logging.Formatter("[%(asctime)s] %(levelname)s:%(name)s: %(message)s")
)

logger.addHandler(hdlr=handler)
logger.addHandler(hdlr=stream_handler)
