from textual.coordinate import Coordinate
import asyncio
from typing import Literal

from textual import on, work
from textual.app import ComposeResult, Screen
from textual.containers import Horizontal, Vertical
from textual.widgets import DataTable, Input, Label, Switch

import api_utils
import sql_utils
from common_ui_elements.quit import Quit

type searchTypes = Literal["favorites","meals"]

class Search(Screen):
    def __init__(self, db, food_api, search_type: searchTypes):
        super().__init__()
        self.db: sql_utils.DB = db
        self.food_api: api_utils.USDA_API = food_api
        self.search_type = search_type

    def compose(self) -> ComposeResult:
        with Horizontal(id="search_query"):
            with Vertical(id="search_input_container"):
                yield Label("Search Input")
                yield Input(id="search_input")
            with Vertical(id="use_branded_container"):
                yield Label("Include Brand Names?")
                yield Switch(id="use_branded")
        yield SearchResults(self.search_type, id="search_results")
        with Horizontal(id="bottom_search_pane"):
            yield Quit()

    @on(Quit.QuitPressed)
    def quit(self, event: Quit.Pressed):
        event.stop()
        self.dismiss()

    @on(Input.Submitted, "#search_input")
    @work(exclusive=True)
    async def get_results(self, event: Input.Submitted):
        sr = self.query_one(SearchResults)
        sr.loading = True

        use_branded = self.query_one("#use_branded", Switch)
        results = await asyncio.to_thread(self.food_api.search_food, event.input.value, use_branded.value)

        foods: list[api_utils.Food] = results["foods"]
        for food in foods:
            self.db.add_food(
                food.fdcId,
                food.description,
                food.carbs,
                food.fat,
                food.protein,
                food.fiber,
                food.serving_size,
                food.serving_size_uom
            )

        db_results = await asyncio.to_thread(self.db.get_food,[food.fdcId for food in foods])
        sr.update_results(db_results)
        sr.loading = False

    @on(DataTable.RowSelected)
    def update_favorite(self, event: DataTable.RowSelected):
        fdc_id_coord = Coordinate(event.cursor_row, 1)
        fdc_id = event.data_table.get_cell_at(fdc_id_coord)

        if self.search_type == "favorites":
            db_food: list[sql_utils.Food] = self.db.get_food([fdc_id])
            if db_food is None or len(db_food) < 1:
                return
            new_favorited_status = not bool(db_food[0].favorited)
            self.db.update_favorited_status(fdc_id, new_favorited_status)
            favorited_coord = Coordinate(event.cursor_row, 0)
            event.data_table.update_cell_at(favorited_coord, "yes" if new_favorited_status else "no")
        elif self.search_type == "meals":
            self.dismiss(fdc_id)


class SearchResults(DataTable):
    def __init__(self, last_column_type: searchTypes, **kwargs):
        super().__init__(**kwargs)
        self.last_column_type = last_column_type
        self.cursor_type = "row"

    def on_mount(self) -> None:
        if self.last_column_type == "favorites":
            COLUMNS = ("Favorited?", "FDC ID", "Name", "Calories (cal)", "Carbs (g)", "Fat (g)", "Protein (g)", "Fiber (g)")
        elif self.last_column_type == "meals":
            COLUMNS = ("FDC ID", "Name", "Calories (cal)", "Carbs (g)", "Fat (g)", "Protein (g)", "Fiber (g)")
        self.add_columns(*COLUMNS)

    def update_results(self, results: list[sql_utils.Food]):
        self.clear()
        ROWS = []
        for food in results:
            if self.last_column_type == "favorites":
                ROWS.append((
                    "yes" if food.favorited else "no",
                    food.fdc_id,
                    food.name,
                    food.calories,
                    food.carbs,
                    food.fat,
                    food.protein,
                    food.fiber
                ))
            elif self.last_column_type == "meals":
                ROWS.append((
                    food.fdc_id,
                    food.name,
                    food.calories,
                    food.carbs,
                    food.fat,
                    food.protein,
                    food.fiber
                ))

        self.add_rows(ROWS)
        self.loading = False
