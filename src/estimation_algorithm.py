#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
EstimationAlgorithm - Classe pour estimation immobilière par scoring multi-critères
Phase 3 - Algorithmes d'estimation
"""

import logging
import math
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
import pandas as pd
import numpy as np

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class SimilarityScorer:
    """Calcule les scores de similarité multi-critères (0-100)"""

    # Paramètres de scoring
    DISTANCE_WEIGHT = 0.25
    SURFACE_WEIGHT = 0.25
    TYPE_WEIGHT = 0.25
    ANCIENNETE_WEIGHT = 0.25

    # Limites
    SURFACE_TOLERANCE_PCT = 0.20  # ±20%
    DISTANCE_MAX_KM = 15.0
    ANCIENNETE_MAX_MOIS = 36

    @staticmethod
    def score_distance(distance_km: float) -> float:
        """
        Scoring exponentiel pour la distance.
        Plus proche = meilleur score (100 à 0km, 0 à 15km)
        """
        if distance_km < 0:
            return 0
        if distance_km >= SimilarityScorer.DISTANCE_MAX_KM:
            return 0

        # Décroissance exponentielle
        score = 100 * math.exp(-0.3 * distance_km)
        return max(0, min(100, score))

    @staticmethod
    def score_surface(surface_target: float, surface_comparable: float) -> float:
        """
        Scoring de surface avec tolérance ±20%.
        100 = match exact, 0 = hors tolérance
        """
        if surface_target <= 0 or surface_comparable <= 0:
            return 0

        ratio = surface_comparable / surface_target
        tolerance = SimilarityScorer.SURFACE_TOLERANCE_PCT

        # Tolérance (±20%)
        if 1 - tolerance <= ratio <= 1 + tolerance:
            # Linéaire dans tolérance
            deviation = abs(ratio - 1)
            score = 100 * (1 - deviation / tolerance)
            return max(0, score)

        # Hors tolérance = 0
        return 0

    @staticmethod
    def score_type(type_target: str, type_comparable: str) -> float:
        """
        Match de type : 100 si identique, 50 si compatible, 0 sinon
        """
        if type_target.lower() == type_comparable.lower():
            return 100

        # Compatibilité partielle
        compatible_pairs = [
            ("maison", "appartement"),
            ("studio", "apartement"),
        ]

        pair = (type_target.lower(), type_comparable.lower())
        if pair in compatible_pairs or (pair[1], pair[0]) in compatible_pairs:
            return 50

        return 0

    @staticmethod
    def score_anciennete(date_mutation: datetime) -> float:
        """
        Score ancienneté (récence des données).
        100 = <12 mois, 80 = 12-24 mois, 50 = 24-36 mois, 0 = >36 mois
        """
        try:
            if isinstance(date_mutation, str):
                date_mutation = datetime.strptime(date_mutation, "%Y-%m-%d")

            # Convertir date en datetime si nécessaire
            if hasattr(date_mutation, 'date'):
                # C'est déjà un datetime
                pass
            else:
                # C'est une date, la convertir en datetime
                date_mutation = datetime.combine(date_mutation, datetime.min.time())

            mois_ecoulis = (datetime.now() - date_mutation).days / 30.44

            if mois_ecoulis <= 12:
                return 100
            elif mois_ecoulis <= 24:
                return 80 - (mois_ecoulis - 12) * (30 / 12)  # Déclin à 50 à 24 mois
            elif mois_ecoulis <= 36:
                return 50 - (mois_ecoulis - 24) * (50 / 12)  # Déclin à 0 à 36 mois
            else:
                return 0
        except Exception as e:
            logger.warning(f"Erreur scoring ancienneté: {e}")
            return 50

    @staticmethod
    def _normalize_property_type(type_str: str) -> str:
        """
        Normalise le type de bien DVF+ vers format standard.
        Ex: "UN APPARTEMENT" → "Appartement", "UNE MAISON" → "Maison"
        """
        if not type_str:
            return "Inconnu"

        type_str = type_str.strip().upper()

        # Mapping DVF+ → standard
        if "APPARTEMENT" in type_str:
            return "Appartement"
        elif "MAISON" in type_str:
            return "Maison"
        elif "STUDIO" in type_str:
            return "Studio"
        elif "TERRAIN" in type_str:
            return "Terrain"
        else:
            return type_str.title()

    @staticmethod
    def calculate_comparable_score(
        target_latitude: float,
        target_longitude: float,
        target_surface: float,
        target_type: str,
        comparable: Dict
    ) -> float:
        """
        Calcule le score global de similarité (0-100) pour un comparable.

        Args:
            target_latitude, target_longitude: Coordonnées du bien cible
            target_surface: Surface du bien cible en m²
            target_type: Type du bien cible
            comparable: Dict avec keys: latitude, longitude, sbati, libtypbien, datemut

        Returns:
            Score 0-100
        """
        try:
            # Convertir tous les valeurs Decimal en float
            def to_float(val):
                """Convertit Decimal ou autre type en float"""
                from decimal import Decimal
                if isinstance(val, Decimal):
                    return float(val)
                return float(val) if val is not None else 0

            # Distance
            distance_km = SimilarityScorer.haversine_distance(
                to_float(target_latitude),
                to_float(target_longitude),
                to_float(comparable.get("latitude")),
                to_float(comparable.get("longitude"))
            )
            distance_score = SimilarityScorer.score_distance(distance_km)

            # Surface
            surface_score = SimilarityScorer.score_surface(
                to_float(target_surface),
                to_float(comparable.get("sbati", 0))
            )

            # Type - normalize DVF+ type to standard format
            comparable_type_raw = comparable.get("libtypbien", "Inconnu")
            comparable_type_normalized = SimilarityScorer._normalize_property_type(comparable_type_raw)
            type_score = SimilarityScorer.score_type(
                target_type,
                comparable_type_normalized
            )

            # Ancienneté
            anciennete_score = SimilarityScorer.score_anciennete(
                comparable.get("datemut")
            )

            # Score pondéré
            total_score = (
                distance_score * SimilarityScorer.DISTANCE_WEIGHT +
                surface_score * SimilarityScorer.SURFACE_WEIGHT +
                type_score * SimilarityScorer.TYPE_WEIGHT +
                anciennete_score * SimilarityScorer.ANCIENNETE_WEIGHT
            )

            return max(0, min(100, total_score))
        except Exception as e:
            logger.error(f"Erreur calcul score comparable: {e}")
            return 0

    @staticmethod
    def haversine_distance(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
        """Calcule la distance en km entre deux points (lat, lon) via Haversine"""
        try:
            R = 6371  # Rayon Terre en km

            lat1_rad = math.radians(lat1)
            lat2_rad = math.radians(lat2)
            delta_lat = math.radians(lat2 - lat1)
            delta_lon = math.radians(lon2 - lon1)

            a = math.sin(delta_lat/2)**2 + math.cos(lat1_rad) * math.cos(lat2_rad) * math.sin(delta_lon/2)**2
            c = 2 * math.asin(math.sqrt(a))

            return R * c
        except Exception as e:
            logger.error(f"Erreur calcul distance: {e}")
            return 999


class EstimationEngine:
    """Moteur d'estimation basé sur comparables avec pondération par scores"""

    MIN_COMPARABLE_SCORE = 40  # Score minimum pour inclure un comparable (baissé de 70 pour inclusivité)

    @staticmethod
    def calculate_estimation(
        comparables_with_scores: List[Tuple[Dict, float]]
    ) -> Dict:
        """
        Calcule l'estimation du prix basée sur les comparables.

        Args:
            comparables_with_scores: List de tuples (comparable_dict, score)

        Returns:
            Dict avec keys: prix_estime, prix_min, prix_max, nb_comparables_utilises
        """
        # Filtrer les comparables par score minimum
        valides = [
            (c, s) for c, s in comparables_with_scores
            if s >= EstimationEngine.MIN_COMPARABLE_SCORE
        ]

        if not valides:
            return {
                "prix_estime": None,
                "prix_min": None,
                "prix_max": None,
                "nb_comparables_utilises": 0,
                "erreur": f"Pas de comparables valides (score >= {EstimationEngine.MIN_COMPARABLE_SCORE})"
            }

        # Extraction prix et scores
        prix_list = []
        scores_list = []

        for comparable, score in valides:
            prix = comparable.get("valeurfonc")
            if prix and prix > 0:
                prix_list.append(prix)
                scores_list.append(score)

        if not prix_list:
            return {
                "prix_estime": None,
                "prix_min": None,
                "prix_max": None,
                "nb_comparables_utilises": 0,
                "erreur": "Aucun prix valide dans les comparables"
            }

        # Calcul moyenne pondérée
        prix_array = np.array(prix_list)
        scores_array = np.array(scores_list)

        # Normaliser scores pour pondération
        weights = scores_array / scores_array.sum()
        prix_estime = np.sum(prix_array * weights)

        return {
            "prix_estime": round(prix_estime),
            "prix_min": round(np.percentile(prix_array, 25)),
            "prix_max": round(np.percentile(prix_array, 75)),
            "nb_comparables_utilises": len(prix_list),
            "erreur": None
        }

    @staticmethod
    def calculate_prix_au_m2(
        prix_estime: float,
        surface: float
    ) -> float:
        """Calcule le prix au m² à partir du prix estimé"""
        if surface <= 0:
            return 0
        return round(prix_estime / surface, 2)


