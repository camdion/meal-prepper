from textual.reactive import reactive
from textual import on, work
from textual.app import ComposeResult, Screen
from textual.containers import Horizontal, Vertical, VerticalScroll
from textual.message import Message
from textual.widgets import Button, Footer, Input, Label, Placeholder

from common_ui_elements.quit import Quit
from screens.search import Search
from sql_utils import DB, Meal, MealIngredient


class DisplayTotals(Horizontal):
    def __init__(self, total_calories, total_carbs, total_fat, total_protein, total_fiber, **kwargs):
        super().__init__(**kwargs)
        self.total_calories = total_calories
        self.total_carbs = total_carbs
        self.total_fat = total_fat
        self.total_protein = total_protein
        self.total_fiber = total_fiber

    def compose(self):
        yield Placeholder(f"Total Calories: {self.total_calories}")
        yield Placeholder(f"Total Carbs: {self.total_carbs}")
        yield Placeholder(f"Total Fat: {self.total_fat}")
        yield Placeholder(f"Total Protein: {self.total_protein}")
        yield Placeholder(f"Total Fiber: {self.total_fiber}")

class EMMealIngredient(Horizontal):
    def __init__(self, mi: MealIngredient):
        super().__init__()
        self.fdc_id = mi.fdc_id
        self.meal_id = mi.meal_id
        self.mi_name = mi.name
        self.amount = mi.amount
        self.calories = mi.calories
        self.carbs = mi.carbs
        self.fat = mi.fat
        self.protein = mi.protein
        self.fiber = mi.fiber
        self.mi = mi

    class IngredientRemoved(Message):
        def __init__(self, mi: "EMMealIngredient"):
            super().__init__()
            self.mi = mi

    def compose(self):
        yield Placeholder(f"{self.mi_name}")
        yield Placeholder(f"{self.amount:.1f}")
        yield Placeholder(f"{self.calories:.1f}")
        yield Placeholder(f"{self.carbs:.1f}")
        yield Placeholder(f"{self.fat:.1f}")
        yield Placeholder(f"{self.protein:.1f}")
        yield Placeholder(f"{self.fiber:.1f}")
        yield Button("Remove Ingredient", id="em_mi_remove", variant="error")

    @on(Button.Pressed, "#em_mi_remove")
    def remove_ingredient(self, _event: Button.Pressed):
        self.post_message(self.IngredientRemoved(self))


class EditMealScreen(Screen):
    total_calories = reactive(0.0)
    total_carbs = reactive(0.0)
    total_fat = reactive(0.0)
    total_protein = reactive(0.0)
    total_fiber = reactive(0.0)
    def __init__(self, meal: "Meal", db: DB, food_api):
        super().__init__()
        self.meal: Meal = meal
        self.db: DB = db
        self.food_api = food_api
        self.meal_ingredients = self.db.get_food_for_meals(self.meal.meal_id)
        self.calculate_totals()

    def calculate_totals(self):
        self.total_calories = 0.0
        self.total_carbs = 0.0
        self.total_fat = 0.0
        self.total_protein = 0.0
        self.total_fiber = 0.0
        for meal_ingredient in self.meal_ingredients:
            self.total_calories += meal_ingredient.calories
            self.total_carbs += meal_ingredient.carbs
            self.total_fat += meal_ingredient.fat
            self.total_protein += meal_ingredient.protein
            self.total_fiber += meal_ingredient.fiber

    def compose(self) -> ComposeResult:
        with Horizontal(id="edit_meal_screen_display_totals"):
            yield Placeholder(f"Total Calories: {self.total_calories:.1f}")
            yield Placeholder(f"Total Carbs: {self.total_carbs:.1f}")
            yield Placeholder(f"Total Fat: {self.total_fat:.1f}")
            yield Placeholder(f"Total Protein: {self.total_protein:.1f}")
            yield Placeholder(f"Total Fiber: {self.total_fiber:.1f}")

        with VerticalScroll(id="edit_meal_screen_vc_ingredients"):
            for meal_ingredient in self.meal_ingredients:
                yield EMMealIngredient(meal_ingredient)
        yield Button("Add Ingredient", id="edit_meal_screen_add_ing", variant="success")
        with Horizontal(id="bottom_pane"):
            yield Button("Save Changes", id="edit_meal_screen_save_changes", variant="success")
            yield Quit()

    @on(Button.Pressed, "#edit_meal_screen_save_changes")
    def save_changes(self, event: Button.Pressed):
        event.stop()
        self.dismiss(self.meal_ingredients)

    @on(EMMealIngredient.IngredientRemoved)
    @work
    async def remove_ingredient(self, event: EMMealIngredient.IngredientRemoved):
        event.stop()
        self.db.remove_food_from_meal(self.meal.meal_id, event.mi.fdc_id)
        vc = self.query_one("#edit_meal_screen_vc_ingredients", VerticalScroll)
        self.meal_ingredients = self.db.get_food_for_meals(self.meal.meal_id)
        self.calculate_totals()
        await vc.remove_children()
        for mi in self.meal_ingredients:
            await vc.mount(EMMealIngredient(mi))
        event.mi.remove()

    class EnterAmount(Screen):
        def __init__(self, meal: Meal, ingredient_name: str, ingredient_uom: str):
            self.meal_name = meal.name
            self.ingredient_name = ingredient_name
            self.ingredient_uom = ingredient_uom
            super().__init__()

        def compose(self):
            with Vertical():
                with Horizontal():
                    yield Placeholder(f"Meal Name: {self.meal_name}")
                    yield Placeholder(f"Ingredient Name: {self.ingredient_name}")
                    yield Placeholder(f"Ingredient UOM: {self.ingredient_uom}")
                yield Input(placeholder="Enter ingredient amount...",id="edit_meal_screen_new_ing_amount_input", type="number")

        @on(Input.Submitted, "#edit_meal_screen_new_ing_amount_input")
        def yeet_name_up(self, event: Input.Submitted):
            event.stop()
            amount = event.input.value
            self.dismiss(amount)

    @on(Button.Pressed, "#edit_meal_screen_add_ing")
    @work
    async def add_ingredient(self, event: Button.Pressed):
        event.stop()
        new_ing_fdc_id = await self.app.push_screen_wait(Search(self.db, self.food_api, "meals"))
        if new_ing_fdc_id is None:
            return
        db_results = self.db.get_food([new_ing_fdc_id])
        if db_results is None or len(db_results) < 1:
            return
        new_ing = db_results[0]
        new_ing_amount  = await self.app.push_screen_wait(self.EnterAmount(self.meal, new_ing.name, new_ing.serving_size_uom))
        self.db.add_food_to_meal(self.meal.meal_id, new_ing_fdc_id, float(new_ing_amount))
        vc = self.query_one("#edit_meal_screen_vc_ingredients", VerticalScroll)
        self.meal_ingredients = self.db.get_food_for_meals(self.meal.meal_id)
        self.calculate_totals()
        await vc.remove_children()
        for mi in self.meal_ingredients:
            await vc.mount(EMMealIngredient(mi))


    @on(Quit.QuitPressed)
    def quit(self, event: Quit.Pressed):
        event.stop()
        self.dismiss()

