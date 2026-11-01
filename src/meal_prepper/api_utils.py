import urllib.parse

import requests


class USDA_API:
    def __init__(self) -> None:
        self.__base_url = "https://api.nal.usda.gov/fdc/v1"

    def connect(self, token: str) -> bool:
        self.__token = token
        return self.get_food(["746782"],"abridged") is not None

    def get_food(self,
        fdcIds: list[str],
        format: str = "full",
        nutrients: list[str] | None = None
    ):
        if len(fdcIds) < 1:
            print("fdcIds parameter must have at least one ID")
            return None

        try:
            # Create request URL
            request_url = self.__base_url + "/foods?"
            for fdcId in fdcIds:
                request_url += f"fdcIds={fdcId}&"

            if format == "abridged":
                request_url += "format=abridged&"

            if nutrients is None:
                nutrients = [
                    "203",
                    "204",
                    "205",
                    "291"
                ]
            for nutrient in nutrients:
                request_url += f"nutrients={nutrient}&"

            request_url += f"api_key={self.__token}"

            # Go get that food!
            response = requests.get(request_url, headers={"accept":"application/json"})

            # Handle response
            if response.status_code != 200:
                print(f"Error: {response.status_code}")
                return None

            trunkedResults = []
            try:
                for result in response.json():
                    r = {
                        "fdcId": result["fdcId"],
                        "description": result["description"],
                        "dataType": result["dataType"],
                        "protein": 0,
                        "fat": 0,
                        "carbs": 0,
                        "fiber": 0
                    }
                    if format != "abridged":
                        if result["dataType"] == "Branded":
                            if not "servingSize" in result:
                                continue
                            r["servingSize"] = result["servingSize"]
                            r["servingSizeUOM"] = result["servingSizeUnit"]
                        elif result["dataType"] == "Foundation":
                            if not "foodPortions" in result:
                                continue
                            r["servingSize"] = result["foodPortions"][0]["gramWeight"]
                            r["servingSizeUOM"] = "g"

                    if "foodNutrients" not in result:
                        continue

                    if format != "abridged":
                        food_nutrients = result["foodNutrients"]
                        for nutrient in food_nutrients:
                            if "nutrient" not in nutrient:
                                continue
                            match nutrient["nutrient"]["number"]:
                                case "203":
                                    r["protein"] = nutrient["amount"]
                                case "204":
                                    r["fat"] = nutrient["amount"]
                                case "205":
                                    r["carbs"] = nutrient["amount"]
                                case "291":
                                    r["fiber"] = nutrient["amount"]


                    trunkedResults.append(r)

                print(trunkedResults)
                return trunkedResults
            except KeyError as ke:
                print(ke)
                return None


        except requests.exceptions.RequestException as e:
            print(f"Request Error: {e}")
            return None


    def search_food(
        self,
        query: str, # May include search operators. See https://fdc.nal.usda.gov/help#bkmk-2
        getBranded: bool = True,
        brandOwner: str | None = None # Only applies to branded food
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
            params["pageSize"] = "200"
            params["pageNumber"] = "1"
            params["api_key"] = self.__token
            if brandOwner is not None:
                params["brandOwner"] = brandOwner
            request_url = query_start + urllib.parse.urlencode(params)

            response = requests.get(request_url, headers={"accept":"application/json"})
            if response.status_code != 200 and not response.text.strip():
                print(f"Error: {response.status_code}")
                return None

            pageNum = 1
            allResults = response.json()["foods"]

            while response.json()["totalPages"] > pageNum:
                pageNum += 1
                params["pageNumber"] = str(pageNum)
                request_url = query_start + urllib.parse.urlencode(params)
                response = requests.get(request_url, headers={"accept":"application/json"})
                if response.status_code != 200 and not response.text.strip():
                    print(f"Error in search: {response.status_code}")
                    print(params)

                allResults.append(response.json()["foods"])

            fdcIds = []
            for result in allResults:
                fdcIds.append(result["fdcId"])

            return self.get_food(fdcIds)


        except requests.exceptions.RequestException as e:
            print(f"Request Error: {e}")
            return None

    def print_response(self, response: requests.Response) -> None:
        # Debugging time
        def r_print(obj: dict | list, buffer: str = ""):
            if type(obj) == list:
                for o in obj:
                    print(buffer + "[")
                    r_print(o, buffer + "    ")
                    print(buffer + "]")
            elif type(obj) == dict:
                for key, value in obj.items(): # ty: ignore[unresolved-attribute]
                    if type(value) == dict:
                        print(buffer + key + ": {")
                        r_print(value, buffer + "    ")
                        print(buffer + "}")
                    elif type(value) == list:
                        r_print(value, buffer + "    ")
                    else:
                        print(f"{buffer}{key}: {value}")
            else:
                print(f"{buffer}{obj}")

        print()
        print("Headers")
        print("====================")
        if hasattr(response, "headers") and response.headers == None:
            print("so no head?")
        else:
            r_print(dict(response.headers))

        print()
        print("Content")
        print("====================")
        print(type(response.json()))
        if response.json() is None:
            print("no content here!")
        else:
            r_print(response.json())
