#!/usr/bin/env python3
"""
File Organization & Archival Automation Script

Purpose: Automated project structure management, archival of obsolete files,
and maintenance of clean directory organization.

Usage:
    python file_organizer.py --scan                    # Analyze current structure
    python file_organizer.py --suggest-archives        # Get recommendations
    python file_organizer.py --archive --dry-run      # Preview archival
    python file_organizer.py --archive                 # Execute archival
    python file_organizer.py --generate-report        # Create inventory
"""

import os
import shutil
import json
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Tuple
import argparse
import logging


# Configuration
PROJECT_ROOT = Path(__file__).parent.parent.parent
ARCHIVE_ROOT = PROJECT_ROOT / "archive"
OBSOLETE_PATTERNS = {
    "app_versions": ["app_simple.py", "app_estimation.py", "app_estimation_fixed.py",
                     "app_estimation_tableau.py"],
    "import_scripts": ["import_dvf_schema.py", "import_dvf_data.py", "quick_import_dvf.py",
                       "final_import_dvf.py", "import_dvf_complete_schema.py",
                       "import_dvf_cleaned.py", "phase2_dvf_lite_final.py",
                       "correction_reimport_chablais_annemasse.py", "correction_phase3_communes.py"],
    "validation_scripts": ["validate_phase3_simple.py", "validate_phase3_mock_data.py"],
    "old_tests": ["Test.py", "test_data.py", "test_db_connection.py"],
    "phase_docs": ["PHASE2_RESUME_EXECUTIF.md", "PHASE2_RAPPORT_FINAL.md", "PHASE2_RECAP.txt",
                   "PHASE2_RECAP_POUR_PHASE3.md", "PHASE3_RECAP_COMPLET.md", "START_PHASE3_DEMAIN.md"],
    "old_scripts": ["create_views_and_indexes.py", "phase2_create_schema.sql",
                    "update_config.py", "phase3_import_chablais.py", "phase3_exec.py",
                    "phase4_validation.py"]
}

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class FileOrganizer:
    """Manages project file organization and archival."""

    def __init__(self, project_root: Path):
        self.project_root = project_root
        self.archive_root = project_root / "archive"
        self.archive_log = self.archive_root / "ARCHIVAL_LOG.json"

    def scan_structure(self) -> Dict:
        """Scan project structure and identify files."""
        logger.info(f"Scanning project structure: {self.project_root}")

        root_files = []
        file_categories = {}

        for item in self.project_root.iterdir():
            if item.is_file() and not item.name.startswith('.'):
                root_files.append(item.name)

                # Categorize
                if item.suffix == '.py':
                    category = 'Python Scripts'
                elif item.suffix == '.md':
                    category = 'Documentation'
                elif item.suffix == '.json':
                    category = 'Configuration'
                elif item.suffix == '.txt':
                    category = 'Text Files'
                elif item.suffix == '.csv':
                    category = 'Data Files'
                else:
                    category = 'Other'

                if category not in file_categories:
                    file_categories[category] = []
                file_categories[category].append(item.name)

        return {
            'total_files': len(root_files),
            'files': sorted(root_files),
            'by_category': file_categories
        }

    def suggest_archives(self) -> Dict:
        """Suggest files for archival based on patterns."""
        logger.info("Analyzing files for archival suggestions")

        suggestions = {}
        for category, patterns in OBSOLETE_PATTERNS.items():
            for filename in patterns:
                filepath = self.project_root / filename
                if filepath.exists():
                    if category not in suggestions:
                        suggestions[category] = []

                    mod_time = filepath.stat().st_mtime
                    mod_date = datetime.fromtimestamp(mod_time).strftime('%Y-%m-%d')

                    suggestions[category].append({
                        'file': filename,
                        'modified': mod_date,
                        'size_bytes': filepath.stat().st_size,
                        'archive_to': f"archive/{category.replace('_', '-')}/"
                    })

        return suggestions

    def archive_files(self, dry_run: bool = True) -> Tuple[List[str], List[str]]:
        """Archive obsolete files with metadata."""
        logger.info(f"Archival mode: {'DRY_RUN' if dry_run else 'EXECUTE'}")

        archived = []
        failed = []

        suggestions = self.suggest_archives()

        for category, files in suggestions.items():
            archive_dir = self._get_archive_dir(category)

            for file_info in files:
                src = self.project_root / file_info['file']
                timestamp = datetime.now().strftime('%Y%m%d')

                # Generate descriptive archive name
                name_parts = [file_info['file'].replace('.py', '').replace('.md', '')
                              .replace('.txt', '').replace('.sql', '')]
                name_parts.append(f"archived-{timestamp}")
                name_parts.append(category.replace('_', '-').rstrip('s'))

                dest_name = '-'.join(name_parts) + Path(file_info['file']).suffix
                dest = archive_dir / dest_name

                if dry_run:
                    logger.info(f"[DRY_RUN] Would archive: {src.name} → {dest.relative_to(self.project_root)}")
                    archived.append(str(dest.relative_to(self.project_root)))
                else:
                    try:
                        archive_dir.mkdir(parents=True, exist_ok=True)
                        shutil.move(str(src), str(dest))
                        logger.info(f"✓ Archived: {src.name} → {dest.relative_to(self.project_root)}")
                        archived.append(str(dest.relative_to(self.project_root)))

                        # Log archival
                        self._log_archival(src.name, dest, category)
                    except Exception as e:
                        logger.error(f"✗ Failed to archive {src.name}: {e}")
                        failed.append(file_info['file'])

        return archived, failed

    def _get_archive_dir(self, category: str) -> Path:
        """Get archive directory for category."""
        category_map = {
            'app_versions': 'obsolete_apps',
            'import_scripts': 'phase2/import_scripts',
            'validation_scripts': 'phase3/validation_scripts',
            'old_tests': 'phase1',
            'phase_docs': 'phase_docs',
            'old_scripts': 'phase2'
        }

        subdir = category_map.get(category, 'other')
        return self.archive_root / subdir

    def _log_archival(self, original: str, archived_path: Path, category: str):
        """Log archival operation."""
        try:
            log_data = {}
            if self.archive_log.exists():
                with open(self.archive_log) as f:
                    log_data = json.load(f)

            if 'archives' not in log_data:
                log_data['archives'] = []

            log_data['archives'].append({
                'original_filename': original,
                'archived_as': archived_path.name,
                'category': category,
                'timestamp': datetime.now().isoformat(),
                'path': str(archived_path.relative_to(self.project_root))
            })

            with open(self.archive_log, 'w') as f:
                json.dump(log_data, f, indent=2)
        except Exception as e:
            logger.warning(f"Could not log archival: {e}")

    def generate_report(self) -> str:
        """Generate structure report."""
        logger.info("Generating project structure report")

        structure = self.scan_structure()
        suggestions = self.suggest_archives()

        report = []
        report.append("=" * 70)
        report.append("PROJECT FILE STRUCTURE REPORT")
        report.append(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        report.append("=" * 70)
        report.append("")

        report.append("ROOT DIRECTORY CONTENTS:")
        report.append(f"Total files in root: {structure['total_files']}")
        report.append("")

        for category, files in sorted(structure['by_category'].items()):
            report.append(f"{category}: ({len(files)} files)")
            for f in sorted(files):
                report.append(f"  - {f}")
            report.append("")

        total_archivable = sum(len(files) for files in suggestions.values())
        if total_archivable > 0:
            report.append("=" * 70)
            report.append(f"ARCHIVAL CANDIDATES: {total_archivable} files")
            report.append("=" * 70)
            report.append("")

            for category, files in sorted(suggestions.items()):
                report.append(f"{category}: ({len(files)} files)")
                for f in files:
                    report.append(f"  - {f['file']} (modified: {f['modified']}, {f['size_bytes']} bytes)")
                report.append("")

        report.append("=" * 70)
        return "\n".join(report)

    def clean_pycache(self, dry_run: bool = True) -> Tuple[int, int]:
        """Remove Python cache files."""
        logger.info(f"Cleaning Python cache (dry_run={dry_run})")

        removed = 0
        skipped = 0

        # Find __pycache__ directories
        for pycache in self.project_root.rglob('__pycache__'):
            if dry_run:
                logger.info(f"[DRY_RUN] Would remove: {pycache.relative_to(self.project_root)}")
                skipped += 1
            else:
                try:
                    shutil.rmtree(pycache)
                    logger.info(f"✓ Removed: {pycache.relative_to(self.project_root)}")
                    removed += 1
                except Exception as e:
                    logger.error(f"✗ Failed to remove {pycache}: {e}")
                    skipped += 1

        # Find .pyc files
        for pyc in self.project_root.rglob('*.pyc'):
            if dry_run:
                logger.info(f"[DRY_RUN] Would remove: {pyc.relative_to(self.project_root)}")
                skipped += 1
            else:
                try:
                    pyc.unlink()
                    logger.info(f"✓ Removed: {pyc.relative_to(self.project_root)}")
                    removed += 1
                except Exception as e:
                    logger.error(f"✗ Failed to remove {pyc}: {e}")
                    skipped += 1

        return removed, skipped


def main():
    parser = argparse.ArgumentParser(
        description="File organization and archival automation"
    )
    parser.add_argument('--scan', action='store_true', help='Scan project structure')
    parser.add_argument('--suggest-archives', action='store_true', help='Suggest files for archival')
    parser.add_argument('--archive', action='store_true', help='Archive obsolete files')
    parser.add_argument('--dry-run', action='store_true', help='Preview changes without executing')
    parser.add_argument('--generate-report', action='store_true', help='Generate structure report')
    parser.add_argument('--clean-pycache', action='store_true', help='Remove Python cache files')

    args = parser.parse_args()

    organizer = FileOrganizer(PROJECT_ROOT)

    if args.scan or not any([args.archive, args.suggest_archives, args.generate_report, args.clean_pycache]):
        structure = organizer.scan_structure()
        print(f"\nProject Structure Summary:")
        print(f"  Total files in root: {structure['total_files']}")
        print(f"\n  By category:")
        for category, files in sorted(structure['by_category'].items()):
            print(f"    - {category}: {len(files)} files")

    if args.suggest_archives:
        suggestions = organizer.suggest_archives()
        print(f"\nArchival Suggestions:")
        for category, files in suggestions.items():
            print(f"  {category}: {len(files)} files")
            for f in files:
                print(f"    - {f['file']}")

    if args.archive:
        archived, failed = organizer.archive_files(dry_run=args.dry_run)
        print(f"\nArchival Summary:")
        print(f"  Processed: {len(archived)} files")
        if failed:
            print(f"  Failed: {len(failed)} files")
            for f in failed:
                print(f"    - {f}")

    if args.generate_report:
        report = organizer.generate_report()
        print(f"\n{report}")

        report_file = PROJECT_ROOT / "FILE_STRUCTURE_REPORT.txt"
        with open(report_file, 'w') as f:
            f.write(report)
        print(f"  Report saved to: {report_file}")

    if args.clean_pycache:
        removed, skipped = organizer.clean_pycache(dry_run=args.dry_run)
        print(f"\nPython Cache Cleanup:")
        print(f"  Removed: {removed}")
        print(f"  Skipped: {skipped}")


if __name__ == "__main__":
    main()
