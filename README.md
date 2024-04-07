# Vaccine Scheduler CLI Application

This Python command-line application simplifies the process of scheduling vaccine appointments. Utilizing a MySQL database hosted on Azure, it offers features such as user registration, appointment scheduling, cancellation, and more, directly from your command line.

## Features

- **User Registration and Login**: Secure your access.
- **Appointment Scheduling and Cancellation**: Manage your vaccine appointments.
- **Doctor Schedule Query**: Find available times from doctors to plan your visits.
- **Vaccine Information**: Detailed information about different vaccines.
- **Notification System**: Get notified about your appointment details. (todo)
- **Appointment History**: Keep track of your past and future appointments.
- **Feedback System**: Provide feedback about your vaccination experience. (todo)

## Prerequisites

- Python 3.6 or higher.
- MySQL Server (Azure-hosted MySQL is used in this application).
- An Azure account, if hosting the database on Azure.

## Quick Start

1. **Clone the repository and navigate to the project directory:**

    ```bash
    git clone https://github.com/Skymore/Vaccine-Scheduler-CLI-Application.git
    cd Vaccine-Scheduler-CLI-Application
    ```

2. **Install the required Python packages:**

    ```bash
    pip install -r requirements.txt
    ```

3. **Set up your database connection:**

   The application uses environment variables to manage database connection settings. Set the following environment variables in your system or development environment:

   - `Server`: Your Azure database server name (without the `.database.windows.net` part).
   - `DBName`: The name of your database.
   - `UserID`: Your database login username.
   - `Password`: Your database login password.

   Example of setting environment variables in a Unix-like shell:

   ```bash
   export Server=your_server_name
   export DBName=your_db_name
   export UserID=your_user_id
   export Password=your_password

4. **Run the application:**

    ```bash
    python src/main/scheduler/Scheduler.py
    ```

    Follow the on-screen instructions to navigate through the application.

## Contributing

Your contributions are welcome! Please feel free to fork the repository, create your feature branch, commit your changes, push to your branch, and open a pull request.

## License

This project is licensed under the MIT License - see the LICENSE file for more details.

## Contact

- **Your Name** - realruitao@gmail.com
- **Project Link** - [Vaccine Scheduler CLI Application](https://github.com/Skymore/Vaccine-Scheduler-CLI-Application)
