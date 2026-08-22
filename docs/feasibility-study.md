# Feasibility Study — lawyer-bot-ve

**Public WhatsApp/Telegram bot answering questions about Venezuelan law, grounded on official sources, for Venezuelan lawyers.**

- **Status:** Final — synthesized from wayfinder map #1, tickets #2–#7 (all resolved, August 2026). **Updated 2026-08-22 (map #15, issue #19): the PO re-decided the platform — Telegram only; WhatsApp discarded.** The WhatsApp analysis in §2 is retained as the comparative record.
- **Sources:** research findings under `research/<name>/findings.md` (corpus, whatsapp, telegram, topic-gating, regulation) and the resolution of ticket #7 (response format, grilled HITL).
- **Language / finance note:** this study contains no monetary figures — costs are described qualitatively only (free tier, paid tier, per-conversation pricing above allowances).

---

## 1. Executive verdict

**The bot is viable. Build it — Telegram only.** (2026-08-22 PO decision: WhatsApp discarded — see §2.4. The original "WhatsApp first, Telegram as a mirror" verdict is superseded.)

All four feasibility gates of the map close GREEN (with documented conditions):

| Gate | Verdict | One-line basis |
|---|---|---|
| (1) Official legal corpus obtainable in usable form | ✅ Feasible | Gaceta Oficial digital portal (~2012→present) + TSJ catalogs (~90 laws) + AN; official texts are outside copyright (LDA); ~8/15 classic laws obtainable today, with OCR and four pre-2012 gaps to manage |
| (2) Platform reachable for Venezuelan lawyers | ✅ Feasible | WhatsApp is the dominant professional channel in Venezuela and is **not** restricted by Meta; OFAC's Venezuela program is targeted and expressly licenses internet-communications services; Telegram is a near-zero-friction secondary channel |
| (3) Reliable topic gating | ✅ Feasible | Hybrid 3-stage pipeline (deterministic pre-filter + LLM gate + retrieval gate) reaches estimated false-accept < 1% with false-reject ≤ 10%, precision-biased |
| (4) Regulatory / liability risks assessed | ✅ Feasible with standard safeguards | No binding VE data-protection statute in force; CC 1185 fault liability is hard to trigger for a labeled informational tool; **lawyers as verified users is the single strongest defense** |

**Recommended architecture (outline):** a single backend serving one thin channel adapter (Telegram Bot API). User-initiated sessions; topic-gated; retrieval over the official corpus only; answers as legal-memo citations with links to official texts; onboarding disclosure + `/disclaimer` command; short retention and no profiling. (Posture updated 2026-08-22 — WhatsApp discarded, see §2.4.)

**The risks are operational, not technical or regulatory.** With WhatsApp discarded (2026-08-22), the key operational fragility is Telegram reach — the Jan 2025 state-ordered block showed availability can be interrupted by government action (§2.2). Everything else has a tested path.

---

## 2. Platform analysis: WhatsApp vs Telegram (original record)

