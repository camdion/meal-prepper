#!/usr/bin/env python3
import sqlite3

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

    db = sqlite3.connect("meal_prepper.db")

    # ok so here's the fucking thing jane
    # idk how this works but I think this is my plan
    # 1. figure out layout

if __name__ == "__main__":
    main()
