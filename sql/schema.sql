DROP DATABASE IF EXISTS cinema_management;
CREATE DATABASE IF NOT EXISTS cinema_management;
USE cinema_management;

DROP TABLE IF EXISTS Accounts;
CREATE TABLE Accounts (
    AccountID INT AUTO_INCREMENT PRIMARY KEY,
    Username VARCHAR(50) UNIQUE,
    Password VARCHAR(255),
    Role ENUM('admin','customer') NOT NULL
);

DROP TABLE IF EXISTS Movies;
CREATE TABLE Movies (
    MovieID INT AUTO_INCREMENT PRIMARY KEY,
    MovieTitle VARCHAR(100),
    Genre VARCHAR(50),
    DurationMinutes INT
);

DROP TABLE IF EXISTS CinemaRooms;
CREATE TABLE CinemaRooms (
    RoomID INT AUTO_INCREMENT PRIMARY KEY,
    RoomName VARCHAR(50),
    Capacity INT
);

DROP TABLE IF EXISTS Screenings;
CREATE TABLE Screenings (
    ScreeningID INT AUTO_INCREMENT PRIMARY KEY,
    MovieID INT,
    RoomID INT,
    ScreeningDate DATE,
    ScreeningTime TIME,
    FOREIGN KEY (MovieID) REFERENCES Movies(MovieID),
    FOREIGN KEY (RoomID) REFERENCES CinemaRooms(RoomID)
);

DROP TABLE IF EXISTS Customers;
CREATE TABLE Customers (
    CustomerID INT AUTO_INCREMENT PRIMARY KEY,
    CustomerName VARCHAR(100),
    PhoneNumber VARCHAR(10),
    Email VARCHAR(100),
    AccountID INT,
    FOREIGN KEY (AccountID) REFERENCES Accounts(AccountID)
);

DROP TABLE IF EXISTS Tickets;
CREATE TABLE Tickets (
    TicketID INT AUTO_INCREMENT PRIMARY KEY,
    CustomerID INT,
    ScreeningID INT,
    SeatNumber VARCHAR(10),
    Price INT,
    FOREIGN KEY (CustomerID) REFERENCES Customers(CustomerID),
    FOREIGN KEY (ScreeningID) REFERENCES Screenings(ScreeningID),
    CONSTRAINT unique_seat_per_screening UNIQUE (ScreeningID, SeatNumber)
);