**Update 2026-08-22 — PO decision:** WhatsApp is discarded; the bot is **Telegram-only** (map #15, issue #19). §2.1–§2.3 are the original comparison and recommendation, kept as the decision record; §2.4 records the new posture.

### 2.1 WhatsApp Business Platform (Cloud API) — 🟢 PRIMARY

**Verdict: GREEN for feasibility, with a YELLOW onboarding checklist** (research: `research/whatsapp/findings.md`).

- **Sanctions / availability — clear.** Venezuela is **not** on WhatsApp Business Platform's restricted list (only Crimea/Cuba/Iran/North Korea/Syria). The OFAC Venezuela program is targeted (GoV, SDN persons, oil/gold sectors); General License 25 expressly authorizes "exchange of communications over the internet" services, and GL 24A covers telecom services. A Venezuelan business may legally operate a WABA and reach +58 users. Practically: dominant professional channel in-country (~17.5M internet users, 61.6% penetration); Venezuelan "WhatsApp for law firms" products already exist.
- **Platform fit — green.** The On-Premises API is sunset (Oct 23, 2025); only the Meta-hosted **Cloud API** remains, with free hosting and a free messaging tier at low volume. The **24-hour customer-service window fits a user-initiated Q&A bot exactly**: a user's question opens a window inside which the bot may send free-form messages; outside a window only pre-approved templates may be sent. Design: sessions are user-initiated and capped to one window; optional template-based nudge/opt-in.
- **Yellow risks (operational, not blockers):**
  - Meta **business verification** with Venezuelan documents — plan days-to-weeks (Partner-Led Business Verification via a BSP is the fastest path).
  - **Display-name and message-template approvals** are separate Meta review tracks; legal-content templates may draw extra review.
  - A dedicated **+58 mobile number** able to receive the verification SMS/call (virtual numbers unsupported for verification).
  - **Meta billing/payment rails for a Venezuelan entity are unverified** — the single most practical unknown. Mitigations: confirm a VE payment method works early; if not, evaluate a BSP that invoices from abroad. **(Do this before committing to WhatsApp as primary.)**
  - OFAC **SDN screening** of business counterparties (not end users) as standard hygiene.
- Cost posture (qualitative): free tier + free hosting; per-conversation pricing once free allowances are exceeded; optional BSP fees.

### 2.2 Telegram Bot API — 🟢 SECONDARY MIRROR

**Verdict: YELLOW-to-GREEN — GREEN as a launch/technical channel, YELLOW on reach** (research: `research/telegram/findings.md`).

- **Launch friction — near zero.** Bot created via @BotFather in minutes; token issued immediately; no business verification, no approval queue, no documents. Free platform, verified free hosting tiers exist.
- **No conversation window** — a bot may message any user who started it (a real advantage over WhatsApp's window), and there is no per-message fee. Message cap is 4096 chars (chunk long answers, or send the corpus PDF up to 50 MB via `sendDocument`); MarkdownV2/HTML make citations clickable.
- **Reach — yellow.** No official Telegram usage figure for Venezuela exists (DataReportal publishes none); WhatsApp dominates in-country. **On Jan 10–11, 2025 the state ordered ISPs to block Telegram; the block was lifted within ~24h.** Currently unblocked per OONI measurements, but availability can be interrupted by government action — a genuine fragility for a professional service.
- Platform terms: operator is "solely responsible" for bot content (Telegram disclaims) — favorable for a legitimate service, but compliance liability sits with us.
- Cost posture (qualitative): free platform; near-zero marginal cost once the backend exists.

### 2.3 Decision and rationale

| Criterion | WhatsApp (Cloud API) | Telegram Bot API |
|---|---|---|
| Reach among VE lawyers | Dominant professional channel; local legal-sector products exist | No in-country figures; WhatsApp is the baseline |
| Launch friction | Days–weeks (verification, approvals) | Minutes (BotFather) |
| Conversation model | 24h window, templates outside it | No window; stateless, keyed by chat_id |
| Availability risk | None found (not restricted, OFAC-clear) | Jan 2025 state-ordered block (lifted ~24h) |
| Messaging constraints | Free-form inside window; templates outside | 4096-char cap; chunk/sendDocument |
| Cost (qualitative) | Free tier + free hosting; per-conversation above allowances | Free platform + free hosting tiers |

**Recommendation: WhatsApp primary, Telegram mirror launched early with the same backend.** WhatsApp wins on reach and professional-channel dominance — the research's core reach evidence — and the product is usable within its window model. Telegram is nearly free to add (same backend, thin adapter), proves demand fast, and hedges both WhatsApp's onboarding friction and Telecom's reach gap. **Decision rule for the implementation map:** start WhatsApp onboarding (esp. the billing-rails question) first; if billing rails for a VE entity prove impossible, flip the posture to Telegram-first with WhatsApp deferred — the architecture makes the primary swappable.

### 2.4 Post-decision addendum — Telegram-only (2026-08-22)

**Decision:** the PO discarded WhatsApp completely (issue #19, closed not-planned). lawyer-bot-ve will operate on **Telegram only** — no WABA, no Meta onboarding, no +58 number, no billing-rails probe. The WhatsApp onboarding checklist was not executed; there are no Meta status facts to record.

**Consistency with the study:** §2.3's decision rule made the platform posture conditional on the billing-rails probe and kept the primary swappable; the PO exercised that swap in the strongest direction (Telegram-first → Telegram-only). The reach argument for WhatsApp (§2.1) is real but is weighed against the onboarding/verification/billing burden; the decision resolves the open operational question by removing the platform rather than completing the checklist.

**Implications for the implementation map (#15):** single Telegram adapter — long polling first, webhook (`secret_token`) once on a cloud host; state keyed by `chat_id`; answers chunked to ≤4096 chars; MarkdownV2 citations; `sendDocument` for corpus PDFs (≤50 MB); no conversation window (a bot may message any user who started it); rate limiting ≤1 msg/s per chat; reach fragility monitored via OONI/press (Jan 2025 block precedent).

**Artifacts:** `research/whatsapp/findings.md` retained as archived reference (banner added); map #15 destination/scope updated; tickets #22/#23 refreshed; CONTEXT.md glossary updated.

---

## 3. Corpus approach: official sources only

**Verdict: feasible from official sources only** (research: `research/corpus/findings.md`).

### 3.1 Sources and formats

| Source | What it offers | Format |
|---|---|---|
| **Gaceta Oficial digital portal** (`gacetaoficial.gob.ve`) | ~2012→present; latest gazettes already indexed; structured metadata (Nº, type, date, sumario) + PDF per gazette; no API | Text-layer PDFs from ~2017+; OCR needed for 2012–2016 scans; some broken records (e.g. LISLR 6.210 404) |
| **TSJ catalogs** (`tsj.gob.ve/leyes`, `/codigos`, `/constitucion`) | ~90+ laws (organic ~51, ordinary ~94, 5 codes, Constitution), 1988–2022, each entry already carries the official Gaceta citation | PDF **image scans (empty text layer) → OCR required** |
| **Asamblea Nacional** (`asambleanacional.gob.ve/leyes/vigentes`) | Laws sanctioned under the current session (2016–2026); Constitution PDF **has a text layer** | HTML cards + per-law PDF |
| **TSJ gaceta mirror** (`historico.tsj.gob.ve/gaceta*`) | Backup copies (~2013–2022) for gazettes whose portal PDF is broken | PDFs |
| **Not usable:** SENIAT (no law texts), Poder Judicial portal (unreachable from abroad), Imprenta Nacional main site (unreachable), official APIs (none exist anywhere) | | |

### 3.2 Licensing

**Republication of official normative texts is permissible.** The Venezuelan *Ley sobre el Derecho de Autor* (GOE 4.638 Ext., 01/10/1993) excludes laws and official acts of State organs from copyright; judicial decisions are likewise official acts. No State license is required. (Pending item: re-confirm the exact LDA article — cited as Art. 43 — against the published text of GOE 4.638 Ext. before launch; a Caracas IP lawyer can settle it in minutes.)

**Recommended attribution practice** (quality bar, not a legal mandate): every corpus record and every answer carries Gaceta Nº + date + page, the issuing institution, and the source URL — which also serves the authenticity goal (the Gaceta portal even offers a certificate-verification service).

### 3.3 Coverage and the four gaps

~8/15 of the classic most-consulted corpus is obtainable from official online sources today, but **only ~3 in born-machine-readable form**: the Constitution (text-layer PDF from AN or TSJ), the Código Orgánico Tributario 2020 (Gaceta 6.533, text-layer), and anything published 2017+ in the digital Gaceta. The COPP 2012, LOTTT 2012, Código Penal 2005, LOPNNA 2007, CPC 1990, LISLR 2015 (PDF currently broken — needs re-check/Wayback), and most organic laws are **scans requiring OCR**.

**Hard gaps — not in any machine-readable official source online:** Código Civil (1982), Código de Comercio (1955), Ley Orgánica de Amparo (1988), Ley de Registro Civil (2009). Options: (a) OCR from an official printed source, (b) negotiate with AN/TSJ libraries, or (c) temporarily source text from a third-party digitization **explicitly flagged "not yet verified against official text"** in the bot until cross-checked against a physical Gaceta. Transparent per-document verification-level headers in answers.

### 3.4 Recommended pipeline

1. **Primary: crawl the Gaceta portal** (~2012-01 → today, one month at a time) — enumerate gazettes via the advanced search (`fecha_desde/hasta`), fetch detail pages (Nº, type, date, sumario rows), download `/storage/YYYY/...pdf`; parse text directly for 2017+, **OCR (tesseract `spa`) for 2012–2016**; re-check broken records individually; TSJ gaceta mirror as fallback copy.
2. **Backfill classics via TSJ catalogs** — build the law→Gaceta→PDF map from `/leyes`, `/codigos`, `/constitucion` (each entry carries the official citation = provenance header); download scans and OCR. Do **not** trust TSJ "current text" where the Gaceta portal has a newer version (COT 2001 vs COT 2020/6.533 — always prefer the newer Gaceta).
3. **Update cadence:** daily poll of the Gaceta portal for new Ordinarias/Extraordinarias; one provenance record per document (Gaceta Nº, date, pages, source URL, SHA-256).
4. **Operational care:** several official URLs 403/404 intermittently and `.gov.ve` vs `.gob.ve` host confusion breaks links — build retries and dual-source fallbacks into the crawler.
5. **Start small, ship value fast:** no OCR needed for the Constitution and COT 2020 (text-layer) — launch the corpus with those, then expand into the OCR backlog.

### 3.5 Implication for citations (§7)

The pipeline must retain **per-document metadata (law name, gazette number, date) and stable URLs/ids** so the response layer can generate full formal citations from retrieved chunks. OCR work for 2012–2016 Gaceta and TSJ scans must preserve gazette numbers.

---

## 4. Topic gating design

**Verdict: a hybrid three-stage pipeline with strict precision bias achieves the reliability target** (research: `research/topic-gating/findings.md`).

### 4.1 Architecture

1. **Deterministic pre-filter** (zero cost): empty/too-short messages, greetings and identity patterns → canned product copy (no LLM call).
2. **LLM topic gate** (primary semantic filter): a separate call — outside the chat context, so user prompts can never mutate the rules — temperature 0, structured JSON output (`in_scope: yes|no|uncertain, branch_of_law, legal_subject, reason`), a rubric listing all in-scope Venezuelan law branches plus an out-of-scope taxonomy, 8–12 Spanish few-shot examples per class. `UNCERTAIN` routes to stage 3 — never hard-rejects (this one choice rescues most false-rejects).
3. **Retrieval gate** (second independent filter + answer grounding): hybrid retriever over the **official corpus only** — BM25 + multilingual legal embeddings (e.g. `paraphrase-multilingual-MiniLM`-class / BGE-M3; cross-encoder re-rank; benchmark RigoBERTA/LegalBERT-style Spanish-legal backbones later); top-k=5; threshold θ calibrated on a labeled eval set; direct regex fast-path for article-number queries. **Answer only from retrieved chunks; instruct the model to cite article numbers and to say "no tengo esa información" when the needed rule is not in the excerpts.**
4. **Optional output groundedness check** (insurance layer): SynCheck-style faithfulness monitor (AUROC 0.85) or Azure Content Safety Groundedness once it supports Spanish/legal domains; on violation → regenerate or fall back to the unanswerable copy.
5. **Telemetry + eval**: log every gate decision and rejection reason; **build the labeled eval set now** (~20 in-scope branches × 10+ queries + off-topic categories: foreign law, art/sports, identity, mixed, adversarial injection); run it as a regression gate on every prompt/corpus change; sample production rejects for human review.

### 4.2 Reliability

- Published evidence: legal AI tools hallucinate **17–33% even with RAG** → grounding is necessary but not sufficient; LLM classifiers reach 95%+ with rubric + exemplars + CoT; LLMs are overconfident out-of-domain → **never threshold the LLM gate's self-reported confidence**; corpus-density abstention is strong on easy negatives but ~20%+ leak on deliberately adversarial near-domain inputs — hence two independent gates.
- **Estimated achievable target on typical traffic: false-accept < 1%, false-reject ≤ 10%**, with the hybrid (leaks multiply across independent gates). Stricter false-accept (<0.5%) is possible at 15–20%+ false-reject — the product should stay **precision-biased**: a wrongly-answered off-topic question erodes trust and invites liability; a false rejection costs one retry.
- **Two distinct reject outcomes (product requirement):** `OUT_OF_SCOPE` (subject not covered) vs `IN_SCOPE_UNANSWERABLE` (legal VE question not in corpus) — different copy, different guidance (see §7.4).

### 4.3 Policy edge cases (ratified by the PO during grilling, recorded here)

Procedural questions are in scope (route to retrieval; unanswerable → `IN_SCOPE_UNANSWERABLE`, never topic-reject). Mixed legal+non-legal → answer the legal sub-part only, state the rest is ignored; extraction failure → mixed-query copy. Law homework: explaining a statute is in scope; producing a deliverable for evaluation is out. Meta-prompts/injection → always out-of-scope + canned copy. Multi-turn: follow-ups inherit scope unless a clearly new off-topic subject appears; re-run the gate on the latest message (or a compacted summary), never the whole history. Language: classify by topic, not language; answer in Spanish.

---

## 5. Regulation & liability

**Verdict: feasible with standard safeguards; lawyers-as-users is the strongest defense** (research: `research/regulation/findings.md`).

### 5.1 Data protection

- **No binding data-protection statute is verifiably in force.** Operative framework: Art. 60 CRBV (privacy/`habeas data`) and the Ley Orgánica del Derecho de Acceso a la Información (2012). The *Ley Orgánica de Protección de Datos Personales* (Decreto 1.404, 2021) is reported passed but **no Gaceta publication was verified** — treat its requirements (consent, minimization, retention, sensitive data, international transfer) as **best-practice standards, not enforceable obligations**.
- Adopt GDPR-style practices proactively: consent notice in onboarding, **short retention (48–72h)** of message bodies/phones, no cross-user profiling, aggregated non-personal metrics only, international-transfer safeguards (no operative VE authorization regime exists).

### 5.2 Civil liability for wrong answers

- Fault-based regime (CC Arts. 1.185, 1.191, 1.196) can in principle ground daño-moral/material claims, but **fault + causation + loss is hard to show for a labeled informational tool**. Disclaimers defeat the reliance element; **licensed professional users cannot credibly claim reliance on an unverified tool** — a verified-attorney gate exploits this. Stay on the legal-**information** side of the *Ley de Abogados* (1967) line: topic-gated, cited, no "you should", no case-specific application, no client relationship.

### 5.3 Platform terms / sanctions

- Both platforms place operational/compliance liability on the operator, and both terms permit legitimate legal content. Telegram's Bot ToS makes the operator "solely responsible"; Meta Business terms require lawful use. OFAC: targeted Venezuela program, GL 25/GL 24A cover communications services — full analysis in §2.1 and the whatsapp findings.

### 5.4 Risk register

| Risk | Likelihood | Impact | Mitigation |
|---|---|---|---|
| LOPDP 2021 (if ever in force): consent/minimization/retention/transfer | Low–Med | Med–High | GDPR-style practices proactively; short retention; consent in onboarding |
| Art. 60 / habeas-data claim over user data | Low–Med | Med | Minimize data, delete fast (48–72h), no profiling |
| Civil liability for a wrong answer (CC 1185) by a harmed third party | Med | Med | Persistent disclaimers, citations, verified-lawyer gate, "no reliance" posture, groundedness check |
| Unauthorized practice / misleading the public (Ley de Abogados) | Low–Med | Med | Information-only framing; never case-specific advice; topic gating; escalation to human lawyers |
| Platform takedown/ban (spam/ToS) | Med | Med | Bot-ToS compliance; no bulk messaging; rate limits; graceful fallback |
| Regulatory/state scrutiny of a legal-info service | Low–Med | Med–High | Transparent operator identity; Venezuelan-law-grounded; conservative moderation |
| OFAC sanctions exposure (operator side) | Low–Med | High | SDN screening of counterparties; general-license analysis (GL 25/24A) |
| **Residual:** enthusiastic user reliance despite onboarding disclosure | Low–Med | Med | Recorded trade-off from ticket #7: onboarding + `/disclaimer` disclosure instead of per-answer footer; mitigated by lawyer audience + gating + citations |

### 5.5 Mandatory disclosures (product requirements)

- **Onboarding identity statement** (first interaction): «Soy un asistente de consultas jurídicas sobre el derecho venezolano. No soy un abogado; brindo información general basada en los textos legales vigentes.»
- **On-demand full disclaimer** via `/disclaimer` (see §7.4 for exact copy) + privacy notice (data minimization, retention, contact).
- **Jurisdiction/choice-of-law clause → Venezuela**; clear "operated by [entity]" identification.

---

## 6. Response format contract

**Decision from ticket #7 (grilled HITL with the PO).** The exact user-facing copy below is final and ships verbatim in implementation.

### 6.1 Citations

**Full formal citation + source link** for every legal reference: «Artículo N de la Ley X, Gaceta Oficial N° Y del DD/MM/AAAA» followed by a direct URL to the official text when the corpus holds a digital copy; laws without a digitized corpus source (e.g. the Código Civil gap) keep the full citation without a link. Rationale: lawyers verify at a glance; the official-only corpus makes every citation point at verifiable text; a link removes the last verification step on messaging platforms.

### 6.2 Answer structure

**Legal-memo style:** context/premise → analysis with citations → conclusion at the end. Deliberately not "verdict first" — the exposition carries the citations and the conclusion lands with its basis shown.

### 6.3 Disclaimer policy

Disclosure at first interaction + on-demand `/disclaimer` command — **not** appended to every answer. **Recorded trade-off:** lighter than the strongest defense identified in regulation research (persistent footer defeats reliance under CC 1185); the residual risk is carried in the risk register above; the lawyer-focused audience, topic gating and grounded citations remain the primary defenses.

### 6.4 Rejection copy (final, formal register — no emojis, polite imperative)

*Identity / meta (canned):*
> Soy un asistente de consultas jurídicas sobre el derecho venezolano. No soy un abogado; brindo información general basada en los textos legales vigentes.

*Out-of-scope:*
> Este asistente solo responde consultas sobre temas jurídicos de Venezuela: leyes, códigos, normas y procedimientos vigentes. Su mensaje no parece corresponder a esa materia. Por favor, reformule su consulta en términos legales.

*Coverage + retry guidance:*
> Puedo asistirle, por ejemplo, con: «¿Cuáles son los requisitos para un divorcio en Venezuela?», «¿Qué establece la Ley Orgánica del Trabajo sobre las vacaciones?» o «¿Cómo se tramita una solicitud de insolvencia?». Por favor, formule su pregunta sobre una norma, un derecho o un trámite en Venezuela.

*In-scope but unanswerable from corpus:*
> Su consulta corresponde a materia legal venezolana, pero no dispongo de esa información en mis fuentes (textos oficiales de las leyes venezolanas). Le recomiendo consultar la Gaceta Oficial o el portal del TSJ, o contactar a un abogado.

*Mixed legal + non-legal:*
> Puedo asistirle con el aspecto jurídico de su consulta. Por favor, reformúlela enfocándose únicamente en el tema legal venezolano.

*/disclaimer:*
> Esta respuesta es información jurídica general basada en los textos legales vigentes; no constituye asesoría legal para su caso particular. Para orientación sobre su caso concreto, consulte a un abogado.

*Human-lawyer escalation (opt-in):*
> Si necesita orientación sobre su caso concreto, puede agendar una consulta con un abogado: [contacto/enlace]. Recuerde que esta información general no sustituye la asesoría legal profesional.

### 6.5 Tone

**Neutral and clear** — plain accessible language; legal terms only where indispensable; straightforward prose. Legal-memo structure organizes exposition; the formal register is reserved for rejections and identity copy. (Contract technicality: all canned copy lives in a constants file, stable across turns — a behavioral requirement from the gating research.)

---

## 7. Implementation architecture outline (for the next map)

A single stateless backend (a fast API + queue) with one thin channel adapter — Telegram (posture updated 2026-08-22, see §2.4):

- **Shared core:** topic-gating pipeline (deterministic pre-filter → LLM gate → retrieval gate, optional groundedness), retrieval over the official corpus (BM25 + embeddings + re-ranker), answer generation with citation formatting, constants file with all canned copy, eval-set regression harness, telemetry.
- **Telegram adapter (Bot API):** long polling first (free always-on host), webhook (HTTPS, port 443, `secret_token`) once on a cloud host; state keyed by `chat_id`; chunk answers to ≤4096 chars; MarkdownV2 citations; `sendDocument` for corpus PDFs (≤50 MB); queuing/retry and rate limiting ≤1 msg/s per chat.
- **Data posture:** 48–72h retention, no profiling, aggregated metrics only (mirrors §5.1). Verified-attorney gate (bar-number check or attestation) + opt-in human-lawyer escalation.
- **Ops:** daily Gaceta poll for corpus updates with provenance records (Gaceta Nº, date, pages, URL, SHA-256); monitoring of bot health and OONI/press for network-level restrictions.

---

## 8. Open items — what the next map should ticket

These are deliberately **not** settled here; they belong to the implementation effort and are listed in rough priority order:

1. **OCR feasibility probe on a sample** (recommended: YES to ticket it) — run tesseract `spa` on a TSJ scan (e.g. Código Penal 2005, GOE 5.768) and a 2012–2016 Gaceta scan to measure real quality/speed before committing to the full ~2005–2016 OCR backlog. Cheap; de-risks the corpus build.
2. **Corpus ingestion pipeline**: chunking, vector store, OCR batch job, provenance records, daily update poll, broken-record re-check strategy (LISLR 6.210, 403/404 handling).
3. **LLM/RAG choices**: model selection for the answer engine and the topic gate, embedding model (multilingual), re-ranker, hosting — the gating research prescribes corpus-only retrieval + multilingual embeddings; the exact stack is an implementation decision.
4. **Labeled eval set for gating** (~20 branches × 10+ queries + off-topic categories) — recommended to start during implementation's first sprint, before prompt/corpus tuning.
5. **Platform execution (Telegram-only)**: the posture decision is made (§2.4); the remaining channel work is the Telegram adapter design (chunking, citations, reach monitoring). The original WhatsApp onboarding item is discarded by the 2026-08-22 PO decision.
6. **Verified-attorney gate design**: bar-number validation path vs attestation opt-in; UX for the public fallback.

**Handoff:** this study is the input to a larger implementation map. The destination of that map: a running **Telegram** bot with the corpus ingested for its top-N most-consulted laws, gating calibrated on the eval set, and the §7 architecture live.

---

## 9. Sources

- Map: [Map: lawyer-bot-ve — Feasibility study (#1)](https://github.com/davidsilva131/lawyer-bot-ve/issues/1)
- Ticket #2 — [Official sources of the Venezuelan legal corpus (#2)](https://github.com/davidsilva131/lawyer-bot-ve/issues/2) · `research/corpus/findings.md` (PR #9)
- Ticket #3 — [WhatsApp Business API in Venezuela (#3)](https://github.com/davidsilva131/lawyer-bot-ve/issues/3) · `research/whatsapp/findings.md` (PR #10)
- Ticket #4 — [Telegram Bot API: reach in Venezuela (#4)](https://github.com/davidsilva131/lawyer-bot-ve/issues/4) · `research/telegram/findings.md` (PR #11)
- Ticket #5 — [Topic gating (#5)](https://github.com/davidsilva131/lawyer-bot-ve/issues/5) · `research/topic-gating/findings.md` (PR #12)
- Ticket #6 — [Regulation & liability (#6)](https://github.com/davidsilva131/lawyer-bot-ve/issues/6) · `research/regulation/findings.md` (PR #13)
- Ticket #7 — [Response format for lawyers (#7)](https://github.com/davidsilva131/lawyer-bot-ve/issues/7) (resolution comment holds the final copy)