# Phase Learnings - Estimateur Immobilier

**Last Updated** : 2025-10-26

---

## 📚 Phase 2 Insights - Supabase + DVF+ Import

### Lesson 1 : INSEE Codes vs Postal Codes ⚠️ CRITICAL
**Problem** :
- DVF+ table `dvf_plus_2025_2_mutations` has field `l_codinsee`
- First assumption : contains postal codes (74xxx)
- Reality : contains INSEE administrative codes ({74056} format = Thonon commune)

**Impact** :
- Initial import : 1,643 mutations (80% below target)
- Filtering logic failed on postal code assumption
- Wasted 2-3 hours debugging

**Solution** :
- Created mapping CSV : 42 communes → 42 INSEE codes
- File : `insee_mapping.csv`
- Result : 56,216 mutations (2014-2025 correct data)

**Takeaway** :
- Always inspect raw data fields FIRST
- French administrative codes (INSEE) ≠ postal codes
- CSV mapping > assumptions

---

### Lesson 2 : Data Quality Validation 📊
**Discovery** :
- After fixing INSEE filtering, data looked reasonable
- Average price : EUR 288,329 (realistic for Chablais)
- Year distribution : 2014-2025 looks natural
- Surface range : 20-500m² (expected residential)

**Validation Steps** :
```python
# Sanity checks
print(df.groupby('year')['price'].count())  # Distribution OK
print(df['surface'].describe())              # Min/Max reasonable
print(df['price'].quantile([0.25, 0.75]))  # IQR sensible
```

**Takeaway** :
- Validate data distribution, not just row counts
- Outliers (price < 50k or > 10M) may be errors
- Phase 3 : Implement data cleaning pipeline

---

### Lesson 3 : PostGIS Spatial Queries Performance
**Observation** :
- Initial query without index : ~2.3s for 100 results
- After CREATE INDEX GIST : ~0.2s (10x faster)
- After B-tree index on type_local : ~0.15s

**Optimization Applied** :
```sql
CREATE INDEX idx_dvf_geom ON dvf_plus_2025_2_mutations USING GIST(geom);
CREATE INDEX idx_dvf_type ON dvf_plus_2025_2_mutations (type_local);
CREATE INDEX idx_dvf_surface ON dvf_plus_2025_2_mutations (surface_reelle_bati);
```

**Takeaway** :
- PostGIS requires explicit indexes (not auto)
- GIST for spatial, B-tree for attributes
- Test performance BEFORE Phase 4

---

### Lesson 4 : Supabase Connection Pooling
**Issue Found** :
- Opening/closing connections per query : expensive
- Thread pool : unnecessary for Streamlit
- Solution : Connection context manager

**Pattern Used** :
```python
from contextlib import contextmanager

@contextmanager
def get_supabase_connection():
    client = create_client(url, key)
    try:
        yield client
    finally:
        pass  # Supabase manages internally
```

**Takeaway** :
- Connection management important for prod
- Phase 4 : Add connection timeout (30s)
- Phase 5 : Monitor query latency

---

### Lesson 5 : Env Variables Management
**Problem** :
- Oct 18 : API keys exposed in commits
- `.env.example` had real values
- Documentation copy-pasted with secrets

**Solution** :
- `.env` (local) : .gitignored, has real values
- `.env.example` : template with placeholders only
- Pre-commit hooks : detect secret patterns

**Takeaway** :
- NEVER commit real keys
- GitHub secret scanner revokes keys (auto)
- Use `.env.example` as template, not config

---

## ⏳ Phase 3 Expectations (EN COURS)

### Algorithm Development

**Scoring Implementation** :
- Distance exponential : farther = lower score
- Surface tolerance ±20% : outside = filtered
- Type exact match : same type = bonus
- Ancienneté : <1 year optimal, <3 years OK
- Characteristics : garage/piscine/terrasse = bonus

**Expected Challenges** :
- Weighting coefficients : need tuning Phase 5
- Outlier handling : some comparables may be duplicates
- Edge cases : few comparables in rural areas

**Estimated Duration** : 2-3 hours coding + testing

---

### Testing Strategy

**Unit Tests** :
- `test_similarity_score()` : 10+ cases
- `test_price_estimation()` : edge cases (1 vs 30 comparables)
- `test_reliability_score()` : threshold validation
- `test_outlier_filtering()` : suspicious high/low prices

**Integration Tests** :
- `test_full_workflow()` : address → comparables → estimation → PDF
- `test_edge_cases()` : rural areas, new constructions, renovations

**Coverage Goal** : ≥80% `pytest --cov=src/`

---

