#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script simple de validation Phase 3 - Test EstimationAlgorithm
"""

import sys
import os

# Fix encoding
os.environ['PYTHONIOENCODING'] = 'utf-8'
sys.stdout.reconfigure(encoding='utf-8', errors='ignore')

sys.path.insert(0, '/c/analyse_immobiliere')

from src.supabase_data_retriever import SupabaseDataRetriever
from src.estimation_algorithm import EstimationAlgorithm


def test_thonon():
    """Test 1: Thonon-les-Bains"""
    print("\n[TEST 1] Thonon-les-Bains - Appartement")
    print("-" * 60)

    retriever = SupabaseDataRetriever()
    algo = EstimationAlgorithm()

    try:
        # Récupérer comparables
        comparables_df = retriever.get_comparables(
            latitude=46.3719,
            longitude=6.4727,
            type_bien="Appartement",
            surface_min=60,
            surface_max=110,
            rayon_km=10,
            annees=3,
            limit=30
        )

        if comparables_df is None or len(comparables_df) == 0:
            print("FAIL: No comparables found")
            return False

        print(f"OK: Found {len(comparables_df)} comparables")

        # Convert to list
        comparables = comparables_df.to_dict('records')

        # Estimate
        result = algo.estimate(
            target_latitude=46.3719,
            target_longitude=6.4727,
            target_surface=85,
            target_type="Appartement",
            comparables=comparables
        )

        if result["success"]:
            est = result["estimation"]
            fiat = result["fiabilite"]
            print(f"OK: Prix estime = {est['prix_estime_eur']:,} EUR")
            print(f"    Prix/m2 = {est['prix_au_m2_eur']:,} EUR/m2")
            print(f"    Fiabilite = {fiat['score_global']}/100")
            return True
        else:
            print(f"FAIL: {result.get('erreur', 'Unknown')}")
            return False

    except Exception as e:
        print(f"FAIL: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_annemasse():
    """Test 2: Annemasse"""
    print("\n[TEST 2] Annemasse - Appartement")
    print("-" * 60)

    retriever = SupabaseDataRetriever()
    algo = EstimationAlgorithm()

    try:
        comparables_df = retriever.get_comparables(
            latitude=46.1896,
            longitude=6.2402,
            type_bien="Appartement",
            surface_min=75,
            surface_max=125,
            rayon_km=10,
            annees=3,
            limit=30
        )

        if comparables_df is None or len(comparables_df) == 0:
            print("FAIL: No comparables found")
            return False

        print(f"OK: Found {len(comparables_df)} comparables")

        comparables = comparables_df.to_dict('records')

        result = algo.estimate(
            target_latitude=46.1896,
            target_longitude=6.2402,
            target_surface=100,
            target_type="Appartement",
            comparables=comparables
        )

        if result["success"]:
            est = result["estimation"]
            fiat = result["fiabilite"]
            print(f"OK: Prix estime = {est['prix_estime_eur']:,} EUR")
            print(f"    Prix/m2 = {est['prix_au_m2_eur']:,} EUR/m2")
            print(f"    Fiabilite = {fiat['score_global']}/100")
            return True
        else:
            print(f"FAIL: {result.get('erreur', 'Unknown')}")
            return False

    except Exception as e:
        print(f"FAIL: {e}")
        return False


def test_evian():
    """Test 3: Evian-les-Bains"""
    print("\n[TEST 3] Evian-les-Bains - Maison")
    print("-" * 60)

    retriever = SupabaseDataRetriever()
    algo = EstimationAlgorithm()

    try:
        comparables_df = retriever.get_comparables(
            latitude=46.3981,
            longitude=6.5818,
            type_bien="Maison",
            surface_min=120,
            surface_max=180,
            rayon_km=10,
            annees=3,
            limit=30
        )

        if comparables_df is None or len(comparables_df) == 0:
            print("FAIL: No comparables found")
            return False

        print(f"OK: Found {len(comparables_df)} comparables")

        comparables = comparables_df.to_dict('records')

        result = algo.estimate(
            target_latitude=46.3981,
            target_longitude=6.5818,
            target_surface=150,
            target_type="Maison",
            comparables=comparables
        )

        if result["success"]:
            est = result["estimation"]
            fiat = result["fiabilite"]
            print(f"OK: Prix estime = {est['prix_estime_eur']:,} EUR")
            print(f"    Prix/m2 = {est['prix_au_m2_eur']:,} EUR/m2")
            print(f"    Fiabilite = {fiat['score_global']}/100")
            return True
        else:
            print(f"FAIL: {result.get('erreur', 'Unknown')}")
            return False

    except Exception as e:
        print(f"FAIL: {e}")
        return False


def main():
    """Main"""
    print("=" * 60)
    print("VALIDATION PHASE 3 - EstimationAlgorithm")
    print("=" * 60)

    results = []
    results.append(("Thonon", test_thonon()))
    results.append(("Annemasse", test_annemasse()))
    results.append(("Evian", test_evian()))

    print("\n" + "=" * 60)
    print("RESUME")
    print("=" * 60)

    successes = sum(1 for _, r in results if r)
    print(f"Succes: {successes}/3")

    for name, result in results:
        status = "OK" if result else "FAIL"
        print(f"  {name:20} : {status}")

    if successes >= 2:
        print("\n[OK] PHASE 3 VALIDATION: SUCCESS")
        return 0
    else:
        print("\n[FAIL] PHASE 3 VALIDATION: FAILED")
        return 1


if __name__ == "__main__":
    sys.exit(main())
