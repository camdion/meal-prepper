#!/usr/bin/env python3
from screens.favorites import Favorites
import dotenv
from textual import on
from textual.app import App, ComposeResult
from textual.containers import Container
from textual.widgets import Button, Header, Label

from api_utils import USDA_API
from common_ui_elements.quit import Quit
from constants import *
from screens.meals import Meals
from screens.search import Search
from sql_utils import DB


class MyApp(App):
    TITLE = "Meal Prepper"
    SUB_TITLE = "Macro tracking - Hard Mode"
    CSS_PATH = "style_sheet.tcss"

    def __init__(self, db, food_api):
        super().__init__()
        self.db = db
        self.food_api = food_api

    def compose(self) -> ComposeResult:
        yield Header()
        with Container():
            yield Label("Welcome to the Meal Pepper App!")
            yield Button("View Favorites", id="favorites", variant="primary")
            yield Button("Search Food", id="food", variant="primary")
            yield Button("View Meals", id="meals", variant="success")
            yield Quit()

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "favorites":
            self.push_screen(Favorites(self.db))
        elif event.button.id == "food":
            self.push_screen(Search(self.db, self.food_api))
        elif event.button.id == "meals":
            self.push_screen(Meals(self.db, self.food_api))
        else:
            print("nope")

    @on(Quit.QuitPressed)
    def quit(self, event: Quit.Pressed):
        event.stop()
        self.exit()

def main():
    usda_key = dotenv.get_key("./.env","USDA_API_KEY") or "foobar"
    food_api = USDA_API()
    if not food_api.connect(usda_key):
        usda_key = input("Enter USDA API Key: ")
        while usda_key != "exit" and not food_api.connect(usda_key):
            usda_key = input("Invalid USDA API Key (\"exit\" to quit): ")

        if usda_key == "exit":
            print("Ending program...")
            return
        dotenv.set_key("./.env", "USDA_API_KEY", usda_key)

    print("Connection to USDA API Successful")
    print("Starting Program...")

    db = DB()
    print(db.search_food("", True))
    app = MyApp(db, food_api)
    reply = app.run()

    print(reply)
    print("Ending Program...")
    return True

if __name__ == "__main__":
    main()
