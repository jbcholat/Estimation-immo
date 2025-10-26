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

load_dotenv()


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
            DataFrame avec colonnes: idmutation, datemut, valeurfonc, sbati, distance_km, libnatmut
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
                        libnatmut,
                        nblocmut,
                        ST_AsText(geomlocmut) as geom_text
                    FROM dvf_plus_2025_2.dvf_plus_mutation
                    WHERE sbati >= :surface_min
                      AND sbati <= :surface_max
                      AND valeurfonc > 0
                      AND datemut IS NOT NULL
                      AND geomlocmut IS NOT NULL
                    ORDER BY datemut DESC
                    LIMIT :limit
                """)

                result = conn.execute(query, {
                    'surface_min': surface_min,
                    'surface_max': surface_max,
                    'limit': limit
                })

                rows = result.fetchall()
                columns = result.keys()

                df = pd.DataFrame(rows, columns=columns)

                if len(df) > 0:
                    # Parser "POINT(X Y)" de ST_AsText et convertir Lambert 93 → WGS84
                    import re
                    def parse_point(geom_text):
                        match = re.search(r'POINT\(([\d.]+)\s+([\d.]+)\)', geom_text)
                        if match:
                            x, y = float(match.group(1)), float(match.group(2))
                            return pd.Series(self._lambert93_to_wgs84(x, y))
                        return pd.Series([None, None])

                    df[['latitude', 'longitude']] = df.apply(
                        lambda row: parse_point(row['geom_text']),
                        axis=1
                    )

                    # Calculer distance Haversine avec coordonnées réelles
                    df['distance_km'] = df.apply(
                        lambda row: self._haversine_distance(latitude, longitude, row['latitude'], row['longitude']),
                        axis=1
                    )

                    # Trier par distance
                    df = df.sort_values('distance_km')

                return df

        except Exception as e:
            print(f"[ERROR] Erreur get_comparables: {e}")
            return pd.DataFrame()

    def _lambert93_to_wgs84(self, x: float, y: float) -> tuple:
        """
        Convertit coordonnées Lambert 93 (EPSG:2154) → WGS84 (EPSG:4326)
        Utilise formule approximative Mollweide (suffisante pour Chablais)
        """
        import math

        # Paramètres Lambert 93
        n = 0.7256077650532670
        C = 11563377.45
        X_c = 700000.0
        Y_c = 12655612.05
        lat0 = 46.5  # latitude origine
        lon0 = 3.0   # longitude origine

        # Inverse Lambert 93 → lat/lon (approximatif)
        rho = math.sqrt((x - X_c)**2 + (y - Y_c)**2)
        lat_iso = -1.0/n * math.log(rho / C)

        # Conformal latitude → géographique (itération)
        lat_rad = 2 * math.atan(math.exp(lat_iso)) - math.pi/2
        lat_deg = math.degrees(lat_rad)

        # Longitude approximative
        lon_deg = lon0 + math.degrees(math.atan2(x - X_c, y - Y_c)) / n

        return (lat_deg, lon_deg)

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
