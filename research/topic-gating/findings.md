#  — Findings

Research for ticket # (wayfinder map #1, repo lawyer-bot-ve). Researched 2026-08-16 by an AFK subagent; verified via primary-source fetches.

# Topic Gating for a Venezuelan Legal Q&A Bot — Research Report

**Scope note on sourcing:** The research network (Venezuela-region) could not reach `platform.openai.com`/`platform.claude.com` (Cloudflare/region block) or DuckDuckGo/Bing (CAPTCHA/noise), so Anthropic/OpenAI claims below are cited from **verified mirrors** (official GitHub cookbooks, arXiv, MS Learn, project sites). Where a canonical URL is cited but not re-verified from this network, it is flagged as such.

---

## (1) APPROACH OPTIONS

### (a) LLM guardrail / classifier prompt (decide in-scope vs out-of-scope before answering)

**How it works.** A separate LLM call (or the same model) classifies the user message into `IN_SCOPE` / `OUT_OF_SCOPE` (optionally 3-way: `UNCERTAIN`) using a rubric + few-shot examples, returning **structured JSON** (`{in_scope: bool, topic: enum, reason: str}`). Only `IN_SCOPE` reaches the answering pipeline. Hugely popular: Anthropic's own cookbook builds exactly this — an LLM ticket classifier with category definitions, RAG-retrieved labeled examples, and chain-of-thought, documenting accuracy gains **from ~70% baseline to 95%+** ([anthropic-cookbook `capabilities/classification/guide.ipynb`](https://github.com/anthropics/anthropic-cookbook/blob/main/capabilities/classification/guide.ipynb)). Llama Guard is the canonical "LLM-as-classifier guardrail" research product, showing a **risk taxonomy is what makes prompt classification work** ([arXiv:2312.06674](https://arxiv.org/abs/2312.06674)). Guardrails frameworks operationalize this: NeMo Guardrails (programmable "rails", topic refusal rails) ([arXiv:2310.10501](https://arxiv.org/abs/2310.10501), [GitHub](https://github.com/NVIDIA/NeMo-Guardrails)) and Guardrails AI (input/output guards + validators) ([GitHub README](https://github.com/guardrails-ai/guardrails)).

**Pros.** No training data needed; handles subtle semantics (foreign-law-vs-VE-law, mixed queries) far better than lexical/embedding signals; trivially extended to output a reason for the UX fallback; easy to iteratively improve (just edit the rubric/examples).
**Cons.** Costs an extra LLM call per message (qualitative cost note: fine at low volume, matters at scale); adds latency; inherits the model's overconfidence (see §3); brittle under prompt-injection framing ("ignora tus reglas"); classification quality depends heavily on prompt discipline (temperature 0, structured output, few-shot balance).
**Failure modes.** Jailbroken/meta prompts; similes and indirect phrasing; brand-new topics not covered by few-shots; sarcasm/mixed intent; LLM returns malformed JSON → needs strict parsing with a default-to-reject on parse failure.

### (b) Retrieval-grounded gating (answer ONLY if corpus retrieval returns relevant official articles)

