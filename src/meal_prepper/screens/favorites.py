from textual import on, work
from textual.app import ComposeResult, Screen
from textual.containers import Horizontal, Vertical
from textual.coordinate import Coordinate
from textual.widgets import Button, DataTable, Label

from common_ui_elements.quit import Quit
from sql_utils import DB


class AreYouSure(Screen):
    def __init__(self, fdc_id: int, food_name: str, db: DB):
        super().__init__()
        self.db: DB = db
        self.fdc_id = fdc_id
        self.food_name = food_name

    def compose(self):
        with Vertical():
            yield Label(f"Are you sure you want to unfavorite {self.food_name}?")
            with Horizontal():
                yield Button("Yes", id="are_you_sure_yes", variant="error")
                yield Button("No", id="are_you_sure_no", variant="success")

    @on(Button.Pressed, "#are_you_sure_yes")
    def unfavorite(self):
        self.db.update_favorited_status(self.fdc_id, False)
        self.dismiss()

    @on(Button.Pressed, "#are_you_sure_no")
    def goodbye(self):
        self.dismiss()

class Favorites(Screen):
    def __init__(self, db):
        super().__init__()
        self.db: DB = db

    def compose(self) -> ComposeResult:
        yield DataTable(id="favorites_table")
        with Horizontal(id="bottom_favorites_pane"):
            yield Quit()

    def on_mount(self) -> None:
        COLUMNS = ("FDC ID", "Name", "Calories (cal)", "Carbs (g)", "Fat (g)", "Protein (g)", "Fiber (g)")
        table = self.query_one(DataTable)
        table.cursor_type = "row"
        table.add_columns(*COLUMNS)
        self.update_table()

    def update_table(self) -> None:
        favorites = self.db.search_food("", True)
        ROWS = []
        for favorite in favorites:
            ROWS.append((
                favorite.fdc_id,
                favorite.name,
                favorite.calories,
                favorite.carbs,
                favorite.fat,
                favorite.protein,
                favorite.fiber
            ))

        table = self.query_one(DataTable)
        table.clear()
        table.add_rows(ROWS)

    @on(DataTable.RowSelected, "#favorites_table")
    @work
    async def try_to_unfavorite(self, event: DataTable.RowSelected):
        fdc_id_coord = Coordinate(event.cursor_row, 0)
        fdc_id = event.data_table.get_cell_at(fdc_id_coord)
        food_name_coord = Coordinate(event.cursor_row, 1)
        food_name = event.data_table.get_cell_at(food_name_coord)
        await self.app.push_screen_wait(AreYouSure(fdc_id, food_name, self.db))
        self.update_table()


    @on(Quit.QuitPressed)
    def quit(self, event: Quit.Pressed):
        event.stop()
        self.dismiss()
