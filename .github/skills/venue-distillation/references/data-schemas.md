# Data Schemas

All data files are stored in `literature/corpus/{topic_id}/`.

## Accepted Paper Schema

**File:** `papers.jsonl` (one JSON object per line)

```json
{
  "paper_id": "openalex-2024-12345",
  "title": "Paper Title",
  "abstract": "Full abstract text...",
  "authors": [{"name": "First Author"}, {"name": "Second Author"}],
  "venue": "ICML",
  "year": 2024,
  "citation_count": 42,
  "url": "https://arxiv.org/abs/...",
  "source": "openalex",
  "full_text": "Full paper text (≤60k chars, null if not available)"
}
```

**Fields:**
| Field | Type | Description |
|-------|------|-------------|
| `paper_id` | str | Unique ID (source-prefixed) |
| `title` | str | Paper title |
| `abstract` | str | Full abstract |
| `authors` | list[dict] | Each with `name` key |
| `venue` | str | Conference/journal name (NeurIPS, ICML, ICLR, etc.) |
| `year` | int | Publication year |
| `citation_count` | int | Total citations at collection time |
| `url` | str | Paper URL (usually arxiv) |
| `source` | str | Data source: `"openalex"` or `"s2"` (Semantic Scholar) |
| `full_text` | str\|null | Extracted PDF text (up to 60,000 chars) |

## Rejected Paper Schema

**File:** `rejected_papers_openreview.jsonl` (one JSON object per line)

```json
{
  "openreview_id": "abc123xyz",
  "forum": "abc123xyz",
  "title": "Rejected Paper Title",
  "abstract": "Abstract text...",
  "keywords": ["keyword1", "keyword2"],
  "authors": ["Author One", "Author Two"],
  "venue": "ICLR",
  "year": 2024,
  "reviews": [
    {
      "rating": "5: marginally below the acceptance threshold",
      "confidence": "4: You are confident in your assessment",
      "soundness": "2 fair",
      "presentation": "3 good",
      "contribution": "2 fair",
      "summary": "Review summary text...",
      "strengths": "Strengths text (≤500 chars)...",
      "weaknesses": "Weaknesses text (≤500 chars)..."
    }
  ],
  "full_text": "Full paper text (≤60k chars)",
  "has_full_text": true,
  "avg_rating": 4.5,
  "decision": "Reject",
  "collected_at": "2026-04-05T12:00:00",
  "paper_id": "rej-ICLR-2024-abc123xyz"
}
```

**Review Sub-Schema:**
| Field | Type | Scale | Description |
|-------|------|-------|-------------|
| `rating` | str | "1: strong reject" to "10: strong accept" | Overall score (numeric extracted via regex) |
| `confidence` | str | "1" to "5" | Reviewer confidence |
| `soundness` | str | "1 poor" to "4 excellent" | Technical soundness (v2 API) |
| `presentation` | str | "1 poor" to "4 excellent" | Writing quality (v2 API) |
| `contribution` | str | "1 poor" to "4 excellent" | Significance (v2 API) |
| `summary` | str | — | Review summary |
| `strengths` | str | — | Strengths (truncated to 500 chars) |
| `weaknesses` | str | — | Weaknesses (truncated to 500 chars) |

**Note:** v1 API (ICLR 2022-2023) may not have `soundness`/`presentation`/`contribution` fields.

## Distillation Output Schemas

### Layer 1: Rigor Facets

**File:** `facets.json` (JSON array)

```json
[
  {
    "paper_id": "openalex-2024-12345",
    "title": "Paper Title",
    "has_pretrained_baseline": true,
    "baseline_types": ["pretrained_model", "heuristic"],
    "has_ablation": true,
    "has_real_data": true,
    "data_type": "real",
    "dataset_names": ["GSM8K", "MATH", "HumanEval"],
    "reports_std": true,
    "num_seeds_mentioned": 5,
    "has_statistical_test": false,
    "domain_specific_practices": ["error analysis", "case study"],
    "methodology_keywords": ["chain-of-thought", "self-reflection"],
    "agent_frameworks": ["ReAct", "Reflexion"],
    "planning_reasoning": true,
    "multi_agent": false,
    "used_full_text": true
  }
]
```

### Layer 2: Idea DNA

**File:** `idea_dna.json` (JSON array)

