from db_utils import get_connection

def book_ticket(screening_id, customer_id, seat):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("CALL BookTicket(%s,%s,%s)", (screening_id, customer_id, seat))
    conn.commit()
    cursor.close()
    conn.close()
    print("Ticket booked successfully!")

def cancel_ticket(ticket_id):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM Tickets WHERE TicketID=%s", (ticket_id,))
    conn.commit()
    cursor.close()
    conn.close()
    print("Ticket cancelled successfully!")
