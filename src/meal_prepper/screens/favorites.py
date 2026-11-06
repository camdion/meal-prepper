from textual.app import ComposeResult, Screen
from textual.widgets import Button, DataTable

from sql_utils import DB


class Favorites(Screen):
    def __init__(self, db):
        super().__init__()
        self.db: DB = db

    def compose(self) -> ComposeResult:
        yield Button("Quit", id="quit", variant="error")
        yield DataTable()

    def on_mount(self) -> None:
        ROWS = [
            ("Name", "Calories (cal)", "Carbs (g)", "Fat (g)", "Protein (g)", "Fiber (g)")
        ]
        favorites = self.db.search_food("", True)
        for favorite in favorites:
            ROWS.append((favorite.name, favorite.calories, favorite.carbs, favorite.fat, favorite.protein, favorite.fiber))

        table = self.query_one(DataTable)
        table.add_columns(*ROWS[0])
        table.add_rows(ROWS[1:])


    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "quit":
            event.stop()
            self.dismiss()
