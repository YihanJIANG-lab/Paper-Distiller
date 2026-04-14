# Multi-Discipline Distillation Design

## Motivation

The original Layers 1-3 distillation was designed for CS/AI venues (NeurIPS, ICML, ICLR). To support journals in economics, finance, management, and other disciplines, we introduced a **discipline schema** system: the 5-layer extraction/aggregation/formatting pipeline stays the same, but each layer's fields, prompt definitions, classification taxonomies, and aggregation rules are loaded from YAML configuration files.

## Architecture: Unified Engine + Per-Discipline Schema

```
                     ┌─────────────────────────────┐
                     │     discipline_schema.py     │
                     │   load_schema(family) →      │
                     │   DisciplineSchema dataclass  │
                     └──────────┬──────────────────┘
                                │
              ┌─────────────────┼─────────────────┐
              │                 │                  │
         cs.yaml          economics.yaml      (future)
              │                 │                  │
              ▼                 ▼                  ▼
        ┌─────────────────────────────────────────────┐
        │         rigor_distiller.py                   │
        │  ┌─ Layer 1: schema.l1_boolean_facets ──┐   │
        │  │  schema.l1_list_facets               │   │
        │  │  schema.l1_enum_facets               │   │
        │  │  schema.l1_int_facets                │   │
        │  ├─ Layer 2: schema.l2_novelty_types ───┤   │
        │  │  schema.l2_novelty_examples          │   │
        │  ├─ Layer 3: schema.l3_figure_types ────┤   │
        │  │  schema.l3_discussion_elements       │   │
        │  ├─ Layer 4: schema.l4_rejection_cats ──┤   │
        │  └─ Layer 5: regex engine (universal) ──┘   │
        └─────────────────────────────────────────────┘
```

## Schema File Format (YAML)

Each discipline family has a YAML file in `discipline-schemas/`. Required top-level keys:

```yaml
discipline_family: economics          # identifier
display_name: "Economics / Finance"   # human-readable
default_venues: [...]                 # target journals

layer1_rigor:
  system_prompt: "..."                # discipline-specific system role
  boolean_facets:                     # field_name → prompt description
    has_robustness_check: "does the paper include robustness checks?"
  list_facets:                        # field_name → {prompt, options?}
    model_types:
      prompt: "list of model types"
      options: ["OLS", "XGBoost", ...]
  enum_facets:                        # field_name → {prompt, options}
    data_type:
      prompt: "type of data"
      options: ["panel", "cross_sectional", ...]
  int_facets:                         # field_name → description
    sample_size: "total observations"
  aggregation_pct_fields: [...]       # which booleans to aggregate as %
  skill_extra_lines: [...]            # display templates for skill file

layer2_idea_dna:
  novelty_types:                      # label → definition
    new_empirical_evidence: "provides first empirical evidence..."
  novelty_examples:                   # label → example list
    new_empirical_evidence: ["first large-scale comparison..."]
  gap_hypothesis_prompt_context: "..." # economics-style gap framing

layer3_narrative:
  expected_figure_types: [...]
  expected_discussion_elements: [...]
  related_work_strategies: [...]

layer4_rejection:
  review_source: "peer_review_general"
  rejection_categories: [...]
```

## Currently Available Schemas

### `cs.yaml` — Computer Science / AI (Default)

Codifies all original hardcoded defaults. Backward-compatible: selecting `cs` or omitting the family parameter yields identical behavior to the pre-schema engine.

**Layer 1**: `has_pretrained_baseline`, `has_ablation`, `has_real_data`, `reports_std`, `has_statistical_test`, `planning_reasoning`, `multi_agent`; lists for `baseline_types`, `dataset_names`, `methodology_keywords`, `agent_frameworks`

**Layer 2**: 4 novelty types — `incremental`, `new_formulation`, `new_application`, `paradigm_shift`

### `economics.yaml` — Economics / Finance / Management

Designed for journals like Energy Economics, JFE, Management Science, AER, QJE.

**Layer 1**: 11 boolean facets (robustness check, endogeneity treatment, heterogeneity analysis, panel data, fixed effects, placebo test, etc.), 6 list facets (model_types with 23 options, dataset_names, dependent/independent variables, identification strategy with 9 options), 2 enum facets (data_type, data_granularity), 3 int facets (sample_size, num_countries, time_span_years)

**Layer 2**: 6 novelty types — `new_empirical_evidence`, `new_identification_strategy`, `new_methodology`, `new_application`, `new_theoretical_mechanism`, `incremental`

**Layer 4**: 13 rejection categories including `endogeneity_unaddressed`, `sample_selection_bias`, `robustness_inadequate`, `identification_weak`

## DisciplineSchema API

```python
from pipeline.discipline_schema import load_schema

schema = load_schema("economics")  # or "cs", or None for default

# Layer 1 prompt helpers
schema.build_l1_json_schema()     # → JSON template string for LLM
schema.build_l2_novelty_prompt()  # → novelty type definitions with examples
schema.build_l3_figure_list()     # → comma-separated figure types
schema.build_l3_discussion_list() # → comma-separated discussion elements

# Valid novelty labels for parsing
schema.l2_valid_novelty_labels    # → set of strings
```

## Adding a New Discipline

1. Create `discipline-schemas/<family>.yaml` following the format above
2. The engine automatically discovers it via `load_schema("<family>")`
3. No code changes needed — all prompt building, parsing, aggregation, and skill generation adapts to the schema

Candidate families for future addition:
- `natural_science` — Physics, Chemistry, Biology journals
- `medical` — Medical/Clinical journals (JAMA, Lancet, BMJ)
- `engineering` — IEEE/ACM engineering journals
- `social_science` — Psychology, Sociology, Political Science
