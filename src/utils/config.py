#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Configuration Management - Charge variables d'environnement
Phase 4 - Streamlit MVP
"""

import os
from typing import Optional
from dotenv import load_dotenv

# Charger .env.local en priorité, puis .env
load_dotenv('.env.local', override=True)
load_dotenv('.env', override=True)


class Config:
    """Gestion centralisée de la configuration"""

    # Supabase
    SUPABASE_URL: str = os.getenv("SUPABASE_URL", "")
    SUPABASE_DB_PASSWORD: str = os.getenv("SUPABASE_DB_PASSWORD", "")
    SUPABASE_KEY: str = os.getenv("SUPABASE_KEY", "")

    # Google Maps
    GOOGLE_MAPS_API_KEY: str = os.getenv("GOOGLE_MAPS_API_KEY", "")

    # Streamlit
    STREAMLIT_SERVER_PORT: int = int(os.getenv("STREAMLIT_SERVER_PORT", "8501"))

    # Debug
    DEBUG: bool = os.getenv("DEBUG", "False").lower() == "true"
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")

    @classmethod
    def validate(cls) -> bool:
        """Valide que toutes les clés requises sont présentes"""
        required = [
            ("SUPABASE_URL", cls.SUPABASE_URL),
            ("SUPABASE_DB_PASSWORD", cls.SUPABASE_DB_PASSWORD),
            ("GOOGLE_MAPS_API_KEY", cls.GOOGLE_MAPS_API_KEY),
        ]

        missing = [name for name, value in required if not value]

        if missing:
            print(f"[ERROR] Configuration manquante: {', '.join(missing)}")
            print("   -> Verifier .env.local ou .env")
            return False

        print("[OK] Configuration valide")
        return True

    @classmethod
    def get_db_url(cls) -> str:
        """Construit l'URL de connexion Supabase"""
        return f"postgresql+psycopg2://postgres:{cls.SUPABASE_DB_PASSWORD}@db.fwcuftkjofoxyjbjzdnh.supabase.co:5432/postgres"


if __name__ == "__main__":
    Config.validate()