### Known Risks Phase 3

| Risk | Probability | Impact | Mitigation |
|------|-------------|--------|-----------|
| Weighting coefficients wrong | High | Estimations inaccurate | Test Phase 5 user feedback |
| Too few comparables (rural) | Medium | Low reliability | Expand rayon or accept low score |
| Duplicate transactions | Low | Biased estimation | Add deduplication logic |
| Outlier prices (money laundering?) | Low | Distort average | Implement z-score filtering |

---

## 🎯 Phase 4 Planning (Streamlit MVP)

### User Stories to Implement

**US1 : Address Input + Geocoding**
- Form fields : address, city, postal code
- Google Maps real-time validation
- Coordinates extraction
- Expected : <2 sec response

**US2 : Dashboard Estimation**
- Display estimated price (EUR)
- Confidence interval (min/max)
- Reliability score (0-100%)
- Number of comparables used
- Bar chart confidence levels

**US3 : Comparables Table**
- Interactive table with all comparables
- Columns : address, price, surface, type, date, similarity score
- Sortable + filterable
- Delete button : exclude outliers, recalculate

**US4 : Map Viewer**
- Folium map centered on property
- Markers for all comparables
- Circle radius = search radius
- Popup = comparable details

**US5 : PDF Export**
- Report : estimation + method + comparables table
- Logo + formatting
- Download button
- Future : API Gamma integration

---

### Streamlit Components Structure

```python
# app.py - Main entry
st.set_page_config(title="Estimateur Immobilier", layout="wide")

# Page sections
col1, col2 = st.columns([1, 1])

with col1:
    from src.streamlit_components import form_input
    property_data = form_input.render()

with col2:
    from src.streamlit_components import dashboard_metrics
    if property_data:
        dashboard_metrics.render(property_data, comparables)

# Lower section
st.markdown("---")

tab1, tab2, tab3 = st.tabs(["Comparables", "Carte", "Export PDF"])

with tab1:
    from src.streamlit_components import comparables_table
    comparables_table.render(comparables)

with tab2:
    from src.streamlit_components import map_viewer
    map_viewer.render(property_data, comparables)

with tab3:
    from src.streamlit_components import pdf_export
    pdf_export.render(property_data, comparables, estimation)
```

---

### Performance Expectations

| Component | Target | Current |
|-----------|--------|---------|
| Address geocoding | <2s | TBD |
| Comparable query | <3s | ~0.15s ✅ |
| Estimation calc | <1s | TBD |
| PDF generation | <5s | TBD |
| Page load | <5s | TBD |

---

## 🧪 Phase 5 Validation Strategy

### User Testing Protocol

**Setup** :
- 10-20 properties zone Chablais/Annemasse
- Mix : houses, apartments, various sizes/prices
- Compare : MVP estimate vs manual estimate

**Metrics** :
- Accuracy : ±10-15% acceptable
- Speed : 2-3 min per property acceptable
- UX : SUS (System Usability Score) target >70

**Actions if fails** :
- Accuracy <±10% : Adjust weights Phase 3
- Speed >3 min : Optimize queries
- UX <70 : Consider Streamlit → Next.js migration

---

## 📝 Troubleshooting Log

### Bug : "No results" for valid addresses
**Cause** : Comparable search radius too small (default 5km)
**Fix** : Increase to 10km + logging
**Prevention** : Default rayon=10 in config

### Bug : "Connection timeout" Supabase
**Cause** : Network latency + no retry logic
**Fix** : Add exponential backoff + 30s timeout
**Prevention** : Connection pooling + monitoring

### Bug : "Exact duplicate transactions"
**Cause** : Same property sold twice same month (inheritance case)
**Fix** : Deduplication by address + date range
**Prevention** : Data cleaning Phase 5

---

## 📊 Costs Summary to Date

| Component | Spent | Budget | Status |
|-----------|-------|--------|--------|
| Supabase | €0 | €0 | ✅ Gratuit |
| Google Maps | €0 | €50 | ⏳ Not yet billed |
| Vercel | €0 | €0 | ✅ Gratuit |
| **TOTAL** | **€0** | **~€50/mo** | ✅ Under budget |

---

## 🚀 Next Immediate Actions

1. **Phase 3 Development** : `estimation_algorithm.py` (today)
2. **Phase 3 Testing** : `test_estimation_algorithm.py` (today)
3. **Phase 4 Prep** : Component architecture design (review)
4. **Phase 5 Prep** : User testing protocol finalize (tomorrow)

---

**Last Review** : 2025-10-26
**Next Review** : After Phase 3 completion (EOD today)