**How it works.** The bot only answers when retrieval over the *official Venezuelan law corpus* returns relevant chunks above a similarity threshold (e.g., hybrid BM25 + embedding search, top-k chunks, cross-encoder re-ranking, max-score threshold θ); otherwise it refuses. This is "retrieval-grounded rejection": grounding in RAG ("Retrieval-Augmented Generation", [Lewis et al.](https://arxiv.org/abs/2005.11401)) extended with abstention. Microsoft productizes the analogous *output*-side check: **Azure AI Content Safety Groundedness detection** — binary (non-reasoning) or reasoning mode, task types (QnA/Summarization), domain selection (MEDICAL/GENERIC — no legal domain yet), an auto-correction feature, and an explicit caveat that **accuracy is optimized for English** ([MS Learn](https://learn.microsoft.com/en-us/azure/ai-services/content-safety/concepts/groundedness)). Research on abstention for RAG: energy-based density scoring over the corpus reaches **AUROC 0.961** for near-distribution detection with **FPR@95 = 0.235** on semantically *hard* out-of-scope negatives (vs 0.331 for calibrated softmax) ([arXiv:2509.04482](https://arxiv.org/abs/2509.04482)); [Self-RAG](https://arxiv.org/abs/2310.11511) and [CRAG](https://arxiv.org/abs/2401.15884) both add explicit "is the retrieved context relevant/usable?" critique steps precisely so the system can refuse or re-retrieve.

**Pros.** Grounds answers in the official corpus (the hard product requirement); no LLM call for gating (embeddings are cheap, ms-level); gives a citation trace; out-of-scope detection is *explainable* ("no article matches").
**Cons.** Gates on *retrievability*, not *law-ness*: a genuine Venezuelan legal question phrased so that no corpus chunk scores high (paraphrase, colloquialism, procedural "how do I file…" wording, article-number queries) gets false-rejected; conversely, near-domain out-of-scope content (foreign law with similar vocabulary, legal-sounding hypotheticals) can slip through; embedding quality on **Spanish legal text** matters enormously (English-centric models degrade — BEIR shows zero-shot cross-domain retrieval degrades sharply for generic models, [arXiv:2104.08663](https://arxiv.org/abs/2104.08663)); thresholds need per-corpus calibration (scores vary by article length/chunking).
**Failure modes.** Corpus gaps (areas of law not ingested → all true rejects); chunking artifacts; threshold drift after corpus updates; queries that are legal but *unanswerable from the corpus* vs *out-of-scope* are conflated — needs two distinct reject messages (see §4).

### (c) Hybrid (recommended combination)

**How it works.** Classifier gate first (LLM or small model), then retrieval gate as a second independent filter; answer only if **both** pass; optionally an output-side groundedness check (e.g., a SynCheck-style monitor — **AUROC 0.85** at detecting unfaithful sentences, [arXiv:2406.13692](https://arxiv.org/abs/2406.13692), or Azure grounding detection once Spanish support or a legal domain exists). The signal sources are complementary: the classifier reasons over semantics, the retriever over lexical/topical match to official texts.
**Pros.** False-accepts multiply down (~product of both gates' leak rates, see §3); failure modes are disjoint; each stage is independently testable; lets you route `UNCERTAIN` classifier outputs to the retrieval gate instead of hard-rejecting.
**Cons.** Highest complexity; more moving parts to monitor; false-rejects add up (union of both gates' false-reject rates) unless the reject path is handled well (escalation/retry copy).
**Failure modes.** Configuration errors (mismatched thresholds between stages); both gates share the embedding model's blind spots if you reuse the same vector store for gating and retrieval.

### (d) Dedicated small classifiers (fine-tuned embeddings / zero-shot transformers)

**How it works.** A small model classifies in/out-of-scope directly: (i) **zero-shot** NLI-style, e.g. `facebook/bart-large-mnli` via the HF pipeline ([HF zero-shot docs](https://huggingface.co/docs/transformers/tasks/zero_shot_classification)); (ii) **embedding + logistic regression** (OpenAI's cookbook pattern: embeddings + sklearn classifier, with the caveat that *fine-tuned models beat embeddings for many tasks* and you want more examples than embedding dimensions) ([Classification_using_embeddings.ipynb](https://github.com/openai/openai-cookbook/blob/main/examples/Classification_using_embeddings.ipynb)); (iii) **SetFit** — prompt-free few-shot fine-tuning of sentence transformers, achieving results comparable to PEFT/PET with orders-of-magnitude fewer parameters, and **multilingual by swapping the sentence-transformer body** (relevant: a Spanish/multilingual body for VE legal text) ([arXiv:2209.11055](https://arxiv.org/abs/2209.11055)). For Spanish legal text specifically, domain-adapted encoders exist: **LegalBERT** documents that legal-domain fine-tuning strategies differ from generic best practice ([arXiv:2010.02559](https://arxiv.org/abs/2010.02559)); **RigoBERTa** is a state-of-the-art Spanish RoBERTa usable as a classification backbone ([arXiv:2205.10233](https://arxiv.org/abs/2205.10233)); the **MARCELL** project provides large modern-legal-language corpora including Spanish for training ([marcell-project.eu](https://marcell-project.eu/)).
**Pros.** ~ms latency; deterministic; cheap; offline; runs as the fast pre-gate in front of an LLM gate.
**Cons.** Needs labeled data (500–2,000 example queries for solid binary gating) and periodic retraining; no explanations; brittle to typos, code-switching, neologisms; zero-shot BART-MNLI is English-centric and measurably weaker on Spanish; per-class recall/precision tuning is fiddly.
**Failure modes.** Training-label drift vs real traffic; sampling bias (users never ask like your eval set); near-boundary classes collapse together; silent degradation after model/embedding version bumps.

---

## (2) INPUT/OUTPUT CONTRACT

**IN-SCOPE (bot MUST answer):** any question about **the legal system of Venezuela** — i.e., interpretation, requirements, procedures, rights/obligations under current Venezuelan law. All branches: civil, penal, laboral, constitucional, tributario, procesal (civil/penal procedure), mercantil, administrativo, familia, inmobiliario, contractual, etc. Also in scope: *hypothetical or real fact patterns analyzed under Venezuelan law* ("si me despiden sin preaviso, ¿qué me corresponde?"), statute explanation ("explícame el artículo 87 de la Constitución"), and procedural questions ("¿cómo introduzco una demanda laboral en Venezuela?") — the latter must be answered only if the corpus contains the procedural law; otherwise it's a *scope-in-but-unanswerable* rejection (different copy, see §4), never a topic rejection.

**OUT-OF-SCOPE (bot MUST refuse):**
- Foreign law ("en Colombia, ¿…?", "US custody law")
- General chat / identity / meta: "hola", "¿cómo estás?", "¿quién eres?", "¿eres un abogado?" (answer with canned product copy, not a legal answer)
- Non-legal topics: art, sports, cooking, tech support, news ("¿qué pasó con X hoy?")
- Politics/opinion without a legal frame ("¿estás de acuerdo con el gobierno?" — even if corpus-adjacent, it's opinion; legal framing of a political fact IS in scope if corpus-grounded)
- Advice on non-Venezuelan law; international/private-international-law comparisons asking about other systems
- "Hazme el trabajo": producing essays, jurisprudential monographs, or memoranda *for submission* (see homework edge case)

**Edge cases (policy decisions the PO should ratify):**
1. **Procedural questions** → IN scope, but route to retrieval; if the corpus lacks procedural codes, respond with the *unanswerable* copy + point to official sources (TSJ/Gaceta Oficial), not the out-of-scope copy.
2. **Mixed legal + non-legal** ("¿qué pasa si me botan del trabajo y cómo hago un pan de jamón?") → extract and answer the legal sub-question only; explicitly say you're ignoring the non-legal part. If extraction fails → reject with the *mixed-query* copy. Extraction can be delegated to the LLM gate (return `legal_subpart` in JSON).
3. **Law homework** → explaining a statute a student doesn't understand is IN scope (it's legal information); *producing a deliverable for evaluation* (essay, full case brief) is OUT — recommend: answer explanations, refuse deliverable-writing, with copy stating the boundary. PO decision required.
4. **Legal advice vs legal information** → bot provides *general legal information* with citation + disclaimer; *personalized advice* ("dime si gano mi caso", "¿qué me conviene hacer?") → answer with the general rule AND escalate to a human lawyer. Every answer should carry the disclaimer: *"Esta respuesta es información jurídica general basada en textos legales vigentes; no constituye asesoría legal."*
5. **Multi-turn** → context inheritance: if turn N was judged in-scope, follow-ups inherit scope unless they introduce a clearly new off-topic subject; re-run the gate on the *latest user message* (or on a compacted conversation summary), never on the whole history.
6. **Language mixing** → classify by *topic*, not language: a French/English question about Venezuelan law is still in scope (product choice: respond in Spanish and note you answer in Spanish).
7. **Meta-prompts / injection** → always out-of-scope + canned copy; never let a user instruction change the system rules (the gate is a separate system-controlled call, not part of the chat context).

---

## (3) RELIABILITY

**Honest caveat up front:** no published false-accept/false-reject numbers exist for *Venezuelan-legal topic gating* specifically. The figures below are **engineering estimates triangulated from adjacent published evidence**; the project must measure on its own labeled eval set. What published evidence exists:

- Legal AI tools hallucinate **17–33% of the time even with RAG** (Stanford preregistered study, [Magesh et al.](https://arxiv.org/abs/2405.20362)) → *retrieval grounding is necessary but not sufficient*; don't trust a RAG pipeline without gating + groundedness checks.
- LLM classifiers can reach **95%+ accuracy** with rubric + RAG-exemplars + CoT ([Anthropic cookbook](https://github.com/anthropics/anthropic-cookbook/blob/main/capabilities/classification/guide.ipynb)).
- LLMs are **overconfident on out-of-domain inputs** — raw model confidence is a poor abstention signal ([Klein & Nabi](https://arxiv.org/abs/2006.09462): softmax-probability abstention answered only 48% of questions at 80% accuracy vs 56% for a trained calibrator; also [To Believe or Not to Believe Your LLM](https://arxiv.org/abs/2406.02543)); the same paper's logic applies to *classification* confidence → **never threshold the LLM gate's own self-reported confidence**; use rubric-hardened outputs and retrieval evidence instead.
- Corpus-density gating: **AUROC 0.961 / FPR@95 0.235** on semantically *hard* near-distribution negatives (energy-based abstention, RAG healthcare study [arXiv:2509.04482](https://arxiv.org/abs/2509.04482)) → the worst-case leak through a well-tuned embedding gate is ~20%+ **on deliberately adversarial near-domain inputs**, but near-zero on easy negatives (art/sports/greetings).
- Faithfulness monitoring of generated answers: **AUROC 0.85** (SynCheck, [arXiv:2406.13692](https://arxiv.org/abs/2406.13692)).
- Retrieval quality degrades out-of-domain for generic retrievers ([BEIR](https://arxiv.org/abs/2104.08663)) → Spanish-legal-tuned retrieval (RigoBERTA/MARCELL-style, LegalBERT findings) is a precondition; multilingual embedding space for the corpus is not optional.

**Estimated rates on real Spanish user traffic** (assumes well-built eval set, threshold tuning, mostly *easy* negatives in real traffic — real users asking about art/sports/identity dominate the off-topic distribution):

| Approach | False-accept (answered off-topic) | False-reject (rejected valid VE-legal) |
|---|---|---|
| (a) LLM prompt classifier (frontier model, temp 0, rubric+few-shot) | **1–3%** typical; 5–10% on adversarial/mixed phrasing | **1–5%** (tunable; a "when in doubt, reject" policy pushes this to 5–10%) |
| (b) Retrieval threshold only | **~0.1–1%** on easy negatives; **5–20%** on semantically near out-of-scope (foreign law, legal-sounding hypotheticals) at workable thresholds | **3–10%** typical (paraphrases, procedural wording); **10–20%** at very tight thresholds |
| (c) Hybrid (a)+(b)+(output groundedness) | **~0.1–1%** (leaks multiply) | **5–15%** (leaks add) — mitigated by unanswerable-vs-out-of-scope routing |
| (d) Small classifier | Fine-tuned (500+ Spanish labels): **2–5%**; zero-shot BART-MNLI on Spanish: **7–15%** | Fine-tuned: **2–5%**; zero-shot: similar |

**Achievable target:** with the hybrid, **false-accept < 1% while keeping false-reject ≤ 10%** is realistic on typical traffic. Stricter (false-accept < 0.5%) is achievable at 15–20%+ false-reject and more human escalations — a trade the PO should set, biased toward *precision* (a wrongly answered off-topic question erodes trust and invites liability; a false rejection just costs one retry message).

---

## (4) UX FALLBACK (what the bot must say/do on rejection)

Requirements: (1) explicitly state the subject is out of scope, (2) state what IS covered, (3) offer retry guidance with an example, (4) optionally escalate to a human lawyer, (5) log the rejected query for eval-set growth.

**Exact copy suggestions (Spanish):**

*Out of scope (generic):*
> ⚠️ **Fuera de alcance.** Este asistente solo responde consultas sobre **temas jurídicos de Venezuela** (leyes, códigos, normas y procedimientos vigentes). Tu mensaje parece no estar relacionado con esa materia. Por favor, reformula tu consulta en términos legales.

*What's covered + retry guidance:*
> Puedo ayudarte con, por ejemplo: «¿Cuáles son los requisitos para un divorcio en Venezuela?», «¿Qué dice la Ley Orgánica del Trabajo sobre las vacaciones?» o «¿Cómo se tramita una solicitud de insolvencia?». Intenta hacer tu pregunta sobre una norma, un derecho o un trámite en Venezuela.

*Mixed legal + non-legal:*
> Puedo ayudarte con la parte jurídica de tu consulta. ¿Podrías reformularla enfocándote solo en el aspecto legal venezolano?

*In-scope but unanswerable from corpus (different from out-of-scope!):*
> Tu consulta sí es de materia legal venezolana, pero **no tengo esa información en mis fuentes** (textos oficiales de leyes venezolanas). Te recomiendo consultar la Gaceta Oficial o el portal del TSJ, o contactar a un abogado.

*Identity/meta questions:* canned — «Soy un asistente de consultas jurídicas sobre el derecho venezolano. No soy un abogado; brindo información general basada en textos legales.»

*Escalation to a human lawyer:*
> Si necesitas orientación sobre tu caso concreto, puedes agendar una consulta con un abogado: [contacto/enlace]. Recuerda que esta información general no sustituye la asesoría legal profesional.

*Persistent disclaimer (append to every answer):*
> *Esta respuesta es información jurídica general basada en los textos legales vigentes; no constituye asesoría legal para tu caso particular.*

**Behavioral requirements:** the rejection must come from the *gate's reason*, never look like the model "didn't know"; keep the same rejection copy stable across turns (don't let a following message flip an out-of-scope topic to in-scope without a genuine subject change); never auto-escalate without explicit opt-in (privacy); log rejection reasons for eval-set curation.

---

## (5) RECOMMENDATION — architecture for this bot

**Hybrid three-stage pipeline with strict precision bias:**

1. **Deterministic pre-filter** (zero cost): empty/too-short messages, greeting/identity patterns (regex) → canned copy.
2. **LLM topic gate** (primary semantic filter): separate call, temperature 0, **structured JSON output** (`{in_scope: yes|no|uncertain, branch_of_law, legal_subject, legal_subpart_for_mixed, reason}`), rubric listing all Venezuelan law branches as in-scope + an out-of-scope taxonomy (foreign law, general chat, identity, non-legal topics, deliverable-writing), 8–12 few-shot examples per class in Spanish. `UNCERTAIN` → route to stage 3 instead of rejecting (this single choice rescues most false-rejects). Model: a fast/cheap capable model; frontier model needed only if single-model setup.
3. **Retrieval gate** (second filter + answer grounding): hybrid retriever over the **official VE law corpus only** — BM25 + multilingual legal embeddings (start with `paraphrase-multilingual-MiniLM`-class or BGE-M3; fine-tune/search-rerank with a cross-encoder; benchmark against RigoBERTA/LegalBERT-style backbones and MARCELL-style data for future fine-tuning), top-k=5, cross-encoder re-rank, threshold θ tuned on a labeled eval set. Article-number queries get a regex fast-path (high-precision direct lookup). **Answer only from retrieved chunks; instruct the model to cite article numbers and to say "no tengo esa información" when the needed rule isn't in the excerpts.** Keep two distinct reject outcomes: `OUT_OF_SCOPE` vs `IN_SCOPE_UNANSWERABLE`.
4. **Optional output groundedness check** (insurance layer, low cost): SynCheck-style faithfulness monitor (0.85 AUROC) or Azure Content Safety Groundedness when it supports Spanish/legal domain; on violation → regenerate or fall back to the unanswerable copy.
5. **Fallback + telemetry**: exact Spanish copy per §4; opt-in human-lawyer escalation; log every gate decision + rejection reason; **build the eval set now** (≈20 in-scope branches × 10+ queries, plus off-topic categories: foreign law, art/sports, identity, mixed, adversarial injection) and run it as a regression gate on every prompt/corpus change; sample production rejects for human review.

**Rationale.** (i) *Precision over recall:* a legal bot that answers one off-topic question breaks trust and, for a law-adjacent product, invites risk; the Stanford study ([2405.20362](https://arxiv.org/abs/2405.20362)) is the cautionary tale that grounding alone doesn't guarantee correctness — gating + groundedness both needed. (ii) *Two independent gates = multiplicative leak reduction*: LLM semantic gate and retrieval topical gate fail on different inputs, so combined false-accept lands well under 1% while a single `UNCERTAIN` escape hatch keeps false-reject around 5–10%. (iii) *The corpus-only rule is the product's best friend*: "answered only from official Venezuelan law texts" is simultaneously a scope policy, a hallucination control (RAG grounding), and an explainability feature (citations). (iv) *Cost-wise* (qualitative only): one cheap gate call + embedding search per message is negligible at low volume; the small classifier in (d) is the natural scale-up path and should be evaluated with SetFit once a few hundred labeled gating examples accumulate.

---

## Sources

- Magesh et al., *Hallucination-Free? Assessing Reliability of Leading AI Legal Research Tools* (Stanford, 2024) — https://arxiv.org/abs/2405.20362
- Anthropic, *Classification with Claude* cookbook guide (70%→95%+ classifier via rubric+RAG+CoT) — https://github.com/anthropics/anthropic-cookbook/blob/main/capabilities/classification/guide.ipynb
- Inan et al., *Llama Guard: LLM-based Input-Output Safeguard* — https://arxiv.org/abs/2312.06674
- Rebedea et al., *NeMo Guardrails: A Toolkit with Programmable Rails* — https://arxiv.org/abs/2310.10501 · repo: https://github.com/NVIDIA/NeMo-Guardrails
- Guardrails AI (input/output guards, validators, Guardrails Index benchmark, Feb 2025) — https://github.com/guardrails-ai/guardrails
- Microsoft, *Azure AI Content Safety: Groundedness detection* (binary/reasoning modes, QnA task, domains, auto-correction, English-only caveat) — https://learn.microsoft.com/en-us/azure/ai-services/content-safety/concepts/groundedness · *Jailbreak/Prompt-shield detection* — https://learn.microsoft.com/en-us/azure/ai-services/content-safety/concepts/jailbreak-detection
- *Energy Landscapes Enable Reliable Abstention in RAG for Healthcare* (AUROC 0.961, FPR@95 0.235) — https://arxiv.org/abs/2509.04482
- *SynCheck: Synchronous Faithfulness Monitoring* (AUROC 0.85) — https://arxiv.org/abs/2406.13692
- Klein & Nabi, *Selective Question Answering under Domain Shift* (abstention/coverage trade-off; overconfident softmax) — https://arxiv.org/abs/2006.09462
- Cohen et al., *To Believe or Not to Believe Your LLM* (uncertainty/abstention) — https://arxiv.org/abs/2406.02543
- Lewis et al., *RAG for Knowledge-Intensive NLP* — https://arxiv.org/abs/2005.11401 · Asai et al., *Self-RAG* — https://arxiv.org/abs/2310.11511 · Yan et al., *CRAG* — https://arxiv.org/abs/2401.15884
- Es et al., *RAGAS* (reference-free RAG evaluation) — https://arxiv.org/abs/2309.15217 · Saad-Falcon et al., *ARES* — https://arxiv.org/abs/2311.09476
- Thakur et al., *BEIR* (zero-shot retrieval degradation) — https://arxiv.org/abs/2104.08663
- Tunstall et al., *SetFit: Efficient Few-Shot Learning Without Prompts* (multilingual-capable) — https://arxiv.org/abs/2209.11055
- Chalkidis et al., *LEGAL-BERT* (legal-domain fine-tuning guidance) — https://arxiv.org/abs/2010.02559 · Gutiérrez-Fandiño et al., *RigoBERTa* (Spanish SOTA LM) — https://arxiv.org/abs/2205.10233 · *MARCELL* legal-language corpus project — https://marcell-project.eu/
- OpenAI cookbook, *Classification using embeddings* — https://github.com/openai/openai-cookbook/blob/main/examples/Classification_using_embeddings.ipynb · *Question answering using embeddings* — https://github.com/openai/openai-cookbook/blob/main/examples/Question_answering_using_embeddings.ipynb
- Anthropic, *Effective context engineering for AI agents* — https://www.anthropic.com/engineering/effective-context-engineering-for-ai-agents
- Hugging Face, *Zero-shot text classification* (BART-MNLI pipeline) — https://huggingface.co/docs/transformers/tasks/zero_shot_classification
- Canonical references *not re-verifiable from this network* (region-blocked): OpenAI *Safety best practices* / *Moderation* — https://platform.openai.com/docs/guides/safety-best-practices · Anthropic *Guardrails* docs — https://platform.claude.com/docs/en/build-with-claude/guardrails

**Delivery notes:** No files created/modified in the repo or workspace (research artifacts only in the OS temp cache); no git/GitHub activity. The report above is the complete deliverable.