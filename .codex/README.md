# Codex Workflow Configuration (v1)

This directory contains reusable multi-agent workflow configuration files.

The workflow is intentionally:
- Lightweight
- Repository-agnostic
- Easy to extend
- Safe by default

---

# Structure

```text
.codex/
  README.md
  agents/
    lead-orchestrator.toml
    requirements-analyst.toml
    developer-coding-agent.toml
    test-review-agent.toml