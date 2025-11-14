# ✅ Checklist Démarrage Session #3

## 🎯 Quick Start (First 5 minutes)

### 1. Vérifier l'État
```bash
# Terminal
git status                    # Doit montrer: "working tree clean"
git log --oneline -5          # Vérifier commit 39c2d87 est le dernier
```

### 2. Lancer Streamlit
```bash
python -m streamlit run app.py
# Doit être accessible sur http://localhost:8501
```

### 3. Vérifier Credentials
- `.env.local` ligne 10: `SUPABASE_DB_PASSWORD=tetrarchic-gazumping-lares-mercaptide` ✅
- Si "Connection timed out" → vérifier `.env.local`

---

## 🎯 Travail à Faire (Priorité)

### ❌ URGENT - Issue #4: Comparables de Sciez
**Test rapide:**
1. Lance l'app
2. Adresse: "16 Rue de l'Anneau de Songy"
3. Params: 100m², Maison, 4 pièces
4. Clique "Estimer"
5. Regarde le tableau: Y a-t-il des comparables de Sciez?

**Si NON (toujours bloqué):**
- Ajouter debug logging pour voir les distances réelles
- Investiguer conversion Lambert93 → WGS84
- Vérifier si données Sciez existent en DB

**Voir:** `.claude/memories/session_20251114_bilan.md` Section "Issue #4"

### ⏸️ PUIS - Issue #3: Score Bloqué à 35
**Après Issue #4 fixé:**
1. Réduire les thresholds de scoring
2. Tester recalcul dynamique

---

## 📋 Files d'Attente

| Issue | Statut | Commit | Notes |
|-------|--------|--------|-------|
| #2 | ✅ DONE | 8ef5dc1 | 9 colonnes tableau |
| #3 | ❌ TODO | - | Score bloqué à 35 |
| #4 | ❌ TODO | - | Sciez comparables |

---

## 🔗 Fichiers Clés
- `.claude/memories/session_20251114_bilan.md` - Bilan complet
- `src/supabase_data_retriever.py` - Data retrieval logic
- `src/estimation_algorithm.py` - Scoring logic (Issue #3)
- `docs/CONTEXT_PROJET.md` - Context business

---

## 💾 Recent Changes (Session #2)
```
39c2d87 - docs: Session #2 bilan
8ef5dc1 - feat: Issue #2 - Update comparables table with 9 columns
707b22b - chore: Reorganize project structure (baseline)
```

---

## ⚡ Quick Commands

```bash
# Tuer Streamlit
powershell -Command "Get-Process python | Stop-Process -Force"

# Lancer Streamlit
python -m streamlit run app.py

# Test DB connexion
python -c "from src.supabase_data_retriever import SupabaseDataRetriever; r = SupabaseDataRetriever(); r.test_connection()"

# Voir les commits
git log --oneline -10

# Ajouter fichiers & committer
git add <files> && git commit -m "message"
```

---

**Ready to go!** 🚀
