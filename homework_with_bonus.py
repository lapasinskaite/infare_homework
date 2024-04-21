# 1. Implement a pageload to get the JSON data with your scraper.
# 2. Extract outbound and inbound flight data flying from MAD to AUH. You may choose any dates.
# 3. Make outbound and Inbound flight combinations for each price category (roundtrip flights).
# 4. Extract all available prices and calculate taxes for each combination.
#   Data can be saved into a CSV file for examination.
# 5. Find the cheapest price option for each flight combination.
#   Data can be saved into a CSV file for examination.
# 6. Make sure that scraper can work with flights having 1 connection (example routes: JFK -AUH, CPH-
# MAD). Flights having 2 connections must be skipped.
# 7. Make sure that scraper can work with any search parameter set (origin, destination, dates).
# 8. Save extracted data into CSV file using multiple search parameter sets (choose 10 of any search
# parameters you want).
# 9. Implement an additional filter allowing only flights having a specific connection airport (provided with
# the search parameters) OR direct flights.

# Data to extract (CSV example visible on the start page):
#   Departure and arrival airport three-letter IATA codes for each flight (including connections).
#   Departure and arrival dates with times for each flight (including connections).
#   Flight numbers of each flight (two-character airline company designator with flight number in digits ex.
# BA4040)
#   All roundtrip flight combinations with the cheapest full price.
#   Roundtrip flight combination total taxes.


import requests
import csv

base_endpoint="http://homeworktask.infare.lt/search.php"
csv_file = "flights.csv" # name/location of the CSV file

# Searh parameter sets:
params_set={
    "params_1": { 
        'from': 'MAD',
        'to': 'AUH',
        'depart': '2024-05-09', 
        'return': '2024-05-16',
    },

    "params_2": { 
        'from': 'MAD',
        'to': 'AUH',
        'depart': '2024-05-11', 
        'return': '2024-05-17',
    },
    "params_3":{ 
        'from': 'MAD',
        'to': 'AUH',
        'depart': '2024-06-10', 
        'return': '2024-06-14',
    },
    "params_4":{ 
        'from': 'MAD',
        'to': 'AUH',
        'depart': '2024-07-10',
        'return': '2024-07-16',
    },
    "params_5": { 
        'from': 'MAD',
        'to': 'AUH',
        'depart': '2024-05-22', 
        'return': '2024-05-28',
    },
    "params_6": { 
        'from': 'MAD',
        'to': 'FUE',
        'depart': '2024-05-10',
        'return': '2024-05-16',
    },
    "params_7": { 
        'from': 'MAD',
        'to': 'FUE',
        'depart': '2024-05-12',
        'return': '2024-05-19',
    },
    "params_8": { 
        'from': 'MAD',
        'to': 'FUE',
        'depart': '2024-05-20',
        'return': '2024-05-28',
    },
    "params_9": { 
        'from': 'MAD',
        'to': 'FUE',
        'depart': '2024-06-10',
        'return': '2024-06-16',
    },
    "params_10": { 
        'from': 'MAD',
        'to': 'FUE',
        'depart': '2024-06-13',
        'return': '2024-06-18',
    }
}

# Function to get the JSON data with chosen params
def get_json_from_endpoint(url, params):
    try:
        response = requests.get(url, params=params)
        response.raise_for_status()  # Raise an exception for HTTP errors
        
        # Check if the content type is JSON
        if 'application/json' in response.headers.get('Content-Type', ''):
            json_data = response.json()
            return json_data
        else:
            print("Response is not in JSON format \n","Response text:", response.text, "\n params: ", params) # Print the response text and params if response is not in JSON format 
            return None
    except requests.exceptions.RequestException as e:
        print("Request failed:", e)
        return None
    except Exception as e:
        print("An unexpected error occurred:", e)
        return None
    
# Function to get the base price of the flight (without taxes)
def price(i, totalAvailabilities): 
    for j in totalAvailabilities:
        if i["recommendationId"]==j["recommendationId"]:
            return j["total"]

