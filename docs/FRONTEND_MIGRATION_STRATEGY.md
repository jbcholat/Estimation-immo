# 🏗️ STRATÉGIE DE MIGRATION FRONTEND
## De Streamlit MVP à Architecture Production (Next.js + FastAPI)

**Version:** 2.0 (Architecturée par utilisateur + Agent Plan)
**Date:** 2025-11-08
**Statut:** Planification Phase 6 (Avant Phase 5 completion)
**Auteur:** Jean-Baptiste CHOLAT + Claude Code

---

## 📋 RÉSUMÉ EXÉCUTIF

### Architecture Proposée (Validée ✅)

```
Utilisateur Interne
    ↓
[Frontend: Next.js]
├→ REST API Calls → [Backend: FastAPI on Railway.app]
└→ Optional Direct SQL Reads → [Database: Supabase PostgreSQL + PostGIS]
    ↓
    [Business Logic]
    ├─ Geocoding (Google Maps)
    ├─ Estimation (Multi-criteria scoring)
    ├─ PDF Generation (ReportLab)
    └─ PostGIS Queries
```

### Phases de Migration

| Phase | Timeline | Objectif | Statut |
|-------|----------|----------|--------|
| **Phase 5** | Nov 8-22, 2025 | Finaliser Streamlit MVP | ⏳ EN COURS |
| **Phase 6** | Nov 25 - Dec 20 | Backend API extraction (FastAPI + Railway) | ⏳ À VENIR |
| **Phase 7** | Dec 23 - Feb 14 | Frontend (Next.js + Vercel) | ⏳ À VENIR |
| **Phase 8** | Feb 17-28 | Testing & validation complets | ⏳ À VENIR |
| **Phase 9** | Mar 2-16 | Production deployment & cutover | ⏳ À VENIR |

**Total Timeline:** ~14 semaines (Nov 2025 → Mar 2026)

---

## 🎯 DÉCISIONS CLÉS

### 1. **Next.js 15** (React Framework)

**Pourquoi?**
- ✅ Production-ready (Netflix, Airbnb, Uber)
- ✅ Vercel natif (zero-config deployment)
- ✅ Écosystème massif (shadcn/ui, Tailwind, etc.)
- ✅ TypeScript support (type-safe)
- ✅ Performance excellente (App Router, Server Components)

**Alternative Considéré:** SvelteKit
- ✗ Écosystème plus petit
- ✗ Moins de developers disponibles
- ✓ Mais: Plus rapide à développer (4-6 weeks vs 6-8 weeks)

**Recommandation:** Next.js pour production long-term

---

### 2. **FastAPI** (Backend Python)

**Pourquoi?**
- ✅ Réuse code Python existant (supabase_retriever, estimation_algo)
- ✅ Performance excellente (async/await, UV loop)
- ✅ Auto-generated Swagger documentation
- ✅ Pydantic models (type-safe validation)
- ✅ Minimal boilerplate

**Alternative:** Node.js (Express/NestJS)
- ✗ Rewrite Python modules to TypeScript
- ✗ Extra complexity

**Recommandation:** FastAPI wins

---

### 3. **Railway.app** (Backend Hosting)

**Pourquoi?**
- ✅ EUR 5-50/mo (vs Heroku EUR 50+/mo)
- ✅ Built-in PostgreSQL integration
- ✅ Excellent DX
- ✅ Auto-scaling
- ✅ Docker support

**Alternatives:** Heroku, AWS Lambda, render.com
- Railway offers best balance of cost + DX

**Recommandation:** Railway.app

---

### 4. **Hybrid SQL Strategy**

**Question:** Peut-on faire des lectures directes Supabase du frontend?

**Réponse:** OUI, mais stratégiquement

```typescript
// ✅ AUTORISÉ: Lecture simple directe
const { data } = await supabase
  .from('dvf_mutations')
  .select('*')
  .limit(100);

// ❌ MIEUX via API: Calculs complexes
// POST /api/comparables (PostGIS scoring)
// POST /api/estimate (multi-criteria)
```

**Architecture Recommandée:**
- Frontend: Lectures simples + React Query caching
- Backend: Calculs complexes (scoring, PDF, estimation)

---

## 📊 ARCHITECTURE DÉTAILLÉE

### 1️⃣ FRONTEND: Next.js + Vercel

