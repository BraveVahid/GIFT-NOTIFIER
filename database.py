import sqlite3


class DBManager:
    _instance = None

    def __new__(cls, db_name=None):
        if cls._instance is None:
            cls._instance = super(DBManager, cls).__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def __init__(self, db_name="gift_notifier.sqlite3"):
        if self._initialized:
            return

        self.connection = sqlite3.connect(db_name)
        self.cursor = self.connection.cursor()
        self._create_tables()
        self._initialized = True

    def _create_tables(self):
        self.cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT UNIQUE,
            user_id INTEGER UNIQUE,
            receptor TEXT,
            token TEXT,
            sender TEXT,
            subscription_count INTEGER
        );
        """)

        self.cursor.execute("""
        CREATE TABLE IF NOT EXISTS gifts (
            id INTEGER PRIMARY KEY AUTOINCREMENT UNIQUE,
            gift_id INTEGER
        );
        """)

        self.connection.commit()

    def add_user(self, user_id, receptor, sender, token, subscription_count):
        try:
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
                return False
        except sqlite3.Error as e:
            print(f"Error adding user: {e}")
            return False

    def remove_user(self, user_id):
        try:
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
            self.cursor.execute("SELECT * FROM users")
            return self.cursor.fetchall()
        except sqlite3.Error as e:
            print(f"Error getting all users: {e}")
            return []

    def get_user(self, user_id):
        try:
            self.cursor.execute("SELECT * FROM users WHERE user_id = ?", (user_id,))
            return self.cursor.fetchone()
        except sqlite3.Error as e:
            print(f"Error getting user: {e}")
            return None

    def update_subscription_count(self, user_id, subscription_count):
        try:
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
            self.cursor.execute("INSERT INTO gifts (gift_id) VALUES (?)", (gift_id,))
            self.connection.commit()
            return True
        except sqlite3.Error as e:
            print(f"Error adding gift: {e}")
            return False

    def get_all_gifts(self):
        try:
            self.cursor.execute("SELECT * FROM gifts")
            return self.cursor.fetchall()
        except sqlite3.Error as e:
            print(f"Error getting all gifts: {e}")
            return []
