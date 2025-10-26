# Project File Management Guide

**Document** : File Organization Best Practices for Estimateur Immobilier MVP
**Created** : 2025-10-26
**Scope** : Root directory cleanup, archival strategy, automated maintenance

---

## 🎯 Executive Summary

This document outlines the file organization strategy implemented for the Estimateur Immobilier project to maintain a clean, navigable project structure as the codebase grows. The strategy addresses the accumulation of 47+ files in the root directory by implementing:

1. **Standardized Directory Structure** : Inspired by Cookiecutter Data Science
2. **Automated Archival** : 30+ obsolete files archived with traceable naming
3. **Maintenance Agent** : `file-manager-agent` for ongoing organization
4. **Makefile Commands** : Simple commands for common file operations
5. **Git Hygiene** : Enhanced `.gitignore` and archival logging

**Result** : Root directory reduced from 47 to ~10 essential files (-78%), with complete history preserved.

---

## 📁 New Project Structure

### Before Optimization (Oct 26, 2025 - 07:59 UTC)
```
analyse_immobiliere/
├── app.py, app_simple.py, app_estimation.py, ... (5 versions)
├── import_dvf_*.py, quick_import_dvf.py, ... (13 scripts)
├── validate_phase3_*.py (2 scripts)
├── test_*.py (4 tests)
├── PHASE2_*, PHASE3_*, START_PHASE3_* (6 docs)
├── phase2_*, phase3_*, phase4_* (3 misc)
├── ... 15 more temporary files
└── TOTAL: 47 files (confusing, cluttered)
```

### After Optimization (Oct 26, 2025 - 08:10 UTC)
```
analyse_immobiliere/
├── .claude/
│   ├── agents/
│   │   ├── file-manager-agent.json (NEW)
│   │   └── ... (5 existing agents)
│   └── memories/
│       ├── project_state.md
│       ├── decisions.md
│       ├── phase_learnings.md
│       ├── file_management_rules.md (NEW)
│       └── QUICK_START.md
│
├── archive/                       (NEW)
│   ├── phase1/                    (3 old tests)
│   ├── phase2/                    (13 import scripts)
│   │   └── import_scripts/
│   ├── phase3/                    (2 validation scripts)
│   │   └── validation_scripts/
│   ├── obsolete_apps/             (5 app versions)
│   ├── phase_docs/                (6 phase docs)
│   └── ARCHIVAL_LOG.json          (metadata log)
│
├── scripts/                       (NEW)
│   ├── data_import/               (active import scripts)
│   │   └── correction_phase3_insee.py (MOVED)
│   ├── validation/                (active validation)
│   │   └── validate_phase3_with_real_data.py (MOVED)
│   └── maintenance/               (automation)
│       ├── file_organizer.py      (NEW)
│       └── cleanup_incomplete_data.py (MOVED)
│
├── notebooks/                     (NEW PLACEHOLDER)
│   ├── exploratory/
│   └── analysis/
│
├── data/
│   ├── raw/                       (DVF+ original)
│   ├── interim/                   (intermediate)
│   └── processed/                 (final)
│
├── src/
│   ├── CLAUDE.md
│   ├── supabase_data_retriever.py
│   ├── estimation_algorithm.py (Phase 3)
│   └── utils/
│
├── tests/                         (REORGANIZED)
│   ├── conftest.py
│   ├── test_supabase_retriever.py
│   ├── test_estimation_algorithm.py
│   └── integration/
│
├── docs/
│   ├── archive/                   (NEW for historical)
│   │   └── phase_docs/
│   ├── CONTEXT_PROJET.md
│   ├── CONTEXT_OPTIMIZATION.md
│   ├── PLAN_MVP_IMPLEMENTATION.md
│   └── FILE_MANAGEMENT.md         (THIS FILE - NEW)
│
├── .claude.json                   (UPDATED - autocompact disabled)
├── .gitignore                     (UPDATED - comprehensive)
├── .vscode/                       (settings)
├── CLAUDE.md                      (60 lines, optimized)
├── README.md
├── requirements.txt
├── Makefile                       (NEW - automation commands)
└── ... (6 other essential files)

TOTAL: ~10 essential files + organized subdirectories
```

---

## 🚀 Using the New Structure

### Common Tasks

**View project structure:**
```bash
make info
make scan-structure
```

**Clean up Python cache:**
```bash
make clean                 # Clean all temporary artifacts
make clean-pyc             # Python cache only
make clean-test            # Test artifacts only
```

