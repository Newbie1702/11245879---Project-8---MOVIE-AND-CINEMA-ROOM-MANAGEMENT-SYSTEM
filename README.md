# 11245879---Project-8---MOVIE-AND-CINEMA-ROOM-MANAGEMENT-SYSTEM
# 🎬 Movie & Cinema Room Management System

> **Project 08 – Student ID: 11245879**  
> NEU College of Technology – DATCOM Lab  
> National Economics University

---

## 📌 Introduction

**Movie & Cinema Room Management System** is a full-stack web application built with **Python (Flask)** and **MySQL**, designed to digitize and streamline cinema operations. The system supports two user roles — **Admin** (cinema manager) and **Customer** (cinema-goer) — each with a dedicated interface and set of features.

---

## 🛠️ Technology Stack

| Component | Technology |
|---|---|
| Backend | Python 3.x, Flask |
| Database | MySQL 8.0 |
| Frontend | HTML5, Bootstrap 5, Jinja2 Templates |
| DB Connector | `mysql-connector-python` |
| Sample Data | `Faker`, `random` (Python) |

---

## 📁 Project Structure

```
📦 MOVIE-AND-CINEMA-ROOM-MANAGEMENT-SYSTEM/
├── app.py                        # Main Flask app — all routes & business logic
│
├── python/
│   └── generate_data.py          # Data seeding script (500 customers, ~7,500 tickets)
│
├── sql/
│   ├── schema.sql                # CREATE DATABASE + all core tables
│   ├── audits.sql                # AuditLogs table
│   ├── view.sql                  # TodayScreenings + RevenuePerScreening views
│   ├── procedures.sql            # BookTicket stored procedure
│   ├── functions.sql             # OccupancyRate user-defined function
│   ├── triggers.sql              # prevent_duplicate_booking trigger
│   ├── indexes.sql               # Performance indexes
│   └── securities.sql           # DB user roles and GRANT statements
│
└── templates/
    ├── base.html                 # Shared layout (navbar, Bootstrap, CSS)
    ├── login.html                # Login page
    ├── admin_dashboard.html      # Admin KPI dashboard + revenue report
    ├── admin_accounts.html       # Account list management
    ├── account_detail.html       # Individual account + ticket history
    ├── movies.html               # Movie list
    ├── add_movie.html            # Add/edit movie form
    ├── screenings.html           # Screening list
    ├── add_screening.html        # Add screening form
    ├── tickets.html              # Ticket list (admin + customer views)
    ├── customer_dashboard.html   # Today's screenings for customers
    ├── seats.html                # Interactive seat map
    └── audit_logs.html           # Admin audit log viewer
```

---

## 🗄️ Database Schema

**Database name:** `cinema_management`

### Core Tables

| Table | Key Columns | Description |
|---|---|---|
| `Accounts` | AccountID, Username, Password, Role | Login accounts (admin/customer) |
| `Customers` | CustomerID, CustomerName, PhoneNumber, Email, AccountID | Customer profile linked to account |
| `Movies` | MovieID, MovieTitle, Genre, DurationMinutes | Movie catalog |
| `CinemaRooms` | RoomID, RoomName, Capacity | Screening rooms (10 rooms, 150 seats each) |
| `Screenings` | ScreeningID, MovieID, RoomID, ScreeningDate, ScreeningTime | Scheduled showings |
| `Tickets` | TicketID, CustomerID, ScreeningID, SeatNumber, Price | Purchased tickets |
| `AuditLogs` | LogID, AccountID, Action, TicketID, SeatNumber, Timestamp | Immutable action history |

> **Key constraint:** `UNIQUE (ScreeningID, SeatNumber)` on Tickets prevents double-booking at the database level.

### Advanced Database Objects

| Object | Name | Description |
|---|---|---|
| **View** | `TodayScreenings` | All screenings for the current date with movie & room details |
| **View** | `RevenuePerScreening` | Total revenue and ticket count per screening (used in admin dashboard) |
| **Stored Procedure** | `BookTicket(scrID, custID, seat)` | Inserts a new ticket for a given screening and seat |
| **Function** | `OccupancyRate(scrID)` | Returns occupancy % = (booked seats / room capacity) × 100 |
| **Trigger** | `prevent_duplicate_booking` | BEFORE INSERT on Tickets — raises SQLSTATE 45000 if seat already booked |
| **Index** | `idx_movie_title` | On `Movies(MovieTitle)` — speeds up movie search/sort |
| **Index** | `idx_screening_date` | On `Screenings(ScreeningDate)` — speeds up today's screening filter |
| **Security** | `cinema_admin` | DB user with full SELECT/INSERT/UPDATE/DELETE rights |
| **Security** | `cinema_customer` | DB user with SELECT on `TodayScreenings` view only |