```json
[
  {
    "paper_id": "openalex-2024-12345",
    "title": "Paper Title",
    "gap_description": "Existing agents fail to...",
    "hypothesis": "By incorporating X, we can achieve Y...",
    "gap_to_hypothesis_reasoning": "Logical chain from gap to solution...",
    "contribution_framing": [
      "We propose the first framework for...",
      "We demonstrate that..."
    ],
    "novelty_type": "new_formulation",
    "positioning_strategy": "Builds on X but addresses limitation Y",
    "rejection_risk_factors": [
      "Limited to specific domain",
      "Scalability not demonstrated"
    ],
    "one_sentence_pitch": "We show that X achieves Y by Z.",
    "used_full_text": true
  }
]
```

**`novelty_type` values:** `incremental` | `new_formulation` | `new_application` | `paradigm_shift`

### Layer 3: Narrative Structure

**File:** `narrative_structure.json` (JSON array)

```json
[
  {
    "paper_id": "openalex-2024-12345",
    "title": "Paper Title",
    "intro_funnel_pattern": "Broad capability → specific limitation → our solution",
    "experiment_storyline": "Benchmark comparison → ablation → qualitative analysis",
    "table_figure_types": [
      "architecture_diagram", "performance_table",
      "bar_comparison", "qualitative_examples"
    ],
    "discussion_elements": ["limitations", "future_work", "broader_impact"],
    "related_work_strategy": "by_subfield",
    "section_flow": [
      "Introduction", "Related Work", "Preliminaries",
      "Method", "Experiments", "Conclusion"
    ],
    "used_full_text": true
  }
]
```

**`related_work_strategy` values:** `by_subfield` | `dedicated_section` | `integrated_in_intro` | `in_appendix` | `minimal_or_none`

### Aggregated Distillation

**File:** `distillation_aggregated.json`

```json
{
  "topic_id": "topic_1",
  "aggregated_idea_patterns": {
    "n_papers": 238,
    "novelty_type_distribution": {
      "new_formulation": 156,
      "new_application": 57,
      "incremental": 20,
      "paradigm_shift": 5
    },
    "top_rejection_risks": ["Limited evaluation scope", "..."],
    "example_pitches": ["We show that...", "..."],
    "example_reasoning_chains": [
      {
        "title": "Paper Title (≤80 chars)",
        "gap": "Gap description (≤300 chars)",
        "hypothesis": "Hypothesis (≤300 chars)",
        "reasoning": "Full reasoning chain",
        "contributions": ["Contribution 1", "Contribution 2"],
        "novelty_type": "new_formulation"
      }
    ],
    "contribution_examples": {
      "We propose the first": ["Full text 1", "Full text 2"],
      "We demonstrate that": ["Full text 3"]
    }
  },
  "aggregated_narrative_patterns": {
    "n_papers": 238,
    "figure_table_type_frequency": {
      "performance_table": 203,
      "bar_comparison": 198,
      "architecture_diagram": 156
    },
    "discussion_elements_frequency": {
      "limitations": 230,
      "future_work": 211,
      "broader_impact": 203
    },
    "related_work_strategies": {
      "by_subfield": 142,
      "dedicated_section": 78
    },
    "common_section_flows": [
      "Introduction → Related Work → Method → Experiments → Conclusion"
    ],
    "intro_funnel_examples": [
      {"title": "Paper Title", "pattern": "Pattern description"}
    ],
    "experiment_storyline_examples": [
      {"title": "Paper Title", "storyline": "Storyline description"}
    ]
  },
  "aggregated_citation_patterns": {
    "accepted": {
      "source": "OpenAlex API metadata",
      "n_papers": 60,
      "n_papers_with_ref_data": 56,
      "reference_count_stats": {
        "mean": 43.4, "median": 38, "min": 7, "max": 184,
        "p25": 26, "p75": 52
      }
    },
    "rejected": {
      "source": "OpenReview full text (regex extraction)",
      "n_papers": 120,
      "reference_count_stats": {"mean": 27.0, "median": 18},
      "citation_density_stats": {"mean": 3.43, "median": 3.06},
      "citation_style_distribution": {"author_year": 109, "mixed": 9, "numeric": 2},
      "section_citation_distribution_pct": {
        "Related Work": 26.9, "Experiments": 25.9,
        "Introduction": 18.2, "Method": 11.8
      },
      "avg_intro_citation_pct": 18.2,
      "avg_related_work_citation_pct": 24.4,
      "avg_cluster_citation_pct": 14.5,
      "avg_recent_3yr_reference_pct": 39.3
    }
  },
  "n_papers_analyzed": 238,
  "distilled_at": "2026-04-06T04:47:34"
}
```

### Rejected Distillation

