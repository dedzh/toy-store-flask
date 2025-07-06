from flask import Flask, render_template, request, redirect, url_for, session, flash
import sqlite3
import os
import re
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', '2113')  # Использовать переменные окружения для продакшена
DATABASE = 'toy_store.db'


def get_db():
    """
    Устанавливает соединение с базой данных и возвращает его.
    Использует Row factory для доступа к колонкам по именам.
    """
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    """
    Инициализирует базу данных при первом запуске, если файл БД не существует.
    """
    if not os.path.exists(DATABASE):
        from init_db import initialize_database
        initialize_database()
        print("База данных инициализирована")


@app.route('/')
def index():
    """
    Главная страница. Отображает каталог товаров с возможностью фильтрации
    по категории, возрасту и поисковому запросу.
    """
    conn = get_db()
    cursor = conn.cursor()

    category_id = request.args.get('category_id')
    min_age = request.args.get('min_age')
    search = request.args.get('search')

    query = "SELECT * FROM products WHERE stock_quantity > 0"
    params = []

    if category_id:
        query += " AND category_id = ?"
        params.append(category_id)
    if min_age:
        query += " AND age_min <= ?"
        params.append(min_age)
    if search:
        query += " AND name LIKE ?"
        params.append(f'%{search}%')

    cursor.execute(query, params)
    products = cursor.fetchall()

    cursor.execute("SELECT * FROM categories")
    categories = cursor.fetchall()

    conn.close()
    return render_template('index.html', products=products, categories=categories)


