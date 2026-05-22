from flask import Flask, request, render_template, redirect, url_for, session, flash
import mysql.connector
from functools import wraps
import os
from flask import send_file

app = Flask(__name__)
app.secret_key = "cinema_management_secret_key_v2"

# =====================================================================
# DB CONNECTION
# =====================================================================
def get_connection():
    return mysql.connector.connect(
        host="localhost",
        user="root",
        password="170206",
        database="cinema_management"
    )
# TÀI KHOẢN ADMIN
cursor.execute("INSERT INTO Accounts (Username, Password, Role) VALUES (%s, %s, %s)", ("admin1", "adminpass", "Admin"))

# =====================================================================
# DECORATORS
# =====================================================================

def login_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):

        if (
            'username' not in session or
            'role' not in session or
            'account_id' not in session
        ):
            session.clear()
            flash("Vui lòng đăng nhập!", "warning")
            return redirect(url_for('login_page'))

        return f(*args, **kwargs)

    return decorated


def admin_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):

        if session.get('role') != 'admin':
            flash("Bạn không có quyền truy cập!", "danger")
            return redirect(url_for('login_page'))

        return f(*args, **kwargs)

    return decorated


def customer_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):

        if session.get('role') != 'customer':
            flash("Vui lòng đăng nhập tài khoản khách hàng!", "danger")
            return redirect(url_for('login_page'))

        return f(*args, **kwargs)

    return decorated


# =====================================================================
# AUTH
# =====================================================================
@app.route('/')
def home():
    # Mỗi lần vào trang chủ đều xóa session và quay về login
    session.clear()
    return redirect(url_for('login_page'))


@app.route('/login', methods=['GET', 'POST'])
def login_page():
    if request.method == 'GET':
        return render_template('login.html')

    if request.method == 'POST':
        username = request.form['username'].strip()
        password = request.form['password']

        conn = get_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute(
            "SELECT AccountID, Username, Password, Role FROM Accounts WHERE Username=%s AND Password=%s",
            (username, password)
        )
        account = cursor.fetchone()
        cursor.close()
        conn.close()

        if account:
            session.clear()
            session['account_id'] = account['AccountID']
            session['username'] = account['Username']
            session['role'] = account['Role'].lower()

            flash(f"Chào mừng {username}!", "success")

            if session['role'] == 'admin':
                return redirect(url_for('admin_dashboard'))
            elif session['role'] == 'customer':
                return redirect(url_for('customer_dashboard'))
            else:
                flash("Role không hợp lệ!", "danger")
                return render_template('login.html')
        else:
            flash("Sai tài khoản hoặc mật khẩu!", "danger")
            return render_template('login.html')


@app.route('/logout')
def logout():
    session.clear()
    flash("Đã đăng xuất thành công!", "info")
    return redirect(url_for('login_page'))

# =====================================================================
# ADMIN – Dashboard & Báo cáo
# =====================================================================
@app.route('/admin/dashboard')
@login_required
@admin_required
def admin_dashboard():
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)

    # Tổng doanh thu
    cursor.execute("SELECT IFNULL(SUM(Price), 0) AS total FROM Tickets")
    total_revenue = cursor.fetchone()['total']

    # Tổng số vé
    cursor.execute("SELECT COUNT(*) AS cnt FROM Tickets")
    total_tickets = cursor.fetchone()['cnt']

    # Tổng số phim
    cursor.execute("SELECT COUNT(*) AS cnt FROM Movies")
    total_movies = cursor.fetchone()['cnt']

    # Tổng số khách hàng
    cursor.execute("SELECT COUNT(*) AS cnt FROM Customers")
    total_customers = cursor.fetchone()['cnt']

    # Doanh thu theo từng suất chiếu (view)
    cursor.execute("SELECT * FROM RevenuePerScreening ORDER BY ScreeningDate DESC, ScreeningTime DESC")
    reports = cursor.fetchall()

    cursor.close()
    conn.close()
    return render_template(
        "admin_dashboard.html",
        reports=reports,
        total_revenue=total_revenue,
        total_tickets=total_tickets,
        total_movies=total_movies,
        total_customers=total_customers
    )


