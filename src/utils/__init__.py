from .database import *
from .database.tickets import TicketDatabase
from .database.forms import FormsDatabase
from .database.logger import LoggerDatabase
from .database.backups import BackupsDatabase
from .database.invite import InviteTrackerDatabase

economy = Economy("economy")
main_db = MainDatabase("bot")
ticket = TicketDatabase("ticket")
forms = FormsDatabase("form")
logger = LoggerDatabase("logger")
backups = BackupsDatabase("backups")
invites = InviteTrackerDatabase("invites")
