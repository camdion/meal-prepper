# make the screen for searching food
from typing import Literal

from textual.app import ComposeResult, Screen
from textual.containers import Container
from textual.widgets import Button, Header, Input, Placeholder


class Search(Screen):
    def __init__(self, db, food_api, search_type: Literal["food","favorites"]):
        super().__init__()
        self.db = db
        self.food_api = food_api
        self.search_type = search_type

    def compose(self) -> ComposeResult:
        yield Header()
        yield Input()
        yield Button("Quit", id="quit", variant="error")

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "quit":
            event.stop()
            self.dismiss(self.search_type)

class SearchResults(Container):
    def compose(self) -> ComposeResult:
        yield Placeholder()
