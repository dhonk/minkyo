from pydantic import BaseModel, Field, ConfigDict

type PlaceId = str
type PolylineEncode = str

class PBaseModel(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

class LatLng(BaseModel):
    latitude: float
    longitude: float

class Circle(BaseModel):
    center: LatLng
    radius: float

class Rectangle(BaseModel):
    low: LatLng
    high: LatLng

class LocationBias(BaseModel):
    circle: Circle | None = None
    rectangle: Rectangle | None = None

class LocationRestriction(BaseModel):
    circle: Circle | None = None
    rectangle: Rectangle | None = None

class AutocompleteRequestBias(PBaseModel):
    input: str
    location_bias: LocationBias = Field(alias='locationBias')

class AutocompleteRequestRestriction(PBaseModel):
    input: str
    location_restriction: LocationRestriction = Field(alias='locationRestriction')

class Matches(BaseModel):
    end_offset: int = Field(alias='endOffset')

class Text(BaseModel):
    text: str
    matches: list[Matches]

class PlacePrediction(PBaseModel):
    place: str
    place_id: PlaceId = Field(alias='placeId')
    text: Text

class QueryPrediction(BaseModel):
    text: Text

class Suggestion(BaseModel):
    placePrediction: PlacePrediction | None = None
    queryPrediction: QueryPrediction | None = None

class AutocompleteResponse(BaseModel):
    suggestions: list[Suggestion]

class Location(PBaseModel):
    lat_lng: LatLng = Field(alias='latLng')

class Point(PBaseModel):
    location: Location | None = None
    place_id: PlaceId | None = Field(None, alias='placeId')

class RouteModifiers(PBaseModel):
    avoid_tolls: bool = Field(False, alias='avoidTolls')
    avoid_highways: bool = Field(False, alias='avoidHighways')
    avoid_ferries: bool = Field(False, alias='avoidFerries')

class RouteRequest(PBaseModel):
    origin: Point
    destination: Point
    travel_mode: str = Field('DRIVE', alias='travelMode')
    routing_preference: str = Field('TRAFFIC_AWARE', alias='routingPreference')
    coupute_alternative_routes: bool = Field(False, alias='computeAlternativeRoutes')
    route_modifiers: RouteModifiers = Field(alias='routeModifiers')
    language_code: str = Field('en-US', alias='languageCode')
    units: str = Field('METRIC')

class Polyline(PBaseModel):
    encoded_polyline: PolylineEncode = Field(alias='encodedPolyline')

class Route(PBaseModel):
    distance_meters: float = Field(alias='distanceMeters')
    duration: str
    polyline: Polyline

class RouteResponse(BaseModel):
    routes: list[Route]