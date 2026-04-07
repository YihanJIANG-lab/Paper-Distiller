---
name: venue-distillation
description: 'Distill accepted and rejected papers from a conference/journal into structured skills for AI agent paper writing. Use when: setting up a new research topic, preparing for a new venue submission, bootstrapping agent knowledge for a conference (NeurIPS, ICML, ICLR, ACL, EMNLP, CVPR, etc.), building a corpus of positive/negative writing examples, extracting reviewer preference patterns. Covers: paper collection from OpenReview/Semantic Scholar/OpenAlex, 3-layer LLM-based distillation (rigor/idea/narrative), rejected paper heuristic analysis, skill file generation, and pipeline injection.'
argument-hint: 'Target venue name and topic (e.g., "NeurIPS 2025, LLM Agents")'
---

# Venue Distillation Skill

End-to-end methodology for collecting venue papers (accepted + rejected), distilling structured knowledge, and injecting it into an AI research agent's paper-writing pipeline.

## Overview

```
┌─ Phase 1: Collect ──────────────────────────────────────────┐
│  Accepted papers ← OpenAlex / Semantic Scholar / OpenReview │
│  Rejected papers ← OpenReview API (v1 / v2)                │
└─────────────────────────────────────────────────────────────┘
                          ↓
┌─ Phase 2: Distill ─────────────────────────────────────────┐
│  Accepted → LLM 3-layer extraction:                        │
│    Layer 1: Rigor Facets (baselines, ablation, datasets)   │
│    Layer 2: Idea DNA (gap→hypothesis reasoning chains)     │
│    Layer 3: Narrative Structure (figure types, section flow)│
│                                                             │
│  Rejected → Rule-based extraction:                          │
│    Layer 4: Rejection Anti-Patterns                         │
│    (reviewer weaknesses, score distributions, structural    │
│     gaps vs accepted papers)                                │
└─────────────────────────────────────────────────────────────┘
                          ↓
┌─ Phase 3: Package ─────────────────────────────────────────┐
│  generate_skill() → pipeline/skills/{topic_id}.md          │
│  4 layers with <!-- TAG_START/END --> delimiters            │
└─────────────────────────────────────────────────────────────┘
                          ↓
┌─ Phase 4: Inject ──────────────────────────────────────────┐
│  orchestrator._prepare_prompts()                           │
│    → {idea_patterns}      → S4 Idea Generation             │
│    → {narrative_patterns} → S19 Paper Revision / COMPOSE   │
│    → {rejection_patterns} → S4 + S19 (anti-patterns)       │
└─────────────────────────────────────────────────────────────┘
```

## When to Use

- Setting up a new research topic for the pipeline
- Targeting a new venue (conference / journal / workshop)
- Refreshing an existing topic with newer papers
- Diagnosing why generated papers are being rejected
- Understanding what differentiates accepted vs rejected work

## Prerequisites

- Python 3.10+ with packages: `openreview-py`, `PyMuPDF` (fitz), `requests`
- An LLM API key for accepted-paper distillation (Anthropic / OpenAI / Copilot OAuth)
- OpenReview account (guest access works for most data)
- Network access to OpenAlex / Semantic Scholar APIs

## Procedure

### Step 1: Define the Topic

Create a topic configuration with keyword sets:

```yaml
# In pipeline_config.yaml → corpus_builder → topic_keywords
topic_N:
  strong_keywords:    # +3 score each (must-have terms)
    - "your core topic phrase"
    - "another critical term"
  medium_keywords:    # +1 score each
    - "related but broader term"
    - "tangential area"
  threshold: 3        # Paper must score ≥3 to be included
```

Assign a `topic_id` (e.g., `topic_4`) and `topic_name` (e.g., `"Multimodal Reasoning"`).

### Step 2: Collect Accepted Papers

Use the corpus builder to search OpenAlex and Semantic Scholar:

```bash
python -c "
import sys; sys.path.insert(0, '.')
from pipeline.corpus_builder import CorpusBuilder
from pathlib import Path

cb = CorpusBuilder(Path('.'))
cb.build_corpus('topic_N', max_papers=300)
"
```

**Output:** `literature/corpus/topic_N/papers.jsonl`

