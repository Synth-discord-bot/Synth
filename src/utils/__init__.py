from .database import *
from .database.tickets import TicketDatabase
from .database.forms import FormsDatabase
from .database.logger import LoggerDatabase
from .database.backups import BackupsDatabase 

economy = Economy("economy")
main_db = MainDatabase("bot")
ticket = TicketDatabase("ticket")
forms = FormsDatabase("form")
logger = LoggerDatabase("logger")
backups = BackupsDatabase("backups")