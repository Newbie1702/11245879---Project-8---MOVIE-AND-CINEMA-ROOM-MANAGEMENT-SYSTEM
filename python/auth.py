from db_utils import get_connection

def login(username, password):
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM Accounts WHERE Username=%s AND Password=%s", (username, password))
    account = cursor.fetchone()
    cursor.close()
    conn.close()
    if account:
        print(f"Login successful! Role: {account['Role']}")
        return account['Role'], account['AccountID']
    else:
        print("Invalid credentials!")
        return None, None
