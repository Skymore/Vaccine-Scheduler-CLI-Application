import pymssql
from db.ConnectionManager import ConnectionManager
from util.Util import Util
import sys
sys.path.append("../util/*")
sys.path.append("../db/*")


class Caregiver:
    def __init__(self, username, password=None, salt=None, hash=None):
        self.username = username
        self.password = password
        self.salt = salt
        self.hash = hash

    # getters
    def get(self):
        cm = ConnectionManager()
        conn = cm.create_connection()
        cursor = conn.cursor(as_dict=True)

        get_caregiver_details = "SELECT Salt, Hash FROM Caregivers WHERE Username = %s"
        try:
            cursor.execute(get_caregiver_details, self.username)
            if cursor.rowcount == 0:
                print("Invalid username")
                cm.close_connection()
                return None
            for row in cursor:
                curr_salt = row['Salt']
                curr_hash = row['Hash']
                calculated_hash = Util.generate_hash(self.password, curr_salt)
                if not curr_hash == calculated_hash:
                    print("Incorrect password")
                    cm.close_connection()
                    return None
                else:
                    self.salt = curr_salt
                    self.hash = calculated_hash
                    cm.close_connection()
                    return self
        except pymssql.Error as e:
            raise e
        finally:
            cm.close_connection()
        return None

    def get_username(self):
        return self.username

    def get_salt(self):
        return self.salt

    def get_hash(self):
        return self.hash

    def save_to_db(self):
        cm = ConnectionManager()
        conn = cm.create_connection()
        cursor = conn.cursor()

        add_caregivers = "INSERT INTO Caregivers VALUES (%s, %s, %s)"
        try:
            cursor.execute(
                add_caregivers, (self.username, self.salt, self.hash))
            # you must call commit() to persist your data if you don't set autocommit to True
            conn.commit()
        except pymssql.Error:
            raise
        finally:
            cm.close_connection()

    # Insert availability with parameter date d
    def upload_availability(self, d):
        cm = ConnectionManager()
        conn = cm.create_connection()
        cursor = conn.cursor()

        add_availability = "INSERT INTO Availabilities VALUES (%s , %s, 0)"
        try:
            cursor.execute(add_availability, (d, self.username))
            # you must call commit() to persist your data if you don't set autocommit to True
            conn.commit()
        except pymssql.Error:
            # print("Error occurred when updating caregiver availability")
            raise
        finally:
            cm.close_connection()

    @classmethod
    def delete_availability(cls, d, username):
        cm = ConnectionManager()
        conn = cm.create_connection()
        cursor = conn.cursor()
        del_availability = "UPDATE Availabilities SET Status = 1 WHERE Time = %s AND Username = %s"
        try:
            cursor.execute(del_availability, (d, username))
            # you must call commit() to persist your data if you don't set autocommit to True
            conn.commit()
        except pymssql.Error:
            # print("Error occurred when deleting caregiver availability")
            raise
        finally:
            cm.close_connection()

    # Find available caregivers for the date and return
    @classmethod
    def search_availability(cls, d):
        cm = ConnectionManager()
        conn = cm.create_connection()
        cursor = conn.cursor()

        # SQL query to find available caregivers
        search_caregiver_availability = """
            SELECT 
                AV.Username
            FROM 
                Availabilities AS AV
            WHERE 
                AV.Time = %s
                AND AV.Status = 0
            ORDER BY 
                AV.Username
        """
        try:
            cursor.execute(search_caregiver_availability, d)
            return cursor.fetchall()
        except pymssql.Error:
            # print("Error occurred when updating caregiver availability")
            raise
        finally:
            cm.close_connection()
