import os

from dotenv import load_dotenv

from api_utils import USDA_API
from constants import *


def main():
    load_dotenv()
    usda_key = os.getenv("USDA_API_KEY")
    if usda_key is None:
        usda_key = input("Input API Key to USDA API to begin: ")
    food_api = USDA_API(usda_key)

    # ok so here's the fucking thing jane
    # idk how this works but I think this is my plan
    # 1. figure out layout

if __name__ == "__main__":
    main()
