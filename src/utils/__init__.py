from .database import *
from .database.backups import BackupDatabase
from .database.invite import InviteTrackerDatabase
from .database.logger import LoggerDatabase
from .database.private_rooms import PrivateRoomsDatabase
from .database.warns import WarnDatabase
from .database.giveaway import GiveawayDatabase
from .database.commands import CommandDatabase

main_db = MainDatabase("bot")
logger = LoggerDatabase("logger")
backups = BackupDatabase("backups")
invites = InviteTrackerDatabase("invites")
private_rooms = PrivateRoomsDatabase("private_rooms")
warns = WarnDatabase("warns")
giveaway = GiveawayDatabase("giveaway")
commands_db = CommandDatabase("commands")
