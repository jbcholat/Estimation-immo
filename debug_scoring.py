#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Debug Scoring - Script de diagnostic pour analyser les scores en detail
Recupere comparables reels et affiche composantes de scoring
"""

import os
import sys
from datetime import datetime
from dotenv import load_dotenv

# Add src to path
sys.path.insert(0, os.path.dirname(__file__))

from src.supabase_data_retriever import SupabaseDataRetriever
from src.estimation_algorithm import SimilarityScorer
import math

load_dotenv()

def debug_comparable_scores():
    """Debug les scores pour les comparables trouves"""

    print("\n" + "="*100)
    print("DEBUG SCORING - Analyse des comparables pour Thonon-les-Bains (Appartement 100m2)")
    print("="*100)

    # Target property
    target_lat = 46.3719
    target_lon = 6.4727
    target_surface = 100.0
    target_type = "Appartement"

    # Get comparables from Supabase
    print("\n[1] Recuperation des comparables depuis Supabase...")
    retriever = SupabaseDataRetriever()

    comparables_df = retriever.get_comparables(
        latitude=target_lat,
        longitude=target_lon,
        type_bien=target_type,
        surface_min=80,
        surface_max=120,
        rayon_km=10.0,
        limit=50
    )

    print(f"    [OK] {len(comparables_df)} comparables trouves")

    if len(comparables_df) == 0:
        print("    [ERROR] Aucun comparable trouve!")
        return

    # Display columns
    print(f"\n[2] Colonnes disponibles dans le DataFrame:")
    for col in comparables_df.columns:
        print(f"      - {col}")

    # Analyze first 5 comparables in detail
    print(f"\n[3] Analyse detaillee des 5 premiers comparables:")
    print("-" * 100)

    scores_list = []

    for idx, row in comparables_df.head(5).iterrows():
        print(f"\n  COMPARABLE #{idx + 1}")
        print(f"  " + "-" * 96)

        # Get values
        comp_lat = row.get('latitude')
        comp_lon = row.get('longitude')
        comp_surface = row.get('sbati')
        comp_type = row.get('libtypbien', 'UNKNOWN')
        comp_date = row.get('datemut')
        comp_price = row.get('valeurfonc')
        comp_distance = row.get('distance_km')

        print(f"  ID Mutation: {row.get('idmutation')}")
        print(f"  Prix: {comp_price:,.0f} EUR | Surface: {comp_surface}m2 | Type: {comp_type}")
        print(f"  Date: {comp_date} | Distance: {comp_distance:.2f}km")

        # Calculate individual scores
        print(f"\n  SCORING BREAKDOWN:")

        # Distance score
        distance_score = SimilarityScorer.score_distance(comp_distance)
        print(f"    Distance ({comp_distance:.2f}km):")
        print(f"      Formula: 100 * exp(-0.3 * {comp_distance:.2f}) = {distance_score:.1f}")
        print(f"      Weight: 25% | Contribution: {distance_score * 0.25:.1f}")

        # Surface score
        if comp_surface and comp_surface > 0:
            ratio = comp_surface / target_surface
            tolerance = 0.20
            in_tolerance = (1 - tolerance <= ratio <= 1 + tolerance)
            if in_tolerance:
                deviation = abs(ratio - 1)
                surface_score = 100 * (1 - deviation / tolerance)
            else:
                surface_score = 0

            print(f"\n    Surface ({comp_surface}m2 vs {target_surface}m2):")
            print(f"      Ratio: {comp_surface}/{target_surface} = {ratio:.2f}")
            print(f"      Range [0.80-1.20] (+-20%): {in_tolerance}")
            print(f"      Score: {surface_score:.1f}")
            print(f"      Weight: 25% | Contribution: {surface_score * 0.25:.1f}")
        else:
            surface_score = 0
            print(f"\n    Surface: INVALID ({comp_surface})")

        # Type score
        normalized_type = SimilarityScorer._normalize_property_type(comp_type)
        type_score = SimilarityScorer.score_type(target_type, normalized_type)
        print(f"\n    Type ('{target_type}' vs '{comp_type}'):")
        print(f"      Normalized: '{normalized_type}'")
        print(f"      Score: {type_score:.1f}")
        print(f"      Weight: 25% | Contribution: {type_score * 0.25:.1f}")

        # Recency score
        anciennete_score = SimilarityScorer.score_anciennete(comp_date)
        print(f"\n    Anciennete (Date: {comp_date}):")
        print(f"      Score: {anciennete_score:.1f}")
        print(f"      Weight: 25% | Contribution: {anciennete_score * 0.25:.1f}")

        # Total score
        total_score = (
            distance_score * 0.25 +
            surface_score * 0.25 +
            type_score * 0.25 +
            anciennete_score * 0.25
        )

        print(f"\n  TOTAL SCORE: {total_score:.1f} (Threshold: >= 40)")
        if total_score >= 40:
            print(f"  [PASS] PASSE LE SEUIL")
        else:
            print(f"  [FAIL] ECHOUE LE SEUIL")

        scores_list.append({
            'distance_score': distance_score,
            'surface_score': surface_score,
            'type_score': type_score,
            'anciennete_score': anciennete_score,
            'total_score': total_score
        })

    # Summary statistics
    print("\n" + "="*100)
    print("RESUME STATISTIQUE")
    print("="*100)

    if scores_list:
        distances = [s['distance_score'] for s in scores_list]
        surfaces = [s['surface_score'] for s in scores_list]
        types = [s['type_score'] for s in scores_list]
        anciennetes = [s['anciennete_score'] for s in scores_list]
        totals = [s['total_score'] for s in scores_list]

        print(f"\nDistance scores:    Min={min(distances):.1f}, Max={max(distances):.1f}, Avg={sum(distances)/len(distances):.1f}")
        print(f"Surface scores:     Min={min(surfaces):.1f}, Max={max(surfaces):.1f}, Avg={sum(surfaces)/len(surfaces):.1f}")
        print(f"Type scores:        Min={min(types):.1f}, Max={max(types):.1f}, Avg={sum(types)/len(types):.1f}")
        print(f"Anciennete scores:  Min={min(anciennetes):.1f}, Max={max(anciennetes):.1f}, Avg={sum(anciennetes)/len(anciennetes):.1f}")
        print(f"Total scores:       Min={min(totals):.1f}, Max={max(totals):.1f}, Avg={sum(totals)/len(totals):.1f}")

        passing = sum(1 for t in totals if t >= 40)
        print(f"\n{passing}/{len(totals)} comparables passent le seuil (>= 40)")

    print("\n" + "="*100)

if __name__ == "__main__":
    debug_comparable_scores()
