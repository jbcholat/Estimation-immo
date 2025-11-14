# 🏗️ ARCHITECTURE DIAGRAM - Estimateur Immobilier Production

**Version:** 2.0
**Date:** 2025-11-08
**Statut:** Planification Phase 6-9

---

## 📊 GLOBAL ARCHITECTURE (Phase 9 - Production)

### High-Level Diagram

```
┌─────────────────────────────────────────────────────────────────┐
│                   👤 UTILISATEUR INTERNE                        │
│                    (Browser Web Access)                         │
└──────────────────────┬──────────────────────────────────────────┘
                       │
        ┌──────────────┼──────────────┐
        │              │              │
        ▼              ▼              ▼
    ┌────────┐    ┌────────┐    ┌────────┐
    │ FRONT  │    │ BACK   │    │  DB    │
    │ LAYER  │    │ LAYER  │    │ LAYER  │
    └────────┘    └────────┘    └────────┘
        │              │              │
        ▼              ▼              ▼
   [Next.js]      [FastAPI]      [Supabase]
   [Vercel]   [Railway.app] [PostgreSQL+PostGIS]
```

### Component Details

```
┌─────────────────────────────────────────────────────────┐
│ FRONTEND (Next.js on Vercel)                           │
│ ├─ Pages: Landing, Estimation, Dashboard              │
│ ├─ Components: Form, Dashboard, Table, Map, PDF       │
│ ├─ State: React Hooks + React Query (caching)         │
│ ├─ Styling: Tailwind CSS                              │
│ ├─ Maps: Leaflet.js                                   │
│ ├─ Charts: Chart.js                                   │
│ └─ Validation: Zod                                    │
└──────────────┬──────────────────────────────────────────┘
               │ REST API Calls (JSON)
               │ Optional: Direct SQL reads
┌──────────────▼──────────────────────────────────────────┐
│ BACKEND (FastAPI on Railway.app)                       │
│ ├─ Routers:                                            │
│ │  ├─ POST /api/geocode (Google Maps)                 │
│ │  ├─ POST /api/comparables (PostGIS search)          │
│ │  ├─ POST /api/estimate (Multi-criteria scoring)     │
│ │  ├─ POST /api/generate-pdf (ReportLab)              │
│ │  └─ GET /api/health (Health check)                  │
│ ├─ Services:                                           │
│ │  ├─ SupabaseService (Data retrieval)                │
│ │  ├─ EstimationService (Scoring algorithm)           │
│ │  ├─ GeocodingService (Google Maps wrapper)          │
│ │  └─ PDFService (PDF generation)                     │
│ ├─ Middleware:                                         │
│ │  ├─ CORS (Cross-origin requests)                    │
│ │  ├─ Auth (JWT validation - future)                  │
│ │  └─ Error handling                                  │
│ └─ Documentation: Swagger UI (/docs)                  │
└──────────────┬──────────────────────────────────────────┘
               │ SQL Queries
               │ PostGIS spatial functions
┌──────────────▼──────────────────────────────────────────┐
│ DATABASE (Supabase PostgreSQL + PostGIS)               │
│ ├─ Tables:                                             │
│ │  ├─ dvf_mutations (56,216 rows)                     │
│ │  ├─ communes (reference)                           │
│ │  ├─ estimations_historiques (new - future)         │
│ │  └─ estimation_parametres (new - future)           │
│ ├─ PostGIS Functions:                                │
│ │  ├─ ST_Distance (distance calculations)             │
│ │  ├─ ST_Within (bounding box queries)                │
│ │  └─ Spatial indexes                                │
│ └─ Auto-backups: 28-day retention                     │
└─────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────┐
│ EXTERNAL SERVICES                                       │
│ ├─ Google Maps API (Geocoding)                         │
│ ├─ Sentry (Error tracking)                             │
│ └─ Vercel Analytics (Performance)                      │
└─────────────────────────────────────────────────────────┘
```

---

## 🔄 USER FLOW - Complete Estimation Journey

