# Paper-Distiller

[English](README.md) | [中文](README_zh.md)

Paper-Distiller packages a reusable venue distillation workflow as a workspace skill.

The current repository contains one skill, `venue-distillation`, for turning accepted and rejected papers from a target venue into structured guidance that an AI research pipeline can reuse during idea generation, paper drafting, and revision.

**Multi-Discipline Support:** The distillation engine supports discipline-specific schemas via YAML configuration. Currently available schemas: Computer Science / AI (default) and Economics / Finance / Management. New disciplines can be added by creating a YAML file — no code changes required.

## What This Skill Does

The skill covers an end-to-end loop:

1. Collect accepted papers from sources such as OpenAlex, Semantic Scholar, and OpenReview.
2. Collect rejected papers and reviews from OpenReview.
3. Distill accepted papers into rigor, idea, and narrative patterns (Layers 1-3, LLM-based).
4. Distill rejected papers into reviewer-facing anti-patterns (Layer 4, rule-based).
5. Extract citation & reference patterns from full text and API metadata (Layer 5, rule-based, no LLM cost).
6. Package the result into a 5-layer skill file that can be injected into an agent pipeline.

## Repository Layout

```text
.github/
  skills/
    venue-distillation/
      SKILL.md
      references/
        collection-sources.md
        data-schemas.md
        discipline_schema.py        # YAML schema loader module
        discipline-schemas/
          cs.yaml                    # CS/AI default schema
          economics.yaml             # Economics/Finance/Management schema
        distillation-design.md
        multi-discipline.md          # Multi-discipline design doc
        openreview-api.md
        rejection-analysis.md
        skill-file-format.md
```

## How To Use In GitHub Copilot

Open this repository as a workspace in VS Code with GitHub Copilot Chat enabled.

Then ask for a venue distillation workflow in natural language, for example:

```text
Use the venue-distillation skill for NeurIPS 2025 on LLM Agents.
```

For non-CS disciplines:

```text
Use the venue-distillation skill with economics schema for Energy Economics on carbon emissions estimation.
```

Or:

```text
Distill accepted and rejected ICLR papers for multimodal reasoning and tell me how to package them into a skill.
```

The skill description in `.github/skills/venue-distillation/SKILL.md` is written so Copilot can discover it from requests about:

- venue paper distillation
- accepted vs rejected paper analysis
- OpenReview-based reviewer pattern extraction
- building skill files for research-writing agents

If your Copilot client exposes workspace skills as slash commands, you can also try:

```text
/venue-distillation NeurIPS 2025, LLM Agents
```

## How To Use In Claude-Style Skill Layouts

If you want the same content in a Claude-style environment, copy the skill directory to one of these locations in your target project:

- `.github/skills/venue-distillation/`
- `.claude/skills/venue-distillation/`
- `.agents/skills/venue-distillation/`

Keep the folder name aligned with the skill name and preserve `SKILL.md` plus the `references/` directory.

## Main Entry Point

Start with [.github/skills/venue-distillation/SKILL.md](.github/skills/venue-distillation/SKILL.md).

That file describes:

- when to use the skill
- required inputs
- the 5-layer methodology (rigor/idea/narrative/rejection/citation)
- output artifacts
- how the distilled patterns are injected into a writing pipeline

## Reference Files

- [Data Schemas](.github/skills/venue-distillation/references/data-schemas.md): accepted/rejected paper JSON schemas
- [Collection Sources](.github/skills/venue-distillation/references/collection-sources.md): source coverage and collection strategy
- [OpenReview API](.github/skills/venue-distillation/references/openreview-api.md): OpenReview v1/v2 usage details
- [Distillation Design](.github/skills/venue-distillation/references/distillation-design.md): accepted-paper distillation design (Layers 1-3 + Layer 5)
- [Multi-Discipline Design](.github/skills/venue-distillation/references/multi-discipline.md): schema system for cross-discipline distillation
- [Rejection Analysis](.github/skills/venue-distillation/references/rejection-analysis.md): rejected-paper weakness extraction
- [Skill File Format](.github/skills/venue-distillation/references/skill-file-format.md): output 5-layer skill anatomy and tag layout
- [Discipline Schemas](.github/skills/venue-distillation/references/discipline-schemas/): YAML configuration files per discipline family

## Intended Outcome

The goal is not just to summarize papers. The goal is to produce reusable structure that helps an agent:

- propose stronger ideas
- avoid common reviewer complaints
- draft papers in venue-appropriate style
- revise more effectively after feedback