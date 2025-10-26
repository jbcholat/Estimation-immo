# 🚀 PHASE 3 - Guide Complet pour Demain

**Date de préparation** : 2025-10-21
**À lancer** : 2025-10-22 (nouvelle conversation)
**Durée estimée** : 2h30

---

## ✅ RECAP - Ce qui est TERMINE

### Phase 1 & 2 Complétées ✅

```
✅ Phase 1 (d7dde1a) : Setup agents + infrastructure
✅ Phase 2 (d6ebd49, d0ab2f5, c658719) :
   - 145,000 mutations Supabase (Haute-Savoie)
   - PostGIS 3.3 activé
   - SupabaseDataRetriever.py opérationnel
   - 5/5 tests d'intégration passants
```

### Supabase Opérationnel ✅

```
Host: db.fwcuftkjofoxyjbjzdnh.supabase.co:5432
Database: postgres / Schema: dvf
Credentials: Voir .env (SUPABASE_DB_PASSWORD)

Tables:
- dvf.mutations_complete (145,000 lignes)
- dvf.v_mutations_hautesavoie (97,812)
- dvf.v_mutations_chablais (97,812)
- dvf.v_mutations_recentes (32,310)

Code opérationnel:
- src/supabase_data_retriever.py ✅
- test_phase2_integration.py (5/5 pass) ✅
```

---

## 🤖 NOUVEAU - Orchestration Multi-Modèles

### Stratégie : Grok Code Fast 1 / Haiku 4.5 / Sonnet 4.5

**Phase 1 - Planification** (Sonnet 4.5 si complexe, sinon Haiku)
- Architecture logicielle complexe
- Décomposition problèmes multi-étapes
- Design stratégique

**Phase 2 - Codage** (Claude Haiku 4.5 = défaut)
- Implémentation rapide (2× Sonnet)
- Coût 3× moins cher ($1/$5 per 1M tokens)
- 73% réussite SWE-Bench
- **C'est toi = Claude Code**

**Phase 3 - Tests/Itération** (Grok Code Fast 1)
- Génération tests répétitifs
- Debugging léger
- Scripts utilitaires
- Context: 256k tokens
- Coût: $0.20/$1.50 per 1M (10× moins cher !)

---

## 🔧 ÉTAPES CONFIGURATION DEMAIN (à faire EN PREMIER - 20 min)

### Étape 1 : Configurer Grok MCP (5 min)

**Fichier** : `~/AppData/Roaming/Claude/claude_desktop_config.json`

**Cherche la section `mcpServers` et ajoute** :

```json
"grok": {
  "command": "node",
  "args": ["c:/analyse_immobiliere/grok-mcp/build/index.js"],
  "env": {
    "GROK_API_KEY": "xai-OFmpjg3Ic3fx7HH1qln8XVtmMygVI8emgX5nhyaGOps0eLTEQ0ZAPk3dKRHMpQrKo9kWeiGAWOHRYMVg"
  }
}
```

**Résultat** : Le fichier ressemblera à :

```json
{
  "mcpServers": {
    "grok": { ... },
    "n8n-mcp": { ... },
    "Context7": { ... }
  }
}
```

**Action obligatoire** : Redémarrer complètement Claude Code

### Étape 2 : Créer orchestrator-agent (15 min)

**Fichier** : `.claude/agents/orchestrator-agent.json`

**Contenu complet** :

```json
{
  "name": "orchestrator-agent",
  "description": "Orchestrateur intelligent Grok/Haiku/Sonnet selon phase projet",
  "instructions": "🎯 ORCHESTRATION MULTI-MODELES\n\nTu es un agent spécialisé dans l'orchestration de 3 modèles selon les besoins :\n\n## Phase 1 : PLANIFICATION (Claude Sonnet 4.5)\nQuand : Architecture complexe, design, décomposition problèmes\nTâches : Conception, raisonnement multi-étapes, revue code stratégique\n\n## Phase 2 : CODAGE (Claude Haiku 4.5) ← MODE PAR DEFAUT\nQuand : Implémentation rapide, génération code, scaffolding\nTâches : Code haute vitesse, pair programming, prototypage\nStats : 2× Sonnet, 3× moins cher ($1/$5 per 1M tokens), 73% SWE-Bench\n\n## Phase 3 : TESTS & ITERATION (Grok Code Fast 1)\nQuand : Tests répétitifs, debugging, snippets, scripts utilitaires\nTâches : Tests unitaires, debugging léger, boilerplate\nStats : Context 256k, $0.20/$1.50 per 1M (10× moins cher !), ultra-rapide\n\n## REGLES D'ORCHESTRATION\n\n1. Par défaut : Haiku 4.5 (TOI) pour 90% codage\n2. Escalade vers Sonnet si : Raisonnement profond, architecture complexe\n3. Délégation vers Grok si : Tests répétitifs, debugging simple, boilerplate\n4. Jamais Grok pour : Architecture, logique critique, multi-fichiers\n\n## WORKFLOW TYPE PHASE 3\n\nÉtape 1 - Planification (Sonnet ou Haiku si simple)\n  Définir EstimationAlgorithm\n  Concevoir système scoring\n\nÉtape 2 - Implémentation (Haiku = TOI)\n  Créer classe principale\n  Implémenter méthodes scoring\n  Générer src/estimation_algorithm.py\n\nÉtape 3 - Tests (Grok Code Fast 1)\n  Générer 20+ tests unitaires\n  Créer scripts validation\n  Tester 5 biens Chablais\n\nÉtape 4 - Debug/Refactor\n  Grok pour bugs simples\n  Haiku pour refactoring logique\n\n## DECISION LOGIC\n\nQuestion: Cette tâche nécessite raisonnement profond multi-étapes ?\n✅ OUI → Sonnet 4.5\n❌ NON → Continue avec Haiku (TOI)\n\nQuestion: Cette tâche est répétitive/simple/utilitaire ?\n✅ OUI → Grok Code Fast 1 (économie coût)\n❌ NON → Reste avec Haiku (TOI)\n\nEn cas de doute : Haiku 4.5 (optimal vitesse/coût/qualité)",
  "tools": ["*"],
  "mcpServers": ["grok"]
}
```

