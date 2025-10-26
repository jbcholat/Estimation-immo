# File Management Rules & Conventions

**Created** : 2025-10-26
**Last Updated** : 2025-10-26
**Maintained By** : file-manager-agent

---

## 📋 Directory Structure Standards

### Standardized Layout (Cookiecutter Data Science Inspired)

```
analyse_immobiliere/
├── archive/              # Historical & obsolete files
├── data/                 # All project data (lifecycle stages)
├── docs/                 # Active project documentation
├── scripts/              # Reusable automation scripts
├── src/                  # Production source code
├── tests/                # Test suite
├── notebooks/            # Jupyter notebooks (exploratory work)
├── .claude/              # Claude Code configuration
├── .vscode/              # VS Code workspace settings
├── CLAUDE.md             # Project context (60 lines, optimized)
├── README.md             # Project overview
├── requirements.txt      # Python dependencies
├── Makefile              # Common development commands
└── .gitignore            # Version control exclusions
```

### Archive Structure

```
archive/
├── phase1/               # Phase 1 experimental work
├── phase2/               # Phase 2 supporting files
│   ├── import_scripts/   # DVF+ import iterations
│   └── *.py              # Utility scripts
├── phase3/               # Phase 3 supporting files
│   └── validation_scripts/
├── obsolete_apps/        # Old app_*.py versions
└── phase_docs/           # Historical phase documentation
```

### Data Lifecycle

```
data/
├── raw/                  # Original, immutable source data
│   └── DVFPlus_2025-1-0_SQL_LAMB93_R084-ED251/
├── external/             # Third-party data & reference
├── interim/              # Intermediate transformations
│   └── feature_engineered_data.parquet
└── processed/            # Final analysis-ready datasets
    └── chablais_annemasse_2014_2025.parquet
```

### Scripts Organization

```
scripts/
├── data_import/          # Data loading & preprocessing
│   └── correction_phase3_insee.py (ACTIVE, Phase 2)
├── validation/           # Data & model validation
│   └── validate_phase3_with_real_data.py (ACTIVE, Phase 2)
└── maintenance/          # Utilities & cleanup
    ├── file_organizer.py (automation)
    └── cleanup_incomplete_data.py
```

---

## 📝 Naming Conventions

### Active Files (Root Directory)

| File Type | Convention | Examples |
|-----------|-----------|----------|
| Main code | `{name}.py` | `app.py`, `main.py` |
| Config | `{name}.{ext}` | `CLAUDE.md`, `README.md` |
| Package config | `pyproject.toml`, `requirements.txt` | Standard names |
| Docs | `{DESCRIPTIVE_NAME}.md` | `FILE_MANAGEMENT.md` |

### Archived Files (With Metadata)

**Pattern** : `{original-name}-archived-{YYYYMMDD}-{category}.{ext}`

**Examples** :
- `app_simple-archived-20251026-app-version.py`
- `import_dvf_schema-archived-20251026-import-script.py`
- `PHASE2_RECAP-archived-20251026-phase-doc.md`

**Components** :
1. Original descriptive name (lowercased, hyphens)
2. `-archived-` separator
3. Date (YYYYMMDD format)
4. Category (hyphen-separated)
5. Original file extension

### Rationale for Archive Naming
- **Descriptive** : Immediately understand file purpose
- **Timestamped** : Track when archived (find by date)
- **Categorized** : Understand classification (app vs import vs validation)
- **Reversible** : Original name still visible
- **Sortable** : Chronological order in file explorers

---

## 🗑️ Archival Policy

### What Gets Archived (Not Deleted!)

**Experimental Code** :
- Multiple versions of same functionality (`app_v1.py`, `app_v2.py`)
- Failed approaches or prototypes
- One-time setup scripts (once executed successfully)
- ✅ Action : Archive to `archive/obsolete_apps/` or `archive/phase{N}/`

**Superseded Implementations** :
- Replaced import scripts (after validation with new versions)
- Old validation approaches
- ✅ Action : Archive to `archive/phase{N}/{category}/`

**Phase-Specific Documentation** :
- Phase recap documents (after phase completion)
- Historical planning documents
- ✅ Action : Archive to `archive/phase_docs/`

### What Gets Deleted

**Never Delete** :
- Source data (data/raw/)
- Production code (src/)
- Active tests

