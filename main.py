import os
from dotenv import load_dotenv, dotenv_values

def main():
    load_dotenv()
    usda_key = os.getenv("USDA_API_KEY")


if __name__ == "__main__":
    main()
