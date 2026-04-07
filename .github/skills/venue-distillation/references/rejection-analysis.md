# Rejection Analysis Design

## Overview

Rejected paper analysis is **fully rule-based** — no LLM API needed. It uses regex patterns + statistics to extract actionable patterns from reviewer feedback, paper structure, and writing metrics.

## Input

`literature/corpus/{topic_id}/rejected_papers_openreview.jsonl` — Each line contains a paper with `reviews[]` and `full_text`.

## Analysis Components

### 1. Reviewer Weakness Classification (14 Categories)

Each category is a regex pattern matched against `review.weaknesses` text:

| Category | Regex Signals | What it Captures |
|----------|--------------|------------------|
| `writing_clarity` | poor writ, unclear, confus, grammar, typo, readability | Presentation quality |
| `novelty_insufficient` | limited novelty, incremental, not novel, marginal contrib | Contribution significance |
| `experiment_insufficient` | insufficient experiment, lack experiment, limited evaluat | Experimental evidence |
| `baseline_missing` | miss baseline, more baseline, state-of-the-art compar | Comparison completeness |
| `motivation_weak` | motiv unclear, weak, not clear, justif | Research justification |
| `theoretical_gap` | theoretical gap, lack theory, no convergence, no proof | Formal analysis |
| `scalability_concern` | scal, large-scale, real-world, computation cost | Practical applicability |
| `reproducibility` | reproduc, code not avail, implementation detail | Reproducibility |
| `figure_table_quality` | figure unclear, table poor, visualization improve | Visual presentation |
| `dataset_limitation` | small dataset, limited data, toy, synthetic, only benchmark | Data diversity |
| `related_work_gap` | miss related, reference, citation, important work miss | Literature coverage |
| `presentation_issues` | present poor, notation inconsist, symbol undefined | Technical presentation |
| `overclaimed` | overclaim, exaggerat, too strong, unsupported claim | Claim calibration |
| `ablation_missing` | ablation miss, lack, need, should | Component analysis |

**Implementation:**
```python
WEAKNESS_CATEGORIES = {
    "writing_clarity": re.compile(
        r"(?:poor(?:ly)?\s*writ|unclear|confus|hard to (?:follow|read|understand)|"
        r"readability|grammar|typo|poorly.?organized|not.*well.?written|"
        r"writing\s+quality|needs\s+proofread|language\s+quality)", re.I,
    ),
    # ... 13 more categories
}

def categorize_weaknesses(reviews):
    for review in reviews:
        for cat_name, pattern in WEAKNESS_CATEGORIES.items():
            if pattern.findall(review["weaknesses"]):
                counts[cat_name] += 1
```

### 2. Review Score Analysis

Extract numeric ratings from string fields:

```python
def extract_numeric_rating(rating_str):
    """'5: marginally below' → 5.0"""
    m = re.search(r"(\d+(?:\.\d+)?)", str(rating_str))
    return float(m.group(1)) if m else None
```

Compute per-field statistics: `{mean, min, max, n, distribution}`
Fields: `rating`, `confidence`, `soundness`, `presentation`, `contribution`

### 3. Figure/Table Pattern Detection

12 figure type regex patterns matched against full text:

| Type | Regex Signals |
|------|--------------|
| `architecture_diagram` | figure N: architecture, framework, overview, pipeline |
| `bar_chart` | bar chart, bar plot, barplot |
| `line_plot` | learning curve, training curve, convergence, loss curve |
| `ablation_table` | table N: ablation, ablative |
| `performance_table` | table N: result, comparison, performance, benchmark |
| `qualitative_examples` | figure N: qualitative, example, visualization, case study |
| `heatmap` | heatmap, attention map, saliency, grad-cam |
| `scatter_plot` | scatter plot, t-SNE, UMAP, embedding |
| `confusion_matrix` | confusion matrix |
| `pipeline_diagram` | figure N: pipeline, workflow, flowchart |
| `radar_chart` | radar chart, spider chart |
| `box_plot` | boxplot, violin plot |

### 4. Writing Metrics

Computed from full text:
- `n_words` — Total word count
- `avg_sentence_length` — Words per sentence
- `n_paragraphs` — Double-newline separated paragraphs
- `n_equations` — Count of `$...$`, `\[...\]`, `\begin{equation}`
- `n_citations` — Count of `(Author et al., 2024)` and `[1, 2, 3]` patterns
- `equation_density_per_1k_words` — Equations / (words/1000)
- `citation_density_per_1k_words` — Citations / (words/1000)

### 5. Section Structure Analysis

Detect sections via regex on lines:
```python
SECTION_PATTERNS = [
    (re.compile(r"^\s*(?:\d+[\.\s]+)?(?:introduction)\s*$", re.I|re.M), "Introduction"),
    (re.compile(r"^\s*(?:\d+[\.\s]+)?(?:related\s+work|background)\s*$", re.I|re.M), "Related Work"),
    # ... more patterns
]
```

Also detects:
- `discussion_elements`: limitations, future_work, broader_impact, failure_cases, reproducibility_statement
- `related_work_strategy`: by_subfield, dedicated_section, integrated_in_intro, minimal_or_none

### 6. Accepted vs Rejected Comparison

The most actionable insight — compares structural elements between accepted (from `narrative_structure.json`) and rejected papers:

```python
def compare_with_accepted(topic_id, rejected_result):
    accepted_narrs = json.load(open("narrative_structure.json"))
    
    # Compare discussion elements
    for elem in all_elements:
        accepted_pct = count_in_accepted / n_accepted * 100
        rejected_pct = count_in_rejected / n_rejected * 100
        diff = accepted_pct - rejected_pct
        # diff > 15pp → "MUST include this element"
```

**Typical findings:**
| Element | Accepted | Rejected | Implication |
|---------|----------|----------|-------------|
| broader_impact | 85%+ | 15-42% | **Must include** |
| limitations | 96%+ | 60-72% | **Must include** |
| future_work | 78-89% | 42-47% | **Must include** |

## Output Format

See [data-schemas.md](./data-schemas.md#rejected-distillation) for the full JSON schema.

## Extending the Analysis

To add new weakness categories:

```python
# Add to WEAKNESS_CATEGORIES in distill_rejected.py
"new_category": re.compile(
    r"(?:keyword1|keyword2|keyword3)", re.I,
),
```

To add new figure types:

```python
# Add to FIG_PATTERNS
"new_type": re.compile(
    r"(?:figure|fig\.?)\s*\d+\s*[.:]\s*(?:.*?)(?:keyword1|keyword2)", re.I,
),
```
