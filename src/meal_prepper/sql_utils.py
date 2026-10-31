import sqlite3


class DB:
    def __init__(self):
        self.__db_name = "meal_prepper.db"
        conn = sqlite3.connect(self.__db_name)
        cursor = conn.cursor()

        # Create Saved Ingredients Table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS food (
                food_id INTEGER PRIMARY KEY,
                name TEXT,
                calories REAL,
                carbs REAL,
                fat REAL,
                protein REAL,
                fiber REAL
            )
            """)

        # Create Alts Table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS food_alts (
                alt_id INTEGER PRIMARY KEY,
                FOREIGN KEY (alt_id) REFERENCES food(food_id),
                name TEXT,
                calories REAL,
                carbs REAL,
                fat REAL,
                protein REAL,
                fiber REAL
            )
            """)
