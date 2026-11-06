from textual import on
from textual.app import ComposeResult, Screen
from textual.containers import Container
from textual.widgets import Button, Input, ListItem, ListView

from common_ui_elements.quit import Quit
from sql_utils import DB


class MealContainer(ListView):
    def __init__(self, meals):
        super().__init__()
        self.meals = meals

    def compose(self) -> ComposeResult:
        for meal in self.meals:
            yield ListItem(
                Button(label=f"{meal.name}", id=f"edit_meal_{meal.meal_id}", variant="primary"),
                Button(label="X", id=f"remove_meal_{meal.meal_id}", variant="error")
            )

class Ribbon(Container):
    def compose(self) -> ComposeResult:
        yield Button("Create Meal", id="add_meal", variant="success")
        yield Quit()


class Meals(Screen):
    def __init__(self, db, food_api):
        super().__init__()
        self.db: DB = db
        self.food_api = food_api

    def compose(self) -> ComposeResult:
        meals = self.db.get_meals()
        yield Ribbon()
        yield MealContainer(meals)

    @on(Button.Pressed, "#add_meal")
    def add_meal(self):
        self.mount(Input(id="add_meal_input",placeholder="Enter meal name..."))

    @on(Input.Submitted, "#add_meal_input")
    def name_new_meal(self):
        meal_input = self.query_one("#add_meal_input", Input)
        self.db.add_meal(meal_input.value)
        meal_input.remove()

    @on(Quit.QuitPressed)
    def quit(self, event: Quit.Pressed):
        event.stop()
        self.dismiss()
