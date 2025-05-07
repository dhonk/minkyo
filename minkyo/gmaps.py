import dotenv
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
    # print(f'Start pId: {start}, End pId: {end}')
    response = requests.post(route_url, data=json.dumps(data), headers=headers)
    return response.json()

def extract_from_route(response):
    # print(response)
    route = response['routes'][0]
    try: 
        dist = float(route['distanceMeters'])
    except KeyError:
        dist = 0
    time = float(route['duration'][:-1])
    # print(f'distance: {dist} time: {time}')
    return dist, time

if __name__ == '__main__':
    indata = input('from:\n')
    response = get_place(indata)
    ids, adds = extract_from_place(response)
    # print(ids)
    for i, x in enumerate(adds):
        print(f'{i}: {x}')
    selection1 = input('select which option: integer\n')
    selection1 = int(selection1)
    print(ids[selection1])

    indata1 = input('to:\n')
    response1 = get_place(indata1)
    ids1, adds1 = extract_from_place(response1)
    # print(ids1)
    for i, x in enumerate(adds1):
        print(f'{i}: {x}')
    selection2 = input('select which option: integer\n')
    selection2 = int(selection2)
    print(ids1[selection2])

    dist, time = extract_from_route(get_route(ids[selection1],ids1[selection2]))
    print(f'Distance between {adds[selection1]} and {adds1[selection2]} is {dist} meters, will take {time} seconds.')