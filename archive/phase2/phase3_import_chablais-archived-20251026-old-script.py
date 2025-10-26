#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
PHASE 3B : Import DVF+ Chablais avec Filtrage Géographique
Parse dvf_plus_d74.sql et import SEULEMENT mutations Chablais
"""

import os
import sys
import re
from io import StringIO
from dotenv import load_dotenv
import psycopg2
from psycopg2.extras import execute_batch
from tqdm import tqdm
import logging

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Codes postaux Chablais (confirmés Phase 0)
CODES_CHABLAIS = {
    '74110', '74140', '74200', '74270', '74360',
    '74390', '74420', '74430', '74470', '74500', '74890'
}

# Codes INSEE équivalents (à extraire des adresses)
COMMUNES_CHABLAIS = set()

load_dotenv()

# Configuration Supabase
DB_HOST = "db.fwcuftkjofoxyjbjzdnh.supabase.co"
DB_USER = "postgres"
DB_PASSWORD = os.getenv("SUPABASE_DB_PASSWORD")
DB_NAME = "postgres"
DB_PORT = 5432

SQL_FILE = r"c:\analyse_immobiliere\data\raw\DVFPlus_2025-1-0_SQL_LAMB93_R084-ED251\1_DONNEES_LIVRAISON\dvf_plus_d74.sql"


class DVFImporter:
    """Importe DVF+ avec filtrage géographique"""

    def __init__(self):
        self.conn = None
        self.cursor = None
        self.mutation_ids = set()  # IDs mutations Chablais
        self.stats = {
            'adresses_total': 0,
            'adresses_chablais': 0,
            'mutations_total': 0,
            'mutations_chablais': 0,
            'dispositions_imported': 0,
            'locaux_imported': 0
        }

    def connect(self):
        """Connecter à Supabase"""
        logger.info(f"Connexion à Supabase {DB_HOST}...")
        self.conn = psycopg2.connect(
            host=DB_HOST,
            user=DB_USER,
            password=DB_PASSWORD,
            database=DB_NAME,
            port=DB_PORT
        )
        self.cursor = self.conn.cursor()
        logger.info("✅ Connexion réussie")

    def disconnect(self):
        """Fermer connexion"""
        if self.cursor:
            self.cursor.close()
        if self.conn:
            self.conn.close()

    def parse_and_import(self):
        """Parse dvf_plus_d74.sql et importe données Chablais"""
        logger.info("\n" + "="*80)
        logger.info("PHASE 3B : IMPORT DVF+ CHABLAIS")
        logger.info("="*80)

        self.connect()

        try:
            # Étape 1 : Parser adresses pour identifier codes postaux Chablais
            logger.info("\n[Etape 1/4] Parsing adresses pour identifiction communes...")
            self.parse_adresses()

            # Étape 2 : Parser et filtrer mutations
            logger.info("\n[Etape 2/4] Parsing et filtrage mutations...")
            self.parse_mutations()

            # Étape 3 : Parser et filtrer données relationnelles
            logger.info("\n[Etape 3/4] Import donnees relationnelles (disposition, local, etc.)...")
            self.parse_related_tables()

            # Étape 4 : Validation
            logger.info("\n[Etape 4/4] Validation données importees...")
            self.validate()

            self.conn.commit()
            logger.info("\n✅ IMPORT CHABLAIS COMPLETE")

        except Exception as e:
            logger.error(f"❌ ERREUR: {e}")
            self.conn.rollback()
            raise
        finally:
            self.disconnect()

    def parse_adresses(self):
        """Parser table adresses pour identifier communes Chablais"""
        current_table = None

        with open(SQL_FILE, 'r', encoding='utf-8', errors='ignore') as f:
            in_adresse = False

            for line in f:
                if 'COPY dvf_plus_2025_2.dvf_plus_adresse' in line and 'dispoparc' not in line and '_local' not in line:
                    in_adresse = True
                    continue

                if in_adresse:
                    if line.startswith(r'\.'):
                        logger.info(f"  ✅ {self.stats['adresses_total']:,} adresses totales")
                        logger.info(f"  ✅ {self.stats['adresses_chablais']:,} adresses Chablais ({100*self.stats['adresses_chablais']/max(1, self.stats['adresses_total']):.1f}%)")
                        break

                    if line.strip() and not line.startswith('COPY'):
                        self.stats['adresses_total'] += 1
                        fields = line.strip().split('\t')

                        if len(fields) >= 7:
                            codepostal = fields[6]
                            if codepostal in CODES_CHABLAIS:
                                self.stats['adresses_chablais'] += 1
                                # Importer l'adresse
                                try:
                                    self.cursor.execute(
                                        """INSERT INTO dvf_plus_2025_2.dvf_plus_adresse
                                           VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)""",
                                        fields if fields[0] != '\\N' else tuple(None if f == '\\N' else f for f in fields)
                                    )
                                except:
                                    pass  # Skip duplicates

    def parse_mutations(self):
        """Parser table mutations et filtrer par communes Chablais"""
        in_mutation = False
        batch = []
        batch_size = 1000

        with open(SQL_FILE, 'r', encoding='utf-8', errors='ignore') as f:
            for line in tqdm(f, desc="Parsing mutations", unit=" lines"):
                if 'COPY dvf_plus_2025_2.dvf_plus_mutation' in line and 'article_cgi' not in line:
                    in_mutation = True
                    continue

                if in_mutation:
                    if line.startswith(r'\.'):
                        # Flush dernier batch
                        if batch:
                            self.batch_insert('dvf_plus_2025_2.dvf_plus_mutation', batch)
                        logger.info(f"  ✅ {self.stats['mutations_chablais']:,} mutations Chablais importees")
                        break

                    if line.strip() and not line.startswith('COPY'):
                        self.stats['mutations_total'] += 1
                        fields = line.strip().split('\t')

                        # Vérifier si commune est Chablais
                        # l_codinsee est à index 18 (après communes)
                        if len(fields) > 18:
                            communes_str = fields[18]  # Format: "1$74200$THONON..."

                            # Chercher code postal Chablais
                            is_chablais = False
                            for code in CODES_CHABLAIS:
                                if code in communes_str:
                                    is_chablais = True
                                    break

                            if is_chablais:
                                self.stats['mutations_chablais'] += 1
                                idmutation = fields[0]
                                self.mutation_ids.add(idmutation)
                                batch.append(fields)

                                if len(batch) >= batch_size:
                                    self.batch_insert('dvf_plus_2025_2.dvf_plus_mutation', batch)
                                    batch = []

    def parse_related_tables(self):
        """Parser et importer tables relationnelles filtrées"""
        current_table = None
        batch = {}
        batch_size = 5000

        table_columns = {
            'dvf_plus_disposition': 6,
            'dvf_plus_local': 21,
            'dvf_plus_parcelle': 7,
            'dvf_plus_lot': 7,
            'dvf_plus_suf': 10,
            'dvf_plus_volume': 5,
            'dvf_plus_disposition_parcelle': 38
        }

        for table_name in table_columns:
            batch[table_name] = []

        with open(SQL_FILE, 'r', encoding='utf-8', errors='ignore') as f:
            for line in tqdm(f, desc="Parsing tables", unit=" lines"):
                for table_name in table_columns:
                    if f'COPY dvf_plus_2025_2.{table_name}' in line:
                        current_table = table_name
                        break

                if current_table:
                    if line.startswith(r'\.'):
                        if batch[current_table]:
                            self.batch_insert(f'dvf_plus_2025_2.{current_table}', batch[current_table])
                        current_table = None
                        continue

                    if line.strip() and not line.startswith('COPY'):
                        fields = line.strip().split('\t')
                        idmutation_idx = 3 if current_table == 'dvf_plus_disposition' else 3

                        if len(fields) > idmutation_idx:
                            idmutation = fields[idmutation_idx]
                            if idmutation in self.mutation_ids:
                                batch[current_table].append(fields)

                                if len(batch[current_table]) >= batch_size:
                                    self.batch_insert(f'dvf_plus_2025_2.{current_table}', batch[current_table])
                                    batch[current_table] = []

    def batch_insert(self, table, data):
        """Insérer batch de données"""
        if not data:
            return

        # Construire requête INSERT
        num_cols = len(data[0])
        placeholders = ','.join(['%s'] * num_cols)

        sql = f"INSERT INTO {table} VALUES ({placeholders}) ON CONFLICT DO NOTHING"

        try:
            execute_batch(self.cursor, sql, data, page_size=1000)
            self.conn.commit()
        except Exception as e:
            logger.warning(f"  Batch insert warning: {e}")
            self.conn.rollback()

    def validate(self):
        """Valider les données importées"""
        try:
            self.cursor.execute("SELECT COUNT(*) FROM dvf_plus_2025_2.dvf_plus_mutation")
            mutation_count = self.cursor.fetchone()[0]

            self.cursor.execute("SELECT COUNT(*) FROM dvf_plus_2025_2.dvf_plus_local")
            local_count = self.cursor.fetchone()[0]

            self.cursor.execute("SELECT COUNT(*) FROM dvf_plus_2025_2.dvf_plus_disposition")
            dispo_count = self.cursor.fetchone()[0]

            logger.info(f"\n📊 VALIDATION:")
            logger.info(f"  Mutations: {mutation_count:,}")
            logger.info(f"  Locaux: {local_count:,}")
            logger.info(f"  Dispositions: {dispo_count:,}")

        except Exception as e:
            logger.warning(f"  Validation warning: {e}")


def main():
    """Point d'entrée"""
    importer = DVFImporter()
    importer.parse_and_import()


if __name__ == "__main__":
    main()