```
┌──────────────┐
│ User Enters  │
│ Address      │
└──────┬───────┘
       │
       ▼
┌──────────────────────────────────────┐
│ Frontend: FormInput Component        │
│ ├─ Google Places Autocomplete        │
│ ├─ Address validation (Zod)         │
│ └─ Submit button                     │
└──────┬───────────────────────────────┘
       │
       ▼
┌──────────────────────────────────────┐
│ Backend: POST /api/geocode           │
│ ├─ Call Google Maps API             │
│ ├─ Extract: lat, lon, address       │
│ └─ Return JSON                       │
└──────┬───────────────────────────────┘
       │
       ▼
┌──────────────────────────────────────┐
│ Frontend: Display map preview        │
│ Add marker at coordinates            │
└──────┬───────────────────────────────┘
       │
       ▼
┌──────────────────────────────────────┐
│ User Confirms + Submits              │
│ ├─ Type de bien                      │
│ ├─ Surface                           │
│ └─ Characteristics                   │
└──────┬───────────────────────────────┘
       │
       ▼
┌──────────────────────────────────────┐
│ Backend: POST /api/comparables       │
│ ├─ PostGIS query (distance)         │
│ ├─ Score each comparable (5 criteria)│
│ └─ Return 30 best matches            │
└──────┬───────────────────────────────┘
       │
       ▼
┌──────────────────────────────────────┐
│ Backend: POST /api/estimate          │
│ ├─ Calculate weighted price          │
│ ├─ Compute 4-component confidence    │
│ └─ Return estimation result          │
└──────┬───────────────────────────────┘
       │
       ▼
┌──────────────────────────────────────┐
│ Frontend: DashboardMetrics           │
│ ├─ Display: Prix estimé              │
│ ├─ Display: Fourchette (min-max)     │
│ ├─ Display: Fiabilité score          │
│ ├─ Charts: Comparable prices         │
│ ├─ Map: Comparable locations         │
│ └─ Table: Comparable details         │
└──────┬───────────────────────────────┘
       │
       ▼
┌──────────────────────────────────────┐
│ User Clicks: Download PDF            │
└──────┬───────────────────────────────┘
       │
       ▼
┌──────────────────────────────────────┐
│ Backend: POST /api/generate-pdf      │
│ ├─ ReportLab generates PDF           │
│ ├─ Include: Bien, estimation, table  │
│ └─ Return PDF binary                 │
└──────┬───────────────────────────────┘
       │
       ▼
┌──────────────────────────────────────┐
│ Frontend: Download PDF file          │
│ User gets: estimation_rapport.pdf    │
└──────────────────────────────────────┘
```

---

## 🔗 API ENDPOINTS - Detailed

### Endpoint 1: POST /api/geocode

```
REQUEST:
{
  "address": "123 Rue Principal, 74200 Thonon"
}

BACKEND PROCESS:
1. Validate address (string, min 5 chars)
2. Call Google Maps Geocoding API
3. Extract: latitude, longitude, formatted_address
4. Return with confidence score

RESPONSE (200 OK):
{
  "latitude": 46.3709,
  "longitude": 6.4772,
  "formatted_address": "123 Rue Principale, 74200 Thonon-les-Bains",
  "confidence": 0.95
}
```

### Endpoint 2: POST /api/comparables

```
REQUEST:
{
  "latitude": 46.3709,
  "longitude": 6.4772,
  "type_bien": "Appartement",
  "surface_min": 70,
  "surface_max": 130,
  "rayon_km": 10,
  "annees": 3,
  "limit": 30
}

BACKEND PROCESS:
1. Validate input (Pydantic models)
2. PostGIS query: Find mutations within radius
3. Filter by: type, surface, date
4. Score each comparable (5 criteria)
5. Sort by score (descending)
6. Return top 30

RESPONSE (200 OK):
{
  "comparables": [
    {
      "id_mutation": "74056-2024-001234",
      "date_mutation": "2024-09-15",
      "valeur_fonciere": 285000,
      "surface": 95,
      "type_bien": "Appartement",
      "distance_km": 2.3,
      "score_similarite": 0.87,
      ...
    },
    ...
  ],
  "count": 27,
  "mean_price": 288329,
  "median_price": 285000
}
```

### Endpoint 3: POST /api/estimate

