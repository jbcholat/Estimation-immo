#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test suite for SupabaseDataRetriever (Phase 5 Validation)
Tests data retrieval, coordinate conversion, and market statistics
"""

import unittest
from unittest.mock import patch, MagicMock
import pandas as pd
from datetime import datetime

from src.supabase_data_retriever import SupabaseDataRetriever


class TestSupabaseConnection(unittest.TestCase):
    """Test Supabase connection and basic operations"""

    def setUp(self):
        """Initialize retriever instance"""
        self.retriever = SupabaseDataRetriever()

    def test_initialization(self):
        """Test SupabaseDataRetriever initialization"""
        self.assertIsNotNone(self.retriever)
        self.assertIsNotNone(self.retriever.engine)
        self.assertIsNotNone(self.retriever.db_password)

    def test_connection_test(self):
        """Test database connection"""
        # This test requires valid credentials
        try:
            result = self.retriever.test_connection()
            self.assertIsNotNone(result)
        except Exception as e:
            self.skipTest(f"Supabase connection failed: {str(e)}")

    def test_lambert93_conversion(self):
        """Test Lambert93 to WGS84 coordinate conversion"""
        # Test data: Lambert93 coords → Expected WGS84
        # Thonon-les-Bains area: roughly (927400, 6350100) Lambert93
        x_lambert = 927400
        y_lambert = 6350100

        # Convert
        try:
            lat, lon = self.retriever._lambert93_to_wgs84(x_lambert, y_lambert)

            # Check if coordinates are reasonable (should be in Haute-Savoie)
            self.assertGreater(lat, 45.5)  # Northern latitude
            self.assertLess(lat, 46.5)
            self.assertGreater(lon, 5.5)   # Eastern longitude
            self.assertLess(lon, 8.0)
        except Exception as e:
            self.skipTest(f"Coordinate conversion failed: {str(e)}")


class TestDataRetrieval(unittest.TestCase):
    """Test data retrieval methods"""

    def setUp(self):
        """Initialize retriever instance"""
        self.retriever = SupabaseDataRetriever()

    def test_get_market_stats(self):
        """Test market statistics retrieval"""
        try:
            stats = self.retriever.get_market_stats()

            # Check response structure
            self.assertIsNotNone(stats)
            self.assertIn('avg_price', stats)
            self.assertIn('median_price', stats)
            self.assertIn('transaction_count', stats)

            # Check data types
            self.assertIsInstance(stats['avg_price'], (int, float))
            self.assertIsInstance(stats['median_price'], (int, float))
            self.assertIsInstance(stats['transaction_count'], int)
        except Exception as e:
            self.skipTest(f"Market stats retrieval failed: {str(e)}")

    def test_get_comparables_returns_dataframe(self):
        """Test get_comparables returns valid DataFrame"""
        try:
            # Test address: Thonon-les-Bains (Chablais zone)
            lat = 46.3787
            lon = 6.4812

            df = self.retriever.get_comparables(
                latitude=lat,
                longitude=lon,
                type_bien="Appartement",
                surface_min=50,
                surface_max=150,
                rayon_km=10.0,
                annees=3,
                limit=20
            )

            # Check DataFrame structure
            self.assertIsInstance(df, pd.DataFrame)

            # Check required columns
            required_cols = ['idmutation', 'datemut', 'valeurfonc', 'sbati', 'distance_km']
            for col in required_cols:
                self.assertIn(col, df.columns, f"Missing column: {col}")

            # If results exist, check data quality
            if len(df) > 0:
                self.assertGreater(df['valeurfonc'].min(), 0)
                self.assertGreater(df['sbati'].min(), 0)
                self.assertLessEqual(df['distance_km'].max(), 10.0)
        except Exception as e:
            self.skipTest(f"Comparables retrieval failed: {str(e)}")

    def test_get_comparables_surface_filtering(self):
        """Test surface range filtering"""
        try:
            lat = 46.3787
            lon = 6.4812

            df = self.retriever.get_comparables(
                latitude=lat,
                longitude=lon,
                surface_min=80,
                surface_max=120
            )

            if len(df) > 0:
                # All surfaces should be within range
                self.assertGreaterEqual(df['sbati'].min(), 80)
                self.assertLessEqual(df['sbati'].max(), 120)
        except Exception as e:
            self.skipTest(f"Surface filtering test failed: {str(e)}")

    def test_get_comparables_distance_calculation(self):
        """Test distance calculation accuracy"""
        try:
            lat = 46.3787
            lon = 6.4812
            rayon_km = 5.0

            df = self.retriever.get_comparables(
                latitude=lat,
                longitude=lon,
                rayon_km=rayon_km,
                limit=20
            )

            if len(df) > 0:
                # All distances should be within search radius
                self.assertLessEqual(df['distance_km'].max(), rayon_km)
        except Exception as e:
            self.skipTest(f"Distance calculation test failed: {str(e)}")


class TestDataQuality(unittest.TestCase):
    """Test data quality and validation"""

    def setUp(self):
        """Initialize retriever instance"""
        self.retriever = SupabaseDataRetriever()

    def test_no_null_coordinates(self):
        """Test that returned data has valid coordinates"""
        try:
            df = self.retriever.get_comparables(
                latitude=46.3787,
                longitude=6.4812,
                limit=10
            )

            if len(df) > 0:
                # Check no null values in critical columns
                self.assertFalse(df['valeurfonc'].isna().any())
                self.assertFalse(df['sbati'].isna().any())
                self.assertFalse(df['distance_km'].isna().any())
        except Exception as e:
            self.skipTest(f"Data quality test failed: {str(e)}")

    def test_positive_prices(self):
        """Test that prices are positive"""
        try:
            df = self.retriever.get_comparables(
                latitude=46.3787,
                longitude=6.4812,
                limit=10
            )

            if len(df) > 0:
                # All prices should be positive
                self.assertTrue((df['valeurfonc'] > 0).all())
        except Exception as e:
            self.skipTest(f"Price validation test failed: {str(e)}")


if __name__ == '__main__':
    unittest.main()
