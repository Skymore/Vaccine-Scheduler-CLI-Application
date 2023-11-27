CREATE TABLE Caregivers
(
    Username varchar(255),
    Salt BINARY(16),
    Hash BINARY(16),
    PRIMARY KEY (Username)
);

CREATE TABLE Availabilities
(
    Time date,
    Username varchar(255) REFERENCES Caregivers,
    -- 0: 'Available', 1: 'Occupied'
    Status INT,
    PRIMARY KEY (Time, Username)
);

CREATE TABLE Vaccines
(
    Name varchar(255),
    Doses int,
    PRIMARY KEY (Name)
);

CREATE TABLE Patients
(
    Username varchar(255),
    Salt BINARY(16),
    Hash BINARY(16),
    PRIMARY KEY (Username)
)

CREATE TABLE Appointments
(
    ID INT IDENTITY(1, 1) PRIMARY KEY,
    Time DATE NOT NULL,
    -- 0:'Scheduled', 1: 'Completed', 2: 'Cancelled'
    Status INT,
    Pname VARCHAR(255) REFERENCES Patients(Username),
    Cname VARCHAR(255) REFERENCES Caregivers(Username),
    Vname VARCHAR(255) REFERENCES Vaccines(Name),
)
