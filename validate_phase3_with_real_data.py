#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script de validation Phase 3 - EstimationAlgorithm avec biens réels du Chablais
Utilise SupabaseDataRetriever pour récupérer les comparables depuis Supabase
"""

import sys
import logging
from datetime import datetime

# Add src to path
sys.path.insert(0, '/c/analyse_immobiliere')

from src.supabase_data_retriever import SupabaseDataRetriever
from src.estimation_algorithm import EstimationAlgorithm

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class ValidationPhase3:
    """Classe de validation de Phase 3 avec données réelles"""

    # Biens réels du Chablais à tester
    TEST_PROPERTIES = [
        {
            "name": "Thonon-les-Bains - Appartement centre-ville",
            "latitude": 46.3719,
            "longitude": 6.4727,
            "surface": 85,
            "type": "Appartement",
            "code_postal": "74200",
            "description": "Appartement 3 pièces au cœur de Thonon"
        },
        {
            "name": "Annemasse - Appartement proximité gare",
            "latitude": 46.1896,
            "longitude": 6.2402,
            "surface": 100,
            "type": "Appartement",
            "code_postal": "74100",
            "description": "Appartement 4 pièces proche gare SNCF"
        },
        {
            "name": "Évian-les-Bains - Maison vue lac",
            "latitude": 46.3981,
            "longitude": 6.5818,
            "surface": 150,
            "type": "Maison",
            "code_postal": "74500",
            "description": "Maison 5 pièces avec vue sur le lac Léman"
        },
        {
            "name": "Douvaine - Appartement résidentiel",
            "latitude": 46.3469,
            "longitude": 6.3681,
            "surface": 75,
            "type": "Appartement",
            "code_postal": "74140",
            "description": "Appartement 2 pièces quartier résidentiel"
        },
        {
            "name": "Sciez - Maison périphérie",
            "latitude": 46.3231,
            "longitude": 6.5186,
            "surface": 120,
            "type": "Maison",
            "code_postal": "74140",
            "description": "Maison 4 pièces à la périphérie de Sciez"
        }
    ]

    def __init__(self):
        """Initialise la validation"""
        self.retriever = SupabaseDataRetriever()
        self.algo = EstimationAlgorithm()
        self.results = []

    def validate_all(self):
        """Valide l'algorithme sur tous les biens de test"""
        logger.info("=" * 80)
        logger.info("VALIDATION PHASE 3 - EstimationAlgorithm avec données réelles Chablais")
        logger.info("=" * 80)

        for idx, property_data in enumerate(self.TEST_PROPERTIES, 1):
            logger.info(f"\n[{idx}/5] {property_data['name']}")
            logger.info("-" * 80)

            try:
                # Récupérer les comparables depuis Supabase
                logger.info(f"   Recherche comparables dans rayon 10km...")
                comparables_df = self.retriever.get_comparables(
                    latitude=property_data["latitude"],
                    longitude=property_data["longitude"],
                    type_bien=property_data["type"],
                    surface_min=property_data["surface"] * 0.7,
                    surface_max=property_data["surface"] * 1.3,
                    rayon_km=10.0,
                    annees=3,
                    limit=30
                )

                if comparables_df is None or len(comparables_df) == 0:
                    logger.warning(f"   [FAIL] Aucun comparable trouve pour {property_data['name']}")
                    self.results.append({
                        "property": property_data['name'],
                        "status": "FAIL",
                        "reason": "No comparables found"
                    })
                    continue

                # Convertir DataFrame en liste de dicts
                comparables = comparables_df.to_dict('records')
                logger.info(f"   ✓ {len(comparables)} comparables trouvés")

                # Effectuer l'estimation
                logger.info(f"   Calcul estimation...")
                result = self.algo.estimate(
                    target_latitude=property_data["latitude"],
                    target_longitude=property_data["longitude"],
                    target_surface=property_data["surface"],
                    target_type=property_data["type"],
                    comparables=comparables
                )

                # Traiter le résultat
                if result["success"]:
                    estimation = result["estimation"]
                    fiabilite = result["fiabilite"]

                    logger.info(f"   [OK] ESTIMATION REUSSIE")
                    logger.info(f"      Prix estime: {estimation['prix_estime_eur']:,} EUR")
                    logger.info(f"      Fourchette: {estimation['prix_min_eur']:,} - {estimation['prix_max_eur']:,} EUR")
                    logger.info(f"      Prix/m2: {estimation['prix_au_m2_eur']:,} EUR/m2")
                    logger.info(f"      Fiabilite: {fiabilite['evaluation']} ({fiabilite['score_global']}/100)")
                    logger.info(f"      Comparables: {fiabilite['nb_comparables']} utilises")

                    self.results.append({
                        "property": property_data['name'],
                        "status": "SUCCESS",
                        "prix_estime": estimation['prix_estime_eur'],
                        "prix_au_m2": estimation['prix_au_m2_eur'],
                        "fiabilite": fiabilite['score_global'],
                        "nb_comparables": fiabilite['nb_comparables']
                    })
                else:
                    logger.error(f"   [FAIL] ERREUR: {result.get('erreur', 'Unknown error')}")
                    self.results.append({
                        "property": property_data['name'],
                        "status": "FAIL",
                        "reason": result.get('erreur', 'Unknown error')
                    })

            except Exception as e:
                logger.error(f"   [FAIL] EXCEPTION: {e}")
                self.results.append({
                    "property": property_data['name'],
                    "status": "FAIL",
                    "reason": str(e)
                })

    def print_summary(self):
        """Affiche un résumé des résultats"""
        logger.info("\n" + "=" * 80)
        logger.info("RESUME DES RESULTATS")
        logger.info("=" * 80)

        successes = [r for r in self.results if r["status"] == "SUCCESS"]
        failures = [r for r in self.results if r["status"] == "FAIL"]

        logger.info(f"\nTotal: {len(self.results)} biens testes")
        logger.info(f"[OK] Succes: {len(successes)}")
        logger.info(f"[FAIL] Echecs: {len(failures)}")

        if successes:
            logger.info("\nEstimations reussies:")
            for r in successes:
                logger.info(f"  * {r['property']}")
                logger.info(f"    Prix: {r['prix_estime']:,} EUR ({r['prix_au_m2']:,} EUR/m2)")
                logger.info(f"    Fiabilite: {r['fiabilite']}/100")

        if failures:
            logger.info("\nEchecs:")
            for r in failures:
                logger.info(f"  * {r['property']}: {r['reason']}")

        # Tests passants
        success_rate = (len(successes) / len(self.results)) * 100 if self.results else 0
        logger.info(f"\nTaux de reussite: {success_rate:.0f}%")

        if len(successes) >= 3:
            logger.info("\n[OK] PHASE 3 VALIDATION: SUCCESS")
            logger.info("   Au moins 3 estimations reussies sur 5 biens testes")
            return True
        else:
            logger.info("\n[FAIL] PHASE 3 VALIDATION: FAILED")
            logger.info("   Moins de 3 estimations reussies")
            return False


def main():
    """Main entry point"""
    try:
        validator = ValidationPhase3()
        validator.validate_all()
        success = validator.print_summary()
        sys.exit(0 if success else 1)
    except Exception as e:
        logger.error(f"Erreur fatale: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
