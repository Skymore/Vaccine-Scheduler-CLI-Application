import pymssql
from model.User import User
from db.ConnectionManager import ConnectionManager
from util.Util import Util
import sys
sys.path.append("../util/*")
sys.path.append("../db/*")


class Caregiver(User):
    # Insert availability with parameter date d and caregiver username cname
    @classmethod
    def upload_availability(cls, d, cname):
        cm = ConnectionManager()
        conn = cm.create_connection()
        cursor = conn.cursor(as_dict=True)
        # check if this availability already exist
        query = "SELECT Status FROM Availabilities WHERE Time = %s And username = %s"
        try:
            cursor.execute(query, (d, cname))
            if cursor.rowcount != 0:
                for row in cursor:
                    status = row['Status']
                    if status == 0:
                        print("Availability upload failed.")
                        print(f"Availability already exists on {d:%m-%d-%Y}.")
                    else:
                        print("Availability upload failed.")
                        print(f"You have an appointment on {d:%m-%d-%Y}.")
            else:
                add_availability = "INSERT INTO Availabilities VALUES (%s , %s, 0)"
                cursor.execute(add_availability, (d, cname))
                conn.commit()
                print("Availability uploaded!")
        except pymssql.Error:
            # print("Error occurred when updating caregiver availability")
            raise
        finally:
            cm.close_connection()

    @classmethod
    def change_availability(cls, d, cname):
        cm = ConnectionManager()
        conn = cm.create_connection()
        cursor = conn.cursor(as_dict=True)
        try:
            update = "UPDATE Availabilities SET Status = 0 WHERE Time = %s AND username = %s"
            cursor.execute(update, (d, cname))
            conn.commit()
        except pymssql.Error:
            raise
        finally:
            cm.close_connection()

    @classmethod
    def delete_availability(cls, d, cname):
        cm = ConnectionManager()
        conn = cm.create_connection()
        cursor = conn.cursor()
        del_availability = "UPDATE Availabilities SET Status = 1 WHERE Time = %s AND Username = %s"
        try:
            cursor.execute(del_availability, (d, cname))
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
