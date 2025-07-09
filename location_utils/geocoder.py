# location_utils/geocoder.py
from geopy.geocoders import Nominatim
from geopy.extra.rate_limiter import RateLimiter
import time

# Initialize geocoder
geolocator = Nominatim(
    user_agent="geoai_app_v2",
    timeout=10
)
reverse_geocode = RateLimiter(geolocator.reverse, min_delay_seconds=1)

def get_address_from_coords(coords):
    """Convert coordinates to address with retry logic"""
    if not coords or len(coords) != 2:
        return "Invalid coordinates"
    
    lat, lon = coords
    
    # Validate coordinate ranges
    if not (-90 <= lat <= 90) or not (-180 <= lon <= 180):
        return "Invalid coordinate range"
    
    for attempt in range(3):  # Retry logic
        try:
            print(f"[GEOCODER] Attempt {attempt + 1}: Reverse geocoding {lat}, {lon}")
            location = reverse_geocode(f"{lat}, {lon}", language='en', exactly_one=True, timeout=15)
            
            if location:
                print(f"[GEOCODER] Success: {location.address}")
                return location.address
            else:
                print("[GEOCODER] No location found")
                return "Unknown location"
                
        except Exception as e:
            print(f"[GEOCODER] Attempt {attempt+1} failed: {e}")
            if attempt < 2:  # Don't sleep on last attempt
                time.sleep(2)
    
    return "Geocoding service unavailable"
