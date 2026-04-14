# Distillation Design (Layers 1-3 LLM + Layer 5 Rule-Based)

## Architecture Overview

The distillation engine (`pipeline/rigor_distiller.py`) performs a single unified LLM call per paper, extracting Layers 1-3 of structured knowledge simultaneously. This is more cost-effective than 3 separate calls. Layer 5 (Citation & Reference Patterns) is extracted separately via regex and API metadata, with no LLM cost.

## Layer Definitions

### Layer 1: Rigor Facets (Experimental Methodology)

**Purpose:** Capture what constitutes rigorous experiments in this venue/field.

**Key Fields:**
- `has_pretrained_baseline` — Does the paper compare against pre-trained models?
- `baseline_types` — Categories: `pretrained_model`, `heuristic`, `fine_tuned`, `rule_based`, `none`
- `has_ablation` — Are ablation studies present?
- `dataset_names` — Real datasets used (e.g., GSM8K, MATH, CIFAR-10)
- `reports_std` — Does it report standard deviation / confidence intervals?
- `num_seeds_mentioned` — Number of random seeds for experiments
- `has_statistical_test` — Any formal statistical testing?

**Field-Specific Extensions:** Add custom fields per topic. For example:
- LLM Agents: `agent_frameworks`, `planning_reasoning`, `multi_agent`
- Computer Vision: `backbone_models`, `data_augmentation`, `resolution`
- NLP: `tokenizer_type`, `pretraining_data`, `multilingual`

### Layer 2: Idea DNA (Innovation Reasoning)

**Purpose:** Capture how successful papers frame their contributions.

**Key Fields:**
- `gap_description` — What problem/gap does the paper address?
- `hypothesis` — One-sentence testable claim
- `gap_to_hypothesis_reasoning` — Logical chain from gap to proposed solution
- `contribution_framing` — How contributions are worded (2-4 bullet points as authored)
- `novelty_type` — Classification:
  - `incremental` — Improves existing method by X%
  - `new_formulation` — New problem formulation or framework
  - `new_application` — Applies existing technique to new domain
  - `paradigm_shift` — Fundamentally new approach
- `rejection_risk_factors` — Anticipated reviewer concerns (1-3)
- `one_sentence_pitch` — Elevator pitch

### Layer 3: Narrative Structure (Writing Patterns)

**Purpose:** Capture how successful papers are organized and presented.

**Key Fields:**
- `intro_funnel_pattern` — How the intro narrows (e.g., "Broad success → specific limitation → our solution")
- `experiment_storyline` — Experiment narrative arc (e.g., "Main results → ablation → qualitative")
- `table_figure_types` — Types of visualizations used
- `discussion_elements` — What the paper discusses beyond results
- `related_work_strategy` — How related work is organized
- `section_flow` — Ordered list of actual section headings

## LLM Prompt Design

### System Prompt

```
You are an expert ML research analyst with deep experience in top-tier 
conference reviewing (NeurIPS, ICML, ICLR). You will analyze a paper and 
extract THREE layers of structured knowledge simultaneously. 
Only output valid JSON, no explanation.
```

### User Prompt Template (Full Text Available)

```
Analyze the following paper and extract three layers of knowledge.

Title: {title}
Venue: {venue} {year}

Abstract (first 1500 chars):
{abstract}

Introduction (first 2500 chars):
{intro_text}

Experiments section (first 3000 chars):
{experiment_text}

Output a single JSON object with these keys:
{
  "layer1_rigor": {
    "has_pretrained_baseline": bool,
    "baseline_types": [...],
    "has_ablation": bool,
    ...
  },
  "layer2_idea_dna": {
    "gap_description": "...",
    "hypothesis": "...",
    "novelty_type": "incremental|new_formulation|new_application|paradigm_shift",
    ...
  },
  "layer3_narrative": {
    "intro_funnel_pattern": "...",
    "table_figure_types": [...],
    ...
  }
}
```

### Abstract-Only Fallback

When full text is not available, use a reduced template with just title + abstract. The LLM infers all fields from the abstract alone (lower accuracy but still useful).

### Text Region Extraction

Before LLM call, extract relevant regions from full text:

```python
def _extract_intro(text: str) -> str:
    """Extract introduction section (≤2500 chars)."""
    # Look for "1 Introduction" or "1. Introduction" 
    # Then extract until "2 " or "2. " (next section)
    intro_pattern = re.compile(
        r"(?:^|\n)\s*1[\.\s]+(?:introduction|intro)\s*\n(.*?)(?=\n\s*2[\.\s])",
        re.I | re.S,
    )
    m = intro_pattern.search(text)
    return m.group(1)[:2500] if m else text[:2500]

def _extract_experiments(text: str) -> str:
    """Extract experiments section (≤3000 chars)."""
    # Look for sections titled "Experiment*", "Evaluation", "Results"
    exp_pattern = re.compile(
        r"(?:^|\n)\s*\d+[\.\s]+(?:experiment|evaluation|result).*?\n(.*?)(?=\n\s*\d+[\.\s]|\Z)",
        re.I | re.S,
    )
    m = exp_pattern.search(text)
    return m.group(1)[:3000] if m else ""
```

## Aggregation Logic

After individual paper extraction, aggregate across all papers:

### Idea DNA Aggregation

