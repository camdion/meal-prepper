import urllib.parse

import requests


class USDA_API:
    def __init__(self, token: str) -> None:
        self.__base_url = "https://api.nal.usda.gov/fdc/v1"
        self.__token = token

    def get_food(self, fdcIds: list[str], format: str = "full", nutrients: list[str] | None = None):
        if format not in ["abridged", "full"]:
            raise ValueError("format parameter must be \"full\" or \"abridged\"")
        if len(fdcIds) < 1:
            raise ValueError("fdcIds parameter must have at least one ID")

        try:
            # Create request URL
            request_url = self.__base_url + "/foods?"
            for fdcId in fdcIds:
                request_url += f"fdcIds={fdcId}&"

            if format != "full":
                request_url += f"format={format}&"

            if nutrients is not None:
                for nutrient in nutrients:
                    request_url += f"nutrients={nutrients}&"

            request_url += f"api_key={self.__token}"

            # Go get that food!
            response = requests.get(request_url, headers={"accept":"application/json"})

            # Handle response
            if response.status_code == 200:
                return response
            else:
                print(f"Error: {response.status_code}")
                return None

        except requests.exceptions.RequestException as e:
            print(f"Request Error: {e}")
            return None


    def search_food(
        self,
        query: str, # May include search operators. See https://fdc.nal.usda.gov/help#bkmk-2
        dataType: list[str] | None = None, # Branded, Foundation, Survey (FNDDS), or SR Legacy
        pageSize: int = 50, # min is 1, max is 200
        pageNumber: int = 1, # offset into data is pageNumber * pageSize
        sortBy: str = "lowercaseDescription.keyword", # dataType.keyword, lowercaseDescription, fdcId, publishedDate
        sortOrder: str = "asc", # asc or desc (asc is default)
        brandOwner: str | None = None # Only applies to branded food
    ):
        validDTypes = ["Branded", "Foundation", "Survey (FNDDS)", "SR Legacy"]
        if dataType == None or len(dataType) == 0:
            dataType = validDTypes
        for dType in dataType:
            if dType not in validDTypes:
                raise ValueError(f"dataType must be one of {", ".join(validDTypes)}")

        if (pageSize > 200 or pageSize < 1):
            raise ValueError("pageSize must be between 1 and 200")

        validSortKeys = ["lowercaseDescription.keyword","dataType.keyword","fdcId","publishedDate"]
        if sortBy not in validSortKeys:
            raise ValueError(f"sortBy must be one of {", ".join(validSortKeys)}")

        validSortOrders = ["asc","desc"]
        if sortOrder not in validSortOrders:
            raise ValueError(f"sortOrder must be one of {", ".join(validSortOrders)}")


        try:
            # Create request URL
            request_url = self.__base_url + "/foods/search?"
            params = {}
            params["query"] = query
            params["dataType"] = ",".join(dataType)
            params["pageSize"] = str(pageSize)
            params["pageNumber"] = str(pageNumber)
            params["sortBy"] = sortBy
            params["sortOrder"] = sortOrder
            params["api_key"] = self.__token
            if brandOwner is not None:
                params["brandOwner"] = brandOwner
            first_request_url = request_url + urllib.parse.urlencode(params)
            print(f"first_request_url: {first_request_url}")

            response = requests.get(first_request_url, headers={"accept":"application/json"})

            print("break?")
            if response.status_code == 400 and "pageSize * pageNumber exceeded upper search results limit" in response.json():
                params["pageNumber"] = 1
                tmp_request_url = request_url + urllib.parse.urlencode(params)
                response = requests.get(tmp_request_url, headers={"accept":"application/json"})
                params["pageNumber"] = response.json()["totalPages"]
                last_page_request_url = request_url + urllib.parse.urlencode(params)
                response = requests.get(last_page_request_url, headers={"accept":"application/json"})

            if response.status_code == 200 and response.text.strip():
                print(f"Data found (Status Code {response.status_code})")
                return response
            else:
                print(f"Error: {response.status_code}")
                return None

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
