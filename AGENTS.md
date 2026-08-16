# AGENTS.md

## Agent skills

### Issue tracker

Issues, PRDs and wayfinder maps for this repo live as GitHub issues. Use the `gh` CLI. See `docs/agents/issue-tracker.md`.

### Triage labels

Default five-role vocabulary: `needs-triage`, `needs-info`, `ready-for-agent`, `ready-for-human`, `wontfix`. See `docs/agents/triage-labels.md`.

### Domain docs

Single-context: `CONTEXT.md` at the repo root + `docs/adr/` for decisions. See `docs/agents/domain.md`.

## GitHub conventions

- Issues, PRs, and commits in **English**.
- **Financial amounts never go on GitHub** — costs, budgets, and pricing figures stay private. Only qualitative conclusions are allowed in issues, PRs, docs, and ADRs.

## Repo purpose

Feasibility study for **lawyer-bot-ve**: a public WhatsApp/Telegram bot that answers questions about Venezuelan law for Venezuelan lawyers, grounded on official legal sources (Gaceta Oficial, TSJ, Asamblea Nacional), and strictly gated to legal topics (off-topic questions are rejected). This repo hosts the study only; implementation is a later effort.

## Wayfinding

Maps and decision tickets use the `wayfinder:*` labels and live as issues. See `docs/agents/issue-tracker.md` → "Wayfinding operations".