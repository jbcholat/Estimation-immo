#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Wrapper Google Maps Geocoding API
Phase 4 - Streamlit MVP
"""

from typing import List, Dict, Optional, Tuple
import googlemaps
import logging

from .config import Config

logger = logging.getLogger(__name__)


class GeocodingService:
    """Service de géocodage avec wrapper Google Maps"""

    def __init__(self):
        """Initialise le client Google Maps"""
        if not Config.GOOGLE_MAPS_API_KEY:
            logger.error("❌ GOOGLE_MAPS_API_KEY non configurée")
            self.client = None
        else:
            self.client = googlemaps.Client(key=Config.GOOGLE_MAPS_API_KEY)
            logger.info("✅ Google Maps client initialisé")

    def geocode_address(self, address: str) -> List[Dict]:
        """
        Géocode une adresse et retourne liste de suggestions.

        Args:
            address: Adresse à géocoder (ex: "Thonon-les-Bains, 74200")

        Returns:
            Liste de dictionnaires avec keys:
            - 'formatted_address': Adresse formatée
            - 'latitude': Latitude WGS84
            - 'longitude': Longitude WGS84
            - 'place_id': Google Place ID
        """
        if not self.client:
            logger.error("❌ Client Google Maps non initialisé")
            return []

        try:
            results = self.client.geocode(address=address)

            if not results:
                logger.warning(f"⚠️ Aucun résultat pour: {address}")
                return []

            suggestions = []
            for result in results:
                location = result['geometry']['location']
                suggestion = {
                    'formatted_address': result['formatted_address'],
                    'latitude': location['lat'],
                    'longitude': location['lng'],
                    'place_id': result.get('place_id', ''),
                }
                suggestions.append(suggestion)

            logger.info(f"✅ {len(suggestions)} suggestion(s) trouvée(s) pour: {address}")
            return suggestions

        except googlemaps.exceptions.ApiError as e:
            logger.error(f"❌ Erreur API Google Maps: {e}")
            return []
        except Exception as e:
            logger.error(f"❌ Erreur géocodage: {e}")
            return []

    def get_coordinates(self, address: str) -> Optional[Tuple[float, float]]:
        """
        Retourne coordonnées (lat, lon) pour une adresse.
        Utilise le premier résultat si plusieurs suggestions.

        Args:
            address: Adresse à géocoder

        Returns:
            Tuple (latitude, longitude) ou None si erreur
        """
        suggestions = self.geocode_address(address)

        if not suggestions:
            return None

        first = suggestions[0]
        return (first['latitude'], first['longitude'])

    def get_best_match(self, address: str, zone_filter: Optional[str] = None) -> Optional[Dict]:
        """
        Retourne la meilleure suggestion pour une adresse.
        Optionnellement filtre par zone géographique.

        Args:
            address: Adresse à géocoder
            zone_filter: Filtre optionnel (ex: "74100" pour Thonon)

        Returns:
            Dict avec formatted_address, latitude, longitude ou None
        """
        suggestions = self.geocode_address(address)

        if not suggestions:
            return None

        # Si zone_filter, chercher correspondance
        if zone_filter:
            for suggestion in suggestions:
                if zone_filter in suggestion['formatted_address']:
                    return suggestion

        # Sinon retourner premier résultat
        return suggestions[0]


# Instance globale
_geocoding_service: Optional[GeocodingService] = None


def get_geocoding_service() -> GeocodingService:
    """Retourne instance singleton GeocodingService (pour cache Streamlit)"""
    global _geocoding_service
    if _geocoding_service is None:
        _geocoding_service = GeocodingService()
    return _geocoding_service


def geocode_address(address: str) -> List[Dict]:
    """Wrapper pour géocoder une adresse"""
    service = get_geocoding_service()
    return service.geocode_address(address)


def get_coordinates(address: str) -> Optional[Tuple[float, float]]:
    """Wrapper pour obtenir coordonnées (lat, lon)"""
    service = get_geocoding_service()
    return service.get_coordinates(address)


def get_best_match(address: str, zone_filter: Optional[str] = None) -> Optional[Dict]:
    """Wrapper pour obtenir meilleure suggestion"""
    service = get_geocoding_service()
    return service.get_best_match(address, zone_filter)


if __name__ == "__main__":
    # Test
    logging.basicConfig(level=logging.INFO)

    print("🧪 Test géocodage...")
    suggestions = geocode_address("Thonon-les-Bains, 74200")
    print(f"Suggestions: {suggestions}")

    coords = get_coordinates("Évian-les-Bains")
    print(f"Coordonnées: {coords}")

    best = get_best_match("Annemasse", zone_filter="74100")
    print(f"Meilleur match: {best}")
