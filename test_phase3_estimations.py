#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Tests unitaires Phase 3 - EstimationAlgorithm
Tests pour SimilarityScorer, EstimationEngine, ConfidenceCalculator, TemporalAdjuster
"""

import pytest
from datetime import datetime, timedelta
import numpy as np
from src.estimation_algorithm import (
    SimilarityScorer,
    EstimationEngine,
    ConfidenceCalculator,
    TemporalAdjuster,
    EstimationAlgorithm
)


# ============= FIXTURES =============

@pytest.fixture
def scorer():
    """Retourne une instance de SimilarityScorer"""
    return SimilarityScorer()


@pytest.fixture
def engine():
    """Retourne une instance de EstimationEngine"""
    return EstimationEngine()


@pytest.fixture
def confidence():
    """Retourne une instance de ConfidenceCalculator"""
    return ConfidenceCalculator()


@pytest.fixture
def adjuster():
    """Retourne une instance de TemporalAdjuster"""
    return TemporalAdjuster()


@pytest.fixture
def algo():
    """Retourne une instance de EstimationAlgorithm"""
    return EstimationAlgorithm()


# ============= TESTS SIMILARITY SCORER - Distance (5 tests) =============

class TestSimilarityScore_Distance:

    def test_score_distance_zero_km(self, scorer):
        """Distance 0km doit donner score maximal (100)"""
        score = scorer.score_distance(0)
        assert score == pytest.approx(100, abs=1), "Distance 0km devrait donner score ~100"

    def test_score_distance_five_km(self, scorer):
        """Distance 5km doit donner un bon score (exponential decay)"""
        score = scorer.score_distance(5)
        assert 20 < score < 40, "Distance 5km devrait donner score entre 20-40"

    def test_score_distance_fifteen_km_max(self, scorer):
        """Distance >= 15km (max) doit donner score 0"""
        score = scorer.score_distance(15)
        assert score == 0, "Distance >= 15km devrait donner score 0"

    def test_score_distance_negative(self, scorer):
        """Distance négative doit être rejetée (score 0)"""
        score = scorer.score_distance(-5)
        assert score == 0, "Distance négative devrait donner score 0"

    def test_score_distance_one_km(self, scorer):
        """Distance 1km doit donner un score très élevé"""
        score = scorer.score_distance(1)
        assert score > 70, "Distance 1km devrait donner score > 70"


# ============= TESTS SIMILARITY SCORER - Surface (5 tests) =============

class TestSimilarityScore_Surface:

    def test_score_surface_exact_match(self, scorer):
        """Surface identique doit donner score 100"""
        score = scorer.score_surface(100, 100)
        assert score == pytest.approx(100, abs=1), "Surface identique devrait donner score 100"

    def test_score_surface_within_tolerance(self, scorer):
        """Surface ±10% doit donner bon score"""
        score = scorer.score_surface(100, 110)
        assert score >= 49, "Surface +10% devrait donner score >= 49"

    def test_score_surface_at_tolerance_limit(self, scorer):
        """Surface à la limite de tolérance (±20%)"""
        score = scorer.score_surface(100, 120)
        assert score > 0, "Surface +20% devrait donner score > 0"

    def test_score_surface_outside_tolerance(self, scorer):
        """Surface hors tolérance doit donner score 0"""
        score = scorer.score_surface(100, 150)
        assert score == 0, "Surface +50% devrait donner score 0"

    def test_score_surface_zero_target(self, scorer):
        """Surface cible zéro doit donner score 0"""
        score = scorer.score_surface(0, 100)
        assert score == 0, "Surface cible 0 devrait donner score 0"


# ============= TESTS SIMILARITY SCORER - Type (3 tests) =============

class TestSimilarityScore_Type:

    def test_score_type_exact_match(self, scorer):
        """Type identique doit donner score 100"""
        score = scorer.score_type("Appartement", "Appartement")
        assert score == 100, "Type identique devrait donner score 100"

    def test_score_type_case_insensitive(self, scorer):
        """Match de type insensible à la casse"""
        score = scorer.score_type("appartement", "APPARTEMENT")
        assert score == 100, "Type identique (casse différente) devrait donner score 100"

    def test_score_type_different(self, scorer):
        """Type très différent doit donner score 0 ou faible"""
        score = scorer.score_type("Appartement", "Bureau")
        assert score <= 50, "Type très différent devrait donner score <= 50"


# ============= TESTS SIMILARITY SCORER - Ancienneté (3 tests) =============

class TestSimilarityScore_Anciennete:

    def test_score_anciennete_recent_transaction(self, scorer):
        """Transaction récente (<12 mois) doit donner score 100"""
        date_recent = datetime.now() - timedelta(days=30)
        score = scorer.score_anciennete(date_recent)
        assert score == 100, "Transaction <12 mois devrait donner score 100"

    def test_score_anciennete_one_year_old(self, scorer):
        """Transaction 1 an devrait donner score ~80"""
        date_one_year = datetime.now() - timedelta(days=365)
        score = scorer.score_anciennete(date_one_year)
        assert 75 < score <= 100, "Transaction 1 an devrait donner score ~80-100"

    def test_score_anciennete_three_year_old(self, scorer):
        """Transaction 3 ans devrait donner score faible"""
        date_three_year = datetime.now() - timedelta(days=365*3)
        score = scorer.score_anciennete(date_three_year)
        assert score < 50, "Transaction 3 ans devrait donner score < 50"


# ============= TESTS SIMILARITY SCORER - Haversine Distance =============

class TestHaversineDistance:

    def test_haversine_same_point(self, scorer):
        """Distance entre 2 points identiques doit être 0"""
        distance = scorer.haversine_distance(46.37, 6.47, 46.37, 6.47)
        assert distance == pytest.approx(0, abs=0.1), "Points identiques devrait donner distance ~0"

    def test_haversine_known_distance(self, scorer):
        """Distance Thonon-Annemasse doit être raisonnablement calculée"""
        thonon_lat, thonon_lon = 46.3719, 6.4727
        annemasse_lat, annemasse_lon = 46.1896, 6.2402
        distance = scorer.haversine_distance(thonon_lat, thonon_lon, annemasse_lat, annemasse_lon)
        # Distance réelle est environ 20-27 km selon le chemin
        assert 18 < distance < 30, f"Distance Thonon-Annemasse devrait être ~20-27 km, got {distance}"


# ============= TESTS ESTIMATION ENGINE (4 tests) =============

class TestEstimationEngine:

    def test_estimation_with_valid_comparables(self, engine):
        """Estimation avec comparables valides doit fonctionner"""
        comparables_scored = [
            ({"valeurfonc": 300000}, 75),
            ({"valeurfonc": 320000}, 80),
            ({"valeurfonc": 310000}, 70),
        ]
        result = engine.calculate_estimation(comparables_scored)
        assert result["prix_estime"] is not None, "Estimation devrait avoir prix_estime"
        assert result["nb_comparables_utilises"] == 3, "Devrait utiliser 3 comparables"

    def test_estimation_no_valid_comparables(self, engine):
        """Estimation sans comparables valides doit retourner erreur"""
        comparables_scored = [
            ({"valeurfonc": 300000}, 50),  # Score < 70
        ]
        result = engine.calculate_estimation(comparables_scored)
        assert result["erreur"] is not None, "Devrait avoir une erreur"
        assert result["prix_estime"] is None, "prix_estime doit être None"

    def test_prix_au_m2_calculation(self, engine):
        """Calcul prix au m² doit être correct"""
        prix_au_m2 = engine.calculate_prix_au_m2(300000, 100)
        assert prix_au_m2 == 3000, "Prix au m² devrait être 3000"

    def test_prix_au_m2_zero_surface(self, engine):
        """Prix au m² avec surface 0 doit retourner 0"""
        prix_au_m2 = engine.calculate_prix_au_m2(300000, 0)
        assert prix_au_m2 == 0, "Prix au m² avec surface 0 devrait être 0"


# ============= TESTS CONFIDENCE CALCULATOR (3 tests) =============

class TestConfidenceCalculator:

    def test_confidence_with_good_comparables(self, confidence):
        """Score fiabilité avec bons comparables devrait être élevé"""
        comparables_scored = [
            ({"valeurfonc": 300000, "datemut": "2024-01-15"}, 80),
            ({"valeurfonc": 310000, "datemut": "2024-02-15"}, 85),
            ({"valeurfonc": 305000, "datemut": "2024-01-20"}, 82),
            ({"valeurfonc": 295000, "datemut": "2023-12-15"}, 80),
            ({"valeurfonc": 315000, "datemut": "2024-03-15"}, 78),
        ]
        result = confidence.calculate_confidence(comparables_scored)
        assert result["score_global"] > 50, "Score fiabilité devrait être > 50 avec bons comparables"
        assert result["evaluation"] in ["Excellente", "Bonne", "Moyenne"], "Évaluation doit être valide"

    def test_confidence_with_poor_comparables(self, confidence):
        """Score fiabilité avec mauvais comparables devrait être faible"""
        comparables_scored = [
            ({"valeurfonc": 300000, "datemut": "2020-01-15"}, 50),  # Score < 70, pas utilisé
        ]
        result = confidence.calculate_confidence(comparables_scored)
        assert result["score_global"] == 0, "Score fiabilité devrait être 0 avec mauvais comparables"

    def test_confidence_structure(self, confidence):
        """Structure du score fiabilité doit avoir toutes les composantes"""
        comparables_scored = [
            ({"valeurfonc": 300000, "datemut": "2024-01-15"}, 75),
            ({"valeurfonc": 310000, "datemut": "2024-02-15"}, 75),
        ]
        result = confidence.calculate_confidence(comparables_scored)
        assert "volume" in result, "Doit avoir composante volume"
        assert "similarite" in result, "Doit avoir composante similarite"
        assert "dispersion" in result, "Doit avoir composante dispersion"
        assert "anciennete" in result, "Doit avoir composante anciennete"


# ============= TESTS TEMPORAL ADJUSTER (2 tests) =============

class TestTemporalAdjuster:

    def test_adjust_prix_recent_transaction(self, adjuster):
        """Prix récent (2024) doit être proche de l'original"""
        prix_original = 300000
        date_2024 = datetime.now()
        prix_ajuste = adjuster.adjust_prix(prix_original, date_2024)
        assert prix_ajuste == pytest.approx(prix_original, rel=0.05), "Prix 2024 devrait être ~300k"

    def test_adjust_prix_old_transaction(self, adjuster):
        """Prix ancien (2019) devrait être inférieur après ajustement inflation"""
        prix_original = 300000
        date_2019 = datetime(2019, 1, 1)
        prix_ajuste = adjuster.adjust_prix(prix_original, date_2019)
        assert prix_ajuste > prix_original, "Prix 2019 ajusté devrait être plus élevé (inflation)"


