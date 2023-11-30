from model.Caregiver import Caregiver
from model.Patient import Patient
from model.Vaccine import Vaccine
from model.User import User
from model.Appointments import Appointments
from util.Util import Util
from db.ConnectionManager import ConnectionManager
import pymssql
import datetime

'''
Objects to keep track of the currently logged-in user
'''
current_user = None


def username_exists(username, user_table):
    # check if username exists in user_table
    cm = ConnectionManager()
    conn = cm.create_connection()
    cursor = conn.cursor(as_dict=True)

    select_username = f"SELECT * FROM {user_table} WHERE Username = %s"

    try:
        cursor.execute(select_username, username)
        for row in cursor:
            return row['Username'] is not None
    except pymssql.Error as e:
        print("Failed to create user.")
        print("Error occurred when checking username")
        print("Db-Error:", e)
    except Exception as e:
        print("Failed to create user.")
        print("Error occurred when checking username")
        print("Error:", e)
    finally:
        cm.close_connection()
    return False


def create_user(tokens, user_table):
    # check 1: the length for tokens need to be exactly 3 to include all information (with the operation name)
    if len(tokens) != 3:
        print("Failed to create user.")
        print("Invalid input. Please try again.")
        return

    username = tokens[1]
    password = tokens[2]

    # check 2: if the username has been taken already
    if username_exists(username, user_table):
        print("Username taken, try again!")
        return

    salt = Util.generate_salt()
    hash = Util.generate_hash(password, salt)

    # create user
    user = User(username, salt=salt, hash=hash, user_table=user_table)

    # save user information to our database
    try:
        user.save_to_db()
        print("Created user ", username)
    except pymssql.Error as e:
        print("Failed to create user.")
        print("Db-Error:", e)
    except Exception as e:
        print("Failed to create user.")
        print(e)


def create_patient(tokens):
    create_user(tokens, 'Patients')


def create_caregiver(tokens):
    create_user(tokens, 'Caregivers')


def login_user(tokens, user_table):
    # check 1: if someone's already logged-in, they need to log out first
    global current_user
    if current_user is not None:
        print("User already logged in.")
        return

    # check 2: the length fro tokens need to be exactly 3
    if len(tokens) != 3:
        print("Login failed.")
        print("Invalid input. Please try agian.")
        return

    username = tokens[1]
    password = tokens[2]

    user = None
    try:
        user = User(username, password=password, user_table=user_table).get()
        # check 3: if the login was successful
        if user is None:
            print("Login failed.")
        else:
            print("Logged in as: " + username)
            current_user = user
    except pymssql.Error as e:
        print("Login failed.")
        print("Db-Error:", e)
    except Exception as e:
        print("Login failed.")
        print("Error:", e)


def login_patient(tokens):
    # login_patient <username> <password>
    login_user(tokens, 'Patients')


def login_caregiver(tokens):
    # login_caregiver <username> <password>
    login_user(tokens, 'Caregivers')


def search_caregiver_schedule(tokens):
    # search_caregiver_schedule <date>
    # Output the username for the caregivers that are available for the date
    # along with the number of available doses left for each vaccine.
    # Order by the username of the caregiver. Separate each attribute with a space.

    # check 1: if there is a user logged-in
    global current_user
    if current_user is None:
        print("Please login first!")
        return

    # check 2: the length of tokens (2 for date and the operation name)
    if len(tokens) != 2:
        print("Please try agian!")
        print("Invalid input. Please try agian.")
        return

    date = tokens[1]

    try:
        # assume input is hyphenated in the format mm-dd-yyyy
        d = datetime.datetime.strptime(date, "%m-%d-%Y")
        available_caregivers = Caregiver.search_availability(d)
        available_vaccines = Vaccine.search_availability()

        # print available caregivers
        if len(available_caregivers) == 0:
            print("No Caregiver is available!")
        else:
            print("Available Caregivers:")
            for caregiver in available_caregivers:
                print(caregiver[0])

        # print available vaccines
        print("\nAvailable Vaccine Doses:")
        for vaccine in available_vaccines:
            print(f"Vaccine Name: {vaccine[0]}, Available Doses: {vaccine[1]}")

    except pymssql.Error as e:
        print("Please try again!")
        print("Search Caregiver Schedule Failed")
        print("Db-Error:", e)
    except ValueError:
        print("Please try again!")
        print("Please enter a valid date! Use format mm-dd-yyyy.")
    except Exception as e:
        print("Please try again!")
        print("Error occurred when search caregiver schedule")
        print("Error:", e)


