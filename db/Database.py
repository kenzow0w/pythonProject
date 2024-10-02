from abc import ABC, abstractmethod
import sqlite3
import logging

db_name = "database.db"


# Абстрактный класс, представляющий фабрику для подключения к базе данных
class DBFactory(ABC):
    @abstractmethod
    def connect(self, path_to_db: str):
        pass


def create_users_table(cursor):
    # Создание таблицы tbl_users
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS tbl_users (
        username TEXT UNIQUE NOT NULL,
        password TEXT NOT NULL,
        role TEXT NOT NULL,
        created_at DATETIME
    )
    """)


def create_drones_table(cursor):
    # Создание таблицы tbl_drones
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS tbl_drones (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        port TEXT UNIQUE NOT NULL,
        serial_number TEXT NOT NULL,      
        mission TEXT NOT NULL,   
        created_at DATETIME   
    )
    """)


def create_admin_user(conn):
    data = conn.execute("""
    select * from tbl_users
    where username = 'admin'
    """).fetchall()
    if not data:
        conn.execute("""
        INSERT INTO tbl_users (username, password, role, created_at)
        VALUES ('admin', 'admin', 'admin', datetime('now'));
        """)
        logging.info("добавлен админ")
        conn.commit()
    conn.close()


# Реализация фабрики для подключения к PostgreSQL
# (примечание: метод здесь упрощен и возвращает True для демонстрации)
class PostgreSQLDBFactory(DBFactory):
    _instance = None

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super(PostgreSQLDBFactory, cls).__new__(cls)
        return cls._instance

    def connect(self, path_to_db: str):
        logging.info(f"Подключение к PostgreSQL установлено")
        return True


# Реализация фабрики для подключения к SQLite
class SQLiteDBFactory(DBFactory):
    _instance = None

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super(SQLiteDBFactory, cls).__new__(cls)
        return cls._instance

    def connect(self, path_to_db: str):
        try:
            # Подключение к базе данных SQLite
            conn = sqlite3.connect(path_to_db)
            logging.info(f"Подключение к базе {path_to_db} SQLite установлено")
            return conn
        except sqlite3.Error as e:
            # Обработка ошибки подключения
            logging.warning(f"Ошибка подключения: {e}")
            return None

    @classmethod
    def get_db(cls):
        factory = SQLiteDBFactory()
        conn = factory.connect(path_to_db=db_name)  # Подключение к базе данных в памяти
        if conn:
            logging.info("Подключение к БД прошло успешно")
        return conn


def init_db():
    conn = SQLiteDBFactory.get_db()  # Подключение к базе данных в памяти
    if conn:
        logging.info("Подключение к БД прошло успешно")
        cursor = conn.cursor()
        create_users_table(cursor)
        create_drones_table(cursor)
        create_admin_user(conn)
    return conn
