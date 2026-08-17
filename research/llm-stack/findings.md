# Lawyer-bot-ve — LLM/RAG Stack Recommendation

Research for ticket #16 (wayfinder map #15, repo lawyer-bot-ve). Researched 2026-08-16 by an AFK subagent; constrained by `docs/feasibility-study.md` §4/§7 and `research/topic-gating/findings.md` §5.

**Verification note:** all facts below were checked live on **2026-08-16** from a Venezuela-region network. Grades: **[verified]** = fetched and read directly today (HuggingFace API/cards, provider docs via direct curl or a reader proxy that bypassed Cloudflare/region blocks); **[snippet]** = page reachable, content seen only in part or known from repo research; **[unverified]** = official URL region-blocked, cited without direct inspection. No monetary figures appear anywhere in this document (repo policy); costs are qualitative only. No files created in the repo by the research run; scrub data stays in OS temp.

**Constraints honored from `docs/feasibility-study.md` §4/§7 and `research/topic-gating/findings.md` §5:** hybrid 3-stage gating (deterministic pre-filter → LLM gate at temperature 0 with structured JSON, `UNCERTAIN` routes to retrieval → hybrid BM25+embedding retrieval gate with cross-encoder re-rank, top-k=5, threshold θ tuned on a labeled eval set); answers generated only from retrieved chunks of the official corpus; two thin channel adapters (WhatsApp webhook/24h window; Telegram long-poll or webhook/4096-char cap); free-tier-friendly launch with a later scale-up path.

---

## Slot 1 — Answer-generation model (legal Q&A in Spanish, citation-following)

**Candidates:**

