DELIMITER //
CREATE PROCEDURE BookTicket(IN scrID INT, IN custID INT, IN seat VARCHAR(10))
BEGIN
    INSERT INTO Tickets(ScreeningID, CustomerID, SeatNumber)
    VALUES (scrID, custID, seat);
END //
DELIMITER ;
