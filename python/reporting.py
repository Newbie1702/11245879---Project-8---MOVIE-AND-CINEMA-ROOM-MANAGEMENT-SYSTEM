from db_utils import get_connection

def screening_report():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT s.ScreeningID, m.MovieTitle, r.RoomName, s.ScreeningDate, s.ScreeningTime,
               COUNT(t.TicketID) AS TicketsSold, OccupancyRate(s.ScreeningID) AS Rate
        FROM Screenings s
        JOIN Movies m ON s.MovieID = m.MovieID
        JOIN CinemaRooms r ON s.RoomID = r.RoomID
        LEFT JOIN Tickets t ON s.ScreeningID = t.ScreeningID
        GROUP BY s.ScreeningID
    """)
    for row in cursor.fetchall():
        print(row)
    cursor.close()
    conn.close()
