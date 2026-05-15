CREATE TABLE AuditLogs (
    LogID INT AUTO_INCREMENT PRIMARY KEY,
    AccountID INT NOT NULL,
    Action VARCHAR(50) NOT NULL,   -- "Mua vé" hoặc "Hủy vé"
    TicketID INT,
    ScreeningID INT,
    SeatNumber VARCHAR(10),
    Price INT,
    Timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (AccountID) REFERENCES Accounts(AccountID)
);
