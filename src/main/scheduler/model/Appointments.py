from db.ConnectionManager import ConnectionManager
import pymssql


class Appointments:
    def __init__(self, ID=None, time=None, status=0, pname=None, cname=None, vname=None):
        self.ID = ID
        self.time = time
        self.status = status
        self.pname = pname
        self.cname = cname
        self.vname = vname

    # getters
    def get(self):
        cm = ConnectionManager()
        conn = cm.create_connection()
        cursor = conn.cursor()

        get_appointment = "SELECT Time, Status, Pname, Cname, Vname FROM Appointments WHERE ID = %d AND Status = 0"
        try:
            cursor.execute(get_appointment, self.ID)
            for row in cursor:
                self.time = row[0]
                self.status = row[1]
                self.pname = row[2]
                self.cname = row[3]
                self.vname = row[4]
                return self
        except pymssql.Error:
            # print("Error occurred when getting appointment")
            raise
        finally:
            cm.close_connection()
        return None

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
    def show_caregiver_appointments(cls, cname):
        cm = ConnectionManager()
        conn = cm.create_connection()
        cursor = conn.cursor(as_dict=True)
        query = """
            SELECT 
                ID,
                Vname,
                Time,
                Pname
            FROM
                Appointments
            WHERE
                Cname = %s 
                AND Status = 0
            ORDER BY
                ID
        """
        try:
            cursor.execute(query, cname)
            print(f"Appointments for {cname}:")
            for row in cursor:
                print(
                    f"{str(row['ID'])} {str(row['Vname'])} {str(row['Time'])} {str(row['Pname'])}")
        except pymssql.Error as e:
            print("Please try again!")
            print("Db-Error:", e)
        except Exception as e:
            print("Please try again!")
            print("Error:", e)

    @classmethod
    def show_patient_appointments(cls, pname):
        cm = ConnectionManager()
        conn = cm.create_connection()
        cursor = conn.cursor(as_dict=True)
        query = """
            SELECT 
                ID,
                Vname,
                Time,
                Cname
            FROM
                Appointments
            WHERE
                Pname = %s
                AND Status = 0
            ORDER BY
                ID
        """
        try:
            cursor.execute(query, pname)
            print(f"Appointments for {pname}:")
            for row in cursor:
                print(
                    f"{row['ID']} {row['Vname']} {row['Time']} {row['Cname']}")
        except pymssql.Error as e:
            print("Please try again!")
            print("Db-Error:", e)
        except Exception as e:
            print("Please try again!")
            print("Error:", e)

    def cancel_appointment(self):
        cm = ConnectionManager()
        conn = cm.create_connection()
        cursor = conn.cursor()

        del_appointment = "UPDATE Appointments SET Status = 2 WHERE ID = %d"
        try:
            cursor.execute(del_appointment, self.ID)
            conn.commit()
        except pymssql.Error:
            # print("Error occurred when deleting caregiver availability")
            raise
        finally:
            cm.close_connection()