```python
def _aggregate_idea_dna(ideas: list[IdeaDNA]) -> dict:
    novelty_dist = Counter(i.novelty_type for i in ideas)
    
    all_risks = []
    for i in ideas:
        all_risks.extend(i.rejection_risk_factors)
    top_risks = [r for r, _ in Counter(all_risks).most_common(8)]
    
    example_chains = [
        {
            "title": i.title[:80],
            "gap": i.gap_description[:300],
            "hypothesis": i.hypothesis[:300],
            "reasoning": i.gap_to_hypothesis_reasoning,
            "contributions": i.contribution_framing[:4],
            "novelty_type": i.novelty_type,
        }
        for i in ideas if i.gap_description and i.hypothesis
    ][:10]
    
    return {
        "n_papers": len(ideas),
        "novelty_type_distribution": dict(novelty_dist),
        "top_rejection_risks": top_risks,
        "example_reasoning_chains": example_chains,
        "example_pitches": [i.one_sentence_pitch for i in ideas if i.one_sentence_pitch][:8],
    }
```

### Narrative Aggregation

```python
def _aggregate_narrative(narrs: list[NarrativeStructure]) -> dict:
    fig_types = Counter(t for n in narrs for t in n.table_figure_types)
    disc_elems = Counter(e for n in narrs for e in n.discussion_elements)
    rw_strats = Counter(n.related_work_strategy for n in narrs if n.related_work_strategy)
    
    flows = Counter(" → ".join(n.section_flow[:6]) for n in narrs if n.section_flow)
    
    return {
        "n_papers": len(narrs),
        "figure_table_type_frequency": dict(fig_types.most_common(10)),
        "discussion_elements_frequency": dict(disc_elems),
        "related_work_strategies": dict(rw_strats),
        "common_section_flows": [f for f, _ in flows.most_common(3)],
        "intro_funnel_examples": [
            {"title": n.title[:80], "pattern": n.intro_funnel_pattern}
            for n in narrs if n.intro_funnel_pattern
        ][:10],
        "experiment_storyline_examples": [
            {"title": n.title[:80], "storyline": n.experiment_storyline}
            for n in narrs if n.experiment_storyline
        ][:10],
    }
```

## Model Selection

Recommended models by budget:
- **High quality:** `claude-opus-4-6` or `gpt-4o` — Best for nuanced novelty classification
- **Cost-effective:** `claude-sonnet-4-20250514` or `gpt-4o-mini` — Good for 100+ paper batches
- **Local/free:** Not recommended — structured JSON extraction requires strong instruction following

## Cost Estimation

For 200 papers with full text:
- Input: ~3000 tokens/paper (abstract + intro + experiments)
- Output: ~500 tokens/paper (Layers 1-3 JSON)
- Total: ~700K input + 100K output tokens
- Claude Opus 4.6: ~$14 input + $7.50 output = **~$22**
- GPT-4o: ~$1.75 input + $3.00 output = **~$5**

## Layer 5: Citation & Reference Patterns (Rule-Based)

Layer 5 is extracted **without any LLM calls** using regex on full text + API metadata. It runs after the LLM-based layers and adds zero cost.

### Dataclass

```python
@dataclass
class CitationProfile:
    paper_id: str = ""
    title: str = ""
    n_references: int = 0
    citation_style: str = ""             # "numeric" / "author_year" / "mixed"
    citation_density_per_1k_words: float = 0.0
    section_citation_counts: dict[str, int] = field(default_factory=dict)
    intro_citation_ratio: float = 0.0
    related_work_citation_ratio: float = 0.0
    avg_citations_per_paragraph: float = 0.0
    citation_cluster_ratio: float = 0.0  # [1,2,3] style clustered cites
    n_self_citations_approx: int = 0
    recent_year_ratio: float = 0.0       # refs from last 3 years
```

### Extraction Method

`_extract_citation_profile(paper)` uses 8 regex passes:
1. Citation style detection (numeric `[1]` vs author-year `(Smith et al., 2024)`)
2. Reference count (`\bibitem` count or max `[N]`)
3. Citation density (total citations / words * 1000)
4. Section-wise citation counts (splits text at section headers)
5. Per-paragraph average citations
6. Cluster citation ratio (`[1,2,3]` vs `[1]`)
7. Recent reference ratio (years ≥2023 / total)
8. Approximate self-citations (author last names in bibliography)

### Aggregation

`_aggregate_citation_profiles(profiles)` produces:
```json
{
  "n_papers": 60,
  "reference_count_stats": {"mean": 43.4, "median": 38, "p25": 26, "p75": 52},
  "citation_style_distribution": {"numeric": 45, "author_year": 12, "mixed": 3},
  "citation_density_stats": {"mean": 3.43, "median": 3.06},
  "section_citation_distribution_pct": {"Related Work": 26.9, "Experiments": 25.9, ...},
  "avg_intro_citation_pct": 18.2,
  "avg_related_work_citation_pct": 24.4,
  "avg_cluster_citation_pct": 14.5,
  "avg_recent_3yr_reference_pct": 39.3
}
```

### Dual Source Strategy

When full text is not available (e.g., OpenAlex accepted papers):
- Fetch `referenced_works_count` from OpenAlex API per paper
- Produces reference count statistics only (no density/section breakdown)
- The full-text extraction runs on rejected papers (OpenReview) which always have full text

Both sources are combined in the skill file for a complete accepted-vs-rejected comparison.
