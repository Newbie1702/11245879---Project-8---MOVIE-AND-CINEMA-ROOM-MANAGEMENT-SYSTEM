CREATE OR REPLACE VIEW TodayScreenings AS
SELECT s.ScreeningID, m.MovieTitle, r.RoomName, s.ScreeningDate, s.ScreeningTime
FROM Screenings s
JOIN Movies m ON s.MovieID = m.MovieID
JOIN CinemaRooms r ON s.RoomID = r.RoomID
WHERE s.ScreeningDate = CURDATE();

CREATE OR REPLACE VIEW RevenuePerScreening AS
SELECT s.ScreeningID, m.MovieTitle, s.ScreeningDate, s.ScreeningTime,
       SUM(t.Price) AS TotalRevenue, COUNT(t.TicketID) AS TicketsSold
FROM Screenings s
JOIN Movies m ON s.MovieID = m.MovieID
LEFT JOIN Tickets t ON s.ScreeningID = t.ScreeningID
GROUP BY s.ScreeningID, m.MovieTitle, s.ScreeningDate, s.ScreeningTime;
