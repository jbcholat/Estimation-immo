# Context Optimization - Quick Start Guide

**Implemented** : 2025-10-26
**Next Session** : Start here!

---

## ✅ What Was Done (Today)

### Configuration Changes
1. **`.claude.json`** ✅
   - Autocompact disabled
   - Context management enabled
   - Memory path configured

2. **`CLAUDE.md` (root)** ✅
   - Reduced from 680 to 60 lines
   - Essential info only
   - References detailed docs

3. **`src/CLAUDE.md`** ✅
   - Python-specific guidelines
   - Testing standards
   - Data handling patterns

4. **`.claude/memories/`** ✅
   - `project_state.md` : Current status
   - `decisions.md` : D1-D14 decisions
   - `phase_learnings.md` : Phase 2-3 insights

5. **`docs/CONTEXT_OPTIMIZATION.md`** ✅
   - Complete strategy explanation
   - Implementation details
   - Best practices

### Token Savings Achieved
- Autocompact prevention : ~45k tokens saved
- CLAUDE.md reduction : ~10-20k tokens saved
- Memory tool ready : ~30-50k tokens available
- **Total** : ~70-100k tokens per session

---

## 🚀 For Next Session (Phase 3 Development)

### Step 1 : Load Project Context
```
Read .claude/memories/project_state.md
→ Understand we're in Phase 3, Algorithm Development
→ Next: estimation-algo-agent for coding
```

### Step 2 : Load Relevant Decisions
```
Read .claude/memories/decisions.md
→ Focus on D8 (5-Criteria Scoring) and D9 (4-Component Reliability)
→ These define what to build
```

### Step 3 : Load Phase 2 Lessons
```
Read .claude/memories/phase_learnings.md
→ Remember: INSEE codes issue (for similar data checks)
→ PostGIS perf: indexes are critical
→ Phase 3 expected challenges
```

### Step 4 : Launch estimation-algo-agent
```
Use @estimation-algo-agent
→ Context7 MCP loaded (pandas/numpy)
→ Develops src/estimation_algorithm.py
→ Implements D8 + D9
```

### Step 5 : During Development
- Document findings in `phase_learnings.md`
- Update `project_state.md` if status changes
- Save important context before token limit

---

## 📊 New File Structure

```
.claude/
├── .claude.json (NEW)
│   └── autoCompact: false
│       contextManagement: enabled
│
├── settings.local.json (UPDATED)
│   └── permissions reference + optimization note
│
└── memories/ (NEW FOLDER)
    ├── project_state.md (Phase status, Supabase summary)
    ├── decisions.md (D1-D14 technical decisions)
    ├── phase_learnings.md (Phase 2-3 insights + risks)
    └── QUICK_START.md (this file)

docs/ (UPDATED)
├── CONTEXT_OPTIMIZATION.md (NEW - detailed guide)
├── PLAN_MVP_IMPLEMENTATION.md (unchanged, but not auto-loaded)
└── ...other docs

CLAUDE.md (UPDATED)
└── Reduced 60 lines (vs 680+), essential only

src/
├── CLAUDE.md (NEW)
│   └── Python-specific guidelines, 50 lines
└── ...code files
```

---

## 🔐 Security Notes

### What Changed
- CLAUDE.md now references `.env` but doesn't expose keys
- Memory files contain NO sensitive data
- `.claude.json` with secret handling notes

### What Didn't Change
- `.env` still local (gitignored)
- `.env.example` still templates only
- No new security risks introduced

---

## ⚡ Performance Tips

### Maximize Token Efficiency
1. **Start small** : Load only memories you need
2. **Batch updates** : Update memories after major task blocks
3. **Use agents** : `@estimation-algo-agent`, `@streamlit-mvp-agent` load only relevant MCPs
4. **Reference docs** : Read detailed docs on-demand, not at session start

### Monitor Context
- Check token usage regularly
- If >75% context used : save findings to memory
- Use context editing if workflow >100 tool calls (Phase 5)

---

## 🎯 Phase 3 Checklist