# =====================================================================
# ADMIN – Quản lý tài khoản
# =====================================================================
@app.route('/admin/accounts')
@login_required
@admin_required
def admin_accounts():
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT AccountID, Username, Role FROM Accounts ORDER BY AccountID")
    accounts = cursor.fetchall()
    cursor.close()
    conn.close()
    return render_template("admin_accounts.html", accounts=accounts)

@app.route('/admin/accounts/<int:account_id>')
@login_required
@admin_required
def account_detail(account_id):
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)

    # Thông tin account + customer
    cursor.execute("""
        SELECT a.AccountID, a.Username, a.Role,
               c.CustomerName, c.PhoneNumber, c.Email
        FROM Accounts a
        LEFT JOIN Customers c ON a.AccountID = c.AccountID
        WHERE a.AccountID=%s
    """, (account_id,))
    account = cursor.fetchone()

    # Vé đã mua
    cursor.execute("""
        SELECT t.TicketID, m.MovieTitle, s.ScreeningDate, s.ScreeningTime,
            r.RoomName, t.SeatNumber, t.Price
        FROM Tickets t
        JOIN Screenings s ON t.ScreeningID = s.ScreeningID
        JOIN Movies m ON s.MovieID = m.MovieID
        JOIN CinemaRooms r ON s.RoomID = r.RoomID
        WHERE t.CustomerID = (SELECT CustomerID FROM Customers WHERE AccountID=%s)
        ORDER BY s.ScreeningDate DESC, s.ScreeningTime DESC
    """, (account_id,))
    tickets = cursor.fetchall()

    # Tổng số vé và tổng tiền
    cursor.execute("""
        SELECT COUNT(TicketID) AS TotalTickets, SUM(Price) AS TotalAmount
        FROM Tickets
        WHERE CustomerID = (SELECT CustomerID FROM Customers WHERE AccountID=%s)
    """, (account_id,))
    summary = cursor.fetchone()

    cursor.close()
    conn.close()

    return render_template("account_detail.html",
                        account=account,
                        tickets=tickets,
                        summary=summary)


@app.route('/admin/accounts/delete/<int:account_id>', methods=['POST'])
@login_required
@admin_required
def delete_account(account_id):
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("DELETE FROM Customers WHERE AccountID=%s", (account_id,))
        cursor.execute("DELETE FROM Accounts WHERE AccountID=%s", (account_id,))
        # Ghi log hành động xóa
        cursor.execute("INSERT INTO AuditLogs(AccountID, Action, Timestamp) VALUES (%s,%s,NOW())",
                       (account_id, "Xóa tài khoản"))
        conn.commit()
        flash("Đã xóa tài khoản!", "success")
    except mysql.connector.Error as err:
        conn.rollback()
        flash(f"Lỗi: {err.msg}", "danger")
    finally:
        cursor.close()
        conn.close()
    return redirect(url_for('admin_accounts'))

# =====================================================================
# ADMIN – Quản lý phim
# =====================================================================
@app.route('/admin/movies')
@login_required
@admin_required
def admin_movies():
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM Movies ORDER BY MovieTitle")
    movies = cursor.fetchall()
    cursor.close()
    conn.close()
    return render_template("movies.html", movies=movies)


@app.route('/admin/add_movie', methods=['GET', 'POST'])
@login_required
@admin_required
def add_movie():
    if request.method == 'POST':
        title    = request.form['title'].strip()
        genre    = request.form['genre'].strip()
        duration = request.form['duration']
        conn = get_connection()
        cursor = conn.cursor()
        try:
            cursor.execute(
                "INSERT INTO Movies(MovieTitle, Genre, DurationMinutes) VALUES (%s,%s,%s)",
                (title, genre, duration)
            )
            conn.commit()
            flash("Phim đã được thêm thành công!", "success")
            return redirect(url_for('admin_movies'))
        except mysql.connector.Error as err:
            conn.rollback()
            flash(f"Lỗi: {err.msg}", "danger")
        finally:
            cursor.close()
            conn.close()
    return render_template("add_movie.html")


