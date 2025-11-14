# 📚 Memory & Documentation Index

## 🚀 START HERE (Nouvelle Session)

### Quick Access
1. **[next_session_checklist.md](./next_session_checklist.md)** ← **START HERE FIRST**
   - 5-minute checklist to get going
   - Quick commands reference
   - What to test first

2. **[session_20251114_bilan.md](./session_20251114_bilan.md)**
   - Complete Session #2 summary
   - What was done
   - What's pending
   - Commit history

3. **[technical_context.md](./technical_context.md)**
   - Database schema details
   - Coordinate system info
   - Scoring algorithm structure
   - Debug checklists for each issue

---

## 📂 File Guide

### Session Documentation
```
✅ session_20251114_bilan.md      - Session #2 complete bilan
✅ next_session_checklist.md       - Session #3 quick start
✅ technical_context.md            - Technical deep-dive reference
```

### Existing Memory Files (Previous Sessions)
```
📝 decisions.md                   - Architecture decisions
📝 file_management_rules.md       - Rules for file organization
📝 phase_learnings.md             - Phase learnings (1-5)
📝 project_state.md               - Project current state
📝 QUICK_START.md                 - General quick start guide
```

---

## 🎯 Issues Status Tracker

### Issue #2 ✅ COMPLETED (Session #2)
- **What:** Update comparables table with 9 columns
- **Status:** ✅ Deployed
- **Commit:** `8ef5dc1`
- **Details:** See `session_20251114_bilan.md` → "ISSUE #2"

### Issue #3 ❌ TO-DO (Session #3+)
- **What:** Score de fiabilité bloqué à 35/100
- **Priority:** Medium
- **Blocked by:** Issue #4 (logically - fix data first)
- **Details:** See `technical_context.md` → "Scoring Algorithm"

### Issue #4 ❌ URGENT (Session #3+)
- **What:** Comparables de Sciez n'apparaissent pas
- **Priority:** HIGH - THIS IS THE MAIN BLOCKER
- **Action:** Investigate distances & coordinate conversion
- **Details:** See `technical_context.md` → "Issue #4 Debug Checklist"

---

## 🔑 Critical Information

### Credentials Status
- ✅ `.env.local` has correct Supabase password (Session #2 fixed)
- ✅ Google Maps API key present
- ✅ No credentials in git

### Recent Commits (Session #2)
```
2a69f49 - docs: Add session memory files
39c2d87 - docs: Session #2 bilan
8ef5dc1 - feat: Issue #2 - Update comparables table with 9 columns
```

### Development Branch Status
- **Current:** main
- **Diverged from origin/main:** +17 commits (local) vs +3 commits (remote)

---

## 🚦 Next Steps (Priority Order)

### 1️⃣ Session #3 - START HERE
```
1. Read: next_session_checklist.md (5 min)
2. Check: git status (should be clean)
3. Test: Streamlit on http://localhost:8501
4. Focus: Issue #4 (Sciez comparables)
```

### 2️⃣ If Issue #4 Blocked
```
1. Check: technical_context.md → "Issue #4 Debug Checklist"
2. Add debug logging to src/supabase_data_retriever.py
3. Test distance calculation isolated
4. Verify Lambert93 → WGS84 conversion
```

### 3️⃣ After Issue #4 Fixed
```
1. Work on Issue #3 (Score bloqué à 35)
2. Reduce scoring thresholds
3. Test recalculation
```

---

## 💾 How to Update This

When you complete work in a session:

1. **Create a new session file:**
   ```bash
   cp session_20251114_bilan.md session_YYYYMMDD_bilan.md
   # Edit with your work
   ```

2. **Update this README.md** with new status

3. **Commit:**
   ```bash
   git add .claude/memories/
   git commit -m "docs: Session #N bilan"
   ```

---

## 🎓 Learning Resources

### Technical Details
- Database schema: See `technical_context.md`
- Scoring algorithm: See `technical_context.md` → "Scoring Algorithm"
- Coordinate systems: See `technical_context.md` → "Coordinate Systems"

### Previous Context
- Architecture: See `decisions.md`
- Phase summary: See `phase_learnings.md`
- Project state: See `project_state.md`

---

## ⚠️ Important Warnings

1. **Always read session bilan FIRST** before making changes
2. **Conservative approach:** 1 change → Test → Commit (DON'T batch)
3. **If "Connection timed out":** Check `.env.local` credentials first
4. **If Streamlit runs old code:** Kill all Python processes + restart

---

**Last Updated:** 14 Nov 2025 (Session #2 End)
**Status:** Ready for Session #3 🚀
**Focus:** Issue #4 (Sciez) is MAIN BLOCKER
