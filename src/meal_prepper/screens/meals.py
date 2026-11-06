from textual import on
from textual.containers import Container, ScrollableContainer
from textual.app import ComposeResult, Screen
from textual.widgets import Button, Input
from sql_utils import DB


class Meals(Screen):
    def __init__(self, db, food_api):
        super().__init__()
        self.db: DB = db
        self.food_api = food_api

    def compose(self) -> ComposeResult:
        meals = self.db.get_meals()
        with ScrollableContainer():
            for meal in meals:
                yield Button(label=meal.name, id=f"meal_id_{meal.meal_id}", variant="primary")
        yield Button("Create Meal", id="add_meal", variant="success")
        yield Button("Quit", id="quit", variant="error")

    def add_meal(self):
        self.mount(Input(id="add_meal_input",placeholder="Enter meal name..."))

    @on(Input.Submitted)
    def name_new_meal(self):
        name = self.query_one("#add_meal_input", Input).value
        self.db.add_meal(name)



    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "quit":
            event.stop()
            self.dismiss()
        elif event.button.id == "add_meal":
            self.add_meal()
