import os
import sys
import sqlite3
from werkzeug.security import generate_password_hash, check_password_hash

# Lägg till projektets rotkatalog i sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from config import Config

def init_db(database_name=None):
    database_url = Config.SQLALCHEMY_DATABASE_URI
    if database_name:
        database_url = f"sqlite:///{database_name}"

    if database_url.startswith('sqlite:///'):
        database_path = database_url[len('sqlite:///'):]
    else:
        raise ValueError("Unsupported database URL")

    print(f"Initializing database at: {database_path}")  # Debugging

    with sqlite3.connect(database_path) as conn:
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                password TEXT NOT NULL,
                email TEXT UNIQUE NOT NULL,
                profile_picture TEXT,
                bio TEXT,
                balance REAL DEFAULT 0,
                role TEXT NOT NULL CHECK(role IN ('user', 'admin'))
            )
        ''')
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS products (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                price REAL NOT NULL,
                description TEXT,
                image TEXT
            )
        ''')
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS orders (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user TEXT NOT NULL,
                total REAL NOT NULL,
                status TEXT NOT NULL
            )
        ''')
        conn.commit()

def user_exists(username, email, database_name=None):
    """Kontrollerar om en användare redan finns i databasen."""
    database_url = Config.SQLALCHEMY_DATABASE_URI
    if database_name:
        database_url = f"sqlite:///{database_name}"

    if database_url.startswith('sqlite:///'):
        database_path = database_url[len('sqlite:///'):]
    else:
        raise ValueError("Unsupported database URL")

    with sqlite3.connect(database_path) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT 1 FROM users WHERE username = ? OR email = ?", (username, email))
        return cursor.fetchone() is not None

def add_user(username, password, email, role='user', database_name=None):
    """Lägger till en ny användare i databasen."""
    database_url = Config.SQLALCHEMY_DATABASE_URI
    if database_name:
        database_url = f"sqlite:///{database_name}"

    if database_url.startswith('sqlite:///'):
        database_path = database_url[len('sqlite:///'):]
    else:
        raise ValueError("Unsupported database URL")

    if user_exists(username, email, database_path):
        return False

    hashed_password = generate_password_hash(password, method='sha256')

    with sqlite3.connect(database_path) as conn:
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO users (username, password, email, role) VALUES (?, ?, ?, ?)
        ''', (username, hashed_password, email, role))
        conn.commit()
        return True

def verify_user(username, password, database_name=None):
    """Verifierar en användares inloggning."""
    database_url = Config.SQLALCHEMY_DATABASE_URI
    if database_name:
        database_url = f"sqlite:///{database_name}"

    if database_url.startswith('sqlite:///'):
        database_path = database_url[len('sqlite:///'):]
    else:
        raise ValueError("Unsupported database URL")

    with sqlite3.connect(database_path) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT password, role FROM users WHERE username = ?", (username,))
        user = cursor.fetchone()

        if user:
            stored_password, role = user
            if check_password_hash(stored_password, password):
                return role
        return None

def add_product(name, price, description, image, database_name=None):
    """Lägger till en ny produkt i databasen."""
    database_url = Config.SQLALCHEMY_DATABASE_URI
    if database_name:
        database_url = f"sqlite:///{database_name}"

    if database_url.startswith('sqlite:///'):
        database_path = database_url[len('sqlite:///'):]
    else:
        raise ValueError("Unsupported database URL")

    with sqlite3.connect(database_path) as conn:
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO products (name, price, description, image) VALUES (?, ?, ?, ?)
        ''', (name, price, description, image))
        conn.commit()
        return True

def delete_product(product_id, database_name=None):
    """Tar bort en produkt från databasen baserat på dess ID."""
    database_url = Config.SQLALCHEMY_DATABASE_URI
    if database_name:
        database_url = f"sqlite:///{database_name}"

    if database_url.startswith('sqlite:///'):
        database_path = database_url[len('sqlite:///'):]
    else:
        raise ValueError("Unsupported database URL")

    with sqlite3.connect(database_path) as conn:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM products WHERE id = ?", (product_id,))
        conn.commit()

def get_order_status(order_id, database_name=None):
    """Hämtar status för en order."""
    database_url = Config.SQLALCHEMY_DATABASE_URI
    if database_name:
        database_url = f"sqlite:///{database_name}"

    if database_url.startswith('sqlite:///'):
        database_path = database_url[len('sqlite:///'):]
    else:
        raise ValueError("Unsupported database URL")

    with sqlite3.connect(database_path) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT status FROM orders WHERE id = ?", (order_id,))
        result = cursor.fetchone()
        return result[0] if result else None

def get_user_orders(user_token, database_name=None):
    """Hämtar alla ordrar för en användare."""
    database_url = Config.SQLALCHEMY_DATABASE_URI
    if database_name:
        database_url = f"sqlite:///{database_name}"

    if database_url.startswith('sqlite:///'):
        database_path = database_url[len('sqlite:///'):]
    else:
        raise ValueError("Unsupported database URL")

    with sqlite3.connect(database_path) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT id, user, total, status FROM orders WHERE user = ?", (user_token,))
        return cursor.fetchall()

def reset_user_balance(username, database_name=None):
    """Nollställer balansen för en specifik användare."""
    database_url = Config.SQLALCHEMY_DATABASE_URI
    if database_name:
        database_url = f"sqlite:///{database_name}"

    if database_url.startswith('sqlite:///'):
        database_path = database_url[len('sqlite:///'):]
    else:
        raise ValueError("Unsupported database URL")

    with sqlite3.connect(database_path) as conn:
        cursor = conn.cursor()
        cursor.execute("UPDATE users SET balance = 0 WHERE username = ?", (username,))
        conn.commit()

if __name__ == "__main__":
    init_db()
    print("Database initialized successfully!")
