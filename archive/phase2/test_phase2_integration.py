#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Tests d'intégration Phase 2 - 5 adresses réelles
"""

import sys
import io
from src.supabase_data_retriever import SupabaseDataRetriever

if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')


def test_all_addresses():
    """Teste 5 adresses réelles du Chablais"""

    print("=" * 70)
    print("TESTS D'INTEGRATION PHASE 2 - 5 ADRESSES REELLES")
    print("=" * 70)

    retriever = SupabaseDataRetriever()

    # Vérifier connexion
    print("\n1️⃣ Vérification connexion...")
    if not retriever.test_connection():
        print("❌ Impossible de se connecter à Supabase")
        return False

    # 5 adresses test
    tests = [
        {
            'nom': 'Thonon-les-Bains',
            'code_postal': '74200',
            'latitude': 46.3719,
            'longitude': 6.4727,
            'type': 'Appartement',
            'surface_min': 50,
            'surface_max': 100,
            'rayon_km': 5
        },
        {
            'nom': 'Annemasse',
            'code_postal': '74100',
            'latitude': 46.1927,
            'longitude': 6.2357,
            'type': 'Maison',
            'surface_min': 80,
            'surface_max': 150,
            'rayon_km': 10
        },
        {
            'nom': 'Morzine',
            'code_postal': '74110',
            'latitude': 46.1792,
            'longitude': 6.7072,
            'type': 'Appartement',
            'surface_min': 30,
            'surface_max': 70,
            'rayon_km': 10
        },
        {
            'nom': 'Évian-les-Bains',
            'code_postal': '74500',
            'latitude': 46.4001,
            'longitude': 6.5889,
            'type': 'Maison',
            'surface_min': 100,
            'surface_max': 200,
            'rayon_km': 8
        },
        {
            'nom': 'Douvaine',
            'code_postal': '74140',
            'latitude': 46.3056,
            'longitude': 6.3028,
            'type': 'Appartement',
            'surface_min': 40,
            'surface_max': 80,
            'rayon_km': 10
        }
    ]

    results = []

    for i, test in enumerate(tests, 1):
        print(f"\n{i+1}️⃣ Test: {test['nom']} ({test['code_postal']})")
        print(f"   Type: {test['type']}, Surface: {test['surface_min']}-{test['surface_max']}m²")

        try:
            comparables = retriever.get_comparables(
                latitude=test['latitude'],
                longitude=test['longitude'],
                type_bien=test['type'],
                surface_min=test['surface_min'],
                surface_max=test['surface_max'],
                rayon_km=test['rayon_km'],
                limit=20
            )

            nb_comparables = len(comparables)

            if nb_comparables > 0:
                print(f"   ✅ PASS - {nb_comparables} comparables trouvés")
                if 'valeurfonc' in comparables.columns:
                    prix_moyen = comparables['valeurfonc'].mean()
                    print(f"      Prix moyen: {prix_moyen:,.0f}€")
                results.append((test['nom'], True, nb_comparables))
            else:
                print(f"   ⚠️  FAIL - Aucun comparable trouvé")
                results.append((test['nom'], False, 0))

            # Afficher statistiques marché
            stats = retriever.get_market_stats(test['code_postal'])
            if stats and stats.get('nb_transactions', 0) > 0:
                print(f"      Marché: {stats['nb_transactions']} transactions, "
                      f"Prix médian: {stats['prix_median']:,.0f}€")

        except Exception as e:
            print(f"   ❌ ERREUR: {str(e)}")
            results.append((test['nom'], False, 0))

    # Résumé
    print("\n" + "=" * 70)
    print("RÉSUMÉ DES TESTS")
    print("=" * 70)

    pass_count = sum(1 for _, passed, _ in results if passed)
    total_count = len(results)

    for nom, passed, count in results:
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"{status} - {nom}: {count} comparables")

    print(f"\nRésultat: {pass_count}/{total_count} tests passants")

    if pass_count == total_count:
        print("\n🎉 TOUS LES TESTS PASSES - PHASE 2 VALIDEE!")
        return True
    else:
        print(f"\n⚠️  {total_count - pass_count} tests échoués")
        return False


if __name__ == "__main__":
    success = test_all_addresses()
    sys.exit(0 if success else 1)
