"""
Preprocessing, scaling, and categorical encoding utilities for the ML pipeline.
"""
from typing import List, Dict, Tuple


def scale_amounts(features: List[List[float]]) -> List[List[float]]:
    """
    Scale the amount field (first element of feature vectors) using min-max scaling.
    
    Returns a new list of features with scaled amounts in [0, 1].
    """
    if not features:
        return []
    
    amounts = [f[0] for f in features]
    min_amount = min(amounts)
    max_amount = max(amounts)
    range_val = max_amount - min_amount if max_amount > min_amount else 1.0
    
    scaled_features = []
    for f in features:
        scaled_amount = (f[0] - min_amount) / range_val
        scaled_features.append([scaled_amount] + f[1:])
        
    return scaled_features


def encode_categories(categories: List[str]) -> Tuple[List[int], Dict[str, int]]:
    """
    Encode categorical strings into numerical labels.
    
    Returns encoded labels and the label-to-index mapping dictionary.
    """
    unique_cats = sorted(list(set(categories)))
    mapping = {cat: idx for idx, cat in enumerate(unique_cats)}
    encoded = [mapping[cat] for cat in categories]
    return encoded, mapping
