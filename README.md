![icon](/assets/images/readme-icon.svg)

# Meal Prepper
This app allows users to get nutrition info, create meals from selected ingredients, and create grocery lists from selected meals all through the command line.

## Notes
This app grabs the carbs, fat, protein, and fiber for foods. Since the USDA API below uses several fields for calories, this app uses a simple calculation for calories:
> carbs * 4 + fat * 9 + protein * 4 = calories

---

## Plan (change to actual headers later)
Need to:
1. Create interface for grabbing and searching for ingredients from the USDA database(s) -> Done!
1. Use SQLite to build a database -> Done!
2. Create feature for favoriting ingredients
    - Have search function put favorites at the top of the list
3. Create meals features
    - Allow grouping by ingredients
    - Allow calculating total nutrition info
    - Allow changing which nutrition facts are displayed based on config (create menu for updating config?)
4. Create grocery list feature -> Might add later, but
    - Allow adding ingredients
    - Convert amounts to familiar UOMs (g -> cups/lbs/ea)
    - Allow adding meals
    - Send list to equivalent list app (google keep note?) so that list is easily portable

## Getting Started
First, clone the repository using your preferred method.

You'll need a .env file in the same folder as main.py with a value for the USDA_API_KEY key. You can get your own free USDA API key [here](https://fdc.nal.usda.gov/api-key-signup). You can also enter this the first time you run the program.
The .env file key-value mapping should look something like this:
> USDA_API_KEY='mygloriouskeyvalue'

This project uses [uv](https://docs.astral.sh/uv/getting-started/installation/) for creating the virtual environment.

Once that's set you can run the program with the following CLI commands after navigating to the root of the repository directory:
> source .venv/bin/activate
> uv run src/meal_prepper/main.py

## Licensing
This project uses the the following source for data on nutrition:
> U.S. Department of Agriculture, Agricultural Research Service. FoodData Central, 2019. fdc.nal.usda.gov.
