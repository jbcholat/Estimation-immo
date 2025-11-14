#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
SupabaseDataRetriever - Classe pour récupérer données DVF+ depuis Supabase
Phase 2 - Data Retrieval
"""

import os
from typing import List, Dict, Optional
import pandas as pd
from sqlalchemy import create_engine, text
from dotenv import load_dotenv
from pyproj import Transformer

load_dotenv()

# Initialize Lambert93 to WGS84 transformer globally
_TRANSFORMER_2154_4326 = Transformer.from_crs('EPSG:2154', 'EPSG:4326')


class SupabaseDataRetriever:
    """
    Classe spécialisée pour récupérer les données DVF+ depuis Supabase
    Utilise PostgreSQL direct avec PostGIS pour requêtes géospatiales.
    """

    def __init__(self):
        """Initialise la connexion à Supabase"""
        self.db_password = os.getenv("SUPABASE_DB_PASSWORD")
        self.db_url = f"postgresql+psycopg2://postgres:{self.db_password}@db.fwcuftkjofoxyjbjzdnh.supabase.co:5432/postgres"
        self.engine = create_engine(self.db_url, echo=False)

    def get_comparables(
        self,
        latitude: float,
        longitude: float,
        type_bien: str = "Appartement",
        surface_min: float = 50,
        surface_max: float = 150,
        rayon_km: float = 10.0,
        annees: int = 3,
        limit: int = 30
    ) -> pd.DataFrame:
        """
        Récupère les comparables (mutations similaires) pour une adresse donnée.

        Args:
            latitude: Latitude WGS84
            longitude: Longitude WGS84
            type_bien: Type de bien ('Appartement' ou 'Maison')
            surface_min: Surface minimale en m²
            surface_max: Surface maximale en m²
            rayon_km: Rayon de recherche en kilomètres
            annees: Nombre d'années historique à considérer
            limit: Nombre maximal de résultats

        Returns:
            DataFrame avec colonnes: idmutation, datemut, valeurfonc, sbati, distance_km, libtypbien
        """

        try:
            with self.engine.connect() as conn:
                # Requête basée sur le schéma DVF+ réel (dvf_plus_2025_2.dvf_plus_mutation)
                # geomlocmut est en Lambert 93 (EPSG:2154), utilise ST_AsText pour parsing
                query = text("""
                    SELECT
                        idmutation,
                        datemut,
                        valeurfonc,
                        sbati,
                        coddep,
                        libtypbien,
                        nblocmut,
                        ST_AsText(geomlocmut) as geom_text
                    FROM dvf_plus_2025_2.dvf_plus_mutation
                    WHERE sbati >= :surface_min
                      AND sbati <= :surface_max
                      AND valeurfonc > 0
                      AND datemut IS NOT NULL
                      AND geomlocmut IS NOT NULL
                      AND datemut >= CURRENT_DATE - (:annees * 365)::integer * INTERVAL '1 day'
                      AND (libtypbien LIKE :type_pattern OR libtypbien LIKE :type_pattern2)
                    ORDER BY datemut DESC
                    LIMIT :limit
                """)

                # Build type filter patterns
                type_patterns = {
                    "Appartement": ("%APPARTEMENT%", "%STUDIO%"),
                    "Maison": ("%MAISON%", "%VILLA%"),
                    "Terrain": ("%TERRAIN%", "%PARCELLE%")
                }

                if type_bien in type_patterns:
                    type_pattern, type_pattern2 = type_patterns[type_bien]
                else:
                    type_pattern, type_pattern2 = ("%", "%")

                result = conn.execute(query, {
                    'surface_min': surface_min,
                    'surface_max': surface_max,
                    'limit': limit,
                    'annees': annees,
                    'type_pattern': type_pattern,
                    'type_pattern2': type_pattern2
                })

                rows = result.fetchall()
                columns = result.keys()

                df = pd.DataFrame(rows, columns=columns)

                if len(df) > 0:
                    # Convertir TOUTES les colonnes Decimal en float
                    from decimal import Decimal
                    for col in df.columns:
                        if col not in ['idmutation', 'coddep', 'libtypbien', 'geom_text', 'datemut']:
                            try:
                                # Convert Decimal and numeric types to float
                                df[col] = df[col].apply(lambda x: float(x) if x is not None else None)
                            except:
                                pass  # Laisser les colonnes non-numériques

                    # Parser "POINT(X Y)" de ST_AsText et convertir Lambert 93 → WGS84
                    import re
                    def parse_and_convert(geom_text):
                        """Parse POINT geometry et convertit Lambert93→WGS84"""
                        try:
                            match = re.search(r'POINT\(([\d.]+)\s+([\d.]+)\)', geom_text)
                            if match:
                                x_lambert = float(match.group(1))
                                y_lambert = float(match.group(2))
                                lat, lon = self._lambert93_to_wgs84_simple(x_lambert, y_lambert)
                                return lat, lon
                        except:
                            pass
                        return None, None

                    df[['latitude', 'longitude']] = df['geom_text'].apply(
                        lambda x: pd.Series(parse_and_convert(x))
                    )

                    # Filtrer les lignes où conversion a échoué
                    df = df.dropna(subset=['latitude'])

                    # Convertir Decimal à float pour coordonnées
                    for col in ['latitude', 'longitude']:
                        if col in df.columns:
                            df[col] = df[col].astype(float)

                    # Calculer distance Haversine avec coordonnées WGS84
                    df['distance_km'] = df.apply(
                        lambda row: self._haversine_distance(latitude, longitude, row['latitude'], row['longitude']),
                        axis=1
                    )

                    # Trier par distance
                    df = df.sort_values('distance_km').reset_index(drop=True)

                    # Formatter la date
                    if 'datemut' in df.columns:
                        df['datemut'] = pd.to_datetime(df['datemut']).dt.strftime('%d/%m/%Y')

                    # Calculer prix au m²
                    df['prix_m2'] = df['valeurfonc'] / df['sbati']

                    # Ajouter adresses via reverse geocoding
                    try:
                        from src.utils.geocoding import reverse_geocode
                        addresses = []
                        for idx, row in df.iterrows():
                            addr = reverse_geocode(row['latitude'], row['longitude'])
                            addresses.append(addr if addr else f"({row['latitude']:.4f}, {row['longitude']:.4f})")
                        df['adresse'] = addresses
                    except Exception as e:
                        print(f"[WARNING] Erreur reverse geocoding: {e}")
                        # Fallback: utiliser coordonnées
                        df['adresse'] = df.apply(
                            lambda row: f"({row['latitude']:.4f}, {row['longitude']:.4f})",
                            axis=1
                        )

                return df

        except Exception as e:
            print(f"[ERROR] Erreur get_comparables: {e}")
            return pd.DataFrame()

    def _lambert93_to_wgs84_simple(self, x: float, y: float) -> tuple:
        """
        Convertit coordonnées Lambert 93 (EPSG:2154) → WGS84 (EPSG:4326)
        Utilise pyproj pour une conversion exacte
        """
        try:
            lat, lon = _TRANSFORMER_2154_4326.transform(x, y)
            return (lat, lon)
        except Exception as e:
            logger.error(f"[ERROR] Conversion Lambert93: {str(e)}")
            return (None, None)

    def _lambert93_to_wgs84(self, x: float, y: float) -> tuple:
        """Alias pour compatibilité"""
        return self._lambert93_to_wgs84_simple(x, y)

    def _haversine_distance(self, lat1: float, lon1: float, lat2: float, lon2: float) -> float:
        """
        Calcule la distance en km entre deux points (lat/lon).
        Formule de Haversine simplifiée.
        """
        from math import radians, sin, cos, sqrt, atan2

        R = 6371  # Rayon Terre en km

        lat1, lon1, lat2, lon2 = map(radians, [lat1, lon1, lat2, lon2])
        dlat = lat2 - lat1
        dlon = lon2 - lon1

        a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
        c = 2 * atan2(sqrt(a), sqrt(1-a))

        return R * c

    def get_market_stats(self, code_postal: str) -> Dict:
        """
        Retourne statistiques de marché pour un code postal.

        Args:
            code_postal: Code postal (ex: '74100')

        Returns:
            Dict avec: prix_median, nombre_transactions, surface_moyenne
        """

        try:
            with self.engine.connect() as conn:
                query = text("""
                    SELECT
                        COUNT(*) as nb_transactions,
                        AVG(valeurfonc) as prix_moyen,
                        PERCENTILE_CONT(0.5) WITHIN GROUP (ORDER BY valeurfonc) as prix_median,
                        AVG(sbati) as surface_moyenne,
                        MIN(datemut) as date_premiere_vente,
                        MAX(datemut) as date_derniere_vente
                    FROM dvf_plus_2025_2.dvf_plus_mutation
                    WHERE coddep LIKE :code_postal
                """)

                result = conn.execute(query, {'code_postal': code_postal[:2] + '%'})
                row = result.fetchone()

                if row:
                    return {
                        'nb_transactions': row[0],
                        'prix_moyen': float(row[1]) if row[1] else 0,
                        'prix_median': float(row[2]) if row[2] else 0,
                        'surface_moyenne': float(row[3]) if row[3] else 0,
                        'date_premiere_vente': str(row[4]),
                        'date_derniere_vente': str(row[5])
                    }
                else:
                    return {}

        except Exception as e:
            print(f"[ERROR] Erreur get_market_stats: {e}")
            return {}

    def test_connection(self) -> bool:
        """Test la connexion à la base de données"""

        try:
            with self.engine.connect() as conn:
                result = conn.execute(text("SELECT COUNT(*) FROM dvf_plus_2025_2.dvf_plus_mutation"))
                count = result.scalar()
                print(f"[OK] Connexion OK - {count} mutations dans Supabase")
                return True
        except Exception as e:
            print(f"[ERROR] Erreur connexion: {e}")
            return False


if __name__ == "__main__":
    # Test
    retriever = SupabaseDataRetriever()
    retriever.test_connection()

    # Test get_comparables
    print("\n[INFO] Recherche comparables pour Thonon-les-Bains (Appartement 50-100m2)...")
    comparables = retriever.get_comparables(
        latitude=46.3719,
        longitude=6.4727,
        type_bien="Appartement",
        surface_min=50,
        surface_max=100,
        limit=10
    )

    if len(comparables) > 0:
        print(f"\n[OK] Trouve {len(comparables)} comparables:")
        print(comparables[['idmutation', 'datemut', 'valeurfonc', 'sbati', 'distance_km']].head())
    else:
        print("\n[WARNING] Aucun comparable trouve")

    # Test get_market_stats
    print("\n[INFO] Statistiques Thonon-les-Bains...")
    stats = retriever.get_market_stats('74200')
    if stats:
        print(f"   Transactions: {stats.get('nb_transactions', 0)}")
        print(f"   Prix médian: {stats.get('prix_median', 0):,.0f}€")
        print(f"   Surface moyenne: {stats.get('surface_moyenne', 0):.1f}m²")