class MealOptions(Horizontal):
    def __init__(self, meal: Meal):
        super().__init__()
        self.meal: Meal = meal

    class EditMeal(Message):
        def __init__(self, meal):
            super().__init__()
            self.meal_options: MealOptions = meal

    class RemoveMeal(Message):
        def __init__(self, meal):
            super().__init__()
            self.meal_options: MealOptions = meal

    def compose(self):
        yield Placeholder(self.meal.name)
        yield Button("View Meal", id="meal_options_edit_meal", variant="success")
        yield Button("Remove Meal", id="meal_options_remove_meal", variant="error")

    @on(Button.Pressed, "#meal_options_edit_meal")
    def edit_meal(self):
        self.post_message(self.EditMeal(self))

    @on(Button.Pressed, "#meal_options_remove_meal")
    def remove_meal(self):
        self.post_message(self.RemoveMeal(self))

class MealsContainer(VerticalScroll):
    def __init__(self, meals: list[Meal]):
        super().__init__()
        self.meals = meals

    def compose(self):
        for meal in self.meals:
            yield MealOptions(meal)

    def reload_meals(self, meals: list[Meal]):
        self.remove_children()
        self.meals = meals
        for meal in meals:
            self.mount(MealOptions(meal))

class Meals(Screen):
    def __init__(self, db, food_api):
        super().__init__()
        self.db: DB = db
        self.food_api = food_api

    def compose(self) -> ComposeResult:
        yield MealsContainer(self.db.get_meals())
        with Horizontal(id="bottom_pane"):
            yield Button("Add Meal", id="meals_screen_add_meal", variant="success")
            yield Quit()

    @on(Quit.QuitPressed)
    def quit(self, event: Quit.Pressed):
        event.stop()
        self.dismiss()

    class CreateMeal(Screen):
        def compose(self):
            yield Input(placeholder="Enter meal name...",id="meals_screen_add_meal_meal_name")
            yield Footer(Label("Enter meal name and then press enter"))

        @on(Input.Submitted, "#meals_screen_add_meal_meal_name")
        def yeet_name_up(self, event: Input.Submitted):
            event.stop()
            self.dismiss(event.value)

    @on(Button.Pressed, "#meals_screen_add_meal")
    @work
    async def add_meal(self, event: Button.Pressed):
        event.stop()
        meal_name = await self.app.push_screen_wait(self.CreateMeal())
        self.db.add_meal(meal_name)
        self.query_one(MealsContainer).reload_meals(self.db.get_meals())



    @on(MealOptions.EditMeal)
    @work
    async def edit_meal(self, event: MealOptions.EditMeal):
        event.stop()
        _updated_meal = await self.app.push_screen_wait(EditMealScreen(event.meal_options.meal, self.db, self.food_api))

    @on(MealOptions.RemoveMeal)
    def remove_meal(self, event: MealOptions.RemoveMeal):
        event.stop()
        self.db.remove_meal(event.meal_options.meal.meal_id)
        event.meal_options.remove()
