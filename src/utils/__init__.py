from .database import *
from .database.backups import BackupDatabase
from .database.forms import FormsDatabase
from .database.invite import InviteTrackerDatabase
from .database.logger import LoggerDatabase
from .database.private_rooms import PrivateRoomsDatabase
from .database.warns import WarnDatabase
from .database.giveaway import GiveawayDatabase

main_db = MainDatabase("bot")
forms = FormsDatabase("form")
logger = LoggerDatabase("logger")
backups = BackupDatabase("backups")
invites = InviteTrackerDatabase("invites")
private_rooms = PrivateRoomsDatabase("private_rooms")
warns = WarnDatabase("warns")
giveaway = GiveawayDatabase("giveaway")
