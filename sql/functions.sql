DELIMITER //
CREATE FUNCTION OccupancyRate(scrID INT)
RETURNS DECIMAL(5,2)
DETERMINISTIC
BEGIN
    DECLARE totalSeats INT;
    DECLARE bookedSeats INT;
    DECLARE rate DECIMAL(5,2);

    SELECT Capacity INTO totalSeats
    FROM CinemaRooms r JOIN Screenings s ON r.RoomID = s.RoomID
    WHERE s.ScreeningID = scrID;

    SELECT COUNT(*) INTO bookedSeats FROM Tickets WHERE ScreeningID = scrID;

    SET rate = (bookedSeats / totalSeats) * 100;
    RETURN rate;
END //
DELIMITER ;
