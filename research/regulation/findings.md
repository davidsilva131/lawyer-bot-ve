#  — Findings

Research for ticket # (wayfinder map #1, repo lawyer-bot-ve). Researched 2026-08-16 by an AFK subagent; verified via primary-source fetches.

# Regulatory & Liability Landscape — Venezuelan Legal-Q&A Bot for Lawyers

## (1) Venezuela Data Protection

**Current status: no binding data-protection statute appears to be in force.**
- **Verifiable:** Art. 60 of the 1999 Constitution (privacy, intimacy, confidentiality, reputation — *habeas data* right) and the 2012 *Ley Orgánica del Derecho de Acceso a la Información* are the operative framework. [Constitution text](https://pandectasdigital.blogspot.com/) | [VE Sin Filtro 2024 communiqué](https://talcualdigital.com/ong-alerta-sobre-la-falta-de-leyes-y-procedimientos-para-proteger-datos-personales/)
- **Verifiable:** Civil-society sources (VE Sin Filtro, Espacio Público, El Diario, 2024–2026) consistently state there is no specific law and no enforcement authority; the 2001 *Ley Especial Contra Delitos Informáticos* covers cybercrime, not data processing. [El Diario search results](https://eldiario.com/?s=proteccion+de+datos+personales) | [TalCual Apr 2026 report](https://talcualdigital.com/el-peligro-de-vivir-sin-proteccion-de-datos-en-venezuela-como-resguardar-tu-informacion/) | [Espacio Público — "¿En Venezuela se regula la protección de datos personales?"](https://espaciopublico.ong)
- **Murky area (uncertain):** *Ley Orgánica de Protección de Datos Personales* (Decree 1.404, 2021) was reported passed by the (pro-government) Asamblea Nacional — but I could not verify publication in *Gaceta Oficial*. The AN's own [Vigentes list](https://www.asambleanacional.gob.ve/leyes/vigentes) and TSJ/Gaceta pages show no such law; an [Acceso a la Justicia digest of 2021–2022 promulgated laws](https://accesoalajusticia.org/leyes-dictadas-por-la-an-promulgadas-y-publicadas-en-gaceta-oficial-2021-2022/) doesn't list it. If published, it is at best unimplemented (no authority, no fines) — treat its requirements (consent, minimization, retention, sensitive-data, international-transfer authorization) as **best-practice standards, not enforceable obligations today**.
- TSJ Sala Constitucional (2024) has read data protection into Constitutional privacy/habeas-data rights. [Espacio Público — "Protección de datos en Venezuela según la Sala Constitucional"](https://espaciopublico.ong)

**Implication for the bot:** legal questions commonly embed **sensitive data** (criminal, labor, family, health). Even absent a specific law, Art. 60, the habeas-data doctrine, and reputational risk argue for: consent, minimization, short retention, no cross-user profiling. International transfer (host abroad) has **no operative authorization regime** to comply with — simply adopt GDPR-style transfer safeguards.

## (2) Liability for Wrong Answers (Civil)
- **Código Civil Art. 1.185** — fault-based civil liability ("el que con intención, o por negligencia o imprudencia, ha causado un daño a otro, está obligado a repararlo"); **Art. 1.196** (subjective intent), **Art. 1.191** (liability for subordinates/agents), **Art. 1.195** (argument that "remuneración" implies a compensation element). Publisher's liability doctrine also gives Art. 1.187 relevance. These are standard, citable references via [Justia Venezuela](https://venezuela.justia.com/) or [Pandectas Digital](https://pandectasdigital.blogspot.com/).
- A bot operator can, in principle, be drawn into a daño-moral/daño-material claim for bad output — but showing **fault + causation + loss** under Art. 1.185 is hard when the bot is labeled an informational research tool.
- **Disclaimers materially help:** they establish the user knows answers are research-style pointers, not personalized legal opinions — defeating the reliance element and shifting the user's duty to verify.
- **Lawyer-only end users change the calculus:** licensed professionals cannot credibly claim they relied on an unverified tool instead of their own legal duty to check primary sources; this is the single strongest liability defense and should be exploited (verified attorney gate).

## (3) Unauthorized Practice of Law
- **Ley de Abogados (1967)** restricts professional legal practice (*ejercicio de la abogacía*) to registered *abogados*; unlicensed rendering of legal services is unlawful/prone to sanction. Legal sources: [Ley de Abogados](https://pandectasdigital.blogspot.com/), [TSJ — Leyes/Códigos](https://www.tsj.gob.ve/leyes).
- Venezuelan doctrine draws the classic line: **legal information** (explaining what the law says) vs. **legal advice** (applying law to a specific person's case with a professional-client relationship). The bot should be engineered to stay strictly on the "information" side: topic-gated, cite the official corpus, no client-specific application, no documents, no "you should."
- **Uncertain:** no settled Venezuelan authority addresses AI/software "practicing law"; exposure is low for an information-only, topic-gated service to professional users, but increases if the bot ever produces case-specific application, advice-like language, or appears to create a client relationship.

## (4) Platform Terms
- **Telegram ToS** (fetched live): prohibits spam/scams, promoting violence, illegal content, and "activities recognized as illegal in the majority of countries"; allows banning; **Bot Developers ToS** applies to bot operators. [Telegram ToS](https://telegram.org/tos) | [Telegram Bot developers](https://telegram.org)
- **WhatsApp Business**: impose lawful use, no spam/automated abuse, compliance with local law; **Meta Business Terms** and Business Messaging policies require lawful content and prohibit misleading practice; specific policy pages were erroring out during research (rate-limited) — validate live at [business.whatsapp.com/policy](https://business.whatsapp.com/policy) and [Meta Business Terms](https://www.facebook.com/legal/businessservices/help-center/terms).
- Both platforms give the operator (not the user) typical indemnity/liability-heavy terms; content moderation obligations are modest but real (legal content is lawful; keep the bot free of gambling/drugs/hate content).

## (5) Sanctions Cross-Reference
- **One pointer only:** OFAC maintains a broad Venezuela sanctions program (Executive Orders 13884, 13692, expanded in 2017; GLs carve out sectors); serving the Venezuelan public with ordinary information services by a US person can engage the **Venezuela Sanctions Regulations** and warrants a screening of users against the **SDN list** plus a general-license analysis. **Full analysis belongs in the separate WhatsApp ticket.** [OFAC — Venezuela Sanctions](https://ofac.treasury.gov/sanctions-programs-and-country-information/venezuela-related-sanctions)

## (6) Mitigations (recommended)
- Persistent disclaimers: "research/informational only — not legal advice; verify primary sources; consult a licensed Venezuelan attorney"; shown at session start and in every response footer.
- Verified-attorney gate (bar number check or attestation) to preserve the "professional end users" defense.
- Topic-gating hardening (no case-specific application); automatic escalation/refusals for sensitive personal scenarios.
- Retention: delete message bodies/phone numbers after X (e.g., 48–72h); keep only aggregated, non-personal metrics; log only abuse metadata.
- Rate limits + per-user volume caps as abuse control; human-review escalation path for flagged queries; guardrail on "what happens in my case" queries.
- Ground answers in cited official sources (Gaceta/TSJ) with explicit verification pointers.
- Jurisdiction/choice-of-law clause pointing to Venezuela (civil courts) + clear "operated by [entity]" identification.
- Sanctions screening of any business counterparties (not end users).

## Risk Register
| Risk | Likelihood | Impact | Mitigation |
|---|---|---|---|
| LOPDP 2021 (if ever in force) obligations — consent/minimization/retention/transfer | Low–Med (unimplemented today) | Med–High | Adopt GDPR-style practices proactively; short retention; consent notice in onboarding |
| Art. 60 / habeas-data constitutional claim over user data | Low–Med | Med | Minimize data, delete fast, no profiling |
| Civil liability for a wrong answer (Art. 1185 CC) by a harmed third party | Med | Med | Persistent disclaimers, citations, verified-lawyer gate, "no reliance" posture |
| Unauthorized practice / misleading the public (Ley de Abogados) | Low–Med | Med | Information-only framing; never case-specific advice; topic gating |
| Platform takedown/ban (WhatsApp/Telegram spam or ToS) | Med | Med | Compliance with bot ToS; no bulk messaging; rate limits; graceful fallback |
| Regulatory/state scrutiny of an "legal info" service | Low–Med | Med–High | Transparent operator identity, Venezuelan law-grounded, conservative moderation |
| OFAC sanctions exposure (operator side) | Low–Med | High | Separate sanctions ticket; SDN screening; general-license analysis |

## Honest Uncertainty
- The LOPDP (Decreto 1.404, 2021) status is the key open question: approved per reports, **but no Gaceta publication verified**; AN current law list, TSJ pages, and NGO digests suggest it is not in force. I could not hit the AN/TSJ search APIs (403/anti-bot) to do an exhaustive primary check.
- Meta/WhatsApp terms pages returned errors during the session, so those conclusions rest on the public policy pages' known content plus Telegram's live ToS.
- No Venezuelan caselaw specifically on AI/bot legal-advice liability found — analysis is doctrinal (CC arts. 1185–1196) and deductive.

Source URLs collected in the %TEMP%/lawbot folder; the key working links above are the citable ones. A follow-up session should retry browser automation to close the Meta terms and Gaceta-verification gaps.