**Safe to Delete** :
- Python cache (`__pycache__/`, `*.pyc`) via `make clean-pyc`
- Build artifacts via `make clean-build`
- Test cache via `make clean-test`
- Generated temporary outputs

---

## 📊 Retention Policies

### By Category

| Category | Retention | Policy | Review |
|----------|-----------|--------|--------|
| **Experimental Code** | Indefinite | Keep for reference | Quarterly |
| **Successful Scripts** | Active phase | Keep during development | End of phase → archive |
| **Phase Docs** | Indefinite | Archive after completion | After each phase |
| **Model Artifacts** | Current + 1 old | Keep for comparison | Weekly via DVC |
| **Interim Data** | Active development | Delete after validation | End of feature |
| **Test Artifacts** | None | Delete after test run | Auto cleanup |
| **Logs** | 30 days | Auto-cleanup | Via script |

### Archival Triggers

**Manual Archival** :
- Phase completion : Archive phase-specific files
- Script supersedes another : Archive old version immediately
- Monthly review : Run `make scan-structure`

**Automated Archival** :
- Log cleanup : Logs older than 30 days deleted
- Python cache : Daily via pre-commit hook
- Coverage reports : After test run

---

## ✅ Checklist : Archive Decisions

Before archiving, verify:

- [ ] **Why archiving?** Document reason (superseded, experimental, obsolete)
- [ ] **Dependencies?** Ensure no active code references this file
- [ ] **Backup?** Git commit exists before major cleanup
- [ ] **Metadata?** Use naming convention with date & reason
- [ ] **Traceability?** ARCHIVAL_LOG.json updated automatically

---

## 🔍 File Inventory

### Root Directory (After Cleanup - Oct 26, 2025)

**Essential Files** (~10 files) :
```
✓ .claude/                    (directory with agents, memories)
✓ .gitignore                  (version control rules - updated)
✓ .vscode/                    (workspace settings)
✓ CLAUDE.md                   (60 lines, optimized)
✓ README.md                   (project overview)
✓ requirements.txt            (dependencies)
✓ Makefile                    (automation commands - NEW)
✓ app.py                      (Streamlit main - Phase 4 placeholder)
✓ vercel.json                 (Vercel config)
✓ dvf_plus_structure.json    (data reference)
```

**Archived (Oct 26, 2025)** :
- 5 app_*.py versions → `archive/obsolete_apps/`
- 13 import scripts → `archive/phase2/import_scripts/`
- 2 validation scripts → `archive/phase3/validation_scripts/`
- 3 old tests → `archive/phase1/`
- 6 phase docs → `archive/phase_docs/`
- 3 misc scripts → `archive/phase2/`
- **Total archived** : 30+ files

---

## 🚀 Common Operations

### Monthly Cleanup

```bash
make scan-structure              # Identify structure issues
make clean-pyc                   # Remove Python cache
python scripts/maintenance/file_organizer.py --generate-report
```

### Phase Completion

```bash
# 1. Archive phase-specific files
python scripts/maintenance/file_organizer.py --archive

# 2. Update memory files
# - Update project_state.md (new phase)
# - Add phase results to phase_learnings.md

# 3. Commit cleanup
git add archive/ .claude/memories/
git commit -m "archive: Complete Phase N, archive supporting files"
```

### Root Directory Verification

```bash
# Should show only ~10 essential files
ls -la | grep -v ^\. | wc -l

# Desired output:
# Root directory: 10 essential files ✓
```

---

## 🔗 Related Documents

- **CONTEXT_OPTIMIZATION.md** : Memory tool + context window optimization
- **FILE_MANAGEMENT.md** : User guide for file organization
- **QUICK_START.md** : Session startup checklist
- **file_organizer.py** : Automation script for archival

---

## 👤 Agent Responsibilities

The `file-manager-agent` is responsible for:

1. **Monitoring** : Regular structure scans
2. **Suggesting** : Archival recommendations
3. **Maintaining** : Automated cleanup via Makefile
4. **Documenting** : Updates to this file + ARCHIVAL_LOG.json
5. **Reporting** : Structure reports & inventory

---

## 📌 Notes

- All archival operations logged in `archive/ARCHIVAL_LOG.json`
- Use `--dry-run` before executing archival operations
- Archive structure must be committed to Git (preservation)
- Naming convention ensures files can be searched and retrieved
- Regular reviews (monthly) prevent clutter re-accumulation

**Last Maintenance** : 2025-10-26 (30 files archived, structure standardized)