@app.route('/product/<int:product_id>')
def product(product_id):
    """
    Страница с информацией о товаре.
    """
    conn = get_db()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT p.*, c.name AS category_name 
        FROM products p
        JOIN categories c ON p.category_id = c.id
        WHERE p.id = ?
    """, (product_id,))
    product = cursor.fetchone()

    if not product:
        flash('Товар не найден', 'danger')
        return redirect(url_for('index'))

    conn.close()
    return render_template('product.html', product=product)


@app.route('/register', methods=['GET', 'POST'])
def register():
    """
    Регистрация нового пользователя.
    Проверяет уникальность email и валидность данных.
    """
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        full_name = request.form['full_name']
        address = request.form['address']
        phone = request.form.get('phone', '')

        conn = get_db()
        cursor = conn.cursor()

        cursor.execute('SELECT * FROM users WHERE email = ?', (email,))
        account = cursor.fetchone()

        if account:
            flash('Пользователь с таким email уже зарегистрирован', 'danger')
        elif not re.match(r'[^@]+@[^@]+\.[^@]+', email):
            flash('Некорректный email', 'danger')
        elif not password or not full_name or not address:
            flash('Заполните все обязательные поля', 'danger')
        else:
            password_hash = generate_password_hash(password)
            cursor.execute("""
                INSERT INTO users (email, password_hash, full_name, address, phone)
                VALUES (?, ?, ?, ?, ?)
            """, (email, password_hash, full_name, address, phone))
            conn.commit()
            flash('Регистрация прошла успешно! Теперь вы можете войти', 'success')
            return redirect(url_for('login'))

        conn.close()

    return render_template('register.html')
@app.route('/login', methods=['GET', 'POST'])
def login():
    """
    Авторизация пользователя. Проверяет email и пароль.
    Устанавливает сессию при успешном входе.
    """
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']

        conn = get_db()
        cursor = conn.cursor()

        cursor.execute('SELECT * FROM users WHERE email = ?', (email,))
        account = cursor.fetchone()

        if account and check_password_hash(account['password_hash'], password):
            session['loggedin'] = True
            session['user_id'] = account['id']
            session['email'] = account['email']
            session['full_name'] = account['full_name']
            return redirect(url_for('index'))
        else:
            flash('Неверный email или пароль', 'danger')

        conn.close()

    return render_template('login.html')


@app.route('/logout')
def logout():
    """
    Выход пользователя. Очищает сессию.
    """
    session.pop('loggedin', None)
    session.pop('user_id', None)
    session.pop('email', None)
    session.pop('full_name', None)
    session.pop('cart', None)
    return redirect(url_for('index'))


@app.route('/cart', methods=['GET', 'POST'])
def cart():
    """
    Управление корзиной:
    - POST: добавляет товар в корзину
    - GET: отображает корзину
    """
    if 'loggedin' not in session:
        return redirect(url_for('login'))

    if request.method == 'POST':
        try:
            product_id = int(request.form['product_id'])
            quantity = int(request.form['quantity'])
        except ValueError:
            flash("Некорректные данные", "danger")
            return redirect(url_for('index'))

        conn = get_db()
        cursor = conn.cursor()

        cursor.execute("SELECT * FROM products WHERE id = ? AND stock_quantity >= ?", (product_id, quantity))
        product = cursor.fetchone()

        if not product:
            flash('Недостаточно товара на складе', 'danger')
            return redirect(url_for('product', product_id=product_id))

        cart = session.get('cart', {})
        cart[str(product_id)] = cart.get(str(product_id), 0) + quantity
        session['cart'] = cart
        flash('Товар добавлен в корзину', 'success')
        return redirect(url_for('product', product_id=product_id))

    cart_items = session.get('cart', {})
    products = []
    total = 0

    if cart_items:
        product_ids = list(cart_items.keys())
        placeholders = ','.join(['?'] * len(product_ids))

        conn = get_db()
        cursor = conn.cursor()
        cursor.execute(f"SELECT * FROM products WHERE id IN ({placeholders})", tuple(product_ids))
        rows = cursor.fetchall()

        for row in rows:
            product = dict(row)
            product_id = str(row['id'])
            product_quantity = cart_items[product_id]
            product['quantity'] = product_quantity
            product['subtotal'] = row['price'] * product_quantity
            products.append(product)
            total += product['subtotal']

        conn.close()

    return render_template('cart.html', products=products, total=total)


@app.route('/checkout', methods=['POST'])
def checkout():
    """
    Оформление заказа. Создает запись в таблице заказов и очищает корзину.
    """
    if 'loggedin' not in session:
        return redirect(url_for('login'))

    cart = session.get('cart')
    if not cart:
        flash('Ваша корзина пуста', 'danger')
        return redirect(url_for('cart'))

    user_id = session['user_id']
    conn = get_db()
    cursor = conn.cursor()

    try:
            cursor.execute("INSERT INTO orders (user_id, status) VALUES (?, 'Создан')", (user_id,))
            order_id = cursor.lastrowid

            for product_id, quantity in cart.items():
                cursor.execute("SELECT price FROM products WHERE id = ?", (product_id,))
                price = cursor.fetchone()[0]
                cursor.execute("""
                    INSERT INTO order_items (order_id, product_id, quantity, price)
                    VALUES (?, ?, ?, ?)
                """, (order_id, product_id, quantity, price))

                cursor.execute("""
                    UPDATE products 
                    SET stock_quantity = stock_quantity - ? 
                    WHERE id = ?
                """, (quantity, product_id))

            session.pop('cart', None)
            conn.commit()
            flash('Заказ успешно оформлен!', 'success')
            return redirect(url_for('orders'))

    finally:
        conn.close()


@app.route('/orders')
def orders():
    """
    Отображает список заказов текущего пользователя.
    """
    if 'loggedin' not in session:
        return redirect(url_for('login'))

    user_id = session['user_id']
    conn = get_db()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT o.id, o.order_date, o.status, 
               SUM(oi.quantity * oi.price) AS total
        FROM orders o
        JOIN order_items oi ON o.id = oi.order_id
        WHERE o.user_id = ?
        GROUP BY o.id
        ORDER BY o.order_date DESC
    """, (user_id,))
    orders = cursor.fetchall()
    conn.close()
    return render_template('orders.html', orders=orders)

if __name__ == '__main__':
    init_db()
    app.run(debug=True, port=5000)