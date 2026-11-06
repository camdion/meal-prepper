from textual import on
from textual.app import ComposeResult, Screen
from textual.containers import Container
from textual.widgets import Header, Input, Placeholder

from common_ui_elements.quit import Quit


class Search(Screen):
    def __init__(self, db, food_api):
        super().__init__()
        self.db = db
        self.food_api = food_api

    def compose(self) -> ComposeResult:
        yield Header()
        yield Input()
        yield Quit()

    @on(Quit.QuitPressed)
    def quit(self, event: Quit.Pressed):
        event.stop()
        self.dismiss()

class SearchResults(Container):
    def compose(self) -> ComposeResult:
        yield Placeholder()
