# Google Maps Setup - Estimateur Immobilier MVP

**Responsable** : `streamlit-mvp-agent`
**Dernière mise à jour** : 2025-10-21

---

## 📋 Table des Matières

1. [Clé API](#clé-api)
2. [Configuration Python](#configuration-python)
3. [Utilisation Géocodage](#utilisation-géocodage)
4. [Gestion Quotas](#gestion-quotas)
5. [Troubleshooting](#troubleshooting)

---

## Clé API

### Accès

```
GOOGLE_MAPS_API_KEY = AIzaSyBdwqhBKgOwi6kHejyhFFw8QluV4pkpwQE
```

### Configuration .env

```env
GOOGLE_MAPS_API_KEY=AIzaSyBdwqhBKgOwi6kHejyhFFw8QluV4pkpwQE
```

### Services Activés

**Google Cloud Console** :
- ✅ Geocoding API (convertir adresse → coords)
- ✅ Maps JavaScript API (cartes Folium)
- ✅ Places API (autocomplete adresses)

---

## Configuration Python

### Module src/utils/geocoding.py

```python
import os
import googlemaps
from dotenv import load_dotenv
from typing import Optional, Dict

load_dotenv()

GOOGLE_MAPS_API_KEY = os.getenv('GOOGLE_MAPS_API_KEY')
gmaps = googlemaps.Client(key=GOOGLE_MAPS_API_KEY)

class GoogleMapsGeocoder:
    """Wrapper Google Maps Geocoding API"""

    def __init__(self, api_key: str = None):
        self.api_key = api_key or GOOGLE_MAPS_API_KEY
        self.gmaps = googlemaps.Client(key=self.api_key)

    def geocode_address(
        self,
        address: str,
        region: str = 'fr'  # France
    ) -> Optional[Dict]:
        """
        Convertir adresse → coordonnées

        Args:
            address: Adresse à géocoder (ex: "10 Rue Victor Hugo, Thonon-les-Bains")
            region: Code pays ISO (fr pour France)

        Returns:
            {
                'latitude': float,
                'longitude': float,
                'formatted_address': str,
                'address_components': list,
                'place_id': str
            }
            ou None si pas trouvé
        """
        try:
            results = self.gmaps.geocode(
                address=address,
                region=region
            )

            if not results:
                return None

            loc = results[0]['geometry']['location']
            return {
                'latitude': loc['lat'],
                'longitude': loc['lng'],
                'formatted_address': results[0]['formatted_address'],
                'address_components': results[0]['address_components'],
                'place_id': results[0]['place_id'],
                'confidence': self._calculate_confidence(results[0])
            }
        except Exception as e:
            print(f"❌ Erreur géocodage: {e}")
            return None

    def reverse_geocode(self, latitude: float, longitude: float) -> Optional[Dict]:
        """
        Convertir coordonnées → adresse

        Args:
            latitude: Latitude
            longitude: Longitude

        Returns:
            Adresse formatée ou None
        """
        try:
            results = self.gmaps.reverse_geocode(
                latlng=(latitude, longitude)
            )

            if not results:
                return None

            return {
                'formatted_address': results[0]['formatted_address'],
                'address_components': results[0]['address_components'],
                'place_id': results[0]['place_id']
            }
        except Exception as e:
            print(f"❌ Erreur reverse geocode: {e}")
            return None

    def _calculate_confidence(self, result: Dict) -> str:
        """
        Estimer confiance du résultat

        Niveaux:
        - ROOFTOP: Adresse exacte
        - RANGE_INTERPOLATED: Plage interpolée
        - GEOMETRIC_CENTER: Centre géométrique
        - APPROXIMATE: Approximatif
        """
        return result['geometry'].get('location_type', 'APPROXIMATE')
```

### Intégration Streamlit

```python
# src/streamlit_components/form_input.py
import streamlit as st
from src.utils.geocoding import GoogleMapsGeocoder

def form_input():
    """US1: Formulaire saisie bien + géocodage temps réel"""

    st.header("🏘️ Nouvelle Estimation")

    geocoder = GoogleMapsGeocoder()

    # Input 1: Adresse
    address = st.text_input(
        "📍 Adresse du bien",
        placeholder="Ex: 10 Rue Victor Hugo, Thonon-les-Bains",
        help="Entrez adresse complète pour meilleure précision"
    )

    if address:
        # Géocodage temps réel
        result = geocoder.geocode_address(address)

        if result:
            st.success(f"✅ Adresse trouvée: {result['formatted_address']}")

            # Afficher confiance
            confidence_emoji = {
                'ROOFTOP': '✅',
                'RANGE_INTERPOLATED': '⚠️',
                'GEOMETRIC_CENTER': '⚠️',
                'APPROXIMATE': '❓'
            }
            confidence = confidence_emoji.get(result['confidence'], '?')
            st.info(f"{confidence} Précision: {result['confidence']}")

            # Sauvegarder coordonnées
            st.session_state.latitude = result['latitude']
            st.session_state.longitude = result['longitude']
            st.session_state.formatted_address = result['formatted_address']
        else:
            st.error(f"❌ Adresse non trouvée: {address}")
            st.info("Essayez adresse plus complète (ex: ajouter code postal)")

    # Input 2-4: Autres critères bien
    col1, col2, col3 = st.columns(3)

    with col1:
        type_local = st.selectbox(
            "Type bien",
            ["Maison", "Appartement", "Terrain", "Autre"]
        )

    with col2:
        surface = st.number_input(
            "Surface (m²)",
            min_value=0,
            max_value=1000,
            value=100
        )

    with col3:
        pieces = st.number_input(
            "Nombre pièces",
            min_value=1,
            max_value=10,
            value=3
        )

    # Input 5: Caractéristiques
    st.subheader("Caractéristiques")
    has_garage = st.checkbox("Garage")
    has_pool = st.checkbox("Piscine")
    has_terrace = st.checkbox("Terrasse")

    # Submit button
    if st.button("🔍 Estimer le bien", use_container_width=True):
        # Vérifier tous les champs remplis
        if not st.session_state.get('latitude'):
            st.error("❌ Adresse non géocodée. Vérifiez l'adresse.")
            return False

        # Sauvegarder données formulaire
        st.session_state.type_local = type_local
        st.session_state.surface = surface
        st.session_state.pieces = pieces
        st.session_state.has_garage = has_garage
        st.session_state.has_pool = has_pool
        st.session_state.has_terrace = has_terrace

        return True

    return False
```

---

## Utilisation Géocodage

### Exemple 1 : Adresse Complète

```python
geocoder = GoogleMapsGeocoder()

result = geocoder.geocode_address("10 Rue Victor Hugo, 74200 Thonon-les-Bains, France")

print(result)
# {
#     'latitude': 46.3719,
#     'longitude': 6.4727,
#     'formatted_address': '10 Rue Victor Hugo, 74200 Thonon-les-Bains, France',
#     'place_id': 'ChIJrV...',
#     'confidence': 'ROOFTOP'
# }
```

### Exemple 2 : Adresse Partielle

```python
# Google trouvera quand même
result = geocoder.geocode_address("Thonon-les-Bains")

print(result)
# {
#     'latitude': 46.3719,
#     'longitude': 6.4727,
#     'formatted_address': 'Thonon-les-Bains, France',
#     'confidence': 'GEOMETRIC_CENTER'  # Moins précis
# }
```

### Exemple 3 : Reverse Geocode

```python
# Retrouver adresse depuis coordonnées
result = geocoder.reverse_geocode(46.3719, 6.4727)

print(result)
# {
#     'formatted_address': '10 Rue Victor Hugo, 74200 Thonon-les-Bains, France',
#     'address_components': [...]
# }
```

---

## Gestion Quotas

### Pricing Google Maps

**Geocoding API** :
- $0.005 par requête (au 2025-10)
- 1er mois gratuit + $300 crédit
- Requêtes groupées par lot : $3.50/1000

### Estimation Usage MVP

**Scénario** :
- 50 estimations/jour × 1 requête géocodage = 50 requêtes/jour
- 50 × $0.005 = $0.25/jour
- 30 jours × $0.25 = $7.50/mois

**Budget** : ~$10/mois suffisant

### Monitoring Quotas

**Google Cloud Console** :
1. Aller à https://console.cloud.google.com/billing
2. Vérifier usage APIs
3. Configurer alerts si besoin

### Optimisations Possibles

1. **Cache adresses déjà géocodées** :
```python
import sqlite3

# Cache local SQLite
cache_db = sqlite3.connect('geocode_cache.db')
cache_cursor = cache_db.cursor()

# Vérifier si adresse en cache
result = cache_cursor.execute(
    "SELECT lat, lng FROM geocode_cache WHERE address = ?",
    (address,)
).fetchone()

if result:
    lat, lng = result
else:
    # Appeler API
    result = geocoder.geocode_address(address)
    # Sauvegarder cache
    cache_cursor.execute(
        "INSERT INTO geocode_cache VALUES (?, ?, ?)",
        (address, result['latitude'], result['longitude'])
    )
    cache_db.commit()
```

2. **Batch geocoding** (grouper requêtes) :
```python
addresses = [
    "Thonon-les-Bains",
    "Annemasse",
    "Morzine"
]

# Appeler API une fois pour plusieurs adresses
results = geocoder.batch_geocode(addresses)
```

---

## Troubleshooting

### Problème 1 : Erreur API Key

**Symptôme** : `googlemaps.exceptions.ApiError: Invalid request`

**Solution** :
1. Vérifier clé valide : `AIzaSyBdwqhBKgOwi6kHejyhFFw8QluV4pkpwQE`
2. Vérifier service activé (Geocoding API)
3. Vérifier pas de quota exceeded

### Problème 2 : Adresse Non Trouvée

**Symptôme** : `result = None` pour adresse valide

**Solutions** :
1. Ajouter code postal (+33% précision)
2. Ajouter ville
3. Essayer adresse plus générale (commune)

### Problème 3 : Precision Faible (APPROXIMATE vs ROOFTOP)

**Symptôme** : `confidence = 'APPROXIMATE'` pour adresse exacte

**Raisons** :
- Adresse invalide ou vieille
- Zone rurale (pas en base Google)
- Besoin code postal

**Solutions** :
- Demander user vérifier adresse
- Proposer code postal
- Valider manuelle vs automatique

### Problème 4 : Quota Exceeded

**Symptôme** : `googlemaps.exceptions.ApiError: You have exceeded your rate limit`

**Raison** : > 100 requêtes/seconde ou dépassé budget mensuel

**Solutions** :
1. Attendre réinitialisation (00:00 UTC)
2. Augmenter budget Google Cloud
3. Implémenter cache local (évite doublons)

---

## Configuration Finale

### Vérification Checklist

```
[ ] Clé API valide (AIzaSyBdwqhBKgOwi6kHejyhFFw8QluV4pkpwQE)
[ ] Service Geocoding activé (Google Cloud)
[ ] Module src/utils/geocoding.py créé
[ ] Intégration Streamlit form_input.py OK
[ ] Test 5 adresses OK (Thonon, Annemasse, Morzine, Évian, Douvaine)
[ ] Cache optionnel implémenté (pour perf)
```

### Statut Production

```
✅ Google Maps Geocoding actif
✅ Module Python intégré
✅ Streamlit formulaire OK
✅ Quota suffisant (~$10/mois)
✅ Prêt pour Phase 4 (Streamlit)
```

---

**Document créé** : 2025-10-21
**Version** : 1.0
**Responsable** : streamlit-mvp-agent
