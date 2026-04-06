import os
import json
import hashlib
from typing import Any, Optional


CACHE_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "cached")

def get_cache_path(category: str, identifier: str) -> str:
    """Get the full path to a cache file"""
    cat_dir = os.path.join(CACHE_DIR, category)
    os.makedirs(cat_dir, exist_ok=True)
    
    file_hash = hashlib.md5(identifier.encode('utf-8')).hexdigest()
    return os.path.join(cat_dir, f"{file_hash}.json")


def get_cached_data(category: str, identifier: str) -> Optional[Any]:
    cache_path = get_cache_path(category, identifier)
    if os.path.exists(cache_path):
        with open(cache_path, 'r', encoding='utf-8') as f:
            print(f"found cached data in {category}/{os.path.basename(cache_path)}")
            return json.load(f)
    return None


def save_to_cache(category: str, identifier: str, data: Any):
    cache_path = get_cache_path(category, identifier)
    with open(cache_path, 'w', encoding='utf-8') as f:
        print(f"caching data in {category}/{os.path.basename(cache_path)}")
        json.dump(data, f, indent=4)
