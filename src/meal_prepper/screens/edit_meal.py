from textual import on
from textual.app import ComposeResult, Screen

from common_ui_elements.quit import Quit
from sql_utils import DB


class EditMeal(Screen):
    def __init__(self, db, food_api):
        super().__init__()
        self.db: DB = db
        self.food_api = food_api

    def compose(self) -> ComposeResult:
        yield Quit()

    @on(Quit.QuitPressed)
    def quit(self, event: Quit.Pressed):
        event.stop()
        self.dismiss()
