import dotenv
import googlemaps
import json
import os
import requests

dotenv.load_dotenv()

api_key = os.getenv('GMAP_API')
# DONT ACTUALLY DO THIS
print(api_key)

# ALSO BEFORE U FORGET SET UP QUOTAS BEFORE YOU SPEND ALL YOUR MONEY YOU BUM

# first figuring out autocomplete thingy
def get_place(indata):
    autoc_url = 'https://places.googleapis.com/v1/places:autocomplete'
    headers = {
        'Content-Type':'application/json',
        'X-Goog-Api-Key':api_key,
        'X-Goog-FieldMask':'suggestions.placePrediction.placeId,suggestions.placePrediction.text.text'
        }
    data = {
        'input':str(indata)
    }
    response = requests.post(autoc_url, data=json.dumps(data), headers=headers)
    # print(response.json())
    # print(response.status_code)
    return response.json()

# ok now time to process the autocomplete thingy
'''
example json response:
{'suggestions': [
    {'placePrediction': 
        {'placeId': 'EiQxMjIgTm9iZWwgRHJpdmUsIFNhbnRhIENydXosIENBLCBVU0EiMBIuChQKEgkrAw5ExUGOgBElcSBwRGPKCRB6KhQKEgnZhPHdxEGOgBG9kVblpM7MWw', 
         'text': {'text': '122 Nobel Drive, Santa Cruz, CA, USA'}}}]}
'''

def extract_from_place(response):
    ids = [] # placeIds
    adds = [] # addresses
    for s in response['suggestions']:
        ids.append(s['placePrediction']['placeId']) # this gets the placeId
        adds.append(s['placePrediction']['text']['text']) # this gets the place text 
        # idrk if I need to use the other fields...? lowkey these two should suffice 

    return ids, adds

# ok figuring out routes distance between two points now (too lazy to use routes matrix LOL)
def get_route(start, end): # start, end both placeId
    route_url = 'https://routes.googleapis.com/directions/v2:computeRoutes'
    headers = {
        'Content-Type':'application/json',
        'X-Goog-Api-Key':api_key,
        'X-Goog-FieldMask':'routes.duration,routes.distanceMeters'
    }
    data = {
        'origin':{
            'placeId':start
        },
        'destination':{
            'placeId':end
        },
        'travelMode':'DRIVE',
        'routingPreference':'TRAFFIC_AWARE',
        'computeAlternativeRoutes':False,
        "routeModifiers": {
            "avoidTolls": False,
            "avoidHighways": False,
            "avoidFerries": False
        },
        "languageCode": "en-US",
        "units": "IMPERIAL"
    }
    response = requests.post(route_url, data=json.dumps(data), headers=headers)
    return response.json()

def extract_from_route(response):
    route = response['routes'][0]
    dist = float(route['distanceMeters'])
    time = float(route['duration'][:-1])
    return dist, time

if __name__ == '__main__':
    indata = input('lmk where from homie:\n')
    response = get_place(indata)
    print(response)
    ids, adds = extract_from_place(response)
    print(ids)
    print(adds)

    indata1 = input('lmk where to homie:\n')
    response1 = get_place(indata1)
    print(response1)
    ids1, adds1 = extract_from_place(response1)
    print(ids1)
    print(adds1)

    dist, time = extract_from_route(get_route(ids[0],ids1[0]))
    print(f'Distance between {adds[0]} and {adds1[0]} is {dist} meters, will take {time} seconds.')