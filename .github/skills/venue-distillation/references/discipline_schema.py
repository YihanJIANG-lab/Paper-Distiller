"""Discipline Schema Loader — 按学科家族加载蒸馏 schema。

每个学科家族 (cs, economics, ...) 对应一个 YAML 文件，定义了
五层蒸馏中各层的提取字段、prompt 片段、聚合规则和分类体系。

Public API
----------
- ``load_schema(family)`` → ``DisciplineSchema``
- ``DisciplineSchema`` — 统一访问 schema 内容的 dataclass
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import yaml

logger = logging.getLogger(__name__)

_SCHEMA_DIR = Path(__file__).parent / "discipline_schemas"
_DEFAULT_FAMILY = "cs"


@dataclass
class DisciplineSchema:
    """Parsed discipline schema for runtime use."""

    family: str = "cs"
    display_name: str = "Computer Science / AI"
    default_venues: list[str] = field(default_factory=list)

    # Layer 1
    l1_system_prompt: str = ""
    l1_boolean_facets: dict[str, str] = field(default_factory=dict)
    l1_list_facets: dict[str, dict] = field(default_factory=dict)
    l1_enum_facets: dict[str, dict] = field(default_factory=dict)
    l1_int_facets: dict[str, str] = field(default_factory=dict)
    l1_aggregation_pct_fields: list[dict] = field(default_factory=list)
    l1_skill_extra_lines: list[dict] = field(default_factory=list)

    # Layer 2
    l2_novelty_types: dict[str, str] = field(default_factory=dict)
    l2_novelty_examples: dict[str, list[str]] = field(default_factory=dict)
    l2_gap_hypothesis_context: str = ""

    # Layer 3
    l3_figure_types: list[str] = field(default_factory=list)
    l3_discussion_elements: list[str] = field(default_factory=list)
    l3_related_work_strategies: list[str] = field(default_factory=list)

    # Layer 4
    l4_review_source: str = "OpenReview"
    l4_rejection_categories: list[str] = field(default_factory=list)

    # ---- Derived helpers ------------------------------------------------

    def build_l1_json_schema(self) -> str:
        """Build the JSON extraction schema string for Layer 1 prompt."""
        parts = []
        for fname, desc in self.l1_boolean_facets.items():
            parts.append(f'  "{fname}": <bool - {desc}>')
        for fname, meta in self.l1_list_facets.items():
            opts = meta.get("options")
            if opts:
                opts_str = "|".join(f'"{o}"' for o in opts)
                parts.append(f'  "{fname}": [<{opts_str}>]')
            else:
                parts.append(f'  "{fname}": [<str - {meta.get("prompt", "")}>]')
        for fname, meta in self.l1_enum_facets.items():
            opts = meta.get("options", [])
            parts.append(f'  "{fname}": "<{"| ".join(opts)}>"')
        for fname, desc in self.l1_int_facets.items():
            parts.append(f'  "{fname}": <int or null - {desc}>')
        return "{\n" + ",\n".join(parts) + "\n}"

    def build_l2_novelty_prompt(self) -> str:
        """Build the novelty_type prompt with definitions and examples."""
        lines = []
        for ntype, desc in self.l2_novelty_types.items():
            examples = self.l2_novelty_examples.get(ntype, [])
            ex_str = " or ".join(f'"{e}"' for e in examples[:2]) if examples else ""
            line = f"  - {ntype}: {desc}"
            if ex_str:
                line += f". Examples: {ex_str}"
            lines.append(line)
        return "\n".join(lines)

    def build_l3_figure_list(self) -> str:
        """Build the figure/table type list for Layer 3 prompt."""
        return ", ".join(f"'{t}'" for t in self.l3_figure_types)

    def build_l3_discussion_list(self) -> str:
        """Build the discussion elements list for Layer 3 prompt."""
        return ", ".join(f"'{e}'" for e in self.l3_discussion_elements)

    @property
    def l2_valid_novelty_labels(self) -> set[str]:
        return set(self.l2_novelty_types.keys())


def load_schema(family: str | None = None) -> DisciplineSchema:
    """Load a discipline schema by family name.

    Parameters
    ----------
    family : str or None
        e.g. "cs", "economics". If None, loads the default (cs).

    Returns
    -------
    DisciplineSchema
    """
    family = family or _DEFAULT_FAMILY
    schema_path = _SCHEMA_DIR / f"{family}.yaml"
    if not schema_path.exists():
        logger.warning(
            "[discipline] Schema '%s' not found at %s, falling back to '%s'",
            family, schema_path, _DEFAULT_FAMILY,
        )
        schema_path = _SCHEMA_DIR / f"{_DEFAULT_FAMILY}.yaml"
        if not schema_path.exists():
            logger.error("[discipline] Default schema also missing!")
            return DisciplineSchema()

    with open(schema_path, encoding="utf-8") as f:
        raw: dict[str, Any] = yaml.safe_load(f) or {}

    l1 = raw.get("layer1_rigor", {})
    l2 = raw.get("layer2_idea_dna", {})
    l3 = raw.get("layer3_narrative", {})
    l4 = raw.get("layer4_rejection", {})

    return DisciplineSchema(
        family=raw.get("discipline_family", family),
        display_name=raw.get("display_name", family),
        default_venues=raw.get("default_venues", []),
        # Layer 1
        l1_system_prompt=l1.get("system_prompt", ""),
        l1_boolean_facets=l1.get("boolean_facets", {}),
        l1_list_facets=l1.get("list_facets", {}),
        l1_enum_facets=l1.get("enum_facets", {}),
        l1_int_facets=l1.get("int_facets", {}),
        l1_aggregation_pct_fields=l1.get("aggregation_pct_fields", []),
        l1_skill_extra_lines=l1.get("skill_extra_lines", []),
        # Layer 2
        l2_novelty_types=l2.get("novelty_types", {}),
        l2_novelty_examples=l2.get("novelty_examples", {}),
        l2_gap_hypothesis_context=l2.get("gap_hypothesis_prompt_context", ""),
        # Layer 3
        l3_figure_types=l3.get("expected_figure_types", []),
        l3_discussion_elements=l3.get("expected_discussion_elements", []),
        l3_related_work_strategies=l3.get("related_work_strategies", []),
        # Layer 4
        l4_review_source=l4.get("review_source", "OpenReview"),
        l4_rejection_categories=l4.get("rejection_categories", []),
    )
