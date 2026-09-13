# Workflows — Planning & Orchestration

Phase 2 adds the Planning Layer (CampaignPlanner).
Phase 5 adds the Orchestration Layer (CampaignOrchestrator).

The Orchestrator is the brain of BrandOS. It:
- Receives the CampaignBrief and BrandProfile
- Decides which agents run and in what order
- Merges outputs into a CampaignPackage
- Never calls the LLM directly — delegates to agents