class ConfidenceCalculator:
    """Calcule le score de fiabilité de l'estimation (4 composantes)"""

    @staticmethod
    def calculate_confidence(
        comparables_with_scores: List[Tuple[Dict, float]]
    ) -> Dict:
        """
        Calcule 4 scores de fiabilité :
        1. Volume (30%) : Nombre de comparables >= 70
        2. Similarité (30%) : Score moyen des comparables
        3. Dispersion (25%) : Variance prix
        4. Ancienneté (15%) : Fraîcheur données

        Returns:
            Dict avec keys: score_global, volume, similarite, dispersion, anciennete
        """
        # Filtrer comparables valides
        valides = [
            (c, s) for c, s in comparables_with_scores
            if s >= EstimationEngine.MIN_COMPARABLE_SCORE
        ]

        if not valides:
            return {
                "score_global": 0,
                "volume": 0,
                "similarite": 0,
                "dispersion": 0,
                "anciennete": 0,
                "details": "Pas de comparables valides"
            }

        # 1. Score Volume (30%)
        # Excellent : 10+, Bon : 5-9, Moyen : 3-4, Faible : 1-2
        nb_comparables = len(valides)
        if nb_comparables >= 10:
            score_volume = 30
        elif nb_comparables >= 5:
            score_volume = 25
        elif nb_comparables >= 3:
            score_volume = 15
        else:
            score_volume = 5

        # 2. Score Similarité (30%)
        scores = [s for _, s in valides]
        score_moyen = np.mean(scores)
        # Pondération : score ≥70 = bon, ≥80 = très bon
        if score_moyen >= 80:
            score_similarite = 30
        elif score_moyen >= 75:
            score_similarite = 25
        elif score_moyen >= 70:
            score_similarite = 15
        else:
            score_similarite = 0

        # 3. Score Dispersion (25%)
        # Faible dispersion = bon score
        prix_list = [c.get("valeurfonc", 0) for c, _ in valides if c.get("valeurfonc", 0) > 0]
        if len(prix_list) > 1:
            coefficient_variation = np.std(prix_list) / np.mean(prix_list)
            # CV < 0.15 = excellent, < 0.25 = bon
            if coefficient_variation < 0.15:
                score_dispersion = 25
            elif coefficient_variation < 0.25:
                score_dispersion = 20
            elif coefficient_variation < 0.40:
                score_dispersion = 10
            else:
                score_dispersion = 0
        else:
            score_dispersion = 10

        # 4. Score Ancienneté (15%)
        dates_list = []
        for c, _ in valides:
            try:
                date_mut = c.get("datemut")
                if isinstance(date_mut, str):
                    date_mut = datetime.strptime(date_mut, "%Y-%m-%d")
                mois_ecoulis = (datetime.now() - date_mut).days / 30.44
                dates_list.append(mois_ecoulis)
            except:
                pass

        if dates_list:
            mois_moyen = np.mean(dates_list)
            if mois_moyen <= 12:
                score_anciennete = 15
            elif mois_moyen <= 24:
                score_anciennete = 12
            elif mois_moyen <= 36:
                score_anciennete = 8
            else:
                score_anciennete = 3
        else:
            score_anciennete = 5

        # Score global
        score_global = score_volume + score_similarite + score_dispersion + score_anciennete

        # Évaluation qualitative
        if score_global >= 80:
            evaluation = "Excellente"
        elif score_global >= 65:
            evaluation = "Bonne"
        elif score_global >= 50:
            evaluation = "Moyenne"
        else:
            evaluation = "Faible"

        return {
            "score_global": round(score_global),
            "volume": score_volume,
            "similarite": score_similarite,
            "dispersion": score_dispersion,
            "anciennete": score_anciennete,
            "evaluation": evaluation,
            "nb_comparables": nb_comparables
        }


