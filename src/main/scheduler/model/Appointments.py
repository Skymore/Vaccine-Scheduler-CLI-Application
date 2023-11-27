from db.ConnectionManager import ConnectionManager
import pymssql


class Appointments:
    def __init__(self, time, status=0, pname=None, cname=None, vname=None):
        self.ID = None
        self.time = time
        self.status = status
        self.pname = pname
        self.cname = cname
        self.vname = vname

    # getters
    def get_id(self):
        return self.ID

    def get_time(self):
        return self.time

    def get_pname(self):
        return self.pname

    def get_cname(self):
        return self.cname

    def get_vname(self):
        return self.vname

    def save_to_db(self):
        cm = ConnectionManager()
        conn = cm.create_connection()
        cursor = conn.cursor()

        add_appointment = "INSERT INTO Appointments (Time, Status, Pname, Cname, Vname) VALUES (%s, 0, %s, %s, %s);SELECT SCOPE_IDENTITY();"
        try:
            cursor.execute(
                add_appointment, (self.time, self.pname, self.cname, self.vname))
            self.ID = cursor.fetchone()[0]  # set ID
            conn.commit()
        except pymssql.Error:
            # print("Error occurred when add appointment")
            raise
        finally:
            cm.close_connection()

    @classmethod
    def show(cls):
        pass
        '''
        TODO: Part 2
        '''
