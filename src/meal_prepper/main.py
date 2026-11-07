#!/usr/bin/env python3
import dotenv
from textual import on
from textual.app import App, ComposeResult
from textual.containers import Container
from textual.widgets import Button, Header

from api_utils import USDA_API
from common_ui_elements.quit import Quit
from constants import *
from screens.favorites import Favorites
from screens.meals import Meals
from screens.search import Search
from sql_utils import DB


class MyApp(App):
    TITLE = "Meal Prepper"
    SUB_TITLE = "Macro tracking (Hard Mode)"
    CSS_PATH = "style_sheet.tcss"

    def __init__(self, db, food_api):
        super().__init__()
        self.db = db
        self.food_api = food_api

    def compose(self) -> ComposeResult:
        yield Header()
        with Container(id="main_menu_buttons_container"):
            yield Button("View Favorites", id="favorites", variant="default")
            yield Button("Search Food", id="food", variant="primary")
            yield Button("View and Edit Meals", id="meals", variant="success")
            yield Quit()

    @on(Button.Pressed, "#favorites")
    def load_favorites(self):
        self.push_screen(Favorites(self.db))

    @on(Button.Pressed, "#food")
    def load_search_food(self):
        self.push_screen(Search(self.db, self.food_api, "favorites"))

    @on(Button.Pressed, "#meals")
    def load_meals(self):
        self.push_screen(Meals(self.db, self.food_api))

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
    app = MyApp(db, food_api)
    reply = app.run()

    print(reply)
    print("Ending Program...")
    return True

if __name__ == "__main__":
    main()
