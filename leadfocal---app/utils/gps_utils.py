
from PIL import Image
from PIL.ExifTags import TAGS, GPSTAGS
from geopy.geocoders import Nominatim

def get_exif_data(image):
    info = image._getexif()
    if not info:
        return None
    exif_data = {}
    for tag, value in info.items():
        decoded = TAGS.get(tag, tag)
        if decoded == "GPSInfo":
            gps_data = {}
            for t in value:
                sub_decoded = GPSTAGS.get(t, t)
                gps_data[sub_decoded] = value[t]
            exif_data[decoded] = gps_data
    return exif_data

def get_coordinates(info):
    def convert_to_degrees(value):
        d = float(value[0][0]) / float(value[0][1])
        m = float(value[1][0]) / float(value[1][1])
        s = float(value[2][0]) / float(value[2][1])
        return d + (m / 60.0) + (s / 3600.0)
    
    if "GPSInfo" not in info:
        return None

    gps_info = info["GPSInfo"]
    if "GPSLatitude" in gps_info and "GPSLongitude" in gps_info:
        lat = convert_to_degrees(gps_info["GPSLatitude"])
        if gps_info.get("GPSLatitudeRef") == "S":
            lat = -lat
        lon = convert_to_degrees(gps_info["GPSLongitude"])
        if gps_info.get("GPSLongitudeRef") == "W":
            lon = -lon
        return lat, lon
    return None

def get_gps_location(image):
    try:
        exif_data = get_exif_data(image)
        coords = get_coordinates(exif_data)
        if coords:
            geolocator = Nominatim(user_agent="geoapiExercises")
            location = geolocator.reverse(coords, language='en')
            return location.address if location else "Unknown location"
    except:
        return None
    return None
