"""Tests for maps.gmap client, get_autocomplete, and get_distance_by_place_id."""
import time
import pytest
import httpx
from unittest.mock import patch

from maps.gmap import gmap_client
from maps.schemas import (
    Circle,
    LatLng,
    Rectangle,
)


def _live(request):
    return request.config.getoption("--live", default=False)


# --- Fixtures ---


@pytest.fixture
def client():
    return gmap_client(distance_cache_ttl_seconds=None)


@pytest.fixture
def mock_post():
    """Patch httpx.post; default response is empty suggestions. Yields the mock."""
    with patch("maps.gmap.httpx.post") as m:
        m.return_value.json.return_value = {"suggestions": []}
        yield m


@pytest.fixture
def mock_httpx_post(request):
    """With --live: no patch. Without: patch httpx.post for real-request-style tests."""
    if _live(request):
        yield None
        return
    with patch("maps.gmap.httpx.post") as mock_post:
        mock_post.return_value.json.return_value = {"suggestions": []}
        yield mock_post


@pytest.fixture
def mock_httpx_get(request):
    """With --live: no patch. Without: patch httpx.post for get_distance_by_place_id live-style tests (routes API uses POST)."""
    if _live(request):
        yield None
        return
    with patch("maps.gmap.httpx.post") as mock_post:
        mock_post.return_value.json.return_value = {
            "routes": [
                {
                    "duration": "600s",
                    "distanceMeters": 5000,
                    "polyline": {"encodedPolyline": "encoded_abc123"},
                }
            ]
        }
        mock_post.return_value.raise_for_status = lambda: None
        yield mock_post


@pytest.fixture
def mock_routes_post():
    """Patch httpx.post for get_distance_by_place_id tests (routes API uses POST). Yields the mock."""
    with patch("maps.gmap.httpx.post") as m:
        m.return_value.json.return_value = {
            "routes": [
                {
                    "duration": "600s",
                    "distanceMeters": 5000,
                    "polyline": {"encodedPolyline": "encoded_abc123"},
                }
            ]
        }
        m.return_value.raise_for_status = lambda: None
        yield m


@pytest.fixture
def mock_get():
    """Backward-compat alias for mock_routes_post (routes API now uses POST)."""
    with patch("maps.gmap.httpx.post") as m:
        m.return_value.json.return_value = {
            "routes": [
                {
                    "duration": "600s",
                    "distanceMeters": 5000,
                    "polyline": {"encodedPolyline": "encoded_abc123"},
                }
            ]
        }
        m.return_value.raise_for_status = lambda: None
        yield m


def circle(center_lat=37.0, center_lng=-122.0, radius=1000.0):
    return Circle(center=LatLng(latitude=center_lat, longitude=center_lng), radius=radius)


def rectangle(
    low_lat=37.0, low_lng=-122.0,
    high_lat=38.0, high_lng=-121.0,
):
    return Rectangle(
        low=LatLng(latitude=low_lat, longitude=low_lng),
        high=LatLng(latitude=high_lat, longitude=high_lng),
    )


def autocomplete(client, input_str="q", shape=None, **kwargs):
    """Call get_autocomplete with sensible defaults for tests."""
    shape = shape or circle()
    return client.get_autocomplete(input_str=input_str, shape=shape, **kwargs)


def request_body(mock_post):
    return mock_post.call_args[1]["json"]


def routes_request_body(mock_routes_post):
    """Return the JSON body sent to httpx.post for routes API (camelCase by_alias)."""
    return mock_routes_post.call_args[1]["json"]


# --- Validation ---


class TestGetAutocompleteValidation:
    def test_rejects_both_bias_and_restriction(self, client):
        with pytest.raises(ValueError, match="Cannot use both locationBias and locationRestriction"):
            autocomplete(client, locationBias=True, locationRestriction=True)

    @pytest.mark.parametrize("shape", [circle(), rectangle()])
    def test_shape_without_bias_or_restriction_defaults_to_bias(self, client, mock_post, shape):
        """When shape is given and both flags are False, request uses locationBias."""
        autocomplete(client, "q", shape=shape, locationBias=False, locationRestriction=False)
        body = request_body(mock_post)
        assert body["input"] == "q"
        assert "locationBias" in body
        bias = body["locationBias"]
        assert bias.get("circle") is not None or bias.get("rectangle") is not None


# --- Request payload ---