See [accepted paper schema](./references/data-schemas.md#accepted-paper-schema).

Alternatively, if targeting OpenReview venues specifically, use the venue_papers approach documented in [collection-sources.md](./references/collection-sources.md).

### Step 3: Collect Rejected Papers

```bash
python scripts/fetch_openreview_rejected.py --max 150 --workers 4
```

This script:
1. Queries OpenReview for rejected submissions (v1 API for ICLR 2022-2023, v2 API for ICLR 2024+, NeurIPS 2024+)
2. Scores each paper against topic keywords
3. Downloads PDFs (90s timeout per paper, PyMuPDF text extraction, ≤60k chars)
4. Fetches reviewer scores and text (rating, confidence, soundness, presentation, contribution, strengths, weaknesses)
5. Saves incrementally with checkpoints every 10 papers

**Modes:**
- `--reviews-only` — Fill missing reviews for already-downloaded papers
- `--pdf-only` — Fill missing PDFs
- `--expand-topic topic_N --threshold 2` — Broaden keyword match to get more papers

**Output:** `literature/corpus/topic_N/rejected_papers_openreview.jsonl`

See [rejected paper schema](./references/data-schemas.md#rejected-paper-schema) and [OpenReview API guide](./references/openreview-api.md).

### Step 4: Distill Accepted Papers (LLM-based, 3 layers)

```bash
python -c "
import sys; sys.path.insert(0, '.')
from pipeline.rigor_distiller import RigorDistiller
from pathlib import Path

rd = RigorDistiller(Path('.'))
result = rd.distill_all('topic_N', n_papers=30, model='claude-opus-4-6')
print(f'Distilled {result.n_papers_analyzed} papers')
"
```

This performs a **single unified LLM call per paper** extracting 3 layers simultaneously.

**Outputs:**
- `literature/corpus/topic_N/facets.json` — Layer 1 raw data
- `literature/corpus/topic_N/idea_dna.json` — Layer 2 raw data
- `literature/corpus/topic_N/narrative_structure.json` — Layer 3 raw data
- `literature/corpus/topic_N/distillation_aggregated.json` — Aggregated statistics

See [3-layer distillation design](./references/distillation-design.md).

### Step 5: Distill Rejected Papers (Rule-based, no LLM needed)

```bash
python scripts/distill_rejected.py
```

This extracts from full text + review data:
- Reviewer weakness classification (14 categories via regex)
- Review score distributions (rating, soundness, presentation, contribution)
- Figure/table type frequency and writing metrics
- Section structure analysis
- **Accepted vs rejected comparison** (structural gaps)

**Output:** `literature/corpus/topic_N/rejected_distillation.json`

See [rejection analysis design](./references/rejection-analysis.md).

### Step 6: Generate Skill File

```bash
python -c "
import sys; sys.path.insert(0, '.')
from pipeline.rigor_distiller import RigorDistiller
from pathlib import Path

ws = Path('.')
rd = RigorDistiller(ws)
result = RigorDistiller.load_distillation_result(ws, 'topic_N')
skill_path = rd.generate_skill(result)
print(f'Skill generated: {skill_path}')
"
```

**Output:** `pipeline/skills/topic_N.md` — Self-contained skill with 4 layers, ready for orchestrator injection.

### Step 7: Verify Integration

```python
from pipeline.rigor_distiller import RigorDistiller
from pathlib import Path

ws = Path('.')
skill = RigorDistiller.load_skill(ws, 'topic_N')
print(f"idea_patterns:     {len(skill['idea_patterns'])} chars")
print(f"narrative_patterns: {len(skill['narrative_patterns'])} chars")
print(f"rejection_patterns: {len(skill['rejection_patterns'])} chars")
```

All three should return non-empty strings. The orchestrator will now automatically inject them into prompts at S4 (idea generation) and S19 (paper revision).

## Data Flow Reference

```
literature/corpus/{topic_id}/
├── papers.jsonl                        ← Step 2 (accepted papers)
├── rejected_papers_openreview.jsonl    ← Step 3 (rejected papers)
├── facets.json                         ← Step 4 (Layer 1 raw)
├── idea_dna.json                       ← Step 4 (Layer 2 raw)
├── narrative_structure.json            ← Step 4 (Layer 3 raw)
├── distillation_aggregated.json        ← Step 4 (aggregated stats)
├── rejected_distillation.json          ← Step 5 (rejection analysis)
└── rigor_report.md                     ← Step 4 (human-readable report)

pipeline/skills/{topic_id}.md           ← Step 6 (packaged skill)
```

## Key Design Decisions

1. **Single LLM call per accepted paper** — Extract 3 layers in one JSON response to minimize API cost
2. **Rule-based rejected analysis** — No LLM needed; regex + statistics suffice for pattern extraction
3. **Two-tier loading** — Preformatted `.md` skill (fast) with JSON fallback (runtime formatting)
4. **HTML comment delimiters** — `<!-- TAG_START -->` / `<!-- TAG_END -->` for section extraction without markdown parsing
5. **Accepted-vs-rejected comparison** — Most actionable insight: structural elements that differentiate acceptance

## Detailed References

- [Data Schemas](./references/data-schemas.md) — Full field definitions for all JSON files
- [Collection Sources](./references/collection-sources.md) — OpenReview, OpenAlex, Semantic Scholar API details
- [OpenReview API Guide](./references/openreview-api.md) — v1/v2 differences, auth, rate limiting, venue filters
- [3-Layer Distillation Design](./references/distillation-design.md) — LLM prompts, dataclasses, aggregation logic
- [Rejection Analysis Design](./references/rejection-analysis.md) — Regex patterns, metrics, comparison methodology
- [Skill File Format](./references/skill-file-format.md) — Anatomy of a generated skill .md file
