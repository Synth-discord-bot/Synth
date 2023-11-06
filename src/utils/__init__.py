from .database import *
from .database.backups import BackupDatabase
from .database.forms import FormsDatabase
from .database.invite import InviteTrackerDatabase
from .database.logger import LoggerDatabase
from .database.tickets import TicketDatabase
from .database.private_rooms import PrivateRoomsDatabase
from .database.warns import WarnDatabase

economy = EconomyDatabase("economy")
main_db = MainDatabase("bot")
ticket = TicketDatabase("ticket")
forms = FormsDatabase("form")
logger = LoggerDatabase("logger")
backups = BackupDatabase("backups")
invites = InviteTrackerDatabase("invites")
private_rooms = PrivateRoomsDatabase("private_rooms")
warns = WarnDatabase("warns")
