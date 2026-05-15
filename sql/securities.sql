-- Admin có toàn quyền
GRANT SELECT, INSERT, UPDATE, DELETE ON cinema_management.* TO 'cinema_admin'@'localhost';

-- Customer chỉ được SELECT từ view
GRANT SELECT ON cinema_management.TodayScreenings TO 'cinema_customer'@'localhost';