**File:** `rejected_distillation.json`

```json
{
  "topic_id": "topic_1",
  "topic_name": "LLM Agents",
  "summary": {
    "n_papers": 100,
    "n_with_full_text": 100,
    "n_with_reviews": 100,
    "venue_distribution": {"ICLR2024": 45, "NeurIPS2024": 35, "NeurIPS2023": 20}
  },
  "reviewer_weakness_patterns": {
    "total_weakness_mentions": 287,
    "weakness_categories_ranked": [
      {
        "category": "writing_clarity",
        "count": 49,
        "percentage": 49.0,
        "examples": ["...snippet...", "...snippet..."]
      }
    ],
    "per_venue": {
      "ICLR2024": {"writing_clarity": 25, "novelty_insufficient": 15}
    }
  },
  "review_score_analysis": {
    "overall": {
      "rating": {"mean": 4.94, "min": 1.0, "max": 10.0, "n": 288},
      "soundness": {"mean": 2.5, "min": 1.0, "max": 4.0, "n": 200},
      "presentation": {"mean": 2.6, "min": 1.0, "max": 4.0, "n": 200}
    },
    "per_venue_avg_rating": {"ICLR2024": {"mean": 4.8, "n": 130}}
  },
  "figure_table_patterns": {
    "avg_figures_per_paper": 5.9,
    "avg_tables_per_paper": 4.7,
    "figure_type_frequency": {"performance_table": 230, "line_plot": 137},
    "per_venue_figure_types": {}
  },
  "writing_style_metrics": {
    "overall": {
      "avg_sentence_length": {"mean": 19.8, "min": 12.1, "max": 32.4},
      "equation_density_per_1k_words": {"mean": 0.1},
      "citation_density_per_1k_words": {"mean": 5.3}
    },
    "per_venue": {}
  },
  "narrative_structure_patterns": {
    "common_section_flows": [
      {"flow": "Introduction → Related Work → Method → Experiments → Conclusion", "count": 28}
    ],
    "discussion_elements_frequency": {
      "limitations": {"count": 71, "percentage": 71.0},
      "future_work": {"count": 47, "percentage": 47.0},
      "broader_impact": {"count": 25, "percentage": 25.0}
    },
    "related_work_strategies": {"dedicated_section": 45, "by_subfield": 30}
  },
  "accepted_comparison": {
    "comparison_available": true,
    "n_accepted_analyzed": 238,
    "n_rejected_analyzed": 100,
    "discussion_elements_comparison": {
      "broader_impact": {"rejected_%": 25.0, "accepted_%": 85.3, "diff": 60.3},
      "limitations": {"rejected_%": 71.0, "accepted_%": 96.6, "diff": 25.6}
    },
    "figure_type_comparison": {},
    "related_work_strategy_comparison": {}
  }
}
```

### Layer 5: Citation Profiles

**File:** `citation_profiles.json` (JSON array — papers with full text)

```json
[
  {
    "paper_id": "rej-ICLR-2024-abc123",
    "title": "Paper Title",
    "n_references": 42,
    "citation_style": "author_year",
    "citation_density_per_1k_words": 3.5,
    "section_citation_counts": {
      "Introduction": 12,
      "Related Work": 18,
      "Method": 5,
      "Experiments": 15,
      "Conclusion": 3
    },
    "intro_citation_ratio": 0.226,
    "related_work_citation_ratio": 0.340,
    "avg_citations_per_paragraph": 1.8,
    "citation_cluster_ratio": 0.15,
    "n_self_citations_approx": 3,
    "recent_year_ratio": 0.45
  }
]
```

**File:** `accepted_citation_meta.json` (JSON array — accepted papers via API)

```json
[
  {
    "paper_id": "openalex-W1234567",
    "title": "Paper Title",
    "n_references": 38,
    "cited_by_count": 25,
    "year": 2024
  }
]
```

| Field | Type | Description |
|-------|------|-------------|
| `n_references` | int | Total reference count |
| `citation_style` | str | `"numeric"` / `"author_year"` / `"mixed"` |
| `citation_density_per_1k_words` | float | Citations per 1000 words |
| `section_citation_counts` | dict | Citation count per detected section |
| `intro_citation_ratio` | float | Fraction of citations in Introduction |
| `related_work_citation_ratio` | float | Fraction of citations in Related Work |
| `citation_cluster_ratio` | float | Proportion of multi-ref citations `[1,2,3]` |
| `recent_year_ratio` | float | Fraction of references from last 3 years |