class TemporalAdjuster:
    """Ajuste le prix pour l'inflation et la dynamique du marché Chablais"""

    # Taux d'inflation annuel (France 2023-2024)
    INFLATION_ANNUELLE = 0.04  # 4%

    # Facteurs de correction par année (marché Chablais spécifique)
    # Basés sur données DVF historiques zone 74
    FACTEURS_MARCHE_CHABLAIS = {
        2019: 0.85,   # Référence future = 1.0
        2020: 0.87,
        2021: 0.91,
        2022: 0.96,
        2023: 0.99,
        2024: 1.00,   # Année actuelle
        2025: 1.02,
    }

    @staticmethod
    def adjust_prix(
        prix_comparable: float,
        date_comparable: datetime,
        date_reference: Optional[datetime] = None
    ) -> float:
        """
        Ajuste un prix comparable à la date de référence.
        Utilise inflation + facteur marché Chablais.

        Args:
            prix_comparable: Prix de vente du comparable
            date_comparable: Date de la transaction
            date_reference: Date de référence (default = aujourd'hui)

        Returns:
            Prix ajusté
        """
        if date_reference is None:
            date_reference = datetime.now()

        try:
            if isinstance(date_comparable, str):
                date_comparable = datetime.strptime(date_comparable, "%Y-%m-%d")

            # Calculer nombre d'années
            delta_jours = (date_reference - date_comparable).days
            annees = delta_jours / 365.25

            # Ajustement inflation simple
            facteur_inflation = (1 + TemporalAdjuster.INFLATION_ANNUELLE) ** annees

            # Ajustement marché (bonus/malus selon année)
            annee_comparable = date_comparable.year
            annee_ref = date_reference.year

            facteur_marche = 1.0
            if annee_comparable in TemporalAdjuster.FACTEURS_MARCHE_CHABLAIS:
                facteur_ancien = TemporalAdjuster.FACTEURS_MARCHE_CHABLAIS[annee_comparable]
                facteur_nouveau = TemporalAdjuster.FACTEURS_MARCHE_CHABLAIS.get(annee_ref, 1.0)
                facteur_marche = facteur_nouveau / facteur_ancien if facteur_ancien > 0 else 1.0

            # Ajustement combiné
            prix_ajuste = prix_comparable * facteur_inflation * facteur_marche

            return round(prix_ajuste)
        except Exception as e:
            logger.error(f"Erreur ajustement prix: {e}")
            return prix_comparable


