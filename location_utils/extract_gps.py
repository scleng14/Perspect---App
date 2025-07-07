# location_utils/extract_gps.py

from PIL import Image
from PIL.ExifTags import TAGS, GPSTAGS

def extract_gps(image_path):
    try:
        image = Image.open(image_path)
        exif_data = image._getexif()
        if not exif_data:
            return None
        
        gps_info = {}
        for tag_id, value in exif_data.items():
            tag = TAGS.get(tag_id, tag_id)
            if tag == "GPSInfo":
                for key in value:
                    sub_tag = GPSTAGS.get(key, key)
                    gps_info[sub_tag] = value[key]
        return gps_info if gps_info else None
    except Exception as e:
        print(f"[GPS ERROR] {e}")
        return None

def convert_gps(gps_info):
    try:
        def _convert(coord, ref):
            deg, minute, sec = coord
            result = deg[0] / deg[1] + minute[0] / minute[1] / 60 + sec[0] / sec[1] / 3600
            return result if ref in ['N', 'E'] else -result

        lat = _convert(gps_info["GPSLatitude"], gps_info["GPSLatitudeRef"])
        lon = _convert(gps_info["GPSLongitude"], gps_info["GPSLongitudeRef"])
        return (lat, lon)
    except Exception as e:
        print(f"[CONVERT ERROR] {e}")
        return None