@app.route('/admin/edit_movie/<int:movie_id>', methods=['GET', 'POST'])
@login_required
@admin_required
def edit_movie(movie_id):
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    if request.method == 'POST':
        title    = request.form['title'].strip()
        genre    = request.form['genre'].strip()
        duration = request.form['duration']
        try:
            cursor.execute(
                "UPDATE Movies SET MovieTitle=%s, Genre=%s, DurationMinutes=%s WHERE MovieID=%s",
                (title, genre, duration, movie_id)
            )
            conn.commit()
            flash("Cập nhật phim thành công!", "success")
            return redirect(url_for('admin_movies'))
        except mysql.connector.Error as err:
            conn.rollback()
            flash(f"Lỗi: {err.msg}", "danger")
        finally:
            cursor.close()
            conn.close()
    else:
        cursor.execute("SELECT * FROM Movies WHERE MovieID=%s", (movie_id,))
        movie = cursor.fetchone()
        cursor.close()
        conn.close()
        if not movie:
            flash("Không tìm thấy phim!", "danger")
            return redirect(url_for('admin_movies'))
        return render_template("add_movie.html", movie=movie)


@app.route('/admin/delete_movie/<int:movie_id>', methods=['POST'])
@login_required
@admin_required
def delete_movie(movie_id):
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("DELETE FROM Movies WHERE MovieID=%s", (movie_id,))
        conn.commit()
        flash("Đã xóa phim!", "success")
    except mysql.connector.Error as err:
        conn.rollback()
        flash(f"Lỗi khi xóa (có thể phim đang có suất chiếu): {err.msg}", "danger")
    finally:
        cursor.close()
        conn.close()
    return redirect(url_for('admin_movies'))


# =====================================================================
# ADMIN – Quản lý suất chiếu
# =====================================================================
@app.route('/admin/screenings')
@login_required
@admin_required
def admin_screenings():
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("""
        SELECT s.ScreeningID, m.MovieTitle, r.RoomName,
               s.ScreeningDate, s.ScreeningTime
        FROM Screenings s
        JOIN Movies m ON s.MovieID = m.MovieID
        JOIN CinemaRooms r ON s.RoomID = r.RoomID
        ORDER BY s.ScreeningDate DESC, s.ScreeningTime
    """)
    screenings = cursor.fetchall()
    cursor.close()
    conn.close()
    return render_template("screenings.html", screenings=screenings)


@app.route('/admin/add_screening', methods=['GET', 'POST'])
@login_required
@admin_required
def add_screening():
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)

    if request.method == 'POST':
        movie_id = request.form['movie_id']
        room_id  = request.form['room_id']
        date     = request.form['date']
        time     = request.form['time']
        try:
            cursor.execute(
                "INSERT INTO Screenings(MovieID, RoomID, ScreeningDate, ScreeningTime) VALUES (%s,%s,%s,%s)",
                (movie_id, room_id, date, time)
            )
            conn.commit()
            flash("Suất chiếu đã được thêm!", "success")
            return redirect(url_for('admin_screenings'))
        except mysql.connector.Error as err:
            conn.rollback()
            flash(f"Lỗi: {err.msg}", "danger")
        finally:
            cursor.close()
            conn.close()
    else:
        cursor.execute("SELECT MovieID, MovieTitle FROM Movies ORDER BY MovieTitle")
        movies = cursor.fetchall()
        cursor.execute("SELECT RoomID, RoomName FROM CinemaRooms ORDER BY RoomName")
        rooms = cursor.fetchall()
        cursor.close()
        conn.close()
        return render_template("add_screening.html", movies=movies, rooms=rooms)


@app.route('/admin/delete_screening/<int:screening_id>', methods=['POST'])
@login_required
@admin_required
def delete_screening(screening_id):
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("DELETE FROM Screenings WHERE ScreeningID=%s", (screening_id,))
        conn.commit()
        flash("Đã xóa suất chiếu!", "success")
    except mysql.connector.Error as err:
        conn.rollback()
        flash(f"Lỗi: {err.msg}", "danger")
    finally:
        cursor.close()
        conn.close()
    return redirect(url_for('admin_screenings'))


# =====================================================================
# ADMIN – Quản lý vé
# =====================================================================
@app.route('/admin/tickets')
@login_required
@admin_required
def admin_tickets():
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("""
        SELECT t.TicketID, c.CustomerName, m.MovieTitle,
               s.ScreeningDate, s.ScreeningTime, r.RoomName,
               t.SeatNumber, t.Price
        FROM Tickets t
        JOIN Customers c ON t.CustomerID = c.CustomerID
        JOIN Screenings s ON t.ScreeningID = s.ScreeningID
        JOIN Movies m ON s.MovieID = m.MovieID
        JOIN CinemaRooms r ON s.RoomID = r.RoomID
        ORDER BY CONCAT(s.ScreeningDate, ' ', s.ScreeningTime) DESC
    """)
    tickets = cursor.fetchall()
    cursor.close()
    conn.close()
    return render_template("tickets.html", tickets=tickets, is_admin=True)


