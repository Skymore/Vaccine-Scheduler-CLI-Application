import pymssql
import os


class ConnectionManager:

    def __init__(self):
        self.server_name = os.getenv("Server") + ".database.windows.net"
        self.db_name = os.getenv("DBName")
        self.user = os.getenv("UserID")
        self.password = os.getenv("Password")
        self.conn = None

    def create_connection(self):
        try:
            self.conn = pymssql.connect(
                server=self.server_name, user=self.user, password=self.password, database=self.db_name)
        except pymssql.Error as db_err:
            print("Database Programming Error in SQL connection processing! ")
            print(db_err)
            quit()
        return self.conn

    def close_connection(self):
        try:
            self.conn.close()
        except pymssql.Error as db_err:
            print("Database Programming Error in SQL connection processing! ")
            print(db_err)
            quit()


# instantiating a connection manager class and cursor
cm = ConnectionManager()
conn = cm.create_connection()
cursor = conn.cursor()


# example 1: getting all names and available doses in the vaccine table
get_all_vaccines = "SELECT Name, Doses FROM Vaccines"
try:
    cursor.execute(get_all_vaccines)
    for row in cursor:
        print("name: " + str(row['Name']) +
              ", available_doses: " + str(row['Doses']))
except pymssql.Error:
    print("Error occurred when getting details from Vaccines")

# example 2: getting all records where the Name matches “Pfizer”
get_pfizer = "SELECT * FROM Vaccines WHERE Name = %s"
try:
    cursor.execute(get_pfizer, 'Pfizer')
    for row in cursor:
        print("name: " + str(row['Name']) +
              ", available_doses: " + str(row['Doses']))
except pymssql.Error:
    print("Error occurred when getting pfizer from Vaccines")