```
REQUEST:
{
  "latitude": 46.3709,
  "longitude": 6.4772,
  "surface": 95,
  "type_bien": "Appartement",
  "comparables_ids": ["id1", "id2", ...],
  "date_estimation": "2025-11-08"
}

BACKEND PROCESS:
1. Fetch comparables from Supabase
2. Calculate weighted estimation
3. Compute 4-component confidence score:
   - Volume of comparables (0-30 pts)
   - Average similarity (0-30 pts)
   - Price dispersion (0-25 pts)
   - Transaction recency (0-15 pts)
4. Adjust for inflation + market trends

RESPONSE (200 OK):
{
  "prix_estime": 285000,
  "prix_min": 245000,
  "prix_max": 325000,
  "intervalle_confiance": 0.95,
  "score_fiabilite": 0.78,
  "fiabilite_label": "Bonne",
  "fiabilite_details": {
    "volume_comparables": 27,
    "similarite_moyenne": 0.85,
    "dispersion_prix": 0.12,
    "anciennete_transactions": 1.2
  },
  "prix_au_m2": 3000,
  "timestamp": "2025-11-08T14:32:00Z"
}
```

### Endpoint 4: POST /api/generate-pdf

```
REQUEST:
{
  "bien_address": "123 Rue Principale, 74200",
  "estimation": {...estimation_result...},
  "comparables": [...array of comparables...],
  "bien_details": {
    "surface": 95,
    "type_bien": "Appartement"
  }
}

BACKEND PROCESS:
1. Validate request (Pydantic)
2. ReportLab creates PDF:
   - Header: Logo + Title
   - Section 1: Bien summary (address, surface, type)
   - Section 2: Estimation (price, range, confidence)
   - Section 3: Charts (price distribution)
   - Section 4: Map (Bien + comparables)
   - Section 5: Comparable table
   - Footer: Date, disclaimer
3. Return PDF binary

RESPONSE (200 OK):
Content-Type: application/pdf
[Binary PDF file: estimation_rapport.pdf]
```

### Endpoint 5: GET /api/health

```
REQUEST:
GET /api/health

RESPONSE (200 OK):
{
  "status": "healthy",
  "database": "connected",
  "google_maps": "ok",
  "timestamp": "2025-11-08T14:32:00Z"
}
```

---

## 🏛️ DEPLOYMENT ARCHITECTURE

### Current (Phase 5 - Streamlit)

```
GitHub Repository
    ↓
Vercel
├─ Streamlit Server (Python)
│  ├─ Frontend (Streamlit UI)
│  └─ Backend (Python logic)
└─ Deployed: `streamlit run app.py`
    ↓
Supabase
└─ Database (PostgreSQL)
```

### Target (Phase 9 - Production)

```
GitHub Repository
    ├─ `/frontend` branch
    │   ↓
    │ Vercel
    │ ├─ Next.js Application
    │ ├─ Auto-deploy on git push
    │ └─ CDN + Edge functions
    │
    └─ `/backend` branch (or separate repo)
        ↓
      Railway.app
      ├─ FastAPI Server
      ├─ Docker container
      ├─ Auto-scaling
      └─ Environment variables
          ↓
        Supabase
        └─ Database (PostgreSQL + PostGIS)
```

---

## 🔐 SECURITY LAYERS

```
┌─────────────────────────────────────┐
│ Layer 1: HTTPS/TLS                 │
│ ├─ Vercel: Auto HTTPS               │
│ ├─ Railway: Auto HTTPS              │
│ └─ Supabase: Auto HTTPS             │
├─────────────────────────────────────┤
│ Layer 2: CORS (Cross-Origin)       │
│ ├─ FastAPI CORS middleware          │
│ ├─ Allow: yourdomain.vercel.app     │
│ └─ Block: Other origins             │
├─────────────────────────────────────┤
│ Layer 3: API Authentication         │
│ ├─ Future: JWT via Supabase Auth    │
│ ├─ Headers: Authorization: Bearer   │
│ └─ Validation: FastAPI middleware   │
├─────────────────────────────────────┤
│ Layer 4: Environment Variables      │
│ ├─ SUPABASE_KEY (backend only)      │
│ ├─ GOOGLE_MAPS_API_KEY (backend)    │
│ └─ NEXT_PUBLIC_* (frontend safe)    │
├─────────────────────────────────────┤
│ Layer 5: Input Validation           │
│ ├─ Frontend: Zod schema              │
│ ├─ Backend: Pydantic models          │
│ └─ Database: PostgreSQL constraints  │
├─────────────────────────────────────┤
│ Layer 6: Error Handling             │
│ ├─ No sensitive data in errors       │
│ ├─ Sentry logging (no PII)          │
│ └─ User-friendly messages            │
└─────────────────────────────────────┘
```

