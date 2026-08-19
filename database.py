import sqlite3


class DataBase:
    def __init__(self, database_name="downloads.db"):
        self.connection = sqlite3.connect(database_name)

    def create_table(self):
        cursor = self.connection.cursor()

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS downloads (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                platform TEXT NOT NULL,
                title TEXT NOT NULL,
                quality TEXT,
                duration INTEGER,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
    """)
        self.connection.commit()

    def save_download(
        self,
        user_id: int,
        platform: str,
        title: str,
        quality: str,
        duration: int | None,
    ):
        cursor = self.connection.cursor()

        cursor.execute(
            """
                       INSERT INTO downloads
                       (user_id,platform,title,quality,duration)
                       VALUES (?, ?, ?, ?, ?)
                       """,
            (user_id, platform, title, quality, duration),
        )

        self.connection.commit()

    def get_history(self, user_id: int, limit: int = 10):
        cursor = self.connection.cursor()

        cursor.execute(
            """
                       SELECT platform,title,quality,duration,created_at
                       FROM downloads
                       WHERE user_id = ?
                       ORDER BY created_at DESC
                       LIMIT ?
                       """,
            (user_id, limit),
        )
        return cursor.fetchall()

    def get_total_downloads(self, user_id: int) -> int:
        cursor = self.connection.cursor()

        cursor.execute(
            """
                       SELECT COUNT(*)
                       FROM downloads
                       WHERE user_id = ?
                       """,
            (user_id,),
        )
        result = cursor.fetchone()
        return result[0]

    def get_platform_downlads(self, user_id: int):
        cursor = self.connection.cursor()

        cursor.execute(
            """
                       
                       SELECT platform,COUNT(*)
                       FROM downloads
                       WHERE user_id = ?
                       GROUP BY platform
                       """,
            (user_id,),
        )

        return cursor.fetchall()
