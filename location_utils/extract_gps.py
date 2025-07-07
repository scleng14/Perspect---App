# location_utils/extract_gps.py

from PIL import Image
from PIL.ExifTags import TAGS, GPSTAGS

def extract_gps(image_path):
    try:
        image = Image.open(image_path)
        
 # Handle different EXIF formats
        if hasattr(image, '_getexif'):
            exif_data = image._getexif()
        elif hasattr(image, 'getexif'):
            exif_data = image.getexif()
        else:
            return None
            
        if not exif_data:
            # Try alternative method for some formats
            try:
                exif_data = image.info.get('exif')
                if exif_data:
                    from PIL.ExifTags import Exif
                    exif_data = Exif().get(exif_data)
            except:
                return None
        
        gps_info = {}
        # Rest of your existing code...
def convert_gps(gps_info):
    try:
        def _safe_convert(coord, ref):
            # 处理不同相机格式
            if isinstance(coord, (int, float)):
                return coord if ref in ['N','E'] else -coord
            
            if len(coord) == 3:  # 标准度分秒格式
                deg, minute, sec = coord
                result = deg[0]/deg[1] + minute[0]/minute[1]/60 + sec[0]/sec[1]/3600
            elif len(coord) == 2:  # 只有度和分
                deg, minute = coord
                result = deg[0]/deg[1] + minute[0]/minute[1]/60
            else:  # 十进制度
                result = coord[0]/coord[1]
                
            return result if ref in ['N','E'] else -result

        required = ["GPSLatitude", "GPSLatitudeRef", "GPSLongitude", "GPSLongitudeRef"]
        if not all(k in gps_info for k in required):
            return None
            
        return (
            _safe_convert(gps_info["GPSLatitude"], gps_info["GPSLatitudeRef"]),
            _safe_convert(gps_info["GPSLongitude"], gps_info["GPSLongitudeRef"])
        )
    except Exception as e:
        print(f"[CONVERT ERROR] {e}")
        return None
