# location_utils/landmark.py
from typing import Optional  
import streamlit as st
import requests
from transformers import CLIPProcessor, CLIPModel
from PIL import Image
import torch

@st.cache_resource  # Streamlit专用缓存装饰器
def load_models():
    print("Loading CLIP model...")  # 调试用
    return (
        CLIPProcessor.from_pretrained("openai/clip-vit-base-patch32"),
        CLIPModel.from_pretrained("openai/clip-vit-base-patch32")
    )

clip_processor, clip_model = load_models() 

# Predefined landmarks with name, city, latitude, longitude
LANDMARK_KEYWORDS = {
    #Malaysia landmarks
    "petronas towers": ["Petronas Twin Towers", "Kuala Lumpur", 3.1579, 101.7116],
    "klcc": ["Kuala Lumpur City Centre", "Kuala Lumpur", 3.1586, 101.7145],
    "kl tower": ["KL Tower", "Kuala Lumpur", 3.1528, 101.7039],
    "batu caves": ["Batu Caves", "Selangor", 3.2379, 101.6831],
    "putrajaya pink mosque": ["Putra Mosque", "Putrajaya", 2.9360, 101.6895],
    "kuala lumpur blue mosque": ["Sultan Salahuddin Abdul Aziz Mosque", "Kuala Lumpur", 3.0788, 101.5031],
    "masjid putra": ["Putra Mosque", "Putrajaya", 2.9360, 101.6895],
    "iron mosque": ["Tuanku Mizan Zainal Abidin Mosque", "Putrajaya", 2.9266, 101.6804],
    "sultan abdul samad building": ["Sultan Abdul Samad Building", "Kuala Lumpur", 3.1466, 101.6945],
    "istana negara": ["Istana Negara", "Kuala Lumpur", 3.1339, 101.6842],
    "malacca straits mosque": ["Masjid Selat Melaka", "Malacca", 2.1885, 102.2497],
    "george town street art": ["George Town Street Art", "Penang", 5.4141, 100.3288],
    "komtar": ["Komtar Tower", "Penang", 5.4143, 100.3288],
    "kek lok si": ["Kek Lok Si Temple", "Penang", 5.3991, 100.2736],
    "penang hill": ["Penang Hill", "Penang", 5.4163, 100.2766],
    "langkawi sky bridge": ["Langkawi Sky Bridge", "Langkawi", 6.3847, 99.6636],
    "gunung mat cincang": ["Gunung Mat Cincang", "Langkawi", 6.3790, 99.6652],
    "genting highlands": ["Genting Highlands", "Pahang", 3.4221, 101.7934],
    "legoland malaysia": ["Legoland Malaysia", "Johor", 1.4274, 103.6315],
    "mount kinabalu": ["Mount Kinabalu", "Sabah", 6.0755, 116.5583],
    "kinabalu park": ["Kinabalu Park", "Sabah", 6.0456, 116.6864],
    "menara alor setar": ["Alor Setar Tower", "Kedah", 6.1219, 100.3716],
    "penang bridge": ["Penang Bridge", "Penang", 5.3364, 100.3606],
    "a famosa": ["A Famosa", "Melaka", 2.1912, 102.2501],
    "sabah state mosque": ["Sabah State Mosque", "Kota Kinabalu", 5.9576, 116.0654],
    "gunung kinabalu": ["Mount Kinabalu", "Sabah", 6.0754, 116.5584],

    # Asia
    "Great Wall": ["Great Wall of China", "China", 40.4319, 116.5704],
    "burj khalifa": ["Burj Khalifa", "Dubai", 25.1972, 55.2744],
    "taipei 101": ["Taipei 101", "Taipei", 25.0330, 121.5654],
    "marina bay sands": ["Marina Bay Sands", "Singapore", 1.2834, 103.8607],

    # Europe
    "big ben": ["Big Ben", "London", 51.5007, -0.1246],
    "louvre": ["Louvre Museum", "Paris", 48.8606, 2.3376],
    "sagrada familia": ["Sagrada Família", "Barcelona", 41.4036, 2.1744],

    # America
    "golden gate bridge": ["Golden Gate Bridge", "San Francisco", 37.8199, -122.4783],
    "times square": ["Times Square", "New York", 40.7580, -73.9855],
    "hollywood sign": ["Hollywood Sign", "Los Angeles", 34.1341, -118.3215],
    "Statue of Liberty": ["Statue of Liberty", "New York", 40.6892, -74.0445],

    # Others
    "machu picchu": ["Machu Picchu", "Peru", -13.1631, -72.5450],
    "christ the redeemer": ["Christ the Redeemer", "Rio de Janeiro", -22.9519, -43.2105],
    "opera house": ["Sydney Opera House", "Sydney", -33.8568, 151.2153],
    "sydney opera house": ["Sydney Opera House", "Sydney", -33.8568, 151.2153],
    "Eiffel Tower": ["Eiffel Tower", "Paris", 48.8584, 2.2945],
    "taj mahal": ["Taj Mahal", "Agra", 27.1751, 78.0421]
}