def reserve(tokens):
    # reserve <date> <vaccine>

    #  check 1: check if the current logged-in user is a patient
    global current_user
    if current_user is None:
        print("Please login first!")
        return
    if current_user.get_user_table() != 'Patients':
        print("Please login as a patient!")
        return

    # check 2: the length for tokens need to be exactly 3 to include all information (with the operation name)
    if len(tokens) != 3:
        print("Please try again! Invalid input.")
        return

    date = tokens[1]
    vaccine_name = tokens[2]
    vaccine = None
    try:
        # check available caregivers and vaccines
        vaccine = Vaccine(vaccine_name).get()
        # assume input is hyphenated in the format mm-dd-yyyy
        d = datetime.datetime.strptime(date, "%m-%d-%Y")
        available_caregivers = Caregiver.search_availability(d)
        if vaccine is None or vaccine.get_available_doses() == 0:
            print("Not enough available doses!")
        elif len(available_caregivers) == 0:
            print("No Caregiver is available!")
        else:
            chosen_cname = available_caregivers[0][0]
            Caregiver.delete_availability(d, chosen_cname)
            appointment = Appointments(time=d, status=0,
                                       pname=current_user.get_username(), cname=chosen_cname, vname=vaccine_name)
            appointment.save_to_db()
            vaccine.decrease_available_doses(1)
            print(
                f"Appointment ID: {appointment.get_id()}, Caregiver username: {chosen_cname}")

    except pymssql.Error as e:
        print("Please try again!")
        print("Error occurred when reserving")
        print("Db-Error:", e)
    except Exception as e:
        print("Please try again!")
        print("Error occurred when reserving")
        print("Error:", e)


def upload_availability(tokens):
    #  upload_availability <date>
    #  check 1: check if the current logged-in user is a caregiver
    global current_user
    if current_user is None:
        print("Please login first!")
        return
    if current_user.get_user_table() != 'Caregivers':
        print("Please login as a caregiver!")
        return

    # check 2: the length for tokens need to be exactly 2 to include all information (with the operation name)
    if len(tokens) != 2:
        print("Please try again! Invalid input.")
        return

    date = tokens[1]

    try:
        # assume input is hyphenated in the format mm-dd-yyyy
        d = datetime.datetime.strptime(date, "%m-%d-%Y")
        cname = current_user.get_username()
        Caregiver.upload_availability(d, cname)
    except pymssql.Error as e:
        print("Upload Availability Failed")
        print("Db-Error:", e)
    except ValueError:
        print("Please enter a valid date! Use format mm-dd-yyyy.")
    except Exception as e:
        print("Error occurred when uploading availability")
        print("Error:", e)


def cancel(tokens):
    # cancel <appointment_id>
    # check 1: if there is a user logged-in
    global current_user
    if current_user is None:
        print("Please login first.")
        return

    # check 2: the length for tokens need to be exactly 2
    if len(tokens) != 2:
        print("Please try again! Invalid input.")
        return

    try:
        aid = tokens[1]
        current_appointment = Appointments(ID=aid).get()

        if current_appointment is None:
            print("Please try again!")
            print(f"Appointment with ID {aid} doesn't exist!")
        else:
            current_appointment.cancel_appointment()
            cname = current_appointment.get_cname()
            cancel_date = current_appointment.get_time()
            Caregiver.change_availability(cancel_date, cname)
            vaccine_name = current_appointment.get_vname()
            vaccine = Vaccine(vaccine_name).get()
            vaccine.increase_available_doses(1)

    except pymssql.Error as e:
        print("Please try again!")
        print("Error occurred when canceling appointment")
        print("Db-Error:", e)
    except Exception as e:
        print("Please try again!")
        print("Error occurred when canceling appointment")
        print("Error:", e)


