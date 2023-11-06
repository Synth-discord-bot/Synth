from .database import *
from .database.backups import BackupsDatabase
from .database.forms import FormsDatabase
from .database.invite import InviteTrackerDatabase
from .database.logger import LoggerDatabase
from .database.tickets import TicketDatabase
from .database.warns import WarnDatabase

economy = Economy("economy")
main_db = MainDatabase("bot")
ticket = TicketDatabase("ticket")
forms = FormsDatabase("form")
logger = LoggerDatabase("logger")
backups = BackupsDatabase("backups")
invites = InviteTrackerDatabase("invites")
warns = WarnDatabase("warns")