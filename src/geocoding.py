from geopy.geocoders import Nominatim
from geopy.exc import GeocoderTimedOut
import json
from pathlib import Path
import time

CACHE_FILE = Path("data/cache/geocoding_cache.json")

def load_cache():
    """Charge le cache de géocodage"""
    if CACHE_FILE.exists():
        with open(CACHE_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    return {}

def save_cache(cache):
    """Sauvegarde le cache"""
    CACHE_FILE.parent.mkdir(parents=True, exist_ok=True)
    with open(CACHE_FILE, 'w', encoding='utf-8') as f:
        json.dump(cache, f, ensure_ascii=False, indent=2)

def geocode_address(address):
    """
    Géocode une adresse en coordonnées GPS
    
    Args:
        address: Adresse à géocoder
        
    Returns:
        dict: {'lat': float, 'lon': float, 'display_name': str} ou None
    """
    # Normalisation
    address_key = address.strip().lower()
    
    # Vérification cache
    cache = load_cache()
    if address_key in cache:
        print(f"📍 Adresse trouvée en cache")
        return cache[address_key]
    
    # Géocodage
    print(f"🔍 Géocodage de : {address}")
    try:
        geolocator = Nominatim(
            user_agent="estimation_immobiliere_74_v1",
            timeout=10
        )
        
        # Recherche avec contexte Haute-Savoie
        search_queries = [
            f"{address}, Haute-Savoie, France",
            f"{address}, 74, France",
            f"{address}, France"
        ]
        
        location = None
        for query in search_queries:
            location = geolocator.geocode(query, exactly_one=True)
            if location:
                break
            time.sleep(1)
        
        if location:
            result = {
                'lat': location.latitude,
                'lon': location.longitude,
                'display_name': location.address
            }
            
            # Sauvegarde en cache
            cache[address_key] = result
            save_cache(cache)
            
            print(f"✅ Trouvé : {location.address}")
            return result
        else:
            print("❌ Adresse non trouvée")
            return None
            
    except GeocoderTimedOut:
        print("⏱️ Timeout du géocodeur")
        return None
    except Exception as e:
        print(f"❌ Erreur : {str(e)}")
        return None