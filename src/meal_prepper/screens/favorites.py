from textual.app import ComposeResult, Screen
from textual.widgets import Button


class Favorites(Screen):
    def __init__(self, db, food_api):
        super().__init__()
        self.db = db
        self.food_api = food_api

    def compose(self) -> ComposeResult:
        yield Button("Quit", id="quit", variant="error")

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "quit":
            event.stop()
            self.dismiss()