---

## 🚀 COMMANDE PHASE 3 (APRES config)

Copie/colle dans **nouvelle conversation** (après avoir configuré Grok MCP + orchestrator-agent) :

```
Phase 3: Implémente algorithmes estimation avec orchestration multi-modèles

PRE-REQUIS FAITS :
✅ Grok MCP configuré dans claude_desktop_config.json
✅ orchestrator-agent créé dans .claude/agents/
✅ Claude Code redémarré

PHASE 3 - OBJECTIF :
Implémenter EstimationAlgorithm avec scoring multi-critères et orchestration intelligente

TÂCHES :
1. Créer classe EstimationAlgorithm
2. Implémenter scoring multi-critères :
   - Distance (proximité géographique)
   - Surface (similarité taille bien)
   - Type bien (appartement vs maison)
   - Ancienneté (ajustement temporel)
3. Estimation pondérée par scores
4. Score de fiabilité (4 composantes)
5. Ajustement temporel (inflation + dynamique Chablais)
6. Tests avec Grok : 5 biens réels + 20 tests unitaires

ORCHESTRATION :
- Haiku pour implémentation EstimationAlgorithm
- Grok Code Fast 1 pour génération massive tests (économie coût ~60%)
- Sonnet si raisonnement architectural profond nécessaire

LIVRABLES ATTENDUS :
- src/estimation_algorithm.py (classe + méthodes scoring)
- test_phase3_estimations.py (20+ tests)
- Documentation complète
- 5/5 tests passants sur biens réels Chablais

DURÉE : 2-3 heures
```

---

## 📁 FICHIERS IMPORTANTS PHASE 3

| Fichier | Usage |
|---------|-------|
| `PHASE2_RECAP_POUR_PHASE3.md` | Détails complets Phase 2 + SupabaseDataRetriever |
| `docs/MVP_REQUIREMENTS.md` | Spécifications MVP complètes |
| `src/supabase_data_retriever.py` | Code retriever (utiliser directement) |
| `test_phase2_integration.py` | Exemples tests validés (5/5 pass) |
| `.env` | Credentials Supabase + Grok |

---

## 🔐 CREDENTIALS (dans .env)

```
SUPABASE_URL=https://fwcuftkjofoxyjbjzdnh.supabase.co
SUPABASE_KEY=sbp_c56fb1e3ee2778583ab929550793aabaa9dc552a
SUPABASE_DB_PASSWORD=tetrarchic-gazumping-lares-mercaptide
GOOGLE_MAPS_API_KEY=AIzaSyBdwqhBKgOwi6kHejyhFFw8QluV4pkpwQE
```

**Grok API Key** (déjà dans MCP config) :
`xai-OFmpjg3Ic3fx7HH1qln8XVtmMygVI8emgX5nhyaGOps0eLTEQ0ZAPk3dKRHMpQrKo9kWeiGAWOHRYMVg`

---

## 📊 TIMELINE PHASE 3

| Activité | Durée | Modèle |
|----------|-------|--------|
| Config Grok MCP + restart | 10 min | Manual |
| Créer orchestrator-agent | 10 min | Manual |
| Planification EstimationAlgorithm | 15 min | Haiku/Sonnet |
| Implémentation classe + scoring | 60 min | **Haiku** |
| Tests unitaires (générer via Grok) | 20 min | **Grok Code Fast 1** |
| Validation 5 biens Chablais | 20 min | **Grok** |
| Debugging/refactoring | 15 min | Haiku |
| **Total** | **2h30** | |

---

## ✅ CHECKLIST AVANT PHASE 3

**À vérifier demain matin** :

- [ ] Grok MCP configuré dans claude_desktop_config.json
- [ ] Claude Code redémarré après config
- [ ] orchestrator-agent créé en `.claude/agents/`
- [ ] `mcp__grok__chat_completion` accessible (test simple)
- [ ] PHASE2_RECAP_POUR_PHASE3.md consulté
- [ ] .env credentials valides
- [ ] Supabase accessible (145k mutations)

**Prêt pour Phase 3 !** 🚀

---

## 🎯 FIN DU GUIDE

**Document créé** : 2025-10-21
**À utiliser** : 2025-10-22 (demain, nouvelle conversation)
**Context** : Nouvelle conversation = 100% context frais
**Statut** : Phase 2 100% terminée et committée ✅

### Pour demain :
1. Copie ce guide dans nouvelle conversation
2. Suis les étapes config (Grok MCP + orchestrator-agent)
3. Redémarre Claude Code
4. Lance Phase 3 avec la commande fournie
5. Profite de l'orchestration intelligente Grok/Haiku/Sonnet pour optimiser coût/vitesse ! 💚