@app.route('/admin/tickets/delete/<int:ticket_id>', methods=['POST'])
@login_required
@admin_required
def delete_ticket(ticket_id):
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("DELETE FROM Tickets WHERE TicketID=%s", (ticket_id,))
        conn.commit()
        flash("Đã hủy vé!", "success")
    except mysql.connector.Error as err:
        conn.rollback()
        flash(f"Lỗi: {err.msg}", "danger")
    finally:
        cursor.close()
        conn.close()
    return redirect(url_for('admin_tickets'))

# =====================================================================
# ADMIN – Backup và Recovery
# =====================================================================
import subprocess
import datetime

@app.route('/admin/backup')
@login_required
@admin_required
def backup_db():
    # tạo file backup
    filename = f"backup_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.sql"
    filepath = os.path.join("backup", filename)
    try:
        subprocess.run(
            ["mysqldump", "-u", "root", "-p170206", "cinema_management"],
            stdout=open(filepath, "w"),
            check=True
        )
        # tải file về cho người dùng
        return send_file(filepath, as_attachment=True)
    except Exception as e:
        flash(f"Lỗi backup: {e}", "danger")
        return redirect(url_for('admin_dashboard'))

@app.route('/admin/recover', methods=['GET', 'POST'])
@login_required
@admin_required
def recover_db():
    if request.method == 'POST':
        file = request.files['backup_file']
        if file:
            filepath = os.path.join("upload", file.filename)
            file.save(filepath)
            try:
                subprocess.run(
                    ["mysql", "-u", "root", "-p170206", "cinema_management"],
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

# =====================================================================
# CUSTOMER – Dashboard xem phim hôm nay
# =====================================================================
@app.route('/customer/dashboard')
@login_required
@customer_required
def customer_dashboard():

    account_id = session.get('account_id')

    if not account_id:
        session.clear()
        flash("Session hết hạn. Vui lòng đăng nhập lại!", "danger")
        return redirect(url_for('login_page'))

    conn = get_connection()
    cursor = conn.cursor(dictionary=True)

    cursor.execute(
        "SELECT CustomerID FROM Customers WHERE AccountID=%s",
        (account_id,)
    )

    customer = cursor.fetchone()

    customer_id = customer['CustomerID'] if customer else None

    cursor.execute("""
        SELECT m.MovieTitle,
               m.Genre,
               m.DurationMinutes,
               s.ScreeningID,
               s.ScreeningDate,
               s.ScreeningTime,
               r.RoomName,
               r.Capacity,
               (
                   SELECT COUNT(*)
                   FROM Tickets t
                   WHERE t.ScreeningID = s.ScreeningID
               ) AS sold
        FROM Screenings s
        JOIN Movies m ON s.MovieID = m.MovieID
        JOIN CinemaRooms r ON s.RoomID = r.RoomID
        WHERE s.ScreeningDate = CURDATE()
        ORDER BY s.ScreeningTime
    """)

    screenings = cursor.fetchall()

    cursor.close()
    conn.close()

    return render_template(
        "customer_dashboard.html",
        screenings=screenings,
        customer_id=customer_id
    )


# =====================================================================
# CUSTOMER – Chọn ghế & đặt vé
# =====================================================================
@app.route('/customer/seats/<int:screening_id>')
@login_required
@customer_required
def view_seats(screening_id):
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)

    cursor.execute("""
        SELECT s.ScreeningID, m.MovieTitle, s.ScreeningDate,
               s.ScreeningTime, r.RoomName, r.Capacity
        FROM Screenings s
        JOIN Movies m ON s.MovieID = m.MovieID
        JOIN CinemaRooms r ON s.RoomID = r.RoomID
        WHERE s.ScreeningID=%s
    """, (screening_id,))
    screening = cursor.fetchone()

    cursor.execute("SELECT SeatNumber FROM Tickets WHERE ScreeningID=%s", (screening_id,))
    booked_seats = {row['SeatNumber'] for row in cursor.fetchall()}

    cursor.execute("SELECT CustomerID FROM Customers WHERE AccountID=%s", (session.get('account_id'),))
    customer = cursor.fetchone()
    customer_id = customer['CustomerID'] if customer else None

    cursor.close()
    conn.close()

    rows = [chr(65 + i) for i in range(10)]
    cols = list(range(1, 16))              

    return render_template(
        "seats.html",
        screening=screening,
        booked_seats=booked_seats,
        rows=rows,
        cols=cols,
        customer_id=customer_id,
        price=100000
    )

