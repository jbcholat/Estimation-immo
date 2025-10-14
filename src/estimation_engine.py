import pandas as pd
import numpy as np

def estimate_property(comparables, target_surface):
    """
    Calcule l'estimation du bien selon méthodologie immobilière
    
    Args:
        comparables: DataFrame des biens comparables
        target_surface: Surface du bien à estimer
        
    Returns:
        dict: Résultats de l'estimation
    """
    if len(comparables) == 0:
        return None
    
    print(f"\n💰 Calcul de l'estimation...")
    
    # Statistiques sur les prix
    prix_median = comparables['valeurfonc'].median()
    prix_q1 = comparables['valeurfonc'].quantile(0.25)
    prix_q3 = comparables['valeurfonc'].quantile(0.75)
    prix_mean = comparables['valeurfonc'].mean()
    
    # Statistiques sur les prix au m²
    prix_m2_median = comparables['prix_m2'].median()
    prix_m2_q1 = comparables['prix_m2'].quantile(0.25)
    prix_m2_q3 = comparables['prix_m2'].quantile(0.75)
    
    # Méthode 1 : Estimation par prix au m² médian
    estimation_prix_m2 = target_surface * prix_m2_median
    
    # Méthode 2 : Ajustement par effet de taille
    # Le prix au m² diminue généralement avec la surface
    surface_median_comparables = comparables['sbati'].median()
    ratio_surface = target_surface / surface_median_comparables
    
    # Facteur d'ajustement progressif
    if ratio_surface > 1:
        # Bien plus grand : prix au m² diminue
        ajustement = 1 - (ratio_surface - 1) * 0.05
    else:
        # Bien plus petit : prix au m² augmente
        ajustement = 1 + (1 - ratio_surface) * 0.05
    
    ajustement = max(0.85, min(1.15, ajustement))  # Limite l'ajustement à ±15%
    
    estimation_ajustee = estimation_prix_m2 * ajustement
    
    # Calcul de la confiance
    nb_comparables = len(comparables)
    
    # Facteurs de confiance
    conf_nombre = min(100, nb_comparables * 5)  # 20 comparables = 100%
    
    # Dispersion des prix (coefficient de variation)
    cv = comparables['prix_m2'].std() / comparables['prix_m2'].mean()
    conf_dispersion = max(0, 100 - cv * 100)  # Plus c'est dispersé, moins c'est fiable
    
    # Distance moyenne
    dist_moyenne = comparables['distance_km'].mean()
    conf_distance = max(0, 100 - dist_moyenne * 10)  # -10% par km
    
    # Confiance globale (moyenne pondérée)
    confidence = (
        conf_nombre * 0.5 +
        conf_dispersion * 0.3 +
        conf_distance * 0.2
    )
    
    print(f"   ✓ Prix estimé : {int(estimation_ajustee):,} €")
    print(f"   ✓ Fourchette : {int(prix_q1):,} - {int(prix_q3):,} €")
    print(f"   ✓ Confiance : {int(confidence)}%")
    
    return {
        'median_price': int(estimation_ajustee),
        'q1_price': int(target_surface * prix_m2_q1),
        'q3_price': int(target_surface * prix_m2_q3),
        'price_per_sqm': int(prix_m2_median),
        'price_per_sqm_q1': int(prix_m2_q1),
        'price_per_sqm_q3': int(prix_m2_q3),
        'nb_comparables': nb_comparables,
        'confidence': int(confidence),
        'prix_min': int(comparables['valeurfonc'].min()),
        'prix_max': int(comparables['valeurfonc'].max()),
        'surface_median_comparables': int(surface_median_comparables),
        'distance_moyenne': round(dist_moyenne, 1)
    }