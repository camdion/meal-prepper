![icon](/assets/images/readme-icon.svg)

# Meal Prepper
This app allows users to get nutrition info, create meals from selected ingredients, and create grocery lists from selected meals all through the command line.

This app is far from polished. However, for a first personal project, it's good enough (for now muahaha)!

This started as a requirement for a boot.dev course in devops. I'm expecting to come back to this at some point, but honestly for now I'm just really excited to continue progression on the course I'm taking. :)

## Notes
This app grabs the carbs, fat, protein, and fiber for foods. Since the USDA API below uses several fields for calories, this app uses a simple calculation for calories:
> carbs * 4 + fat * 9 + protein * 4 = calories

---

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

## Artificial Intelligence Statement
I did my best to use as little artificial intelligence as possible for this. I wanted this to be a learning opportunity for me. When I used AI (mostly Claude), I gave explicit instructions to not give me any code. That being said, I absolutely took advantage of AI to help me debug and understand/find terminology and tools.

## Closing Notes
All the code you see in this repo was written by me, and although very brutally honestly most of it is probably eye-searingly bad, I'm proud that I was able to make something. Now I have a lot more confidence in my ability to wade through docs and get a working prototype. This was a lot of fun, and I can't wait for more!