# ============= TESTS INTEGRATION - EstimationAlgorithm =============

class TestEstimationAlgorithmIntegration:

    def test_complete_estimation_workflow(self, algo):
        """Workflow complet d'estimation avec comparables réels"""
        # Bien cible
        target_lat, target_lon = 46.3719, 6.4727  # Thonon
        target_surface = 85  # 85 m²
        target_type = "Appartement"

        # Comparables fictifs
        comparables = [
            {
                "latitude": 46.3720, "longitude": 6.4725,
                "sbati": 80, "libnatmut": "Appartement",
                "valeurfonc": 300000, "datemut": "2024-01-15"
            },
            {
                "latitude": 46.3718, "longitude": 6.4729,
                "sbati": 90, "libnatmut": "Appartement",
                "valeurfonc": 320000, "datemut": "2024-02-15"
            },
            {
                "latitude": 46.3715, "longitude": 6.4730,
                "sbati": 75, "libnatmut": "Appartement",
                "valeurfonc": 280000, "datemut": "2023-12-15"
            },
        ]

        # Estimation
        result = algo.estimate(target_lat, target_lon, target_surface, target_type, comparables)

        assert result["success"] is True, "Estimation devrait réussir"
        assert result["estimation"]["prix_estime_eur"] is not None, "Devrait avoir prix_estime"
        assert 250000 < result["estimation"]["prix_estime_eur"] < 350000, "Prix estimé doit être raisonnable"

    def test_estimation_with_no_comparables(self, algo):
        """Estimation sans comparables doit retourner erreur"""
        result = algo.estimate(46.37, 6.47, 85, "Appartement", [])
        assert result["success"] is False, "Estimation devrait échouer"
        assert "erreur" in result, "Doit avoir message d'erreur"

    def test_estimation_with_invalid_surface(self, algo):
        """Estimation avec surface invalide doit gérer l'erreur"""
        comparables = [
            {
                "latitude": 46.37, "longitude": 6.47,
                "sbati": 80, "libnatmut": "Appartement",
                "valeurfonc": 300000, "datemut": "2024-01-15"
            }
        ]
        result = algo.estimate(46.37, 6.47, 0, "Appartement", comparables)
        # Devrait soit retourner erreur, soit gérer gracieusement
        assert "success" in result, "Résultat doit avoir clé 'success'"

    def test_estimation_returns_all_keys(self, algo):
        """Résultat d'estimation doit avoir tous les clés requis"""
        comparables = [
            {
                "latitude": 46.37, "longitude": 6.47,
                "sbati": 85, "libnatmut": "Appartement",
                "valeurfonc": 300000, "datemut": "2024-01-15"
            },
            {
                "latitude": 46.37, "longitude": 6.47,
                "sbati": 85, "libnatmut": "Appartement",
                "valeurfonc": 310000, "datemut": "2024-01-16"
            }
        ]
        result = algo.estimate(46.37, 6.47, 85, "Appartement", comparables)

        if result["success"]:
            assert "bien" in result, "Résultat doit avoir 'bien'"
            assert "estimation" in result, "Résultat doit avoir 'estimation'"
            assert "fiabilite" in result, "Résultat doit avoir 'fiabilite'"


