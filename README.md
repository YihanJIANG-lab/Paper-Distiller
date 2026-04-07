# Paper-Distiller

Paper-Distiller packages a reusable venue distillation workflow as a workspace skill.

The current repository contains one skill, `venue-distillation`, for turning accepted and rejected papers from a target venue into structured guidance that an AI research pipeline can reuse during idea generation, paper drafting, and revision.

## What This Skill Does

The skill covers an end-to-end loop:

1. Collect accepted papers from sources such as OpenAlex, Semantic Scholar, and OpenReview.
2. Collect rejected papers and reviews from OpenReview.
3. Distill accepted papers into rigor, idea, and narrative patterns.
4. Distill rejected papers into reviewer-facing anti-patterns.
5. Package the result into a skill file that can be injected into an agent pipeline.

## Repository Layout

```text
.github/
  skills/
    venue-distillation/
      SKILL.md
      references/
        collection-sources.md
        data-schemas.md
        distillation-design.md
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
- the 4-phase methodology
- output artifacts
- how the distilled patterns are injected into a writing pipeline

## Reference Files

- [.github/skills/venue-distillation/references/data-schemas.md](.github/skills/venue-distillation/references/data-schemas.md): accepted/rejected paper JSON schemas
- [.github/skills/venue-distillation/references/collection-sources.md](.github/skills/venue-distillation/references/collection-sources.md): source coverage and collection strategy
- [.github/skills/venue-distillation/references/openreview-api.md](.github/skills/venue-distillation/references/openreview-api.md): OpenReview v1/v2 usage details
- [.github/skills/venue-distillation/references/distillation-design.md](.github/skills/venue-distillation/references/distillation-design.md): accepted-paper distillation design
- [.github/skills/venue-distillation/references/rejection-analysis.md](.github/skills/venue-distillation/references/rejection-analysis.md): rejected-paper weakness extraction
- [.github/skills/venue-distillation/references/skill-file-format.md](.github/skills/venue-distillation/references/skill-file-format.md): output skill anatomy and tag layout

## Intended Outcome

The goal is not just to summarize papers. The goal is to produce reusable structure that helps an agent:

- propose stronger ideas
- avoid common reviewer complaints
- draft papers in venue-appropriate style
- revise more effectively after feedback