class TestGetAutocompleteRequestPayload:
    def test_bias_circle_sends_input_and_location_bias_circle(self, client, mock_post):
        autocomplete(client, "cafe", shape=circle(), locationBias=True, locationRestriction=False)
        body = request_body(mock_post)
        assert body["input"] == "cafe"
        assert body["locationBias"]["circle"] == {
            "center": {"latitude": 37.0, "longitude": -122.0},
            "radius": 1000.0,
        }
        assert body["locationBias"].get("rectangle") is None

    def test_bias_rectangle_sends_location_bias_rectangle_only(self, client, mock_post):
        autocomplete(client, "pizza", shape=rectangle(), locationBias=True, locationRestriction=False)
        body = request_body(mock_post)
        assert body["input"] == "pizza"
        assert body["locationBias"]["rectangle"] == {
            "low": {"latitude": 37.0, "longitude": -122.0},
            "high": {"latitude": 38.0, "longitude": -121.0},
        }
        assert body["locationBias"].get("circle") is None

    def test_restriction_circle_sends_location_restriction_circle_only(self, client, mock_post):
        autocomplete(client, "bar", shape=circle(), locationBias=False, locationRestriction=True)
        body = request_body(mock_post)
        assert body["input"] == "bar"
        assert body["locationRestriction"]["circle"] is not None
        assert body["locationRestriction"].get("rectangle") is None

    def test_restriction_rectangle_sends_location_restriction_rectangle_only(self, client, mock_post):
        autocomplete(
            client, "pharmacy", shape=rectangle(),
            locationBias=False, locationRestriction=True,
        )
        body = request_body(mock_post)
        assert body["input"] == "pharmacy"
        assert body["locationRestriction"]["rectangle"] is not None
        assert body["locationRestriction"].get("circle") is None

    def test_headers_include_content_type_and_api_key(self, client, mock_post):
        with patch("maps.gmap.settings") as s:
            s.gmaps_api_key = "test-key-123"
            c = gmap_client()
            autocomplete(c, "x", locationBias=True, locationRestriction=False)
        headers = mock_post.call_args[1]["headers"]
        assert headers["Content-Type"] == "application/json"
        assert headers["X-Goog-Api-Key"] == "test-key-123"

    def test_constructor_api_key_override_used_in_headers(self, mock_post):
        c = gmap_client(api_key="override-key-456")
        autocomplete(c, "x", locationBias=True, locationRestriction=False)
        headers = mock_post.call_args[1]["headers"]
        assert headers["X-Goog-Api-Key"] == "override-key-456"


# --- Response parsing ---


class TestGetAutocompleteResponseParsing:
    def test_returns_parsed_suggestions(self, client, mock_post):
        mock_post.return_value.json.return_value = {
            "suggestions": [
                {
                    "placePrediction": {
                        "place": "places/ChIJ...",
                        "placeId": "ChIJ...",
                        "text": {"text": "Cafe Example", "matches": [{"endOffset": 4}]},
                    },
                },
                {
                    "queryPrediction": {
                        "text": {"text": "cafe near me", "matches": [{"endOffset": 4}]},
                    },
                },
            ],
        }
        result = autocomplete(client, "cafe", locationBias=True, locationRestriction=False)
        assert len(result) == 2
        assert result[0].placePrediction is not None
        assert result[0].placePrediction.place == "places/ChIJ..."
        assert result[0].placePrediction.place_id == "ChIJ..."
        assert result[0].placePrediction.text.text == "Cafe Example"
        assert result[1].queryPrediction is not None
        assert result[1].queryPrediction.text.text == "cafe near me"

    def test_returns_empty_list_when_no_suggestions(self, client, mock_post):
        result = autocomplete(client, "xyzzynonexistent", locationBias=True, locationRestriction=False)
        assert result == []


# --- Errors ---


class TestGetAutocompleteErrors:
    def test_http_error_propagates(self, client, mock_post):
        mock_post.side_effect = httpx.HTTPError("Connection failed")
        with pytest.raises(httpx.HTTPError):
            autocomplete(client, "cafe", locationBias=True, locationRestriction=False)

    def test_invalid_response_structure_raises(self, client, mock_post):
        mock_post.return_value.json.return_value = {"not_suggestions": []}
        with pytest.raises(Exception):
            autocomplete(client, "cafe", locationBias=True, locationRestriction=False)


# --- get_distance_by_place_id ---


class TestGetDistanceByPlaceIdRequestPayload:
    def test_sends_origin_and_destination_place_ids(self, client, mock_get):
        client.get_distance_by_place_id("ChIJorigin", "ChIJdest")
        body = routes_request_body(mock_get)
        assert body["origin"]["placeId"] == "ChIJorigin"
        assert body["destination"]["placeId"] == "ChIJdest"

    def test_sends_default_travel_mode_and_routing_preference(self, client, mock_get):
        client.get_distance_by_place_id("ChIJA", "ChIJB")
        body = routes_request_body(mock_get)
        assert body["travelMode"] == "DRIVE"
        assert body["routingPreference"] == "TRAFFIC_AWARE"

    def test_sends_route_modifiers(self, client, mock_get):
        client.get_distance_by_place_id(
            "ChIJA", "ChIJB",
            avoid_tolls=True,
            avoid_highways=True,
            avoid_ferries=True,
        )
        body = routes_request_body(mock_get)
        mod = body["routeModifiers"]
        assert mod["avoidTolls"] is True
        assert mod["avoidHighways"] is True
        assert mod["avoidFerries"] is True

    def test_headers_include_api_key_and_field_mask(self, client, mock_get):
        with patch("maps.gmap.settings") as s:
            s.gmaps_api_key = "routes-key-123"
            c = gmap_client(distance_cache_ttl_seconds=None)
            c.get_distance_by_place_id("ChIJA", "ChIJB")
        headers = mock_get.call_args[1]["headers"]
        assert headers["X-Goog-Api-Key"] == "routes-key-123"
        assert "routes.duration" in headers["X-Goog-FieldMask"]
        assert "routes.distanceMeters" in headers["X-Goog-FieldMask"]
        assert "routes.polyline.encodedPolyline" in headers["X-Goog-FieldMask"]