OVERPASS_URL = "http://overpass-api.de/api/interpreter"

def detect_landmark(image_path: str) -> Optional[str]:
    """
    Use CLIP model to match the image with a predefined list of landmarks.
    Returns the best matched keyword if confidence > 0.2, else None.
    """
    try:
        image = Image.open(image_path).convert("RGB")
        keywords = list(LANDMARK_KEYWORDS.keys())

        inputs = clip_processor(text=keywords, images=image, return_tensors="pt", padding=True)
        with torch.no_grad():
            outputs = clip_model(**inputs)
            probs = outputs.logits_per_image.softmax(dim=1).cpu().numpy().flatten()
        idxs = probs.argsort()[::-1][:top_k]
        print("----- CLIP Top-K Candidates -----")
        for rank, idx in enumerate(idxs, start=1):
            name = keywords[idx]
            score = probs[idx]
            print(f"{rank:>2}. {name:30s} → {score:.4f}")

        best_idx = int(idxs[0])
        best_score=float(probs[best_idx])
        best_name=keywords[best_idx]
        print(f"[CLIP SELECT] {best_name} (score={probs[best_idx]:.4f})")
        return best_name.lower()
        
        # 打印 top_k 调试信息
        topk_idxs = probs.argsort()[-top_k:][::-1]
        print(f"\n[CLIP DEBUG] Best match: {best_name} (score={best_score:.3f})")
        for idx in topk_idxs:
            print(f"    {keywords[idx]:<20} → {probs[idx]:.3f}")

        # 根据阈值决定是否返回
        if best_score >= threshold:
            print(f"[CLIP MATCH] {best_name} ({best_score:.3f})\n")
            return best_name.lower()

        print(f"[CLIP LOW CONFIDENCE] best={best_name} ({best_score:.3f})\n")
    except Exception as e:
        print(f"[CLIP ERROR] {e}")
    return None
        
def query_landmark_coords(landmark_name: str) -> tuple | None:
    """
    Return (lat, lon), source if landmark name is found in predefined list or Overpass API.
    """
    if landmark_name.lower() in LANDMARK_KEYWORDS:
        _, _, lat, lon = LANDMARK_KEYWORDS[landmark_name]
        return (lat, lon), "Predefined"

    query = f"""
    [out:json][timeout:25];
    (
      node["name"~"{landmark_name}",i];
      way["name"~"{landmark_name}",i];
    );
    out center;
    """

    try:
        response = requests.post(OVERPASS_URL, data=query, timeout=15)
        response.raise_for_status() 
        data = response.json()
        if data["elements"]:
            element = data["elements"][0]
            if "center" in element:
                return (element["center"]["lat"], element["center"]["lon"]), "Overpass"
            elif "lat" in element:
                return (element["lat"], element["lon"]), "Overpass"
    except Exception as e:
        print(f"[OVERPASS ERROR] {e}")

    return None, "Not coordinates available"