---

## 📈 SCALING ARCHITECTURE

### Horizontal Scaling (Multi-instance)

```
Request Load
    ↓
Vercel CDN (Auto-scaling)
├─ Geographic distribution
├─ Edge caching
└─ Automatic scaling based on demand
    ↓
Railway Backend (Auto-scaling)
├─ Docker containers (n instances)
├─ Load balancing (automatic)
└─ Scales on CPU/memory usage
    ↓
Supabase Database
├─ Connection pooling (PgBouncer)
├─ Read replicas (optional)
└─ Automatic backups
```

### Caching Strategy

```
Browser Cache
├─ Static assets: 1 year
├─ API responses: 5 minutes
└─ Images: 30 days
    ↓
React Query Cache
├─ /api/comparables: 10 minutes
├─ /api/estimate: 30 minutes
└─ User-triggered refresh available
    ↓
Backend Cache (Optional - Redis)
├─ Comparables results: 1 hour
├─ Geocoding: 24 hours
└─ Parameters: 1 week
```

---

## 📊 MONITORING STACK

```
┌─────────────────────────────────────┐
│ Error Tracking: Sentry              │
│ ├─ Backend errors (FastAPI)         │
│ ├─ Frontend errors (React)          │
│ ├─ Alert on >5% error rate          │
│ └─ Slack integration                │
├─────────────────────────────────────┤
│ Performance: Vercel Analytics       │
│ ├─ Lighthouse scores                │
│ ├─ Core Web Vitals (LCP, FID, CLS) │
│ ├─ Response times                   │
│ └─ Deployment insights              │
├─────────────────────────────────────┤
│ API Monitoring: Railway             │
│ ├─ Request/response times           │
│ ├─ Error rates                      │
│ ├─ Database query times             │
│ └─ Uptime tracking                  │
├─────────────────────────────────────┤
│ Database: Supabase Dashboard        │
│ ├─ Query performance                │
│ ├─ Index usage                      │
│ ├─ Connection count                 │
│ └─ Disk usage (107 MB / 500 MB)    │
└─────────────────────────────────────┘
```

---

## 🔄 MIGRATION PATH

```
Phase 5 (Now)              Phase 6-7              Phase 8-9
┌──────────────┐  ┌──────────────┐  ┌──────────────┐
│ Streamlit    │  │ New Stack    │  │ Production   │
│ MVP Running  │  │ Building     │  │ Ready        │
│              │  │ (Parallel)   │  │              │
└──────────────┘  └──────────────┘  └──────────────┘
      │                │                   │
      ▼                ▼                   ▼
Users on Streamlit → Soft launch (beta) → Full cutover
Keep Streamlit        New frontend works  Users on Next.js
as fallback (2 weeks  with FastAPI        Streamlit deprecated
post-launch)          Parallel testing
```

---

## 💰 COST COMPARISON

### Current (Phase 5 - Streamlit)

```
Vercel Pro: EUR 20/month
Supabase: EUR 0-50/month (pay-per-use)
Google Maps: EUR 50-100/year
─────────────────────────
TOTAL: ~EUR 250-400/year
```

### Target (Phase 9 - Production)

```
Vercel Free: EUR 0/month
Railway: EUR 60/year (EUR 5/month)
Supabase: EUR 0-50/month (pay-per-use)
Google Maps: EUR 50-100/year
Sentry: EUR 0 (free tier)
─────────────────────────
TOTAL: ~EUR 110-260/year
```

---

## 🎯 NEXT STEPS SUMMARY

1. ✅ Review this architecture
2. ⏳ Finalize Phase 5 (Streamlit MVP complete)
3. ⏳ Clarify questions (Figma? Domain? Timeline?)
4. ⏳ Phase 6 execution (Backend extraction)

---

**Status:** ARCHITECTURE DOCUMENTED & READY ✅