---

## ⚙️ Installation & Setup

### Prerequisites
- Python 3.8+
- MySQL 8.0+
- pip

### 1. Install Python dependencies

```bash
pip install flask mysql-connector-python faker
```

### 2. Create the database

Run SQL files in order from the `sql/` folder:

```bash
source sql/schema.sql;
source sql/audits.sql;
source sql/view.sql;
source sql/procedures.sql;
source sql/functions.sql;
source sql/triggers.sql;
source sql/indexes.sql;
source sql/securities.sql;
```

### 3. Configure database connection

Edit the `get_connection()` function in **`app.py`** and **`python/generate_data.py`**:

```python
def get_connection():
    return mysql.connector.connect(
        host="localhost",
        user="root",
        password="YOUR_MYSQL_PASSWORD",  # change this
        database="cinema_management"
    )
```
Edit the recovery and backup fucntion in **`app.py`**
```python
def backup_db():
    # tạo file backup
    filename = f"backup_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.sql"
    filepath = os.path.join("backup", filename)
    try:
        subprocess.run(
            ["mysqldump", "-u", "root", "-pYOUR_MYSQL_PASSWORD", "cinema_management"],
            stdout=open(filepath, "w"),
            check=True
        )
        # tải file về cho người dùng
        return send_file(filepath, as_attachment=True)
    except Exception as e:
        flash(f"Lỗi backup: {e}", "danger")
        return redirect(url_for('admin_dashboard'))

def recover_db():
    if request.method == 'POST':
        file = request.files['backup_file']
        if file:
            filepath = os.path.join("upload", file.filename)
            file.save(filepath)
            try:
                subprocess.run(
                    ["mysql", "-u", "root", "-pYOUR_MYSQL_PASSWORD", "cinema_management"],
                    stdin=open(filepath, "r"),
                    check=True
                )
                flash("Phục hồi dữ liệu thành công!", "success")
                return redirect(url_for('admin_dashboard'))
            except Exception as e:
                flash(f"Lỗi phục hồi: {e}", "danger")
                return redirect(url_for('recover_db'))
    # nếu GET thì render trang upload
    return render_template("recover.html")
```
### 4. Generate sample data (optional)

```bash
python python/generate_data.py
```

This creates 1 admin + 500 customer accounts, 8 movies, 10 rooms, 500 screenings, and ~7,500 tickets.

### 5. Run the application

```bash
python app.py
```

Open your browser at: **http://127.0.0.1:5000**

---

## 👤 Default Accounts

| Role | Username | Password |
|---|---|---|
| Admin | `admin1` | `adminpass` |
| Customer | `cust1` | `custpass1` |

---

## 🔧 Features

### 🔐 Authentication
- Session-based login/logout
- Role-based routing via Flask decorators (`@login_required`, `@admin_required`, `@customer_required`)

### 👑 Admin Features

| Feature | Details |
|---|---|
| **Dashboard** | KPI cards (total revenue, tickets, movies, customers) + revenue-per-screening report |
| **Movie Management** | Add, edit, delete movies |
| **Screening Management** | Create and delete screenings (movie + room + date + time) |
| **Account Management** | View all accounts, inspect customer profile + ticket history, delete accounts |
| **Ticket Management** | View all tickets, cancel any ticket |
| **Audit Logs** | Full history of booking and cancellation events |
| **Backup / Recovery** | mysqldump backup to file; restore from uploaded .sql file |

### 🧑 Customer Features

| Feature | Details |
|---|---|
| **Dashboard** | Browse today's screenings with sold/capacity display |
| **Seat Map** | Interactive 10×15 grid — red = booked, grey = available, gold = selected |
| **Book Ticket** | Select seat, confirm at fixed price 100,000 VND |
| **My Tickets** | View full personal ticket history |
| **Cancel Ticket** | Cancel own tickets (logged in AuditLogs) |

---

## 🔒 Security & Data Integrity

- **DB-level roles:** `cinema_admin` (full access) / `cinema_customer` (read-only on view)
- **Trigger:** `prevent_duplicate_booking` blocks double-booking at DB layer
- **UNIQUE constraint:** `(ScreeningID, SeatNumber)` enforces seat uniqueness
- **Parameterized queries:** prevent SQL injection
- **Ownership check:** customers can only cancel their own tickets

> ⚠️ Passwords are stored as plain text for academic purposes only. Use bcrypt/Argon2 in production.

---

## 👨‍💻 Author

- **Student ID:** 11245879  
- **Project:** 08 – Movie and Cinema Room Management System  
- **Institution:** NEU College of Technology – National Economics University  
- **Instructor:** hung.tran@neu.edu.vn