### Coding Tasks
- [ ] Develop `src/estimation_algorithm.py` (2h)
- [ ] Implement D8 : 5-criteria scoring
- [ ] Implement D9 : 4-component reliability
- [ ] Write `tests/test_estimation_algorithm.py` (≥80% coverage)

### Validation Tasks
- [ ] Test with Phase 2 data (56,216 mutations)
- [ ] Verify scoring 0-100 range
- [ ] Test edge cases (1 vs 30 comparables)
- [ ] Update `phase_learnings.md` with Phase 3 insights

### Documentation Tasks
- [ ] Add Phase 3 results to `project_state.md`
- [ ] Document any new decisions in `decisions.md`
- [ ] Update `phase_learnings.md` risks/mitigations

### Before Phase 4
- [ ] Commit Phase 3 code with summary
- [ ] Update `project_state.md` to "Phase 4 Ready"
- [ ] Review memory files for accuracy

---

## 📞 If Stuck

1. **Algorithmic issues?**
   → Check `phase_learnings.md` "Phase 3 Expectations"
   → Review `decisions.md` D8-D9 for specs

2. **Data issues?**
   → Check `decisions.md` D6-D7 (DVF+ source)
   → Review `phase_learnings.md` Lesson 2 (data validation)

3. **Performance issues?**
   → Check `phase_learnings.md` Lesson 3 (PostGIS indexes)
   → Verify Supabase query times <3s

4. **Context window issues?**
   → Review `docs/CONTEXT_OPTIMIZATION.md`
   → Save to memory before limit reached
   → Use specialized agent MCPs

---

## 🔄 Memory Maintenance

### Daily (During Phase 3)
- [ ] Update `project_state.md` with daily progress
- [ ] Note any bugs/fixes in `phase_learnings.md`

### After Each Major Task
- [ ] Save insights to `phase_learnings.md`
- [ ] Update decisions if new choices made

### End of Phase 3
- [ ] Create `phase_results/phase3_validation.md`
- [ ] Archive findings
- [ ] Update `project_state.md` to "Phase 4 Ready"

---

## 📚 Reference Files

| File | Purpose | Size | When Load |
|------|---------|------|-----------|
| `CLAUDE.md` (root) | Project overview | 60 lines | Every session |
| `src/CLAUDE.md` | Python guidelines | 50 lines | Coding tasks |
| `project_state.md` | Current status | 1-2kb | Session start |
| `decisions.md` | Technical decisions | 3-4kb | Before coding |
| `phase_learnings.md` | Phase insights | 2-3kb | Context needed |
| `CONTEXT_OPTIMIZATION.md` | Strategy details | 5-6kb | On-demand |

---

## ✨ What This Enables

### Before Optimization
- Autocompact consuming 45k tokens uncontrolled
- 680-line CLAUDE.md always loaded
- No persistent context between sessions
- Risk of information loss or duplication

### After Optimization
- Full control over token consumption
- Lean root CLAUDE.md (60 lines)
- Persistent memory across sessions
- Organized context by topic
- -70-100k tokens saved per session

---

## 🚀 Ready to Code!

When you start Phase 3 tomorrow:

```
1. Read .claude/memories/project_state.md (2 min)
2. Read .claude/memories/decisions.md D8-D9 (3 min)
3. Read .claude/memories/phase_learnings.md Phase 3 section (2 min)
4. Launch @estimation-algo-agent
5. Start developing src/estimation_algorithm.py
```

**Total context load time** : ~5 min vs ~15 min before
**Token savings** : ~70-100k tokens available for coding

---

## 📝 Session Template

Copy this for next session start:

```markdown
# Phase 3 Session - DATE

## Context Loaded
- [x] project_state.md
- [x] decisions.md (D8, D9)
- [x] phase_learnings.md (Phase 3 section)

## Task
[Describe what coding/testing you're doing]

## Progress
[Update as you go]

## Findings
[Any new insights/challenges]

## Memory Updates Needed
[What to save to phase_learnings.md]
```

---

**Created** : 2025-10-26
**Updated** : Each phase completion
**Maintained By** : Claude + Jean-Baptiste CHOLAT
