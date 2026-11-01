#!/usr/bin/env python3
import dotenv

from api_utils import USDA_API
from constants import *


def main():
    usda_key = dotenv.get_key("./.env","USDA_API_KEY") or "foobar"
    food_api = USDA_API()
    if not food_api.connect(usda_key):
        usda_key = input("Enter USDA API Key: ")
        while usda_key != "exit" and not food_api.connect(usda_key):
            usda_key = input("Invalid USDA API Key (\"exit\" to quit): ")

        if usda_key == "exit":
            print("ending program...")
            return
        dotenv.set_key("./.env", "USDA_API_KEY", usda_key)

    print("Connection to USDA API Successful")
    print("Starting Program...")

    search_query = input("Enter search query for food (\"exit\" to quit): ")
    while search_query != "exit":
        food_api.search_food(search_query)
        search_query = input("Enter search query for food (\"exit\" to quit): ")

    print("Ending Program...")

if __name__ == "__main__":
    main()