**Structure:**
```
frontend/
├── app/ (App Router)
│   ├── page.tsx (Landing)
│   ├── estimation/page.tsx (Main flow)
│   ├── dashboard/page.tsx (Results)
│   └── api/ (Server routes, optional)
│
├── components/
│   ├── FormInput.tsx (Address + type + surface)
│   ├── DashboardMetrics.tsx (Estimation display)
│   ├── ComparablesTable.tsx (Filterable results)
│   ├── MapViewer.tsx (Leaflet.js)
│   └── PDFExport.tsx (Download)
│
├── lib/
│   ├── api.ts (Fetch wrappers → FastAPI)
│   └── validations.ts (Zod schemas)
│
└── hooks/
    ├── useEstimation.ts
    ├── useComparables.ts
    └── useGeocoding.ts
```

**Technologies:**
- Framework: Next.js 15 (React + App Router)
- Styling: Tailwind CSS
- UI: shadcn/ui (pre-built components)
- Maps: Leaflet.js (open-source)
- Charts: Chart.js (lightweight)
- Validation: Zod (type-safe)
- Caching: React Query
- Hosting: Vercel (auto-deploy Git)

---

### 2️⃣ BACKEND: FastAPI + Railway

**Structure:**
```
backend/
├── main.py (Entry point)
│
├── routers/
│   ├── geocoding.py (POST /api/geocode)
│   ├── comparables.py (POST /api/comparables)
│   ├── estimation.py (POST /api/estimate)
│   ├── pdf.py (POST /api/generate-pdf)
│   └── health.py (GET /api/health)
│
├── services/
│   ├── supabase_service.py (Wrapper SupabaseDataRetriever)
│   ├── estimation_service.py (Wrapper EstimationAlgorithm)
│   ├── geocoding_service.py (Google Maps wrapper)
│   └── pdf_service.py (ReportLab wrapper)
│
├── models/
│   ├── requests.py (Pydantic request schemas)
│   ├── responses.py (Pydantic response schemas)
│   └── db.py (SQLAlchemy ORM)
│
└── middleware/
    ├── cors.py (CORS configuration)
    ├── auth.py (JWT validation - future)
    └── error_handler.py (Error handling)
```

**Technologies:**
- Framework: FastAPI
- Server: Uvicorn (ASGI)
- Validation: Pydantic
- Database: SQLAlchemy + geoalchemy2
- PDF: ReportLab
- Hosting: Railway.app (serverless/container)

**API Endpoints:**
1. `POST /api/geocode` - Google Maps geocoding
2. `POST /api/comparables` - Search comparable properties (PostGIS)
3. `POST /api/estimate` - Calculate price estimation
4. `POST /api/generate-pdf` - Generate PDF report
5. `GET /api/health` - Health check

---

### 3️⃣ DATABASE: Supabase (Unchanged)

- ✅ 56,216 mutations DVF+ already imported
- ✅ PostgreSQL + PostGIS
- ✅ 107 MB / 500 MB used (21%)
- ✅ Ready for production

**Optional Future Tables:**
```sql
CREATE TABLE estimations_historiques (
  id UUID PRIMARY KEY,
  user_id UUID,
  bien_address VARCHAR,
  prix_estime DECIMAL,
  fiabilite DECIMAL,
  created_at TIMESTAMP
);
```

---

## 🚀 PHASES DE MIGRATION

### PHASE 5: FINALISER STREAMLIT (Nov 8-22, 2025)

**Objectif:** Complete Phase 5 before migration

**Tâches:**
- [ ] Fix 17 failing tests (22/39 → 39/39)
- [ ] UAT with internal team
- [ ] Document for handoff
- [ ] Validate all 5 user stories

**Timeline:** 2 weeks

---

### PHASE 6: BACKEND API EXTRACTION (Nov 25 - Dec 20, 2025)

**Objectif:** Create FastAPI REST API, decouple backend

**Tâches:**
1. Setup FastAPI project (3 days)
2. Extract Supabase logic (5 days)
3. Extract Estimation logic (5 days)
4. Extract Geocoding logic (3 days)
5. Extract PDF generation (3 days)
6. Configuration & testing (4 days)
7. Deploy to Railway (2 days)

**Livrables:**
- ✅ FastAPI backend opérationnel (5 endpoints)
- ✅ Swagger documentation
- ✅ Deployed on Railway.app
- ✅ 100% backend test coverage

**Timeline:** 3-4 weeks

---

### PHASE 7: FRONTEND NEXT.JS (Dec 23 - Feb 14, 2026)

**Objectif:** Build Next.js frontend

**Tâches:**
1. Setup Next.js project (3 days)
2. Design & mockups Figma (5 days) - **Optional, can skip**
3. Routing & layout (3 days)
4. Form component (4 days)
5. Dashboard component (4 days)
6. Comparables table (3 days)
7. Map component (3 days)
8. PDF export (2 days)
9. Integration & polish (5 days)

