# BrandOS Prompt Templates

This directory contains all LLM prompt templates for BrandOS agents.

## Rules

1. **Zero prompts in Python code.** Every prompt lives here as a `.md` file.
2. **One prompt per agent function.** Don't combine multiple concerns in one template.
3. **Use `{{variable_name}}` for placeholders.** Double-brace syntax is used by `PromptLoader`.
4. **Keep prompts focused.** A prompt should produce one structured JSON output.

## Directory Structure

```
prompts/
├── knowledge/
│   └── brand_extraction.md        # BrandExtractor → BrandProfile
├── planning/
│   └── campaign_strategy.md       # StrategyPlanner → CampaignStrategy (Phase 2)
├── creative/
│   ├── copywriter.md              # Copywriter agent (Phase 3)
│   ├── social_media.md            # SocialMediaAgent (Phase 3)
│   ├── email_specialist.md        # EmailSpecialist (Phase 3)
│   └── seo_specialist.md          # SEOSpecialist (Phase 3)
└── evaluation/
│   └── quality_evaluator.md       # QualityEvaluator (Phase 4)
```

## Adding a New Prompt

1. Create the `.md` file in the appropriate subdirectory.
2. Use `{{placeholder}}` for any variable the Python code will inject.
3. Include a `## Output Format` section with the exact JSON schema the LLM must return.
4. Load it in Python via `PromptLoader().load("category/prompt_name", variable=value)`.
