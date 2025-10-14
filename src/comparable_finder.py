import pandas as pd
import numpy as np
from datetime import datetime, timedelta

def haversine_distance(lat1, lon1, lat2, lon2):
    """Calcule la distance en km entre deux points GPS"""
    R = 6371  # Rayon Terre en km
    
    lat1, lon1, lat2, lon2 = map(np.radians, [lat1, lon1, lat2, lon2])
    dlat = lat2 - lat1
    dlon = lon2 - lon1
    
    a = np.sin(dlat/2)**2 + np.cos(lat1) * np.cos(lat2) * np.sin(dlon/2)**2
    c = 2 * np.arcsin(np.sqrt(a))
    
    return R * c

def find_comparables(
    df,
    target_lat,
    target_lon,
    property_type,
    surface,
    nb_pieces=None,
    anciennete='ancien',
    max_radius_km=10,
    max_age_months=24,
    surface_tolerance=0.25
):
    """
    Trouve les biens comparables selon méthodologie DV3F
    
    Args:
        df: DataFrame des transactions
        target_lat, target_lon: Coordonnées du bien
        property_type: 'Appartement' ou 'Maison'
        surface: Surface en m²
        nb_pieces: 'T1', 'T2', 'T3', 'T4', 'T5+' (pour appartements)
        anciennete: 'neuf', 'recent', 'ancien'
        max_radius_km: Rayon max de recherche
        max_age_months: Ancienneté max des transactions
        surface_tolerance: Tolérance sur la surface (0.25 = ±25%)
        
    Returns:
        pd.DataFrame: Biens comparables triés par pertinence
    """
    print(f"\n🔍 Recherche de comparables...")
    print(f"   Type : {property_type}")
    print(f"   Surface : {surface} m²")
    if nb_pieces:
        print(f"   Pièces : {nb_pieces}")
    print(f"   Ancienneté : {anciennete}")
    
    # Copie du DataFrame
    df_search = df.copy()
    
    # 1. Calcul des distances
    print(f"\n   📏 Calcul des distances...")
    df_search['distance_km'] = df_search.apply(
        lambda row: haversine_distance(
            target_lat, target_lon,
            row['geompar_y'], row['geompar_x']
        ),
        axis=1
    )
    
    # 2. Filtre rayon
    df_search = df_search[df_search['distance_km'] <= max_radius_km]
    print(f"   ✓ {len(df_search)} biens dans rayon {max_radius_km} km")
    
    # 3. Filtre date
    cutoff_date = datetime.now() - timedelta(days=30*max_age_months)
    df_search = df_search[df_search['datemut'] >= cutoff_date]
    print(f"   ✓ {len(df_search)} biens < {max_age_months} mois")
    
    # 4. Filtre type de bien
    if property_type == 'Appartement':
        df_search = df_search[df_search['nblocapt'] > 0]
        
        # Filtre nombre de pièces selon codtypbien
        if nb_pieces:
            code_pieces = nb_pieces[1]  # 'T3' -> '3'
            df_search = df_search[
                df_search['codtypbien'].str.contains(f'121.{code_pieces}', na=False)
            ]
            print(f"   ✓ {len(df_search)} appartements {nb_pieces}")
        else:
            print(f"   ✓ {len(df_search)} appartements")
            
    else:  # Maison
        df_search = df_search[df_search['nblocmai'] > 0]
        print(f"   ✓ {len(df_search)} maisons")
    
    # 5. Filtre ancienneté si spécifié
    if anciennete and anciennete != 'tous':
        if anciennete == 'neuf':
            df_search = df_search[df_search['nblocneuf'] > 0]
        elif anciennete == 'recent':
            df_search = df_search[df_search['nblocrecen'] > 0]
        elif anciennete == 'ancien':
            df_search = df_search[df_search['nblocanc'] > 0]
        print(f"   ✓ {len(df_search)} biens {anciennete}s")
    
    # 6. Filtre surface
    surface_min = surface * (1 - surface_tolerance)
    surface_max = surface * (1 + surface_tolerance)
    
    df_search = df_search[
        (df_search['sbati'] >= surface_min) &
        (df_search['sbati'] <= surface_max)
    ]
    print(f"   ✓ {len(df_search)} biens avec surface {surface_min:.0f}-{surface_max:.0f} m²")
    
    if len(df_search) == 0:
        print(f"\n❌ Aucun comparable trouvé avec ces critères")
        return df_search
    
    # 7. Calcul du score de pertinence
    df_search['score_distance'] = 100 * (1 - df_search['distance_km'] / max_radius_km)
    
    df_search['score_date'] = 100 * (
        1 - (datetime.now() - df_search['datemut']).dt.days / (max_age_months * 30)
    )
    
    df_search['score_surface'] = 100 * (
        1 - abs(df_search['sbati'] - surface) / surface
    )
    
    df_search['score_total'] = (
        df_search['score_distance'] * 0.4 +
        df_search['score_date'] * 0.3 +
        df_search['score_surface'] * 0.3
    )
    
    # Tri par score
    df_search = df_search.sort_values('score_total', ascending=False)
    
    print(f"\n✅ {len(df_search)} comparables trouvés")
    print(f"   Distance moyenne : {df_search['distance_km'].mean():.1f} km")
    print(f"   Prix médian : {df_search['valeurfonc'].median():,.0f} €")
    
    return df_search