**Livrables:**
- ✅ Next.js frontend opérationnel
- ✅ All 5 user stories implemented
- ✅ Responsive design (mobile + desktop)
- ✅ Deployed on Vercel

**Timeline:** 4-6 weeks

---

### PHASE 8: TESTING & VALIDATION (Feb 17-28, 2026)

**Objectif:** Comprehensive testing, no regressions

**Tâches:**
1. Unit tests (backend + frontend)
2. Integration tests (API ↔ Frontend)
3. E2E tests (Playwright)
4. Performance testing (Lighthouse)
5. Security audit
6. User acceptance testing

**Livrables:**
- ✅ All tests passing
- ✅ Performance targets met
- ✅ UAT passed

**Timeline:** 2 weeks

---

### PHASE 9: DEPLOYMENT & CUTOVER (Mar 2-16, 2026)

**Objectif:** Production deployment, zero downtime migration

**Tâches:**
1. Production deployment (1 day)
2. Monitoring setup (1 day)
3. Soft launch (3 days - limited users)
4. Full cutover (1 day)
5. Post-launch monitoring (5 days)
6. Streamlit deprecation (1 day)

**Livrables:**
- ✅ Production stable
- ✅ Zero downtime cutover
- ✅ Error rate < 1%
- ✅ Streamlit deprecated

**Timeline:** 2 weeks

---

## ⚠️ RISQUES & MITIGATIONS

### Risk 1: Backend Breaking During Extraction

**Likelihood:** Medium | **Impact:** High

**Mitigation:**
- Run old Streamlit + new FastAPI side-by-side
- Compare outputs for identical inputs
- Comprehensive pytest (100% coverage)

**Rollback:** Keep Streamlit working, revert FastAPI if bug

---

### Risk 2: Performance Regression

**Likelihood:** Low | **Impact:** Medium

**Mitigation:**
- Lighthouse benchmarks (target: 90+)
- React Query caching
- Code splitting + lazy loading

---

### Risk 3: Extended Timeline

**Likelihood:** High | **Impact:** Medium

**Mitigation:**
- Use component libraries (shadcn/ui saves 40% time)
- Weekly sprint reviews
- Prioritize MVP features

**Contingency:** Defer nice-to-haves (PDF export → Phase 10)

---

### Risk 4: Data Loss

**Likelihood:** Very Low | **Impact:** Catastrophic

**Mitigation:**
- Supabase auto-backups enabled
- Keep Streamlit running 2 weeks post-launch
- No data modifications during migration

---

### Risk 5: User Adoption

**Likelihood:** Low | **Impact:** Medium

**Mitigation:**
- Keep similar UX to Streamlit
- Video tutorial (5 min)
- In-app help tooltips
- Email announcement

---

## 💼 COST BREAKDOWN (Annual)

| Component | Cost | Notes |
|-----------|------|-------|
| **Vercel** | EUR 0 | Free tier (Pro: EUR 200/year if needed) |
| **Railway** | EUR 60 | EUR 5/month for backend |
| **Supabase** | EUR 0-100 | Included or pay-as-you-grow |
| **Google Maps** | EUR 50-100 | ~$5 per 1000 requests |
| **Sentry** | EUR 0 | Free tier (10k events/mo) |
| **TOTAL** | **EUR 110-260/year** | Very affordable |

---

## ❓ QUESTIONS OUVERTES

1. **Figma Design Phase**
   - Créer mockups Figma toi-même?
   - Ou fournir wireframes?
   - Ou coder directement (plus rapide)?

2. **Domain & Deployment**
   - Nom de domaine décidé?
   - Frontend URL?
   - Backend URL?

3. **Timeline**
   - 14 weeks acceptable?
   - Hard deadline?

4. **Scope**
   - Retirer features de Streamlit?
   - Ajouter nouvelles features?

5. **Team & Support**
   - Solo dev (toi) + Claude Code?
   - Autre dev disponible?

6. **Authentication**
   - MVP sans auth?
   - Ou JWT from start?

7. **Monitoring**
   - Sentry pour errors?
   - Custom analytics?

---

## ✅ PROCHAINES ÉTAPES

### Cette Semaine
1. ✅ Review stratégie
2. ⏳ Clarifier questions ouvertes
3. ⏳ Finaliser Phase 5

### Prochaine Semaine
1. ⏳ Phase 6 skeleton (FastAPI)
2. ⏳ Setup Railway account
3. ⏳ Complete Streamlit MVP + UAT

### Décembre - Février
1. ⏳ Phase 6-7 execution
2. ⏳ Parallel development

### Mars
1. ⏳ Phase 8-9 execution
2. ⏳ Production launch

---

**Status:** PRÊT POUR REVIEW & CLARIFICATIONS ✅

