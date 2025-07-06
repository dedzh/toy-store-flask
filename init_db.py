"""
Модуль для инициализации базы данных игрушечного интернет-магазина.

Создаёт и наполняет таблицы:
- users
- categories
- products
- orders
- order_items
- payments
- delivery

После запуска файл создаёт файл базы данных toy_store.db.
"""

import sqlite3
import os
from werkzeug.security import generate_password_hash

DATABASE = 'toy_store.db'

def initialize_database():
    """
    Инициализирует базу данных, создаёт таблицы и наполняет их тестовыми данными.
    При наличии старой базы — удаляет её.
    """

    # Удаление старой базы данных
    if os.path.exists(DATABASE):
        os.remove(DATABASE)
    
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()

    # === Создание таблиц ===
    cursor.execute("""
    CREATE TABLE users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        email TEXT UNIQUE NOT NULL,
        password_hash TEXT NOT NULL,
        full_name TEXT NOT NULL,
        address TEXT NOT NULL,
        phone TEXT,
        registered_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
    """)

    cursor.execute("""
    CREATE TABLE categories (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        description TEXT
    );
    """)

    cursor.execute("""
    CREATE TABLE products (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        description TEXT,
        price REAL NOT NULL CHECK (price > 0),
        stock_quantity INTEGER NOT NULL CHECK (stock_quantity >= 0),
        category_id INTEGER NOT NULL,
        manufacturer TEXT NOT NULL,
        material TEXT NOT NULL,
        age_min INTEGER NOT NULL CHECK (age_min > 0),
        batteries_included BOOLEAN DEFAULT FALSE,
        image_filename TEXT,
        FOREIGN KEY (category_id) REFERENCES categories(id)
        );
    """)

    cursor.execute("""
    CREATE TABLE orders (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL,
        status TEXT NOT NULL DEFAULT 'Создан',
        order_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (user_id) REFERENCES users(id)
    );
    """)

    cursor.execute("""
    CREATE TABLE order_items (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        order_id INTEGER NOT NULL,
        product_id INTEGER NOT NULL,
        quantity INTEGER NOT NULL CHECK (quantity > 0),
        price REAL NOT NULL CHECK (price > 0),
        FOREIGN KEY (order_id) REFERENCES orders(id) ON DELETE CASCADE,
        FOREIGN KEY (product_id) REFERENCES products(id),
        UNIQUE (order_id, product_id)
    );
    """)

    cursor.execute("""
    CREATE TABLE payments (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        order_id INTEGER UNIQUE NOT NULL,
        method TEXT NOT NULL,
        amount REAL NOT NULL CHECK (amount > 0),
        status TEXT NOT NULL DEFAULT 'Ожидание',
        payment_date TIMESTAMP,
        FOREIGN KEY (order_id) REFERENCES orders(id)
    );
    """)

    cursor.execute("""
    CREATE TABLE delivery (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        order_id INTEGER UNIQUE NOT NULL,
        address TEXT NOT NULL,
        status TEXT NOT NULL DEFAULT 'Ожидание',
        shipped_date DATETIME,
        delivered_date DATETIME,
        FOREIGN KEY (order_id) REFERENCES orders(id)
    );
    """)

    # === Индексы для оптимизации ===
    cursor.execute("CREATE INDEX idx_products_category ON products(category_id)")
    cursor.execute("CREATE INDEX idx_orders_user ON orders(user_id)")
    cursor.execute("CREATE INDEX idx_order_items_order ON order_items(order_id)")
    cursor.execute("CREATE INDEX idx_payments_order ON payments(order_id)")
    cursor.execute("CREATE INDEX idx_delivery_order ON delivery(order_id)")

    # === Заполнение таблиц тестовыми данными ===

    # Категории
    categories = [
        ('Конструкторы', 'Развивающие конструкторы для всех возрастов'),
        ('Настольные игры', 'Игры для компании и семьи'),
        ('Куклы', 'Куклы и аксессуары для девочек'),
        ('Радиоуправляемые модели', 'Техника с дистанционным управлением')
    ]
    cursor.executemany("INSERT INTO categories (name, description) VALUES (?, ?)", categories)

    # Товары
    products = [
        ('LEGO Technic', 5999.99, 15, 1, 'LEGO', 'Пластик', 8, 0,'splash.jpg'),
        ('Монополия Deluxe', 2499.50, 8, 2, 'Hasbro', 'Картон', 6, 0,'splash.jpg'),
        ('Барби Дримхаус', 8999.99, 5, 3, 'Mattel', 'Пластик', 3, 0,'splash.jpg'),
        ('Дрон DJI Mavic', 32999.99, 3, 4, 'DJI', 'Пластик', 14, 1,'splash.jpg'),
        ('Конструктор Metall', 3599.00, 20, 1, 'Gigo', 'Металл', 6, 0,'splash.jpg'),
        ('UNO Карты', 599.00, 30, 2, 'Mattel', 'Картон', 3, 0,'splash.jpg'),
        ('LOL Surprise', 2499.00, 12, 3, 'MGA Entertainment', 'Пластик', 4, 0,'splash.jpg'),
        ('Радиоуправляемый вертолет', 4599.99, 7, 4, 'Syma', 'Пластик', 8, 1,'splash.jpg'),
        ('Магформерс Basic', 7990.00, 9, 1, 'Magnetic', 'Пластик/магнит', 3, 0,'splash.jpg'),
        ('Дженга Классик', 1299.00, 18, 2, 'Hasbro', 'Дерево', 6, 0,'splash.jpg'),
        ('Winx Кукла Bloom', 1599.00, 10, 3, 'Giochi Preziosi', 'Пластик', 3, 0,'splash.jpg'),
        ('RC Машина Lamborghini', 7599.00, 6, 4, 'WLtoys', 'Пластик', 8, 1,'splash.jpg'),
        ('LEGO Star Wars', 8999.00, 11, 1, 'LEGO', 'Пластик', 9, 0,'splash.jpg'),
        ('Эрудит Премиум', 3499.00, 7, 2, 'Mattel', 'Пластик', 10, 0,'splash.jpg'),
        ('Братц Кукла', 1999.00, 14, 3, 'MGA Entertainment', 'Пластик', 5, 0,'splash.jpg'),
        ('RC Катер', 5999.00, 4, 4, 'JJRC', 'Пластик', 12, 1,'splash.jpg'),
        ('Tegu Блочный конструктор', 11999.00, 5, 1, 'Tegu', 'Дерево/магнит', 4, 0,'splash.jpg'),
        ('Catan Колонизаторы', 4990.00, 9, 2, 'Asmodee', 'Картон', 10, 0,'splash.jpg'),
        ('Frozen Эльза', 2999.00, 8, 3, 'Disney', 'Пластик', 3, 0,'splash.jpg'),
        ('RC Танк с ИК-пушкой', 3899.00, 7, 4, 'Heng Long', 'Пластик', 10, 1,'splash.jpg')
    ]
    cursor.executemany("""
        INSERT INTO products (name, price, stock_quantity, category_id, manufacturer, material, age_min, batteries_included)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, products)

    # Пользователи
    password_hash = generate_password_hash('123456')
    users = [
        ('ivanov@example.com', password_hash, 'Иван Иванов', 'Москва, ул. Тверская, д.10, кв.25', '+79161234567'),
       ('petrova@mail.ru', password_hash, 'Елена Петрова', 'Санкт-Петербург, Невский пр., д.45', '+78125556677'),
        ('sidorov@gmail.com', password_hash, 'Алексей Сидоров', 'Екатеринбург, ул. Ленина, д.3', '+73432897654'),
        ('smirnova@yandex.ru', password_hash, 'Ольга Смирнова', 'Новосибирск, Красный пр., д.100', '+73832223344'),
        ('kuznetsov@outlook.com', password_hash, 'Дмитрий Кузнецов', 'Казань, ул. Баумана, д.15', '+78435554433'),
        ('nikolaeva@bk.ru', password_hash, 'Мария Николаева', 'Сочи, ул. Навагинская, д.8', '+78622667788'),
        ('fedorov@inbox.ru', password_hash, 'Андрей Федоров', 'Владивосток, ул. Светланская, д.22', '+74231234567'),
        ('alexeeva@proton.me', password_hash, 'Татьяна Алексеева', 'Калининград, Ленинский пр., д.30', '+74012345678'),
        ('morozov@yahoo.com', password_hash, 'Павел Морозов', 'Ростов-на-Дону, ул. Б. Садовая, д.50', '+78633001122'),
        ('orlova@hotmail.com', password_hash, 'Наталья Орлова', 'Самара, ул. Куйбышева, д.125', '+84629998877')
    ]
    cursor.executemany("""
        INSERT INTO users (email, password_hash, full_name, address, phone)
        VALUES (?, ?, ?, ?, ?)
    """, users)
# Заказы
    orders = [
        (1, 'Доставлен'),
        (2, 'В обработке'),
        (3, 'Отправлен'),
        (4, 'Создан'),
        (1, 'Оплачен'),
        (5, 'Доставлен'),
        (6, 'Отменен'),
        (7, 'В обработке'),
        (8, 'Отправлен'),
        (9, 'Доставлен')
    ]
    cursor.executemany("INSERT INTO orders (user_id, status) VALUES (?, ?)", orders)

    # Позиции заказов
    order_items = [
        (1, 3, 1, 8999.99),
        (1, 7, 2, 2499.00),
        (2, 12, 1, 7599.00),
        (3, 5, 1, 3599.00),
        (3, 10, 1, 1299.00),
        (4, 1, 1, 5999.99),
        (5, 4, 1, 32999.99),
        (6, 8, 3, 4599.99),
        (7, 15, 2, 1999.00),
        (8, 18, 1, 4990.00),
        (9, 2, 1, 2499.50),
        (10, 20, 1, 3899.00),
        (10, 14, 1, 3499.00)
    ]
    cursor.executemany("""
        INSERT INTO order_items (order_id, product_id, quantity, price)
        VALUES (?, ?, ?, ?)
    """, order_items)

    # Оплаты
    payments = [
        (1, 'Карта', 13997.99, 'Успешно', '2023-10-01 14:30:00'),
        (2, 'Электронный кошелек', 7599.00, 'Успешно', '2023-10-02 10:15:00'),
        (3, 'Карта', 4898.00, 'Успешно', '2023-10-03 16:45:00'),
        (5, 'Карта', 32999.99, 'Успешно', '2023-10-05 11:20:00'),
        (6, 'Наличные', 13799.97, 'Успешно', '2023-10-06 09:30:00'),
        (8, 'Карта', 4990.00, 'Ожидание', None),
        (9, 'Электронный кошелек', 2499.50, 'Успешно', '2023-10-09 18:40:00'),
        (10, 'Карта', 7398.00, 'Успешно', '2023-10-10 12:00:00')
    ]
    cursor.executemany("""
        INSERT INTO payments (order_id, method, amount, status, payment_date)
        VALUES (?, ?, ?, ?, ?)
    """, payments)

    # Доставка
    deliveries = [
        (1, 'Москва, ул. Тверская, д.10, кв.25', 'Доставлено', '2023-10-01 15:00:00', '2023-10-03 11:30:00'),
        (2, 'Санкт-Петербург, Невский пр., д.45', 'Сборка', None, None),
        (3, 'Екатеринбург, ул. Ленина, д.3', 'В пути', '2023-10-04 09:15:00', None),
        (5, 'Москва, ул. Тверская, д.10, кв.25', 'В пути', '2023-10-06 10:00:00', None),
        (6, 'Казань, ул. Баумана, д.15', 'Доставлено', '2023-10-07 11:30:00', '2023-10-09 13:15:00'),
        (8, 'Калининград, Ленинский пр., д.30', 'Ожидание', None, None),
        (9, 'Ростов-на-Дону, ул. Б. Садовая, д.50', 'Доставлено', '2023-10-10 14:00:00', '2023-10-12 10:45:00'),
        (10, 'Самара, ул. Куйбышева, д.125', 'В пути', '2023-10-11 16:20:00', None)
    ]
    cursor.executemany("""
        INSERT INTO delivery (order_id, address, status, shipped_date, delivered_date)
        VALUES (?, ?, ?, ?, ?)
    """, deliveries)

    
    # Закрытие соединения
    conn.commit()
    conn.close()

    print("✅ База данных успешно создана и заполнена тестовыми данными!")

# Исполнение при запуске как скрипт
if __name__ == "main":
    initialize_database()