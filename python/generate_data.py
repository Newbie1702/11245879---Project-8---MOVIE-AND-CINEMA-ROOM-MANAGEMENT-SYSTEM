import mysql.connector
import random
from faker import Faker
from datetime import datetime, timedelta

fake = Faker()

conn = mysql.connector.connect(
    host="localhost",
    user="root",
    password="170206",
    database="cinema_management"
)
cursor = conn.cursor()

# Xóa data gen cũ
cursor.execute("SET FOREIGN_KEY_CHECKS = 0")
cursor.execute("TRUNCATE TABLE Tickets")
cursor.execute("TRUNCATE TABLE Screenings")
cursor.execute("TRUNCATE TABLE Customers")
cursor.execute("TRUNCATE TABLE CinemaRooms")
cursor.execute("TRUNCATE TABLE Movies")
cursor.execute("TRUNCATE TABLE Accounts")
cursor.execute("SET FOREIGN_KEY_CHECKS = 1")

# Movies: 8 dòng
movies = [
    ("Avengers: Endgame","Action",180),
    ("Titanic","Romance",195),
    ("Inception","Sci-Fi",148),
    ("The Dark Knight","Action",152),
    ("Interstellar","Sci-Fi",169),
    ("Parasite","Drama",132),
    ("Frozen","Animation",102),
    ("Shrek","Animation",90)
]
cursor.executemany("INSERT INTO Movies (MovieTitle, Genre, DurationMinutes) VALUES (%s,%s,%s)", movies)

# CinemaRooms: 10 dòng, capacity = 150
rooms = [(f"Room {chr(65+i)}", 150) for i in range(10)]
cursor.executemany("INSERT INTO CinemaRooms (RoomName, Capacity) VALUES (%s,%s)", rooms)

# Customers: 500 dòng
customers = []
# Sinh 500 account và 500 customer
for i in range(1, 501):
    username = f"cust{i}"
    password = f"custpass{i}"
    role = "Customer"
    # Tạo account cho từng customer
    cursor.execute(
        "INSERT INTO Accounts (Username, Password, Role) VALUES (%s, %s, %s)",
        (username, password, role)
    )
    account_id = cursor.lastrowid
    # Sinh thông tin khách hàng
    name = fake.name()
    phone = fake.phone_number()[:10]
    email = fake.email()
    # Gắn customer với account vừa tạo
    customers.append((name, phone, email, account_id))
# Insert toàn bộ vào bảng Customers
cursor.executemany(
    "INSERT INTO Customers (CustomerName, PhoneNumber, Email, AccountID) VALUES (%s,%s,%s,%s)",
    customers
)

# Screenings: 500 dòng
screenings = []
for i in range(500):
    movie_id = random.randint(1, len(movies))
    room_id = random.randint(1, len(rooms))
    dt = datetime(2026, 5, 15, 19, 0) + timedelta(days=random.randint(0,30), hours=random.randint(0,5))
    screenings.append((movie_id, room_id, dt.date().strftime("%Y-%m-%d"), dt.time().strftime("%H:%M:%S")))
cursor.executemany("INSERT INTO Screenings (MovieID, RoomID, ScreeningDate, ScreeningTime) VALUES (%s,%s,%s,%s)", screenings)

# Tickets: 7500 dòng
tickets = []
seat_numbers = [f"{chr(65+row)}{col}" for row in range(10) for col in range(1,16)]

for scr_id in range(1, 501):  # 500 screenings
    num_tickets = random.randint(5, 20)  # mỗi screening bán 5-20 vé
    chosen_seats = random.sample(seat_numbers, num_tickets)
    for seat in chosen_seats:
        cust_id = random.randint(1, 500)
        price = 100000  # giá vé mặc định
        tickets.append((cust_id, scr_id, seat, price))

cursor.executemany(
    "INSERT INTO Tickets (CustomerID, ScreeningID, SeatNumber, Price) VALUES (%s,%s,%s,%s)",
    tickets
)

conn.commit()
cursor.close()
conn.close()