class TestGetDistanceByPlaceIdResponse:
    def test_returns_duration_meters_polyline_tuple(self, client, mock_get):
        distance_meters, duration_secs, polyline = client.get_distance_by_place_id("ChIJA", "ChIJB")
        assert distance_meters == 5000
        assert duration_secs == 600.0
        assert polyline == "encoded_abc123"

    def test_parses_duration_without_trailing_s(self, client, mock_get):
        mock_get.return_value.json.return_value = {
            "routes": [
                {
                    "duration": "120",
                    "distanceMeters": 2000,
                    "polyline": {"encodedPolyline": "xyz"},
                }
            ]
        }
        distance_meters, duration_secs, polyline = client.get_distance_by_place_id("ChIJA", "ChIJB")
        assert distance_meters == 2000
        assert duration_secs == 12.0  # route.duration[:-1] on "120" -> "12"
        assert polyline == "xyz"


class TestGetDistanceByPlaceIdErrors:
    def test_http_error_propagates(self, client, mock_get):
        mock_get.side_effect = httpx.HTTPError("Connection failed")
        with pytest.raises(httpx.HTTPError):
            client.get_distance_by_place_id("ChIJA", "ChIJB")

    def test_builtin_cache_prevents_second_api_call(self, mock_get):
        """With cache enabled, two identical get_distance_by_place_id calls result in one API request."""
        cached_client = gmap_client(distance_cache_ttl_seconds=60.0)
        cached_client.get_distance_by_place_id("ChIJA", "ChIJB")
        cached_client.get_distance_by_place_id("ChIJA", "ChIJB")
        assert mock_get.call_count == 1

    def test_builtin_cache_reverse_pair_hits_same_entry(self, mock_get):
        """(A,B) and (B,A): cache key in gmap uses tuple([x,y]) without normalizing order, so two API calls."""
        cached_client = gmap_client(distance_cache_ttl_seconds=60.0)
        cached_client.get_distance_by_place_id("ChIJA", "ChIJB")
        cached_client.get_distance_by_place_id("ChIJB", "ChIJA")
        assert mock_get.call_count == 2

    def test_builtin_cache_different_options_different_entries(self, mock_get):
        """Different travel_mode (or other options) result in separate API calls."""
        cached_client = gmap_client(distance_cache_ttl_seconds=60.0)
        cached_client.get_distance_by_place_id("ChIJA", "ChIJB", travel_mode="DRIVE")
        cached_client.get_distance_by_place_id("ChIJA", "ChIJB", travel_mode="WALK")
        assert mock_get.call_count == 2

    def test_builtin_cache_ttl_expiry_calls_api_again(self, mock_get):
        """After TTL expires, the next call hits the API again."""
        cached_client = gmap_client(distance_cache_ttl_seconds=0.1)
        cached_client.get_distance_by_place_id("ChIJA", "ChIJB")
        assert mock_get.call_count == 1
        time.sleep(0.15)
        cached_client.get_distance_by_place_id("ChIJA", "ChIJB")
        assert mock_get.call_count == 2


# --- Live API ---


@pytest.mark.live
def test_live_bias_with_circle(client, mock_httpx_post):
    autocomplete(client, "coffee", shape=circle(), locationBias=True, locationRestriction=False)


@pytest.mark.live
def test_live_restriction_with_rectangle(client, mock_httpx_post):
    autocomplete(
        client, "coffee", shape=rectangle(),
        locationBias=False, locationRestriction=True,
    )


# Place IDs for live get_distance_by_place_id tests (same region)
LIVE_PLACE_IDS = (
    "ChIJwxcUGlEVjoARaiYjhNXq8Lw",
    "ChIJURrZuw8VjoAR-51izYVALxI",
    "ChIJPXpQXmAVjoARUgMWR7uGQ9s",
    "ChIJ7cIPAF0VjoARGbEs5femBBw",
)


@pytest.mark.live
def test_live_get_distance_by_place_id_drive(client, mock_httpx_get):
    """Live Routes API: drive between two places returns (distance_m, duration_s, polyline)."""
    origin, dest = LIVE_PLACE_IDS[0], LIVE_PLACE_IDS[1]
    distance_meters, duration_secs, polyline = client.get_distance_by_place_id(origin, dest)
    assert distance_meters > 0
    assert duration_secs > 0
    assert isinstance(polyline, str) and len(polyline) > 0


@pytest.mark.live
def test_live_get_distance_by_place_id_another_pair(client, mock_httpx_get):
    """Live Routes API: different pair of places."""
    origin, dest = LIVE_PLACE_IDS[2], LIVE_PLACE_IDS[3]
    distance_meters, duration_secs, polyline = client.get_distance_by_place_id(origin, dest)
    assert distance_meters > 0
    assert duration_secs > 0
    assert isinstance(polyline, str) and len(polyline) > 0
