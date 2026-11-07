import urllib.parse

import requests


class Food:
    def __init__(
        self,
        fdcId: int,
        description: str,
        carbs: float,
        fat: float,
        protein: float,
        fiber: float
    ):
        self.fdcId = fdcId
        self.description = description
        self.carbs = carbs
        self.fat = fat
        self.protein = protein
        self.fiber = fiber
        self.serving_size = 100.0
        self.serving_size_uom = "g"
        self.calories = carbs * 4 + fat * 9 + protein * 4

class USDA_API:
    def __init__(self) -> None:
        self.__base_url = "https://api.nal.usda.gov/fdc/v1"

    def connect(self, token: str) -> bool:
        self.__token = token
        return self.search_food("milk") is not None


    def search_food(
        self,
        query: str, # May include search operators. See https://fdc.nal.usda.gov/help#bkmk-2
        getBranded: bool = False,
        brandOwner: str | None = None, # Only applies to branded food
        pageNumber: int = 1
    ):
        dataType = ["Foundation"]
        if getBranded:
            dataType.append("Branded")

        try:
            # Create request URL
            query_start = self.__base_url + "/foods/search?"
            params = {}
            params["query"] = query
            params["dataType"] = ",".join(dataType)
            params["pageSize"] = "100"
            params["pageNumber"] = pageNumber
            params["api_key"] = self.__token
            if brandOwner is not None:
                params["brandOwner"] = brandOwner
            request_url = query_start + urllib.parse.urlencode(params)

            response = requests.get(request_url, headers={"accept":"application/json"})
            if response.status_code != 200 or not response.text.strip():
                print(f"Error: {response.status_code}")
                return None


            response_json = response.json()
            foods = response_json["foods"]
            allFoods = []
            for food in foods:
                carbs, fat, protein, fiber = 0.0, 0.0, 0.0, 0.0
                for n in food["foodNutrients"]:
                    if n["nutrientNumber"] == "203":
                        protein = n["value"]
                    elif n["nutrientNumber"] == "204":
                        fat = n["value"]
                    elif n["nutrientNumber"] == "205":
                        carbs = n["value"]
                    elif n["nutrientNumber"] == "291":
                        fiber = n["value"]
                if food["dataType"] == "Branded":
                    description = food["brandOwner"] + " (" + food["brandName"] + "): " + food["description"]
                else:
                    description = food["description"]
                allFoods.append(Food(food["fdcId"], description, carbs, fat, protein, fiber))

            results = {
                "currentPage": response_json["currentPage"],
                "totalPages": response_json["totalPages"],
                "foods": allFoods
            }

            return results

        except requests.exceptions.RequestException as e:
            print(f"Request Error: {e}")
            return None
