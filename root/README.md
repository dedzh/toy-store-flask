# 🧸 Интернет-магазин игрушек на Flask

Это учебный проект — сайт интернет-магазина игрушек, разработанный с использованием Flask и SQLite.

## 📦 Возможности

- Просмотр каталога игрушек
- Фильтрация по категориям, возрасту и ключевым словам
- Подробная карточка товара
- Работающая структура базы данных: товары, категории, пользователи, заказы
- Простая админская логика для демонстрации заказов (по желанию)

## 📁 Структура проекта

```
проект/
├── app.py            # Основной файл Flask-приложения
├── init_db.py        # Скрипт инициализации базы данных
├── toy_store.db      # SQLite-база данных
├── requirements.txt  # Зависимости проекта
├── templates/        # HTML-шаблоны Jinja2
│   ├── base.html
│   ├── index.html
│   
├── static/           # Статические файлы(CSS,изображения и т.д.)
│   ├── img/
│   └── ...
├── README.md
└── .gitignore
```

## 🚀 Быстрый старт

### 1. Клонируйте репозиторий

```bash
git clone https://github.com/your-username/toy-store-flask.git
cd toy-store-flask
```
### 2. Установите виртуальное окружение и зависимости
```bash
python -m venv venv
venv\Scripts\activate      # Windows
# или
source venv/bin/activate     # macOS/Linux

pip install -r requirements.txt
```

### 3. Создайте и заполните базу данных
```bash
python init_db.py
```

### 4.Ссылка на сайт

https://dedushkazh.pythonanywhere.com/

---

## 🛠 Зависимости

Все зависимости указаны в файле `requirements.txt`. Пример:

Flask
Werkzeug


## 🧑‍🎓 Автор

**Темирова Ангелина Бабаевна**
Студент

---

