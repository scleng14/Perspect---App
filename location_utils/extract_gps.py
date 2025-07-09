# location_utils/extract_gps.py
from PIL import Image
from PIL.ExifTags import TAGS, GPSTAGS

def extract_gps(image_path):
    """Extract GPS information from image EXIF data"""
    try:
        image = Image.open(image_path)
        
        # Handle different EXIF formats
        exif_data = None
        if hasattr(image, '_getexif'):
            exif_data = image._getexif()
        elif hasattr(image, 'getexif'):
            exif_data = image.getexif()
        
        if not exif_data:
            # Try alternative method for some formats
            try:
                exif_data = image.info.get('exif')
                if exif_data:
                    from PIL.ExifTags import Exif
                    exif_data = Exif().get(exif_data)
            except:
                return None
        
        if not exif_data:
            print("[EXIF] No EXIF data found")
            return None
        
        # Extract GPS info
        gps_info = {}
        for tag_id, value in exif_data.items():
            tag = TAGS.get(tag_id)
            if tag == "GPSInfo":
                for key in value:
                    decoded = GPSTAGS.get(key, key)
                    gps_info[decoded] = value[key]
        
        if gps_info:
            print(f"[EXIF] GPS data found: {list(gps_info.keys())}")
            return gps_info
        else:
            print("[EXIF] No GPS data in EXIF")
            return None
            
    except Exception as e:
        print(f"[EXIF ERROR] {str(e)}")
        return None 
   
        
def convert_gps(gps_info):
    
    try:
        def _safe_convert(coord, ref):
            """Safely convert coordinates handling different formats"""
            # Handle direct decimal values
            if isinstance(coord, (int, float)):
                return coord if ref in ['N', 'E'] else -coord
            
            # Handle tuple/list formats
            if isinstance(coord, (tuple, list)):
                if len(coord) == 3:  # Standard degrees, minutes, seconds
                    deg, minute, sec = coord
                    # Handle different fraction formats
                    if isinstance(deg, tuple) and len(deg) == 2:
                        deg_val = deg[0] / deg[1]
                    else:
                        deg_val = float(deg)
                    
                    if isinstance(minute, tuple) and len(minute) == 2:
                        min_val = minute[0] / minute[1]
                    else:
                        min_val = float(minute)
                    
                    if isinstance(sec, tuple) and len(sec) == 2:
                        sec_val = sec[0] / sec[1]
                    else:
                        sec_val = float(sec)
                    
                    result = deg_val + min_val/60 + sec_val/3600
                    
                elif len(coord) == 2:  # Only degrees and minutes
                    deg, minute = coord
                    if isinstance(deg, tuple) and len(deg) == 2:
                        deg_val = deg[0] / deg[1]
                    else:
                        deg_val = float(deg)
                    
                    if isinstance(minute, tuple) and len(minute) == 2:
                        min_val = minute[0] / minute[1]
                    else:
                        min_val = float(minute)
                    
                    result = deg_val + min_val/60
                    
                elif len(coord) == 1:  # Decimal degrees
                    if isinstance(coord[0], tuple) and len(coord[0]) == 2:
                        result = coord[0][0] / coord[0][1]
                    else:
                        result = float(coord[0])
                else:
                    return None
                    
                return result if ref in ['N', 'E'] else -result
            
            return None
        
        # Check for required GPS fields
        required = ["GPSLatitude", "GPSLatitudeRef", "GPSLongitude", "GPSLongitudeRef"]
        missing = [k for k in required if k not in gps_info]
        if missing:
            print(f"[CONVERT] Missing GPS fields: {missing}")
            return None
        
        lat = _safe_convert(gps_info["GPSLatitude"], gps_info["GPSLatitudeRef"])
        lon = _safe_convert(gps_info["GPSLongitude"], gps_info["GPSLongitudeRef"])
        
        if lat is None or lon is None:
            print("[CONVERT] Failed to convert coordinates")
            return None
            
        # Validate coordinate ranges
        if not (-90 <= lat <= 90) or not (-180 <= lon <= 180):
            print(f"[CONVERT] Invalid coordinates: lat={lat}, lon={lon}")
            return None
            
        print(f"[CONVERT] Success: lat={lat:.6f}, lon={lon:.6f}")
        return (round(lat, 6), round(lon, 6))
        
    except Exception as e:
        print(f"[CONVERT ERROR] {e}")
        return None
