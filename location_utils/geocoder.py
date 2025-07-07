#geocoder.py
from geopy.geocoders import Nominatim
from geopy.extra.rate_limiter import RateLimiter
import time

geolocator = Nominatim(
    user_agent="geoai_app_v2",
    timeout=10
)
reverse_geocode = RateLimiter(geolocator.reverse, min_delay_seconds=1)

def get_address_from_coords(coords):
    """Convert coordinates to address"""
    for attempt in range(3):  # Retry logic
        try:
            location = reverse_geocode(coords, language='en')
            return location.address if location else "Unknown location"
        except Exception as e:
            print(f"Geocoding attempt {attempt+1} failed: {e}")
            time.sleep(2)
    return "Geocoding service unavailable"