class EstimationAlgorithm:
    """
    Classe principale orchestrateur pour l'estimation immobilière.
    Combine scoring, estimation, fiabilité et ajustement temporel.
    """

    def __init__(self):
        """Initialise les composants"""
        self.scorer = SimilarityScorer()
        self.engine = EstimationEngine()
        self.confidence = ConfidenceCalculator()
        self.adjuster = TemporalAdjuster()
        logger.info("EstimationAlgorithm initialisé")

    def estimate(
        self,
        target_latitude: float,
        target_longitude: float,
        target_surface: float,
        target_type: str,
        comparables: List[Dict]
    ) -> Dict:
        """
        Effectue une estimation complète pour un bien.

        Args:
            target_latitude: Latitude du bien cible
            target_longitude: Longitude du bien cible
            target_surface: Surface m² du bien cible
            target_type: Type du bien cible (Appartement, Maison, etc.)
            comparables: Liste de comparables (dict avec keys: latitude, longitude, sbati, libtypbien, datemut, valeurfonc)

        Returns:
            Dict complet avec estimation, fiabilité, prix au m², etc.
        """
        if not comparables:
            return {
                "success": False,
                "erreur": "Aucun comparable fourni"
            }

        try:
            # Étape 1 : Scorer les comparables
            comparables_scored = []
            for comparable in comparables:
                score = self.scorer.calculate_comparable_score(
                    target_latitude, target_longitude, target_surface, target_type,
                    comparable
                )
                comparables_scored.append((comparable, score))

            # Étape 2 : Calculer l'estimation
            estimation = self.engine.calculate_estimation(comparables_scored)

            if estimation["erreur"]:
                return {
                    "success": False,
                    "erreur": estimation["erreur"]
                }

            # Étape 3 : Calculer la fiabilité
            confidence = self.confidence.calculate_confidence(comparables_scored)

            # Étape 4 : Ajouter prix au m²
            if estimation["prix_estime"] and estimation["prix_estime"] > 0:
                prix_au_m2 = self.engine.calculate_prix_au_m2(
                    estimation["prix_estime"],
                    target_surface
                )
            else:
                prix_au_m2 = 0

            # Résultat final
            return {
                "success": True,
                "bien": {
                    "latitude": target_latitude,
                    "longitude": target_longitude,
                    "surface_m2": target_surface,
                    "type": target_type
                },
                "estimation": {
                    "prix_estime_eur": estimation["prix_estime"],
                    "prix_min_eur": estimation["prix_min"],
                    "prix_max_eur": estimation["prix_max"],
                    "prix_au_m2_eur": prix_au_m2
                },
                "fiabilite": confidence,
                "nb_comparables_utilises": estimation["nb_comparables_utilises"],
                "comparables_summary": self._comparables_summary(comparables_scored),
                "comparables_with_scores": [
                    {**c, "score": s} for c, s in comparables_scored
                ],
                "timestamp": datetime.now().isoformat()
            }
        except Exception as e:
            logger.error(f"Erreur estimation: {e}")
            return {
                "success": False,
                "erreur": str(e)
            }

    def _comparables_summary(self, comparables_scored: List[Tuple[Dict, float]]) -> Dict:
        """Résumé statistique des comparables"""
        try:
            valides = [(c, s) for c, s in comparables_scored if s >= 40]
            if not valides:
                return {}

            scores = [s for _, s in valides]

            return {
                "score_moyen": round(np.mean(scores), 1),
                "score_min": round(np.min(scores), 1),
                "score_max": round(np.max(scores), 1),
                "nb_comparables_utilises": len(valides)
            }
        except:
            return {}
