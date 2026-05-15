DELIMITER //
CREATE TRIGGER prevent_duplicate_booking
BEFORE INSERT ON Tickets
FOR EACH ROW
BEGIN
    IF EXISTS (SELECT 1 FROM Tickets WHERE ScreeningID = NEW.ScreeningID AND SeatNumber = NEW.SeatNumber) THEN
        SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'Seat already booked!';
    END IF;
END //
DELIMITER ;