# ============= TESTS DE REGRESSION =============

class TestRegressionScores:

    def test_thonon_estimation(self, algo):
        """Test estimé Thonon-les-Bains (cas réel)"""
        comparables = [
            {
                "latitude": 46.3719, "longitude": 6.4727,
                "sbati": 85, "libnatmut": "Appartement",
                "valeurfonc": 300000, "datemut": "2024-01-01"
            },
            {
                "latitude": 46.3720, "longitude": 6.4728,
                "sbati": 90, "libnatmut": "Appartement",
                "valeurfonc": 325000, "datemut": "2024-01-05"
            },
            {
                "latitude": 46.3715, "longitude": 6.4725,
                "sbati": 80, "libnatmut": "Appartement",
                "valeurfonc": 280000, "datemut": "2023-12-01"
            },
        ]
        result = algo.estimate(46.3719, 6.4727, 85, "Appartement", comparables)
        if result["success"]:
            # Estimation raisonnable pour Thonon
            assert 250000 < result["estimation"]["prix_estime_eur"] < 350000

    def test_annemasse_estimation(self, algo):
        """Test estimation Annemasse (cas réel)"""
        comparables = [
            {
                "latitude": 46.1896, "longitude": 6.2402,
                "sbati": 100, "libnatmut": "Appartement",
                "valeurfonc": 450000, "datemut": "2024-01-01"
            },
            {
                "latitude": 46.1900, "longitude": 6.2405,
                "sbati": 110, "libnatmut": "Appartement",
                "valeurfonc": 480000, "datemut": "2024-01-05"
            }
        ]
        result = algo.estimate(46.1896, 6.2402, 100, "Appartement", comparables)
        if result["success"]:
            # Estimation raisonnable pour Annemasse (prix plus élevé)
            assert 400000 < result["estimation"]["prix_estime_eur"] < 550000


# ============= UTILS =============

if __name__ == "__main__":
    # Exécuter avec: pytest test_phase3_estimations.py -v
    pytest.main([__file__, "-v", "--tb=short"])
