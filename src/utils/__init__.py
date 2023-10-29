from .database import *
from .database.tickets import TicketDatabase
from .database.backups import BackupsDatabase

economy = Economy("economy")
main_db = MainDatabase("bot")
ticket = TicketDatabase("ticket")
backups = BackupsDatabase("backups")
