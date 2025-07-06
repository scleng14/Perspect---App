
from deepface import DeepFace
import numpy as np

def analyze_emotion(image):
    result = DeepFace.analyze(image, actions=['emotion'], enforce_detection=False)
    dominant = result[0]["dominant_emotion"]
    emotions = result[0]["emotion"]
    return {"dominant_emotion": dominant, "emotion": emotions}
