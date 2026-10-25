import os

from dotenv import load_dotenv

from api_utils import USDA_API
from constants import *


def main():
    load_dotenv()
    usda_key = os.getenv("USDA_API_KEY")
    if usda_key is None:
        print("USDA_API_KEY Empty. Get an API key here and set that in the .env file: https://fdc.nal.usda.gov/api-key-signup")
        return

    food_api = USDA_API(usda_key)
    if food_api.get_food(["534358"]) is None:
        print("Something has gone wrong. Double check spelling in USDA_API_KEY.")
        return

    print("Connection to USDA API Successful! Starting Textual app now...")

    # ok so here's the fucking thing jane
    # idk how this works but I think this is my plan
    # 1. figure out layout

if __name__ == "__main__":
    main()
