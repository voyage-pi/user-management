import httpx
import json

from app.config.settings import GOOGLE_MAPS_API_KEY
from app.services.redis_client import redis_client

from app.models.request_models import ComputeRoutesRequest, Location, PlaceID
from app.models.response_models import RouteResult

BASE_GOOGLE_URL = "https://routes.googleapis.com/directions/v2:computeRoutes"

async def fetch_routes(request: ComputeRoutesRequest):
    """
    Fetch routes from Google Routes API with the provided parameters.
    Normalizes the response before returning.
    """

    origin = request.origin
    destination = request.destination
    intermediate = request.intermediate
    traveling_mode = request.travelingMode

    if not origin or not destination:
        return {"error": "Origin and destination are required"}

    if not GOOGLE_MAPS_API_KEY:
        raise ValueError("Google Maps API Key is missing!")

    cache_key = f"routes:{get_key(origin)}:{get_key(destination)}"
    cache_key += f":{','.join([get_key(loc) for loc in intermediate])}:{traveling_mode}"

    cached_data = await redis_client.get(cache_key)
    if cached_data:
        print("FROM CACHE")
        return json.loads(cached_data)

    headers = {
        "Content-Type": "application/json",
        "X-Goog-Api-Key": GOOGLE_MAPS_API_KEY,
        "X-Goog-FieldMask": "routes.distanceMeters,routes.duration,routes.polyline.encodedPolyline"
    }

    payload = {
        "origin": get_payload(origin),
        "destination": get_payload(destination),
        "travelMode": traveling_mode,
        "intermediates": [get_payload(loc) for loc in intermediate],
    }

    async with httpx.AsyncClient() as client:
        response = await client.post(BASE_GOOGLE_URL, json=payload, headers=headers)
        data = response.json()

    print("GOOGLE API RAW RESPONSE:", json.dumps(data, indent=2))

    if "routes" not in data:
        return {"error": "Invalid response from Google API", "details": data}

    normalized_data = normalize_google_response(data["routes"])
    
    normalized_data_dict = [route.dict() for route in normalized_data]

    await redis_client.set(cache_key, json.dumps(normalized_data_dict), expire=3600)

    return normalized_data

def get_key(item):
    """Helper function to get a string key for caching and the request"""
    if isinstance(item, Location):
        return f"{item.latitude},{item.longitude}"
    elif isinstance(item, PlaceID):
        return item.place_id
    return ""

def get_payload(item):
    """Helper function to prepare payload data for either Location or PlaceID"""
    if isinstance(item, Location):
        return {"location": {"latLng": {"latitude": item.latitude, "longitude": item.longitude}}}
    elif isinstance(item, PlaceID):
        return {"placeId": item.place_id}
    return {}

def normalize_google_response(routes):
    """
    Normalize Google Routes API response to match the required fields.
    Converts raw data into a list of RouteResult instances.
    """

    normalized = []

    for route in routes:
        polyline_encoded = route.get("polyline", {}).get("encodedPolyline", "")

        duration_str = route.get("duration", "")
        duration = 0
        if duration_str.endswith('s'):
            try:
                duration = int(duration_str[:-1])  # Remove 's' and convert to int
            except ValueError:
                duration = 0  # Default to 0 if there's an issue parsing the duration
        
        distance = route.get("distanceMeters", 0)

        normalized.append(RouteResult(
            polylineEncoded=polyline_encoded,
            duration=duration,
            distance=distance
        ))

    return normalized