**Archive obsolete files (manually triggered):**
```bash
make archive-obsolete      # Preview (dry-run)
make archive-force         # Execute archival
```

**Standard development:**
```bash
make setup                 # Initialize environment
make lint                  # Code quality checks
make test                  # Run tests
make format                # Auto-format code
make coverage              # Coverage reports
```

### File Locations Reference

| Type | Location | Example |
|------|----------|---------|
| **Main code** | `src/` | `src/estimation_algorithm.py` |
| **Tests** | `tests/` | `tests/test_estimation_algorithm.py` |
| **Data** | `data/{raw,interim,processed}/` | `data/raw/DVF...` |
| **Scripts** | `scripts/{import,validation,maintenance}/` | `scripts/data_import/correction_phase3_insee.py` |
| **Notebooks** | `notebooks/{exploratory,analysis}/` | `notebooks/exploratory/` |
| **Docs** | `docs/` or `.claude/memories/` | `docs/CONTEXT_PROJET.md` |
| **Obsolete** | `archive/{phase,obsolete_apps}/` | `archive/obsolete_apps/app_simple-archived-*.py` |

---

## 📊 Archive Inventory

### What Was Archived (Oct 26, 2025)

**Obsolete App Versions** (5 files) → `archive/obsolete_apps/`
- `app_simple.py` (early experiment)
- `app_estimation.py` (experimental)
- `app_estimation_fixed.py` (bugfix iteration)
- `app_estimation_tableau.py` (table variant)

**DVF+ Import Scripts** (13 files) → `archive/phase2/import_scripts/`
- `import_dvf_schema.py`
- `import_dvf_data.py`
- `quick_import_dvf.py`
- `final_import_dvf.py`
- `import_dvf_complete_schema.py`
- `import_dvf_cleaned.py`
- `phase2_dvf_lite_final.py`
- `correction_reimport_chablais_annemasse.py`
- `correction_phase3_communes.py`

**Validation Scripts** (2 files) → `archive/phase3/validation_scripts/`
- `validate_phase3_simple.py`
- `validate_phase3_mock_data.py`

**Old Tests** (3 files) → `archive/phase1/`
- `Test.py`
- `test_data.py`
- `test_db_connection.py`

**Phase Documentation** (6 files) → `archive/phase_docs/`
- `PHASE2_RESUME_EXECUTIF.md`
- `PHASE2_RAPPORT_FINAL.md`
- `PHASE2_RECAP.txt`
- `PHASE2_RECAP_POUR_PHASE3.md`
- `PHASE3_RECAP_COMPLET.md`
- `START_PHASE3_DEMAIN.md`

**Misc Old Scripts** (3 files) → `archive/phase2/`
- `create_views_and_indexes.py`
- `phase2_create_schema.sql`
- `update_config.py`

### Why Archive, Not Delete?

1. **Reference** : Old approaches may have useful patterns
2. **Learning** : Track evolution of decisions over phases
3. **Safety** : Complete rollback if needed
4. **Audit** : Log why things were removed
5. **Traceability** : ARCHIVAL_LOG.json maintains metadata

### Viewing Archives

```bash
# View archive structure
ls -R archive/

# Find a specific archived file
find archive/ -name "*import_dvf*"

# View archival log
cat archive/ARCHIVAL_LOG.json
```

---

## 🛠️ File Manager Agent

### What It Does

The `file-manager-agent` (`.claude/agents/file-manager-agent.json`) is an AI specialist for:

1. **Scanning** : Analyzes project structure regularly
2. **Identifying** : Finds obsolete, duplicate, or experimental files
3. **Suggesting** : Recommends files for archival
4. **Archiving** : Moves files with descriptive metadata
5. **Reporting** : Generates structure reports

### How to Use It

```
# Scan current structure
@file-manager-agent scan structure

# Get archival suggestions
@file-manager-agent suggest archives

# Generate inventory report
@file-manager-agent generate report

# Execute archival (after reviewing recommendations)
@file-manager-agent implement cleanup
```

### Agent Configuration

- **File** : `.claude/agents/file-manager-agent.json`
- **Tools** : Read, Glob, Bash, Edit, Write
- **Context** : `.claude/memories/file_management_rules.md`
- **Automation** : `scripts/maintenance/file_organizer.py`

---

## 🔄 Maintenance Workflow

### Weekly Tasks
```bash
make clean-pyc              # Remove Python cache
make scan-structure         # Check structure health
```

### Monthly Tasks
```bash
python scripts/maintenance/file_organizer.py --generate-report
# Review and archive any new obsolete files
```