@app.route('/customer/checkout', methods=['POST'])
@login_required
@customer_required
def checkout():
    customer_id  = request.form['customer_id']
    screening_id = request.form['screening_id']
    seat         = request.form['seat']   # chỉ 1 ghế
    price        = int(request.form.get('price', 100000))

    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute(
            "SELECT TicketID FROM Tickets WHERE ScreeningID=%s AND SeatNumber=%s",
            (screening_id, seat)
        )
        if cursor.fetchone():
            flash(f"Ghế {seat} đã được đặt!", "danger")
        else:
            cursor.execute(
                "INSERT INTO Tickets(CustomerID, ScreeningID, SeatNumber, Price) VALUES (%s,%s,%s,%s)",
                (customer_id, screening_id, seat, price)
            )
            conn.commit()
            flash(f"Thanh toán thành công 1 vé! Giá: {price} VND", "success")
    except mysql.connector.Error as err:
        conn.rollback()
        flash(f"Lỗi: {err.msg}", "danger")
    finally:
        cursor.close()
        conn.close()
    return redirect(url_for('customer_dashboard'))

# =====================================================================
# CUSTOMER – Lịch sử vé của tôi
# =====================================================================
@app.route('/customer/my_tickets')
@login_required
@customer_required
def my_tickets():
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute(
        "SELECT CustomerID FROM Customers WHERE AccountID=%s",
        (session.get('account_id'),)
    )
    customer = cursor.fetchone()
    if not customer:
        flash("Không tìm thấy thông tin khách hàng!", "danger")
        return redirect(url_for('customer_dashboard'))

    cursor.execute("""
        SELECT t.TicketID, m.MovieTitle, s.ScreeningDate,
               s.ScreeningTime, r.RoomName, t.SeatNumber, t.Price
        FROM Tickets t
        JOIN Screenings s ON t.ScreeningID = s.ScreeningID
        JOIN Movies m ON s.MovieID = m.MovieID
        JOIN CinemaRooms r ON s.RoomID = r.RoomID
        WHERE t.CustomerID=%s
        ORDER BY s.ScreeningDate DESC, s.ScreeningTime DESC
    """, (customer['CustomerID'],))
    tickets = cursor.fetchall()
    cursor.close()
    conn.close()
    return render_template("tickets.html", tickets=tickets, is_admin=False)


@app.route('/customer/cancel_ticket/<int:ticket_id>', methods=['POST'])
@login_required
@customer_required
def cancel_ticket(ticket_id):
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    # Kiểm tra vé có thuộc về customer này không
    cursor.execute(
        "SELECT CustomerID FROM Customers WHERE AccountID=%s",
        (session.get('account_id'),)
    )
    customer = cursor.fetchone()
    cursor2 = conn.cursor()
    try:
        cursor2.execute(
            "DELETE FROM Tickets WHERE TicketID=%s AND CustomerID=%s",
            (ticket_id, customer['CustomerID'])
        )
        cursor2.execute(
            "INSERT INTO AuditLogs(AccountID, Action, TicketID, ScreeningID, SeatNumber, Price) VALUES (%s,%s,%s,%s,%s,%s)",
            (session.get('account_id'), "Hủy vé", ticket_id, None, None, None)
        )
        conn.commit()
        flash("Đã hủy vé thành công!", "success")
    except mysql.connector.Error as err:
        conn.rollback()
        flash(f"Lỗi: {err.msg}", "danger")
    finally:
        cursor.close()
        cursor2.close()
        conn.close()
    return redirect(url_for('my_tickets'))


# =====================================================================
# RUN
# =====================================================================
if __name__ == '__main__':
    app.run(debug=True)
