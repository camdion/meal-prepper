from textual import on
from textual.app import ComposeResult, Screen
from textual.widgets import DataTable, Input

import api_utils
import sql_utils
from common_ui_elements.quit import Quit


class Search(Screen):
    def __init__(self, db, food_api):
        super().__init__()
        self.db: sql_utils.DB = db
        self.food_api = food_api

    def compose(self) -> ComposeResult:
        yield Input(id="search_input")
        yield SearchResults()
        yield Quit()

    @on(Quit.QuitPressed)
    def quit(self, event: Quit.Pressed):
        event.stop()
        self.dismiss()

    @on(Input.Submitted, "#search_input")
    def get_results(self, event: Input.Submitted):
        results = self.food_api.search_food(event.input.value)
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
        db_results = self.db.get_food([food.fdcId for food in foods])
        sr = self.query_one(SearchResults)
        sr.update_results(db_results)

class SearchResults(DataTable):
    def on_mount(self) -> None:
        COLUMNS = ("Name", "Calories (cal)", "Carbs (g)", "Fat (g)", "Protein (g)", "Fiber (g)")
        self.add_columns(*COLUMNS)

    def update_results(self, results: list[sql_utils.Food]):
        for row in self.rows:
            self.remove_row(row)
        ROWS = []
        for food in results:
            ROWS.append((
                food.name,
                food.calories,
                food.carbs,
                food.fat,
                food.protein,
                food.fiber
            ))
        self.add_rows(ROWS)