def add_doses(tokens):
    #  add_doses <vaccine> <number>
    #  check 1: check if the current logged-in user is a caregiver
    global current_user
    if current_user is None:
        print("Please login first!")
        return
    if current_user.get_user_table() != 'Caregivers':
        print("Please login as a caregiver!")
        return

    #  check 2: the length for tokens need to be exactly 3 to include all information (with the operation name)
    if len(tokens) != 3:
        print("Please try again! Invalid Input.")
        return

    vaccine_name = tokens[1]
    doses = int(tokens[2])
    vaccine = None
    try:
        vaccine = Vaccine(vaccine_name, doses).get()

        # if the vaccine is not found in the database, add a new (vaccine, doses) entry.
        # else, update the existing entry by adding the new doses
        if vaccine is None:
            vaccine = Vaccine(vaccine_name, doses)
            vaccine.save_to_db()
        else:
            # if the vaccine is not null, meaning that the vaccine already exists in our table
            vaccine.increase_available_doses(doses)

        print("Doses updated!")

    except pymssql.Error as e:
        print("Error occurred when adding doses")
        print("Db-Error:", e)
    except Exception as e:
        print("Error occurred when adding doses")
        print("Error:", e)


def show_appointments(tokens):
    # check 1: if there is a user logged-in
    global current_user
    if current_user is None:
        print("Please login first.")
        return

    username = current_user.get_username()
    user_table = current_user.get_user_table()
    Appointments.show_appointments(username, user_table)


def logout(tokens):
    # check 1: if there is a user logged-in
    global current_user
    if current_user is None:
        print("Please login first.")
        return
    try:
        current_user = None
        print("Successfully logged out!")
    except:
        print("Please try again!")


def display_command_list():
    print()
    print(" *** Please enter one of the following commands *** ")
    print("> create_patient <username> <password>")
    print("> create_caregiver <username> <password>")
    print("> login_patient <username> <password>")
    print("> login_caregiver <username> <password>")
    print("> search_caregiver_schedule <date>")
    print("> reserve <date> <vaccine>")
    print("> upload_availability <date>")
    print("> cancel <appointment_id>")
    print("> add_doses <vaccine> <number>")
    print("> show_appointments")
    print("> logout")
    print("> Quit")
    print()


def start():
    stop = False

    while not stop:
        display_command_list()
        response = ""
        print("> ", end='')

        try:
            response = str(input())
        except ValueError:
            print("Please try again!")
            break

        response = response.lower()
        tokens = response.split(" ")
        if len(tokens) == 0:
            ValueError("Please try again!")
            continue
        operation = tokens[0]
        if operation == "create_patient":
            create_patient(tokens)
        elif operation == "create_caregiver":
            create_caregiver(tokens)
        elif operation == "login_patient":
            login_patient(tokens)
        elif operation == "login_caregiver":
            login_caregiver(tokens)
        elif operation == "search_caregiver_schedule":
            search_caregiver_schedule(tokens)
        elif operation == "reserve":
            reserve(tokens)
        elif operation == "upload_availability":
            upload_availability(tokens)
        elif operation == "cancel":
            cancel(tokens)
        elif operation == "add_doses":
            add_doses(tokens)
        elif operation == "show_appointments":
            show_appointments(tokens)
        elif operation == "logout":
            logout(tokens)
        elif operation == "quit":
            print("Bye!")
            stop = True
        else:
            print("Invalid operation name!")


if __name__ == "__main__":
    '''
    // pre-define the three types of authorized vaccines
    // note: it's a poor practice to hard-code these values, but we will do this ]
    // for the simplicity of this assignment
    // and then construct a map of vaccineName -> vaccineObject
    '''

    # start command line
    print()
    print("Welcome to the COVID-19 Vaccine Reservation Scheduling Application!")

    start()
