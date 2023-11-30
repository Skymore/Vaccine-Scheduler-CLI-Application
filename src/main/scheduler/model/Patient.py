import pymssql
from model.User import User
from db.ConnectionManager import ConnectionManager
from util.Util import Util
import sys
sys.path.append("../util/*")
sys.path.append("../db/*")


class Patient(User):
    pass
