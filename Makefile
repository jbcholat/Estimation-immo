.PHONY: help setup clean clean-pyc clean-test clean-build scan-structure archive-obsolete setup-dirs install-pre-commit format lint test coverage

help:
	@echo "Estimateur Immobilier MVP - Development Commands"
	@echo "==============================================="
	@echo ""
	@echo "Setup & Installation:"
	@echo "  make setup              Create virtual environment & install dependencies"
	@echo "  make setup-dirs         Create project directory structure"
	@echo ""
	@echo "Python & Cache:"
	@echo "  make clean-pyc          Remove Python cache (__pycache__, *.pyc)"
	@echo "  make clean-test         Remove test cache (.pytest_cache)"
	@echo "  make clean-build        Remove build artifacts"
	@echo "  make clean              Remove all temporary artifacts"
	@echo ""
	@echo "Project Organization:"
	@echo "  make scan-structure     Scan and report project file structure"
	@echo "  make archive-obsolete   Preview obsolete files for archival (dry-run)"
	@echo "  make archive-force      Execute archival of obsolete files"
	@echo ""
	@echo "Code Quality:"
	@echo "  make lint               Run linters (flake8, pylint, mypy)"
	@echo "  make format             Format code with black, isort"
	@echo "  make test               Run test suite"
	@echo "  make coverage           Run tests with coverage report"
	@echo ""
	@echo "Data & Processing:"
	@echo "  make validate-data      Validate Supabase dataset"
	@echo ""

# ============================================================================
# SETUP & INSTALLATION
# ============================================================================

setup: setup-dirs
	@echo "Creating Python virtual environment..."
	python -m venv venv
	@echo "Installing dependencies..."
	./venv/Scripts/pip install -r requirements.txt
	@echo "Setup complete! Run 'source venv/Scripts/activate' to enter environment"

setup-dirs:
	@echo "Creating project directory structure..."
	mkdir -p archive/phase1
	mkdir -p archive/phase2/import_scripts
	mkdir -p archive/phase2
	mkdir -p archive/phase3/validation_scripts
	mkdir -p archive/obsolete_apps
	mkdir -p archive/phase_docs
	mkdir -p scripts/data_import
	mkdir -p scripts/validation
	mkdir -p scripts/maintenance
	mkdir -p tests/integration
	mkdir -p notebooks/exploratory
	mkdir -p notebooks/analysis
	mkdir -p data/interim
	mkdir -p data/processed
	@echo "✓ Directory structure created"

# ============================================================================
# CLEANING
# ============================================================================

clean-pyc:
	@echo "Removing Python cache files..."
	find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete
	find . -type f -name "*.pyo" -delete
	find . -type f -name "*.egg-info" -delete
	@echo "✓ Python cache cleaned"

clean-test:
	@echo "Removing test cache..."
	rm -rf .pytest_cache
	rm -rf .coverage
	rm -rf htmlcov
	@echo "✓ Test cache cleaned"

clean-build:
	@echo "Removing build artifacts..."
	rm -rf build
	rm -rf dist
	rm -rf *.egg-info
	@echo "✓ Build artifacts cleaned"

clean: clean-pyc clean-test clean-build
	@echo "✓ All temporary artifacts cleaned"

# ============================================================================
# PROJECT ORGANIZATION
# ============================================================================

scan-structure:
	@echo "Scanning project file structure..."
	python scripts/maintenance/file_organizer.py --scan --generate-report

archive-obsolete:
	@echo "Previewing files for archival (DRY-RUN)..."
	python scripts/maintenance/file_organizer.py --archive --dry-run

archive-force:
	@echo "⚠️  Archiving obsolete files (EXECUTE MODE)..."
	python scripts/maintenance/file_organizer.py --archive

clean-pycache:
	@echo "Cleaning Python cache files..."
	python scripts/maintenance/file_organizer.py --clean-pycache

# ============================================================================
# CODE QUALITY
# ============================================================================

lint:
	@echo "Running linters..."
	-flake8 src/ tests/ --max-line-length=100
	-pylint src/
	-mypy src/ --ignore-missing-imports
	@echo "✓ Linting complete"

format:
	@echo "Formatting code..."
	black src/ tests/ --line-length=100
	isort src/ tests/ --profile black
	@echo "✓ Code formatted"

# ============================================================================
# TESTING
# ============================================================================

test:
	@echo "Running test suite..."
	pytest tests/ -v

coverage:
	@echo "Running tests with coverage..."
	pytest tests/ -v --cov=src/ --cov-report=term-missing --cov-report=html
	@echo "✓ Coverage report: htmlcov/index.html"

# ============================================================================
# DATA VALIDATION
# ============================================================================

validate-data:
	@echo "Validating Supabase dataset..."
	python scripts/validation/validate_phase3_with_real_data.py

# ============================================================================
# DEVELOPMENT
# ============================================================================

dev:
	@echo "Starting development environment..."
	streamlit run app.py

db-shell:
	@echo "Opening Supabase connection shell..."
	python -c "from src.utils.config import load_env; from supabase import create_client; import os; load_env(); client = create_client(os.getenv('SUPABASE_URL'), os.getenv('SUPABASE_KEY')); print('Supabase connected'); import code; code.interact(local=locals())"

# ============================================================================
# INFO
# ============================================================================

info:
	@echo "Project Information:"
	@echo "  Name: Estimateur Immobilier MVP"
	@echo "  Zone: Chablais/Annemasse (Haute-Savoie)"
	@echo "  Phase: 3 (Algorithm Development)"
	@echo "  Stack: Supabase + Streamlit + Google Maps"
	@echo ""
	@echo "Current Structure:"
	@python -c "from pathlib import Path; import os; root=Path('.'); print(f'  Root files: {len([f for f in root.iterdir() if f.is_file() and not f.name.startswith(\".\")])}'); print(f'  Archive: {len(list((root / \"archive\").rglob(\"*\")))} items' if (root / 'archive').exists() else '  Archive: not created')"
