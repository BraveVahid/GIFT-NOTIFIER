import sqlite3
import threading


class DBManager:
    _instance = None
    _lock = threading.Lock()

    def __new__(cls, db_name=None):
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super(DBManager, cls).__new__(cls)
                    cls._instance._initialized = False
        return cls._instance

    def __init__(self, db_name="gift_notifier.sqlite3"):
        if self._initialized:
            return

        self.db_name = db_name
        self.connection = sqlite3.connect(db_name, check_same_thread=False)
        self.cursor = self.connection.cursor()
        self._create_tables()
        self._initialized = True

    def _create_tables(self):
        self.cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            receptor TEXT NOT NULL,
            token TEXT NOT NULL,
            sender TEXT NOT NULL,
            subscription_count INTEGER NOT NULL DEFAULT 0
        );
        """)

        self.cursor.execute("""
        CREATE TABLE IF NOT EXISTS gifts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            gift_id INTEGER UNIQUE NOT NULL
        );
        """)

        self.cursor.execute("""
        CREATE TABLE IF NOT EXISTS groups (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            chat_id INTEGER UNIQUE NOT NULL 
        );
        """)

        self.connection.commit()

    def add_user(self, user_id, receptor, sender, token, subscription_count):
        try:
            with self._lock:
                self.cursor.execute(
                    "SELECT id FROM users WHERE user_id = ? AND receptor = ?",
                    (user_id, receptor)
                )

                if self.cursor.fetchone() is None:
                    self.cursor.execute("""
                    INSERT INTO users (user_id, receptor, token, sender, subscription_count)
                    VALUES (?, ?, ?, ?, ?)
                    """, (user_id, receptor, token, sender, subscription_count))

                    self.connection.commit()
                    return True
                else:
                    self.cursor.execute("""
                    UPDATE users SET subscription_count = subscription_count + ?
                    WHERE user_id = ? AND receptor = ?
                    """, (subscription_count, user_id, receptor))
                    self.connection.commit()
                    return True
        except sqlite3.Error as e:
            print(f"Error adding user: {e}")
            return False

    def remove_user(self, user_id):
        try:
            with self._lock:
                self.cursor.execute("SELECT id FROM users WHERE user_id = ?", (user_id,))

                if self.cursor.fetchone() is not None:
                    self.cursor.execute("DELETE FROM users WHERE user_id = ?", (user_id,))
                    self.connection.commit()
                    return True
                else:
                    return False
        except sqlite3.Error as e:
            print(f"Error removing user: {e}")
            return False

    def get_all_users(self):
        try:
            with self._lock:
                self.cursor.execute("SELECT * FROM users")
                return self.cursor.fetchall()
        except sqlite3.Error as e:
            print(f"Error getting all users: {e}")
            return []

    def get_user(self, user_id):
        try:
            with self._lock:
                self.cursor.execute("SELECT * FROM users WHERE user_id = ?", (user_id,))
                return self.cursor.fetchone()
        except sqlite3.Error as e:
            print(f"Error getting user: {e}")
            return None

    def update_subscription_count(self, user_id, subscription_count):
        try:
            with self._lock:
                self.cursor.execute(
                    "UPDATE users SET subscription_count = ? WHERE user_id = ?",
                    (subscription_count, user_id)
                )
                self.connection.commit()
                return self.cursor.rowcount > 0
        except sqlite3.Error as e:
            print(f"Error updating subscription count: {e}")
            return False

    def add_gift(self, gift_id):
        try:
            with self._lock:
                self.cursor.execute("INSERT OR IGNORE INTO gifts (gift_id) VALUES (?)", (gift_id,))
                self.connection.commit()
                return True
        except sqlite3.Error as e:
            print(f"Error adding gift: {e}")
            return False

    def get_all_gifts(self):
        try:
            with self._lock:
                self.cursor.execute("SELECT gift_id FROM gifts")
                return [row[0] for row in self.cursor.fetchall()]
        except sqlite3.Error as e:
            print(f"Error getting all gifts: {e}")
            return []

    def add_group(self, chat_id):
        try:
            with self._lock:
                self.cursor.execute("INSERT OR IGNORE INTO group (chat_id) VALUES (?)", (chat_id, ))
                self.connection.commit()
                return True
        except sqlite3.Error as e:
            print(f"Error adding group: {e}")

    def get_all_groups(self):
        try:
            with self._lock:
                self.cursor.execute("SELECT chat_id FROM groups")
                return [row[0] for row in self.cursor.fetchall()]
        except sqlite3.Error as e:
            print(f"Error getting all groups: {e}")

    def remove_group(self, chat_id):
        try:
            with self._lock:
                self.cursor.execute("SELECT chat_id FROM groups WHERE chat_id = ?", (chat_id,))

                if self.cursor.fetchone() is not None:
                    self.cursor.execute("DELETE FROM groups WHERE chat_id = ?", (chat_id,))
                    self.connection.commit()
                    return True
                else:
                    return False
        except sqlite3.Error as e:
            print(f"Error removing group: {e}")
            return False