# Function to find all possible combinations for flights - assuming that both fllights in the combination must have the same recommendationId
def all_combinations (json_data):
    if json_data is None:
        return None
    
    totalAvailabilities = json_data["body"]["data"]["totalAvailabilities"]
    journeys = json_data["body"]["data"]["journeys"]
    combinations = []
    for i in journeys: 
        if i["direction"]=="I": # From
            for j in journeys:
                if i["recommendationId"]==j["recommendationId"] and j["direction"] == "V" and len(i["flights"]) <= 2 and len(j["flights"]) <= 2: # No more than 2 connections
                    flight_price = price(i, totalAvailabilities)+i["importTaxAdl"]+i["importTaxChd"]+i["importTaxInf"] # Price of the flight (including all taxes)
                    combinations.append({
                        "Price": flight_price,
                        "Taxes": i["importTaxAdl"] + j["importTaxAdl"],
                        "outbound 1 airport departure": i["flights"][0]["airportDeparture"]["code"],
                        "outbound 1 airport arrival": i["flights"][0]["airportArrival"]["code"],
                        "outbound 1 time departure": i["flights"][0]["dateDeparture"],
                        "outbound 1 time arrival": i["flights"][0]["dateArrival"],
                        "outbound 1 flight number": i["flights"][0]["companyCode"] + i["flights"][0]["number"],
                        "outbound 2 airport departure": i["flights"][1]["airportDeparture"]["code"] if len(i["flights"]) == 2 else "", # If there is no second flight, there is no data for it
                        "outbound 2 airport arrival": i["flights"][1]["airportArrival"]["code"] if len(i["flights"]) == 2 else "",
                        "outbound 2 time departure": i["flights"][1]["dateDeparture"] if len(i["flights"]) == 2 else "",
                        "outbound 2 time arrival": i["flights"][1]["dateArrival"] if len(i["flights"]) == 2 else "",
                        "outbound 2 flight number": i["flights"][1]["companyCode"] + i["flights"][1]["number"] if len(i["flights"]) == 2 else "",
                        "inbound 1 airport departure": j["flights"][0]["airportDeparture"]["code"],
                        "inbound 1 airport arrival": j["flights"][0]["airportArrival"]["code"],
                        "inbound 1 time departure": j["flights"][0]["dateDeparture"],
                        "inbound 1 time arrival": j["flights"][0]["dateArrival"],
                        "inbound 1 flight number": j["flights"][0]["companyCode"] + j["flights"][0]["number"],
                        "inbound 2 airport departure": j["flights"][1]["airportDeparture"]["code"] if len(j["flights"]) == 2 else "",
                        "inbound 2 airport arrival": j["flights"][1]["airportArrival"]["code"] if len(j["flights"]) == 2 else "",
                        "inbound 2 time departure": j["flights"][1]["dateDeparture"] if len(j["flights"]) == 2 else "",
                        "inbound 2 time arrival": j["flights"][1]["dateArrival"] if len(j["flights"]) == 2 else "",
                        "inbound 2 flight number": j["flights"][1]["companyCode"] + j["flights"][1]["number"] if len(j["flights"]) == 2 else ""
                        })
    return combinations


# Function to find the cheapest combination of flights
def cheapest_combination (json_data):
    if json_data is None:
        return None
    
    cheapest_combination = []
    combinations = all_combinations(json_data)
    if not combinations: # If there are no combinations, return empty list
        return cheapest_combination
    
    cheapest_price = min(combinations, key=lambda x: x["Price"])["Price"] # Finds the cheapest price among all combinations
    for i in combinations: # Finds all combinations with the cheapest price and appends cheapest_combination 
        if i["Price"] == cheapest_price:
            cheapest_combination.append(i)
    return cheapest_combination

# Function to write the data to a CSV file (appending)
def write_to_csv(data, csv_file):
    try:
        with open(csv_file, mode="a", newline="") as csvfile:
            fieldnames = [
                "Price",
                "Taxes",
                "outbound 1 airport departure",
                "outbound 1 airport arrival",
                "outbound 1 time departure",
                "outbound 1 time arrival",
                "outbound 1 flight number",
                "outbound 2 airport departure",
                "outbound 2 airport arrival",
                "outbound 2 time departure",
                "outbound 2 time arrival",
                "outbound 2 flight number",
                "inbound 1 airport departure",
                "inbound 1 airport arrival",
                "inbound 1 time departure",
                "inbound 1 time arrival",
                "inbound 1 flight number",
                "inbound 2 airport departure",
                "inbound 2 airport arrival",
                "inbound 2 time departure",
                "inbound 2 time arrival",
                "inbound 2 flight number"
            ]
            
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            if csvfile.tell() == 0:  # Check if the file is empty - write header
                writer.writeheader()
            for row in data:
                writer.writerow(row)

    except Exception as e:
        print("Error appending to CSV:", e)

def filter_out_json_response(json_data, connection_airport):
    if json_data is None:
        return None
    
    # Filter out journeys if they: have 2+ connections/ have one connection but in different airport
    filtered_journeys = [journey for journey in json_data["body"]["data"]["journeys"] 
                         if len(journey["flights"]) <= 2 
                         and (len(journey["flights"]) != 2 or journey["flights"][1]["airportDeparture"]["code"] == connection_airport)]
    
    # Update the original JSON data with the filtered journeys
    json_data["body"]["data"]["journeys"] = filtered_journeys
    
    return json_data

# Run through all parameter sets and write the cheapest combination to the CSV file
for i in params_set:
    json_response = get_json_from_endpoint(base_endpoint, params_set[i]) # Calls the function to get the JSON data with chosen params
    json_response_filtered = filter_out_json_response(json_response, "LPA") # Filter out journeys with connections in predefined airport - bonus task
    cheapest_combinations = cheapest_combination(json_response_filtered) # Runs through the json data and finds cheapest combinations
    write_to_csv(cheapest_combinations, csv_file) # Writes data to the CSV file


