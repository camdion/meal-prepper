import sqlite3
from collections import namedtuple

Food = namedtuple("Food", ["fdc_id", "name", "calories", "carbs", "fat", "protein", "fiber", "serving_size", "favorited"])
def food_row_factory(_cursor, row) -> Food:
    return Food._make(row)

Meal = namedtuple("Meal", ["meal_id", "name"])
def meal_row_factory(_cursor, row) -> Meal:
    return Meal._make(row)

MealIngredient = namedtuple("MealIngredient", ["meal_ingredient_id","meal_id","fdc_id", "amount", "name", "calories", "carbs", "fat", "protein", "fiber", "serving_size", "favorited"])
def meal_ingredient_row_factory(_cursor, row) -> MealIngredient:
    return MealIngredient._make(row)

MealIngredientAlt = namedtuple("MealIngredientAlt", ["meal_ingredient_alt_id","meal_ingredient_id","alt_fdc_id", "name", "calories", "carbs", "fat", "protein", "fiber", "serving_size", "favorited"])
def meal_ingredient_alt_row_factory(_cursor, row) -> MealIngredientAlt:
    return MealIngredientAlt._make(row)


class DB:
    def __init__(self):
        self._db_name: str = "meal_prepper.db"
        self.__create_tables()

    def __create_tables(self):
        conn = self.connect()
        try:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS food (
                    fdc_id INTEGER PRIMARY KEY NOT NULL,
                    name TEXT NOT NULL,
                    calories REAL,
                    carbs REAL,
                    fat REAL,
                    protein REAL,
                    fiber REAL,
                    serving_size_uom TEXT,
                    favorited INTEGER NOT NULL DEFAULT FALSE
                );
                """)

            conn.execute("""
                CREATE INDEX IF NOT EXISTS name ON food(name ASC)
                """)

            conn.execute("""
                CREATE TABLE IF NOT EXISTS meals (
                    meal_id INTEGER PRIMARY KEY NOT NULL,
                    name TEXT UNIQUE
                );
                """)

            conn.execute("""
                CREATE INDEX IF NOT EXISTS name ON meals(name ASC)
                """)

            conn.execute("""
                CREATE TABLE IF NOT EXISTS meal_ingredients (
                    meal_ingredient_id INTEGER PRIMARY KEY,
                    meal_id INTEGER NOT NULL REFERENCES meals(meal_id) ON DELETE CASCADE,
                    fdc_id INTEGER NOT NULL REFERENCES food(fdc_id) ON DELETE RESTRICT,
                    amount REAL NOT NULL,
                    UNIQUE (meal_id, fdc_id)
                );
                """)

            conn.execute("""
                CREATE TABLE IF NOT EXISTS meal_ingredients_alts (
                    meal_ingredient_alt_id INTEGER PRIMARY KEY,
                    meal_ingredient_id INTEGER NOT NULL REFERENCES meal_ingredients(meal_ingredient_id) ON DELETE CASCADE,
                    alt_fdc_id INTEGER NOT NULL REFERENCES food(fdc_id),
                    UNIQUE (meal_ingredient_id, alt_fdc_id)
                );
                """)

            conn.connection.commit()
        except sqlite3.Error as e:
            print("could not create tables")
            raise sqlite3.Error(e)
        finally:
            conn.connection.close()

    def connect(self) -> sqlite3.Cursor:
        conn = sqlite3.connect(self._db_name)
        conn.execute("PRAGMA foreign_keys = ON;")
        return conn.cursor()

    def add_food(
        self,
        fdc_id: int,
        name: str,
        carbs: float,
        fat: float,
        protein: float,
        fiber: float,
        serving_size: float,
        serving_size_uom: str
    ):
        data = (
            fdc_id,
            name,
            carbs * 100 / serving_size,
            fat * 100 / serving_size,
            protein * 100 / serving_size,
            fiber * 100 / serving_size,
            serving_size_uom,
            False
        )
        cur = self.connect()
        try:
            cur.execute("""
                INSERT INTO food (fdc_id, name, calories, carbs, fat, protein, fiber, serving_size_uom, favorited)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                ON CONFLICT (fdc_id)
                DO UPDATE SET
                    name=excluded.name,
                    calories=excluded.calories,
                    carbs=excluded.carbs,
                    fat=excluded.fat,
                    protein=excluded.protein,
                    fiber=excluded.fiber,
                    serving_size_uom=excluded.serving_size_uom,
                    favorited=excluded.favorited
                """, data)

            cur.connection.commit()
            return True

        except sqlite3.Error as e:
            cur.connection.rollback()
            print(f"add_food failed: {e}")
            return False
        finally:
            cur.connection.close()

    def search_food(
        self,
        name: str,
        favorites_only: bool = False
    ) -> list[Food]:
        cur = self.connect()
        cur.row_factory = food_row_factory
        try:
            data = (
                "%" + name + "%",
                favorites_only or "%"
            )
            c = cur.execute("""
                SELECT
                    fdc_id,
                    name,
                    calories,
                    carbs,
                    fat,
                    protein,
                    fiber,
                    serving_size,
                    favorited
                FROM food
                WHERE name LIKE ?
                AND favorited LIKE ?
                """, (data,))
            return c.fetchall()
        except sqlite3.Error as e:
            print(f"could not get food {name}: {e}")
            return []
        finally:
            cur.connection.close()

    def update_favorited_status(
        self,
        fdc_id: int,
        new_fstatus: bool = True
    ):
        cur = self.connect()
        try:
            c = cur.execute("""
                UPDATE food
                SET favorited=?
                WHERE fdc_id=?
                """, (new_fstatus, fdc_id))

            if c.rowcount != 1:
                print("rolling back last update on food")
                cur.connection.rollback()
                print(f"unexpected rowcount when updating fdc_id {fdc_id} rowcount: {c.rowcount}")
                return False

            cur.connection.commit()
            return True
        except sqlite3.Error as e:
            cur.connection.rollback()
            print(f"failed to update favorite status of fdc_id {fdc_id}: {e}")
            return False
        finally:
            cur.connection.close()

    def add_meal(
        self,
        name: str
    ):
        cur = self.connect()
        try:
            cur.execute("""
                INSERT OR IGNORE INTO meals(name)
                VALUES(?)
                """,(name,))
            cur.connection.commit()
            return True

        except sqlite3.Error as e:
            cur.connection.rollback()
            print(f"meal {name} could not be added to the meals table: {e}")
            return False
        finally:
            cur.connection.close()

    def search_meals(
        self,
        name: str
    ) -> list[Meal]:
        cur = self.connect()
        cur.row_factory = meal_row_factory
        try:
            c = cur.execute("""
                SELECT
                    meal_id,
                    name
                FROM meals
                WHERE name LIKE ?
                """, ("%"+name+"%",))
            return c.fetchall()
        except sqlite3.Error as e:
            print(f"could not get meal {name}: {e}")
            return []
        finally:
            cur.connection.close()

    def get_meals(self) -> list[Meal]:
        cur = self.connect()
        cur.row_factory = meal_row_factory
        try:
            c = cur.execute("""
                SELECT
                    meal_id,
                    name
                FROM meals
                """)
            return c.fetchall()
        except sqlite3.Error as e:
            print(f"could not get meals: {e}")
            return []
        finally:
            cur.connection.close()

    def remove_meal(
        self,
        meal_id: int
    ):
        cur = self.connect()
        try:
            c = cur.execute("""
                DELETE FROM meals
                WHERE meal_id=?
                """, (meal_id,))
            if c.rowcount > 1:
                print(f"unexpected number of rows deleted: {c.rowcount}")
                cur.connection.rollback()
                return False
            print(f"meal {meal_id} deleted")
            cur.connection.commit()
            return True
        except sqlite3.Error as e:
            print(f"meal {meal_id} could not be deleted: {e}")
            cur.connection.rollback()
            return False
        finally:
            cur.connection.close()

    def add_food_to_meal(
        self,
        meal_id: int,
        fdc_id: int,
        amount: float
    ):
        data = (
            meal_id,
            fdc_id,
            amount
        )
        cur = self.connect()
        try:
            cur.execute("""
                INSERT INTO meal_ingredients(meal_id, fdc_id, amount)
                VALUES (?, ?, ?)
                ON CONFLICT (meal_id, fdc_id)
                DO UPDATE SET
                    amount=excluded.amount
                """, data)

            cur.connection.commit()
            return True

        except sqlite3.Error as e:
            cur.connection.rollback()
            print(f"add food to meal failed: {e}")
            return False
        finally:
            cur.connection.close()

    def get_food_for_meals(
        self,
        meal_id: int
    ) -> list[MealIngredient]:
        cur = self.connect()
        cur.row_factory = meal_ingredient_row_factory
        try:
            c = cur.execute("""
                SELECT
                    mi.meal_ingredient_id,
                    mi.meal_id,
                    mi.fdc_id,
                    mi.amount,
                    f.name,
                    f.calories,
                    f.carbs,
                    f.fat,
                    f.protein,
                    f.fiber,
                    f.serving_size,
                    f.favorited
                FROM meal_ingredients mi

                LEFT JOIN food f
                ON f.fdc_id = mi.fdc_id

                WHERE mi.meal_id = ?
                """, (meal_id,))
            return c.fetchall()
        except sqlite3.Error as e:
            print(f"could not get meal ingredients for meal {meal_id}: {e}")
            return []
        finally:
            cur.connection.close()

    def remove_food_from_meal(
        self,
        meal_id: int,
        fdc_id: int
    ):
        data = (
            meal_id,
            fdc_id
        )
        cur = self.connect()
        try:
            cur.execute("""
                DELETE FROM meal_ingredients
                WHERE meal_id=?
                AND fdc_id=?
                """, data)

            cur.connection.commit()
            return True

        except sqlite3.Error as e:
            cur.connection.rollback()
            print(f"remove food from meal failed: {e}")
            return False
        finally:
            cur.connection.close()

    def add_alternate(
        self,
        meal_ingredient_id: int,
        alt_id: int
    ):
        data = (
            meal_ingredient_id,
            alt_id
        )
        cur = self.connect()
        try:
            cur.execute("""
                INSERT OR IGNORE INTO meal_ingredients_alts(meal_ingredient_id, alt_fdc_id)
                VALUES (?, ?)
                """, data)

            print(f"added alternate {alt_id} to meal_ingredient {meal_ingredient_id}")
            cur.connection.commit()
            return True

        except sqlite3.Error as e:
            cur.connection.rollback()
            print(f"add alternate failed: {e}")
            return False
        finally:
            cur.connection.close()

    def get_alternates(
        self,
        meal_id: int,
        fdc_id: int
    ) -> list[MealIngredientAlt]:
        cur = self.connect()
        cur.row_factory = meal_ingredient_alt_row_factory
        try:
            data = (
                meal_id,
                fdc_id
            )
            c = cur.execute("""
                SELECT
                    a.meal_ingredient_alt_id,
                    m.meal_ingredient_id,
                    a.alt_fdc_id,
                    f.name,
                    f.calories,
                    f.carbs,
                    f.fat,
                    f.protein,
                    f.fiber,
                    f.serving_size,
                    f.favorited
                FROM meal_ingredients m

                LEFT JOIN meal_ingredients_alts a
                ON a.meal_ingredient_id = m.meal_ingredient_id

                LEFT JOIN food f
                ON a.alt_fdc_id = f.fdc_id

                WHERE m.meal_id=?
                AND m.fdc_id=?
                """, data)
            return c.fetchall()
        except sqlite3.Error as e:
            print(f"could not get alternates for meal {meal_id} and fdc_id {fdc_id}: {e}")
            return []

        finally:
            cur.connection.close()

    def remove_alternate(
        self,
        meal_ingredient_id: int,
        alt_id: int
    ):
        data = (
            meal_ingredient_id,
            alt_id
        )
        cur = self.connect()
        try:
            cur.execute("""
                DELETE FROM meal_ingredients_alts
                WHERE meal_ingredient_id = ?
                AND alt_fdc_id = ?
                """, data)

            print(f"removed alternate {alt_id} from meal_ingredient {meal_ingredient_id}")
            cur.connection.commit()
            return True

        except sqlite3.Error as e:
            cur.connection.rollback()
            print(f"remove alternate failed: {e}")
            return False

        finally:
            cur.connection.close()
