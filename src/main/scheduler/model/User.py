from util.Util import Util
import pymssql
from db.ConnectionManager import ConnectionManager
import sys


class User:
    def __init__(self, username, password=None, salt=None, hash=None, user_table=None):
        self.username = username
        self.password = password
        self.salt = salt
        self.hash = hash
        self.user_table = user_table

    # getters
    def get(self):
        cm = ConnectionManager()
        conn = cm.create_connection()
        cursor = conn.cursor(as_dict=True)

        get_user_details = f"SELECT Salt, Hash FROM {self.user_table} WHERE Username = %s"
        try:
            cursor.execute(get_user_details, self.username)
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

    def get_user_table(self):
        return self.user_table

    def save_to_db(self):
        cm = ConnectionManager()
        conn = cm.create_connection()
        cursor = conn.cursor()

        add_user = f"INSERT INTO {self.user_table} VALUES (%s, %s, %s)"
        try:
            cursor.execute(
                add_user, (self.username, self.salt, self.hash))
            # you must call commit() to persist your data if you don't set autocommit to True
            conn.commit()
        except pymssql.Error:
            raise
        finally:
            cm.close_connection()
