# Skill File Format

## Anatomy of a Generated Skill File

`pipeline/skills/{topic_id}.md` is the pre-compiled output of the entire distillation pipeline. It contains 5 layers wrapped in HTML comment delimiters for programmatic extraction.

## Structure

```markdown
# Skill: topic_1

> Distilled from 238 NeurIPS/ICML/ICLR papers
> Generated: 2026-04-06T04:47:34

---

## Layer 1: Rigor Facets

- 52% use pretrained baselines
- 85% include ablation studies
- 44% use real data
- 53% report std/variance (median seeds: 5)
- Common baselines: heuristic, pretrained_model, fine_tuned
- Common benchmarks: GSM8K, MATH, HumanEval, MBPP
- Seed distribution: min=2, p25=5, median=5, p75=10, max=200
- ICLR(91): pretrained=58%, ablation=86%, real_data=48%
- ICML(96): pretrained=51%, ablation=85%, real_data=47%
- NeurIPS(51): pretrained=41%, ablation=82%, real_data=31%

---

## Layer 2: Idea DNA

<!-- IDEA_PATTERNS_START -->
[Idea DNA Patterns - distilled from 238 NeurIPS/ICML/ICLR papers]

Novelty distribution in this field:
  - new_formulation: 156 papers
  - new_application: 57 papers
  - incremental: 20 papers
  - paradigm_shift: 5 papers

Common reviewer concerns to anticipate:
  - Evaluation is limited to simulated environments
  - Computational cost not adequately discussed
  ...

Example gap→hypothesis reasoning chains:
  [1] "Paper Title"
      Gap: Current methods fail to...
      Hypothesis: By incorporating X, we can...
      Reasoning: Since A implies B, and B enables C...
      Contributions: We propose...; We demonstrate...

Example one-sentence pitches:
  - "We show that X achieves Y by Z."
  - "We propose A, the first framework for B."
<!-- IDEA_PATTERNS_END -->

---

## Layer 3: Narrative Structure

<!-- NARRATIVE_PATTERNS_START -->
[Narrative Patterns - distilled from 238 NeurIPS/ICML/ICLR papers]

Common figure/table types:
  - performance_table: 203 papers
  - bar_comparison: 198 papers
  - architecture_diagram: 156 papers

Discussion section elements:
  - limitations: 230 papers
  - future_work: 211 papers
  - broader_impact: 203 papers

Common section organization:
  - Introduction → Related Work → Preliminaries → Method → Experiments → Conclusion

Introduction funnel patterns:
  - [Paper Title]: Broad success → specific limitation → our proposed solution

Experiment storyline patterns:
  - [Paper Title]: Main comparison → ablation → qualitative analysis → scaling
<!-- NARRATIVE_PATTERNS_END -->

---

## Layer 4: Rejection Anti-Patterns

<!-- REJECTION_PATTERNS_START -->
[Rejection Anti-Patterns — distilled from 100 rejected papers]

Common rejection reasons to AVOID:
  - writing_clarity (49.0% of rejected papers)
  - scalability_concern (38.0% of rejected papers)
  - experiment_insufficient (29.0% of rejected papers)
  - motivation_weak (28.0% of rejected papers)
  - novelty_insufficient (27.0% of rejected papers)
  - baseline_missing (26.0% of rejected papers)

Structural elements that strongly differentiate accepted from rejected:
  - broader_impact: accepted=85.3% vs rejected=25.0% → MUST include
  - future_work: accepted=88.7% vs rejected=47.0% → MUST include
  - limitations: accepted=96.6% vs rejected=71.0% → MUST include

Rejected papers averaged 5.9 figures and 4.7 tables.
Rejected papers avg sentence length: 19.8 words.
<!-- REJECTION_PATTERNS_END -->

---

## Layer 5: Citation & Reference Patterns

<!-- CITATION_PATTERNS_START -->
[Accepted Paper Reference Counts — 56 papers via OpenAlex API]

Reference list size: median=38, mean=43.4, range=[7-184], IQR=[26-52]

[Rejected Paper Citation Profiles — 120 papers via full text analysis]

Reference list size: median=18, mean=27.0
Citation density: median=3.06/1k words, mean=3.43/1k words
Citation style: author_year: 109, mixed: 9, numeric: 2
Citation distribution across sections:
  - Related Work: 26.9%
  - Experiments: 25.9%
  - Introduction: 18.2%
  - Method: 11.8%

Introduction citations: ~18.2% of total
Related Work citations: ~24.4% of total
Clustered citations ([1,2,3] style): ~14.5%
Recent references (≤3 years old): ~39.3%

Key insight: Accepted papers cite ~38 references (median),
vs ~18 in rejected papers — aim for ≥38 references.
<!-- CITATION_PATTERNS_END -->
```

## Delimiter System

Extraction uses simple string search:

```python
def _extract_section(content: str, tag: str) -> str:
    start_marker = f"<!-- {tag}_START -->"
    end_marker = f"<!-- {tag}_END -->"
    start = content.find(start_marker)
    end = content.find(end_marker)
    if start == -1 or end == -1:
        return ""
    return content[start + len(start_marker):end].strip()
```

**Tags:** `IDEA_PATTERNS`, `NARRATIVE_PATTERNS`, `REJECTION_PATTERNS`, `CITATION_PATTERNS`

Layer 1 (Rigor Facets) is informational only — not currently injected into prompts as a placeholder variable. It informs the `rigor_profiles` in `pipeline_config.yaml` instead.

## Loading Priority

```
orchestrator._prepare_prompts()
  │
  ├─ Try: load_skill(workspace, topic_id)
  │   → Read pipeline/skills/{topic_id}.md
  │   → Extract sections via <!-- TAG --> delimiters
  │   → Return {idea_patterns, narrative_patterns, rejection_patterns, citation_patterns}
  │   → FAST: no JSON parsing, no formatting
  │
  └─ Fallback: load_distillation_result() + load_rejected_distillation()
      → Read distillation_aggregated.json + rejected_distillation.json
      → format_idea_patterns() + format_narrative_patterns() + format_rejection_patterns()
      → SLOW: JSON parse + runtime string formatting
```

## Injection Points

| Variable | Stages | Purpose |
|----------|--------|---------|
| `{idea_patterns}` | S4 (Idea Generation), PAPER_COMPOSE, PAPER_DRAFT | Positive examples: how accepted papers frame ideas |
| `{narrative_patterns}` | S19 (Paper Revision), PAPER_COMPOSE, PAPER_DRAFT | Positive examples: how accepted papers are structured |
| `{rejection_patterns}` | S4 (Idea Generation), S19 (Paper Revision) | Negative examples: what to avoid to prevent rejection |
| `{citation_patterns}` | S19 (Paper Revision), Introduction, Related Work | Reference count targets, citation density, style norms |

## Regeneration

When new papers are added or distillation is re-run:

```python
from pipeline.rigor_distiller import RigorDistiller
from pathlib import Path

ws = Path(".")
rd = RigorDistiller(ws)
result = RigorDistiller.load_distillation_result(ws, "topic_N")
rd.generate_skill(result)  # Overwrites existing skill file
```

The skill file is deterministically generated from the JSON data — it can be safely regenerated at any time.
