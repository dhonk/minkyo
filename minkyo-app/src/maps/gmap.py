import httpx
import json
import time

from maps.schemas import *
from core.config import settings


def _location_bias_from_shape(shape: Circle | Rectangle) -> LocationBias:
    """Build LocationBias with only the field matching the shape type set."""
    if isinstance(shape, Circle):
        return LocationBias(circle=shape, rectangle=None)
    return LocationBias(circle=None, rectangle=shape)

def _location_restriction_from_shape(shape: Circle | Rectangle) -> LocationRestriction:
    """Build LocationRestriction with only the field matching the shape type set."""
    if isinstance(shape, Circle):
        return LocationRestriction(circle=shape, rectangle=None)
    return LocationRestriction(circle=None, rectangle=shape)

def _distance_cache_key(
    x: PlaceId,
    y: PlaceId,
    travel_mode: str,
    routing_preference: str,
    avoid_tolls: bool,
    avoid_highways: bool,
    avoid_ferries: bool,
) -> tuple:
    """Build cache key for distance lookup. Normalize place ID order so (A,B) and (B,A) share one entry."""
    pair = tuple([x, y])
    return (pair, travel_mode, routing_preference, avoid_tolls, avoid_highways, avoid_ferries)


# TODO: later complete this to robustly handle the entire api
class gmap_client:
    def __init__(self, api_key: str | None = None, distance_cache_ttl_seconds: float | None = 86400):
        """Create a Google Maps client. Uses in-memory cache for get_distance_by_place_id by default (24h TTL). Set distance_cache_ttl_seconds=None to disable caching."""
        self.api_key: str = api_key or settings.gmaps_api_key
        self._distance_cache_ttl = distance_cache_ttl_seconds
        self._distance_cache: dict | None = {} if distance_cache_ttl_seconds is not None else None

    def get_autocomplete(self, 
                        input_str: str,
                        shape: Circle | Rectangle,  
                        locationBias: bool | None = True,
                        locationRestriction: bool | None = False,
                        api_key: str | None = None,
                        ) -> list[PlacePrediction]:
        """Request place/query autocomplete suggestions from the Google Places API.

        Sends a request to the Places Autocomplete endpoint with optional
        location bias or restriction. The shape (circle or rectangle) defines
        the area; you must set either locationBias or locationRestriction (but
        not both) when providing a shape.

        Args:
            input_str: The user's input string to complete (e.g. "cafe", "123 main").
            shape: Area to bias or restrict results to (Circle or Rectangle).
            locationBias: If True, use shape as a soft bias toward the area.
            locationRestriction: If True, use shape to restrict results to the area.
            api_key: Optional override for the API key (currently unused).

        Default behavior: If shape is provided and both locationBias and
            locationRestriction are False, locationBias is treated as True
            (shape is used as a soft bias).

        Returns:
            List of Suggestion objects (place and/or query predictions).

        Raises:
            ValueError: If both locationBias and locationRestriction are True.
        """
        if locationBias and locationRestriction:
            raise ValueError('Cannot use both locationBias and locationRestriction')

        # Default: when shape is given but neither bias nor restriction is set, use locationBias.
        if shape and not (locationBias or locationRestriction):
            locationBias = True
        
        url: str = 'https://places.googleapis.com/v1/places:autocomplete'
        
        headers = {
            'Content-Type': 'application/json',
            'X-Goog-Api-Key': self.api_key
        }

        params: AutocompleteRequestBias | AutocompleteRequestRestriction = None

        if locationBias:
            location_bias = _location_bias_from_shape(shape)
            params = AutocompleteRequestBias(input=input_str, location_bias=location_bias)

        if locationRestriction:
            location_restriction = _location_restriction_from_shape(shape)
            params = AutocompleteRequestRestriction(input=input_str, location_restriction=location_restriction)

        body = params.model_dump(exclude_none=True, by_alias=True)
        params_json = json.dumps(body, indent=4)

        print(params_json)

        # TODO: robust http request
        try:
            response = httpx.post(url=url, json=body, headers=headers)
        except Exception as e:
            print(f'An error occured: {e}')
            raise

        print(response)
        print(json.dumps(response.json(), indent=4))
        response_data: AutocompleteResponse = None

        try:
            response_data = AutocompleteResponse.model_validate(response.json(), by_alias=True)        
        except Exception as e:
            print(f'An error occured: {e}')

        return response_data.suggestions

    '''
    TODO: more cool stuff to do with route response: https://developers.google.com/maps/documentation/routes/understand-route-response
    Eg. get a shorter route, eco friendly, waypoints
    '''
    def get_distance_by_place_id(self,
                     x: PlaceId,
                     y: PlaceId,
                     travel_mode: str = 'DRIVE',
                     routing_preference: str = 'TRAFFIC_AWARE',
                     compute_alternative_routes: bool = False,
                     avoid_tolls: bool = False,
                     avoid_highways: bool = False,
                     avoid_ferries: bool = False,
                     langauge_code: str = 'en-US',
                     units: str = 'METRIC',                     
                     ) -> tuple[float, float, PolylineEncode]:
        if self._distance_cache is not None:
            key = _distance_cache_key(x, y, travel_mode, routing_preference, avoid_tolls, avoid_highways, avoid_ferries)
            now = time.monotonic()
            if key in self._distance_cache:
                value, expiry = self._distance_cache[key]
                if now <= expiry:
                    return value
                del self._distance_cache[key]
            result = self._fetch_distance_by_place_id(
                x, y, travel_mode, routing_preference, compute_alternative_routes,
                avoid_tolls, avoid_highways, avoid_ferries, langauge_code, units,
            )
            self._distance_cache[key] = (result, now + self._distance_cache_ttl)
            return result
        return self._fetch_distance_by_place_id(
            x, y, travel_mode, routing_preference, compute_alternative_routes,
            avoid_tolls, avoid_highways, avoid_ferries, langauge_code, units,
        )

    def _fetch_distance_by_place_id(self,
                     x: PlaceId,
                     y: PlaceId,
                     travel_mode: str = 'DRIVE',
                     routing_preference: str = 'TRAFFIC_AWARE',
                     compute_alternative_routes: bool = False,
                     avoid_tolls: bool = False,
                     avoid_highways: bool = False,
                     avoid_ferries: bool = False,
                     langauge_code: str = 'en-US',
                     units: str = 'METRIC',                     
                     ) -> tuple[float, float, PolylineEncode]:
        url: str = 'https://routes.googleapis.com/directions/v2:computeRoutes'
        origin = Point(place_id=x)
        destination = Point(place_id=y)
        mod = RouteModifiers(avoid_tolls=avoid_tolls,
                             avoid_highways=avoid_highways,
                             avoid_ferries=avoid_ferries)
        params = RouteRequest(origin=origin,
                              destination=destination,
                              travel_mode=travel_mode,
                              routing_preference=routing_preference,
                              coupute_alternative_routes=compute_alternative_routes,
                              route_modifiers=mod,
                              language_code=langauge_code,
                              units=units)
        headers = {
            'Content-Type': 'application/json',
            'X-Goog-Api-Key': self.api_key,
            'X-Goog-FieldMask': 'routes.duration,routes.distanceMeters,routes.polyline.encodedPolyline'
        }

        body = params.model_dump(exclude_none=True, by_alias=True)
        print(json.dumps(body, indent=4))

        try:
            response = httpx.post(url=url, json=body, headers=headers)
            response.raise_for_status()
        except httpx.RequestError as e:
            print(f'Error: {e}')

        except Exception as e:
            print(f'Error: {e}')
            raise
        
        print(response)
        print(json.dumps(response.json(), indent=4))

        try:
            response_data = RouteResponse.model_validate(response.json(), by_alias=True)
        except Exception as e:
            print(f'Error: {e}')
            raise
        
        if not compute_alternative_routes:
            route = response_data.routes[0]

        distance = route.distance_meters
        duration = float(route.duration[:-1])
        polyline = route.polyline.encoded_polyline
        
        print(f'Distance: {distance}, Duration: {duration} (seconds), Polyline Encoding: {polyline}')
        return distance, duration, polyline