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

if __name__ == "__main__":
    main()
