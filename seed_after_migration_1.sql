-- Выполнить ПОСЛЕ: alembic upgrade 20250401_1
-- и ДО: alembic upgrade 20250401_2
-- Пример: sqlite3 app.db < seed_after_migration_1.sql

INSERT INTO products (title, price, count) VALUES ('Тетрадь', 120.00, 15);
INSERT INTO products (title, price, count) VALUES ('Карандаш', 35.50, 200);