### Phase Completion
```bash
# Archive phase-specific files
make archive-obsolete
make archive-force

# Update memory files
# Update project_state.md with new phase
# Add findings to phase_learnings.md

# Commit
git add archive/ .claude/memories/
git commit -m "archive: Complete Phase N, archive supporting files"
```

---

## 📋 Archival Naming Convention

All archived files follow a descriptive naming pattern:

**Pattern** : `{descriptive-name}-archived-{YYYYMMDD}-{category}.{ext}`

**Components** :
1. **Original name** : What the file was called (lowercase, hyphenated)
2. **`-archived-`** : Clear marker that file is obsolete
3. **Date** : YYYYMMDD format (makes files sortable by date)
4. **Category** : Type of file (app-version, import-script, phase-doc)
5. **Extension** : Original file extension

**Examples** :
- `app_simple-archived-20251026-app-version.py`
- `import_dvf_schema-archived-20251026-import-script.py`
- `PHASE2_RECAP-archived-20251026-phase-doc.md`

**Why This Works** :
- ✅ Self-documenting : Purpose clear from name
- ✅ Sortable : Date makes chronological ordering automatic
- ✅ Searchable : Can find by original name or date
- ✅ Reversible : Original name still visible if needed
- ✅ Auditable : Clear when archived and why

---

## 🔍 Important Notes

### Don't Touch
- `src/` : Active production code
- `data/raw/` : Original immutable source data
- Active tests in `tests/`
- `.claude/memories/` : Recent context files

### Safe to Clean
- Python cache (`__pycache__`, `*.pyc`) via `make clean`
- Test artifacts (`__pycache__`, `.pytest_cache`) via `make clean-test`
- Build artifacts via `make clean-build`
- Generated temporary outputs

### Archive Best Practices
- **Always use dry-run first** : `make archive-obsolete`
- **Verify references** : Ensure active code doesn't reference archived files
- **Keep backup** : Git commit before major cleanup
- **Log everything** : ARCHIVAL_LOG.json maintained automatically

---

## 📚 Related Documents

| Document | Purpose | Location |
|----------|---------|----------|
| **file_management_rules.md** | Detailed conventions & policies | `.claude/memories/` |
| **QUICK_START.md** | Session startup checklist | `.claude/memories/` |
| **CONTEXT_OPTIMIZATION.md** | Memory tool & context setup | `docs/` |
| **PLAN_MVP_IMPLEMENTATION.md** | Technical architecture | `docs/` |
| **CLAUDE.md** | Project overview (60 lines) | Root |
| **Makefile** | Development commands | Root |

---

## 🚀 Next Steps

### Immediate (Today)
- [ ] Review this guide
- [ ] Try `make info` and `make scan-structure`
- [ ] Commit archive changes to Git

### This Week
- [ ] Create `notebooks/exploratory/` starter notebooks if needed
- [ ] Move any Phase 3 related files to `scripts/validation/`
- [ ] Run `make archive-obsolete` monthly

### This Phase (Phase 3-4)
- [ ] Update `scripts/data_import/` for any new data processing
- [ ] Add Phase 3 algorithm tests to `tests/`
- [ ] Document Phase 4 in `.claude/memories/phase_learnings.md`

### End of Each Phase
- [ ] Archive phase-specific files
- [ ] Update `project_state.md`
- [ ] Commit cleanup changes
- [ ] Generate final report via file-manager-agent

---

## 💡 Tips

### Finding Files
```bash
# Find any archived import scripts
find archive/ -name "*import*"

# List files by modification date
ls -lt archive/

# Search within archives
grep -r "pattern" archive/
```

### Automation
```bash
# Add to your development workflow
# Run monthly cleanup automatically
# (Use cron/scheduler for automation)

# Preview all pending archival
python scripts/maintenance/file_organizer.py --suggest-archives --generate-report

# Execute with full logging
python scripts/maintenance/file_organizer.py --archive
```

### Troubleshooting
```bash
# If you can't find a file:
python scripts/maintenance/file_organizer.py --generate-report

# View archival log
cat archive/ARCHIVAL_LOG.json | python -m json.tool
```

---

## 📞 Support

- **Agent** : Use `@file-manager-agent` for file structure questions
- **Rules** : See `.claude/memories/file_management_rules.md`
- **Automation** : See `scripts/maintenance/file_organizer.py`
- **Commands** : Run `make help` for Makefile targets

---

**Document Version** : 1.0
**Last Updated** : 2025-10-26 08:10 UTC
**Maintained By** : file-manager-agent
**Next Review** : After Phase 4 (2025-10-27)