1. **Google Gemini 2.5 Flash** — API; strong multilingual (Spanish is a first-class language for Gemini); JSON output + temperature support; **free tier exists** with per-project request/token caps and automatic upgrade to a paid tier as volume grows ([verified] models page lists the Flash family incl. 2.5 Flash and 3.x Flash variants — https://ai.google.dev/gemini-api/docs/models; [verified] rate-limits page confirms a Free tier and auto-upgrade mechanics — https://ai.google.dev/gemini-api/docs/rate-limits; [snippet] exact free-tier RPM/RPD live on a JS table at aistudio.google.com/rate-limit — confirm at signup). Also exposes an **OpenAI-compatible endpoint**, so it drops into an OpenAI SDK client ([verified] https://ai.google.dev/gemini-api/docs/openai).
2. **OpenAI GPT-5.6 Luna** (cost-optimized GPT-5.6 variant) — API; strong Spanish; Structured Outputs guarantees schema-valid JSON from the model ([verified via reader proxy] models doc names `gpt-5.6-sol/terra/luna/cyber`, Luna = "cost-sensitive, high-volume workloads": https://platform.openai.com/docs/models; [verified via reader proxy] Structured Outputs page: "ensures the model will always generate responses that adhere to your supplied JSON Schema… For new projects, start with gpt-5.6" — https://platform.openai.com/docs/guides/structured-outputs). **No free tier** — paid per-token tier. Official platform URLs are [unverified] from this network (403 Cloudflare region-block; consistent with repo research note).
3. **Anthropic Claude Haiku 4.5** — API (`claude-haiku-4-5-20251001-v1`), best-in-class instruction-following/citation discipline reputation; Structured Outputs supported ([verified via reader proxy] model overview: Haiku 4.5 alongside Opus 5/Sonnet 5/Fable 5 — https://docs.anthropic.com/en/docs/about-claude/models/overview; [verified] structured-outputs doc — https://docs.anthropic.com/en/docs/build-with-claude/structured-outputs). Paid per-token tier.
4. **Groq-hosted Llama 3.3 70B / OpenAI GPT-OSS 120B (GroqCloud)** — very fast inference with JSON mode; developer plan offers a free tier with per-minute/per-day token+request caps ([verified via reader proxy] model list + developer-plan rate limits — https://console.groq.com/docs/models). Quality below frontier for citation-heavy legal drafting; JSON is `json_object` mode (no schema guarantee like OpenAI's).

**Recommendation: Gemini 2.5 Flash — free tier at launch, with a defined paid flip to OpenAI GPT-5.6 Luna (or Claude Haiku 4.5) when free-tier daily caps bind or the eval set shows citation drift.** Rationale: the launch posture is free-tier-friendly, volume is hundreds→thousands of conversations/month (a few thousand LLM calls/month), Gemini Flash is fast and Spanish-strong, and Google's auto-upgrade + OpenAI-compatible endpoint make the free→paid transition a config change, not a rewrite. Self-hosting (Llama/GPT-OSS quantized) is **not** recommended at launch: a free-tier VM cannot run a 70B-class model at usable latency, and one API call per answer at this volume is the right trade — revisit self-host only at large scale on GPU.

**Blocks/unblocks:** (a) No effect on vector-store choice (LLM is HTTP-decoupled from retrieval); unblocks the citation contract in feasibility §6 (answers cite Gaceta Nº + article numbers pulled from chunks). (b) Language-agnostic, but the OpenAI-compatible surface nudges the backend to use one `openai`-SDK-style client for all providers → Python keeps this simplest.

---

## Slot 2 — Topic-gate model (cheap/fast, structured JSON, Spanish)

**Candidates:**

1. **Gemini 2.5 Flash (free tier) + JSON schema** — same project/key as Slot 1 (one integration); schema-enforced output removes parse failures for `{in_scope: yes|no|uncertain, branch_of_law, legal_subject, reason}`; temperature 0 supported. Rate caps are the constraint (see contingency below). [verified] same URLs as Slot 1.
2. **OpenAI GPT-5.6 Luna with Structured Outputs** — strongest schema guarantee in the market (invalid-enum hallucination impossible by construction); paid per-token tier. Same URLs as Slot 1.
3. **Groq Llama 3.3 70B (free dev tier, `json_object`)** — zero-cost gate with high throughput (1K RPM class); JSON validity guaranteed but schema fields are not — parser default-reject still required; semantic quality for a Spanish legal rubric is competent but must be proven on the eval set.
4. **Self-hosted small OSS (e.g., gpt-oss-20b / Qwen3 8B) via Ollama/llama.cpp** — zero marginal cost, ~1 s latency on a modest CPU VM; the natural scale-up path once a few hundred labeled gating examples exist (mirrors the SetFit trajectory in topic-gating findings §5); risky on a 1 GB host.

**Recommendation: Gemini 2.5 Flash free tier, temperature 0, JSON-schema output, same Google project as Slot 1 — with Groq Llama 3.3 70B as the designated zero-cost relief valve** if the combined gate+answer call volume presses free-tier daily caps (split: gate on Groq, answers on Gemini; both are OpenAI-compatible so the client code is identical). Rationale: cheapest reliable path that keeps the gate's two hard requirements — schema-valid JSON (default-reject on parse failure) and complete isolation from the chat context — and one provider family to operate. The gate must **never** be run on the answer model's chat context (feasibility §4.1).

**Blocks/unblocks:** (a) Fixes the gate JSON contract that the retrieval gate and rejection copy consume (`UNCERTAIN` → retrieval gate; `OUT_OF_SCOPE` vs `IN_SCOPE_UNANSWERABLE` copy); (b) same single OpenAI-compatible client as Slot 1.

---

## Slot 3 — Embedding model (multilingual, Spanish-legal quality)

**Candidates:**

1. **BAAI/bge-m3** — [verified] 1024-dim, 8192-token input, 100+ languages, dense + sparse + ColBERT modes in one model (card: https://huggingface.co/BAAI/bge-m3; benchmark claim in card: top multilingual performance vs OpenAI embeddings). Long-input support means whole legal articles can embed in one vector — a real advantage for article-number retrieval. ~568M params (class of model: heavy for a 1 GB host; OK on a 2–12 GB host, int8/ONNX smaller).
2. **sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2** — [verified] 384-dim, 12 layers, 50+ languages incl. Spanish; the most-deployed multilingual ST model (≈57M downloads, likes 1.3k); tiny CPU footprint — the safe default on a 1 GB always-free VM. (https://huggingface.co/sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2)
3. **intfloat/multilingual-e5-large** — [verified] 1024-dim, 24 layers, ~100 languages, requires `query:`/`passage:` prefixes; strong retrieval quality, heavier than MiniLM. (https://huggingface.co/intfloat/multilingual-e5-large)
4. **Spanish-legal fine-tuned / backbones (RigoBERTa, LegalBERT, MARCELL, community)** — RigoBERTa-2.0 exists as an XLM-RoBERTa fill-mask backbone for Spanish under the IIC org ([verified] https://huggingface.co/IIC/RigoBERTa-2.0; the old `PlanTL-GOB-ES` id 404s), but it is **not** a sentence-embedding model — it needs fine-tuning (SetFit/custom contrastive) on a labeled Spanish-legal corpus before it can serve retrieval. A community BGE-M3 fine-tune on legal Spanish exists ([verified] `wilfredomartel/BGE-M3-Legal-Spanish`, Apache-2.0, but **trained on Ecuadorian case law, ~470 downloads, no benchmark → watchlist only**). LEXTREME is the reference multilingual legal benchmark ([verified] https://arxiv.org/abs/2211.09171). LegalBERT is English-only (arXiv:2010.02559); MARCELL is training data, not a model (marcell-project.eu).

**Recommendation: BGE-M3, self-hosted — with MiniLM-L12 as the chosen model if the host is capped at 1 GB RAM.** Rationale: the corpus is Spanish legal text, retrieval quality is the product's grounding backbone (BEIR: generic models degrade out-of-domain, arXiv:2104.08663), and no benchmarked Spanish-legal embedding model exists yet — so the strongest generic multilingual model is the right launch pick, with Spanish-legal fine-tuning (RigoBERTA-class backbone) as the post-eval-set upgrade path. A self-hosted local model keeps per-message cost at zero and latency at milliseconds; API embeddings (Cohere embed-multilingual v3 — https://docs.cohere.com/docs/embeddings [snippet]; Gemini text-embedding — [verified] `gemini-embedding-001` / `gemini-embedding-2-preview` on the models page) are the fallback only for a serverless route.

**Blocks/unblocks:** (a) **Sets vector dimensionality** — 1024 (BGE-M3) vs 384 (MiniLM) locks the index layout in the vector store (vec0 float columns, pgvector, Qdrant all handle both), and BGE-M3's 8192-token window changes chunking strategy (fewer, larger chunks per law); pick once, then make re-embedding a batch job because the corpus is small (index rebuild is cheap). (b) Python-native libraries (sentence-transformers / FlagEmbedding) → Python backend; if the backend ever goes serverless, Workers AI already hosts BGE-M3 ([verified] bge-m3 on Cloudflare's model list — https://developers.cloudflare.com/workers-ai/models/).

---

## Slot 4 — Cross-encoder re-ranker (multilingual)

**Candidates:**

1. **cross-encoder/mmarco-mMiniLMv2-L12-H384-v1** — [verified] explicitly trained on mMARCO translated to 14 languages **including Spanish** (`es` in the language list), MiniLMv2-L12 base (~118M params), Apache-2.0, fast on CPU; authors note it generalizes to further languages. (https://huggingface.co/cross-encoder/mmarco-mMiniLMv2-L12-H384-v1)
2. **BAAI/bge-reranker-v2-m3** — [verified] multilingual reranker from the BGE family (~568M params), the quality upgrade path; BGE-M3's own card explicitly recommends bge-reranker for post-retrieval filtering (https://huggingface.co/BAAI/bge-reranker-v2-m3).
3. **Cohere Rerank (multilingual)** — hosted API, strong multilingual reranking, paid per-1k pricing; only worth it on a serverless route (https://docs.cohere.com/docs/rerank-overview [snippet]).
4. English-only MS MARCO MiniLM rerankers — excluded (Spanish corpus).

**Recommendation: mmarco-mMiniLMv2-L12-H384-v1 at launch (Spanish covered, ~118M params, top-k=5 re-rank cost is trivial), swap to BGE-reranker-v2-m3 if the labeled eval set shows rerank lift on Spanish legal queries** (needs a 2+ GB host or int8). Rationale: at top-k=5–10 the reranker price-per-query is negligible either way; multilingual coverage is the non-negotiable and both candidates have it; the small one fits every free-to-host scenario.

**Blocks/unblocks:** (a) Independent of the vector store (runs post-retrieval over chunks); only interacts with ingestion via chunk id/payload fields; (b) Python (sentence-transformers `CrossEncoder`), reinforcing the Python backend.

---

## Slot 5 — Vector store (also provenance/metadata joins)

**Candidates:**

1. **SQLite single-file: FTS5 (BM25) + sqlite-vec** — [verified] sqlite-vec is a small pure-C extension, `vec0` virtual tables for float/int8 vectors, metadata columns, runs anywhere SQLite runs (https://github.com/asg017/sqlite-vec) — but it is **pre-v1 (breaking changes)** per its own README. Combined with SQLite's built-in FTS5, **one file gives hybrid retrieval (BM25 + vectors) plus real SQL joins against a provenance table (Gaceta Nº, date, pages, URL, SHA-256)** — the cleanest zero-ops match for feasibility §3.4/§3.5. FTS5's `unicode61` tokenizer supports accent-insensitive indexing (`remove_diacritics=2`) — essential for "artículo/articulo" in Spanish legal text. Mitigate pre-v1: pin the version, keep the index rebuildable from the ingestion pipeline (it is — the corpus pipeline is source-of-truth).
2. **Supabase pgvector (free tier)** — [verified] managed Postgres with pgvector + embeddings docs (https://supabase.com/docs/guides/ai); real SQL joins with provenance; free tier exists but **projects are paused after a period of inactivity** ([verified] going-into-prod doc: "pause your project for inactivity" — https://supabase.com/docs/guides/platform/going-into-prod) → needs a keep-alive or a paid flip; a 1-week silent pause would kill a public bot.
3. **Qdrant (self-hosted or free-forever cloud)** — [verified] free tier = single-node cluster, "free forever", plus free cloud inference for selected embedding models (https://qdrant.tech/pricing/; self-host via https://qdrant.tech/). High-quality HNSW + payload filtering, but payload filters are not real joins — provenance joins would live in app code. Natural scale-up path.
4. **LanceDB** — [verified] embedded/columnar OSS with cloud beta (https://github.com/lancedb/lancedb); simple API, free local; read-mostly fit; less SQL-y than SQLite.

**Recommendation: SQLite (FTS5 + sqlite-vec) in one file alongside the backend, with provenance in a relational `documents` table — pgvector/Supabase as the managed alternative if the team prefers not to run storage on the VM, Qdrant as the scale-up.** Rationale: corpus is small (tens of thousands of chunks at ~500–1,000 chars), so an embedded store is both enough and the lowest-ops option; hybrid BM25+dense in one file matches the mandated retrieval gate; the provenance-joins requirement is free in SQL. Must-pins: version-pin sqlite-vec and keep ingestion rebuildable.

**Blocks/unblocks:** (a) This IS the corpus-ingestion sink — chunk layout, dims (384/1024), FTS5 tables, provenance rows all land here; daily Gaceta poll upserts into it; (b) Python bindings (`sqlite_vec` pip package) → FastAPI-friendly; no separate DB service to run on the free VM.

---

## Slot 6 — Hosting (shared backend + two adapters)

**Candidates:**

1. **Google Cloud e2-micro (always-free VM, US regions only)** — [verified] 1 always-free e2-micro in us-west1/us-central1/us-east1, 30 GB disk, 1 GB egress/month (https://cloud.google.com/free/docs/free-tier-features). True always-on; fits the **MiniLM-L12 + mmarco-reranker** path (int8/ONNX keeps RAM ~0.5 GB alongside FastAPI+Caddy); Caddy gets auto-TLS for both webhooks. US region = no OpenAI/Anthropic region-block issues for the backend. **1 GB RAM is the hard constraint** — BGE-M3 fp32 won't fit.
2. **Oracle Cloud Always-Free ARM (Ampere A1)** — [verified] always-free ARM instance, 12 GB memory usable as 1 or 2 VMs (https://www.oracle.com/cloud/free/); 30-day trial then Always-Free continues. Fits **BGE-M3 + reranker-v2-m3** comfortably. Known operational risk: Oracle has reclaimed idle Always-Free instances (keep utilization up / backups).
3. **Cloudflare Workers + Workers AI (BGE-M3) + Vectorize** — fully serverless, free tiers on all three ([verified] bge-m3 is a Workers AI model; https://developers.cloudflare.com/workers-ai/models/; Vectorize docs https://developers.cloudflare.com/vectorize/ [snippet]). **Weakness: Telegram long-polling is a poor fit for event-driven Workers** — you'd be forced onto Telegram webhook (needs no TLS worry, Workers provides HTTPS) and external writer loops for ingestion; more moving parts than one VM.
4. **Rejected:** Render free — [verified] free web services **spin down after 15 min without inbound traffic** (https://render.com/docs/free), which kills long-polling and injects cold-start latency into every WhatsApp webhook wake-up; Railway — [verified] no permanent free tier, only one-time trial credits (https://docs.railway.com/reference/pricing); Fly.io — [verified] usage-based billing with only limited free allowances (https://fly.io/docs/about/pricing/); Vercel Hobby — [verified] free serverless functions with included quotas (https://vercel.com/docs/pricing) but serverless-only (no long-poll) and function duration limits.

**Recommendation: one always-on US VM — GCP e2-micro for the MiniLM path, Oracle Always-Free ARM if the eval set demands BGE-M3 (+reranker-v2-m3) — running Caddy (auto-TLS), FastAPI, the SQLite store, Telegram long-polling, and the WhatsApp webhook endpoint.** Rationale: the backend must be *always-on* (two webhooks + long-polling + a daily Gaceta poll); a free forever-VM is the only permanent-free option that satisfies that with one moving part. Long-poll-first for Telegram matches feasibility §7; switch to Telegram webhook when moving to any cloud host. Pair with Cloudflare's free proxy in front, if desired, for extra HTTPS/abuse protection.

**Blocks/unblocks:** (a) Host RAM decides the embedding/reranker tier (Slot 3/4) — 1 GB → MiniLM path; 12 GB ARM → BGE-M3 path; if serverless is ever chosen, vector store moves to Vectorize/pgvector and embeddings to Workers AI/API. (b) **Framework language: Python (3.11+) + FastAPI** — the entire chosen ML/retrieval stack (sentence-transformers, FlagEmbedding, sqlite-vec, cross-encoders, tesseract OCR corpus pipeline) is Python-native; the OpenAI-compatible client abstraction keeps all three potential LLM providers behind one interface; TypeScript/Workers is only the fallback serverless route.

---

## Recommended stack (one line per slot)

| Slot | Recommendation |
|---|---|
| 1. Answer model | Gemini 2.5 Flash (free tier) → paid flip: OpenAI GPT-5.6 Luna (alt: Claude Haiku 4.5) |
| 2. Topic-gate model | Gemini 2.5 Flash, JSON schema, temp 0 (relief valve: Groq Llama 3.3 70B free dev tier) |
| 3. Embedding model | BAAI/bge-m3 self-hosted (fallback on 1 GB hosts: paraphrase-multilingual-MiniLM-L12-v2) |
| 4. Cross-encoder | cross-encoder/mmarco-mMiniLMv2-L12-H384-v1 (upgrade: BAAI/bge-reranker-v2-m3) |
| 5. Vector store | SQLite file: FTS5 (BM25) + sqlite-vec + provenance table (alt: Supabase pgvector; scale-up: Qdrant) |
| 6. Hosting | Always-on US VM: GCP e2-micro (free) for the MiniLM path / Oracle Always-Free ARM 12 GB for BGE-M3; Caddy TLS |
| Backend framework | Python 3.11 + FastAPI, single OpenAI-compatible LLM client (base_url per provider) |
| Groundedness (optional) | Deterministic citation-consistency check at launch (each cited "Artículo N" must appear in retrieved chunks; else regenerate/fallback); Azure Content Safety Groundedness / SynCheck-style monitor deferred until Spanish/legal support matures |
| Adapters | WhatsApp Cloud API webhook (24h window, 80 msg/s ceiling — irrelevant at launch; retry/queue anyway) + Telegram long-poll → webhook (4096-char chunking) — per feasibility §7 |

---

## Before committing (tests on real Spanish legal text)

1. **Embedding bake-off:** build ~200–500 query→relevant-article judgment pairs from the gating eval set; compare Recall@5 for BGE-M3 vs MiniLM-L12 vs multilingual-e5-large on *real* Gaceta/TSJ chunk text (accent handling and article-number queries included). This one test decides Slots 3/4/6-tier.
2. **Re-ranker lift:** measure nDCG@5 of mmarco-mMiniLMv2 vs bge-reranker-v2-m3 on the same pairs; if lift is negligible, keep the small model and the 1 GB VM.
3. **BM25/FTS5 sanity:** confirm `unicode61` + `remove_diacritics=2` recall on "artículo"/"articulo", "trabajadores"/"trabajador" (no Spanish stemmer in FTS5 — check whether lexical recall shortfall is covered by dense).
4. **Gate eval:** run the labeled set (≈20 branches × 10+ queries + off-topic/adversarial classes) at temperature 0 on Gemini Flash vs Groq Llama 3.3 70B; measure schema-parse success rate, false-accept/false-reject, and p95 latency; verify `UNCERTAIN` routing behaves.
5. **Answer-model citation audit:** hand-review 30–50 answer runs across Gemini Flash / GPT-5.6 Luna / Claude Haiku 4.5 for citation-following (cites only retrieved article numbers, correct Gaceta citations, honest "no tengo esa información") — the one qualitative judgment that justifies the paid-flip direction.
6. **Rate-limit model at projected volume:** simulate messages/day at "thousands of conversations/month" (gate + answer + groundedness calls per message) against Gemini free-tier RPD and Groq dev-tier TPM; decide the gate/answer provider split before it bites in production.
7. **Host memory probe:** on the chosen free VM, load the chosen embedding + reranker (int8/ONNX where needed) plus FastAPI and measure p95 query latency and memory headroom; Oracle ARM only if BGE-M3 wins test 1.
8. **Vector-store reliability:** sqlite-vec pin + index-rebuild script from the corpus pipeline; HNSW/brute-force recall check on real chunks; backup/restore of the single SQLite file; Supabase pause behavior if that route is chosen.
9. **Channel-endpoint endurance:** 72 h always-on test — Telegram long-poll stability, WhatsApp webhook verification + retry behavior (Meta retries on 5xx), TLS via Caddy.
10. **Groundedness check feasibility:** measure false-positive rate of the deterministic citation-consistency check on eval answers before enabling regenerate/fallback.

---

## Source index (with verification grades)

**Models (all [verified] via HF API/cards):** BGE-M3 https://huggingface.co/BAAI/bge-m3 · MiniLM-L12 https://huggingface.co/sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2 · e5-large https://huggingface.co/intfloat/multilingual-e5-large · mMARCO reranker https://huggingface.co/cross-encoder/mmarco-mMiniLMv2-L12-H384-v1 · bge-reranker-v2-m3 https://huggingface.co/BAAI/bge-reranker-v2-m3 · RigoBERTa-2.0 https://huggingface.co/IIC/RigoBERTa-2.0 · community BGE-M3-Legal-Spanish https://huggingface.co/wilfredomartel/BGE-M3-Legal-Spanish

**Providers:** OpenAI models/structured outputs https://platform.openai.com/docs/models · https://platform.openai.com/docs/guides/structured-outputs ([unverified] direct — 403 region-block; content [verified] via reader proxy) · Anthropic models/structured outputs https://docs.anthropic.com/en/docs/about-claude/models/overview · https://docs.anthropic.com/en/docs/build-with-claude/structured-outputs ([verified] via proxy) · Gemini models/rate-limits/OpenAI-compat https://ai.google.dev/gemini-api/docs/models · /rate-limits · /openai ([verified] direct) · Groq models https://console.groq.com/docs/models ([verified] via proxy)

**Infra:** GCP free tier https://cloud.google.com/free/docs/free-tier-features ([verified]) · Oracle Cloud Free Tier https://www.oracle.com/cloud/free/ ([verified] via proxy) · Cloudflare Workers AI https://developers.cloudflare.com/workers-ai/models/ ([verified]) · Vectorize https://developers.cloudflare.com/vectorize/ ([snippet]) · Render free https://render.com/docs/free ([verified]) · Railway https://docs.railway.com/reference/pricing ([verified]) · Fly.io https://fly.io/docs/about/pricing/ ([verified]) · Vercel https://vercel.com/docs/pricing ([verified]) · sqlite-vec https://github.com/asg017/sqlite-vec ([verified]) · LanceDB https://github.com/lancedb/lancedb ([verified]) · Qdrant https://qdrant.tech/pricing/ ([verified] via proxy) · Supabase AI/pgvector https://supabase.com/docs/guides/ai · pause policy https://supabase.com/docs/guides/platform/going-into-prod ([verified]) · Cohere https://docs.cohere.com/docs/embeddings · /docs/rerank-overview ([snippet])

**Channels:** WhatsApp Cloud API overview (80 msg/s, customer-service window, webhooks) https://developers.facebook.com/docs/whatsapp/cloud-api/overview ([verified] via proxy) · Telegram Bot API (4096 chars; getUpdates long-poll vs webhooks; ~30 msg/s broadcast ceiling with 429s) https://core.telegram.org/bots/api · https://core.telegram.org/bots/faq ([verified] direct)

**Research anchors (all [verified] reachable, arXiv):** LEXTREME legal benchmark 2211.09171 · BEIR retrieval degradation 2104.08663 · SynCheck faithfulness 2406.13692 · RAG energy-abstention 2509.04482 · Stanford legal-AI hallucination 2405.20362 · LegalBERT 2010.02559 · RigoBERTa 2205.10233 · Azure Groundedness https://learn.microsoft.com/en-us/azure/ai-services/content-safety/concepts/groundedness ([snippet] — page is auth-walled today; English-optimized/no-legal-domain caveat per repo research/topic-gating)

---

## Key open questions for the map (resolved by downstream tickets)

- **Embedding tier (BGE-M3 vs MiniLM) and reranker tier depend on the embedding bake-off** (Before-committing test 1), which runs on the gating eval set (ticket #18) — the ingestion ticket (#21) and the architecture ticket (#22) should treat the embedding dim / memory tier as a two-branch decision until that test lands.
- **Hosting tier (GCP e2-micro 1 GB vs Oracle ARM 12 GB) is downstream of the same test** — architecture (#22) should spec both branches.
- **Provider signup facts to confirm at execution time:** Gemini free-tier exact RPM/RPD table (JS-only page), Groq dev-tier limits, OpenAI/Anthropic region availability from Venezuela (region-block noted) — these are signup-time confirmations (ticket #19 WhatsApp onboarding pattern), not design blockers.