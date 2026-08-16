#  — Findings

Research for ticket # (wayfinder map #1, repo lawyer-bot-ve). Researched 2026-08-16 by an AFK subagent; verified via primary-source fetches.

# Telegram Bot for a Venezuelan Legal Q&A Service — Feasibility Research

**Scope:** Public Telegram bot answering Venezuelan legal questions for lawyers; grounded on official legal corpus; topic-gated. Every claim below cites a URL that was fetched and verified during this session (at time of research).

## 1) LAUNCH REQUIREMENTS

**Creating the bot (minutes, no approval queue)**
- A bot account is created via **@BotFather** (inside Telegram) with `/newbot`; you immediately receive an API token. No business verification, no document upload, no review process — this is the documented flow ([core.telegram.org/bots/tutorial](https://core.telegram.org/bots/tutorial), [core.telegram.org/bots/faq](https://core.telegram.org/bots/faq)).
- The bot **username** is 5–32 chars (Latin letters, digits, underscores, case-insensitive) and **must end in `bot`** (e.g. `lawyer_bot_ve_bot`); the username is permanent and cannot be changed; the display name/description/about are editable anytime (`/setdescription` up to 512 chars, `/setabouttext` up to 120 chars, `/setcommands`, profile picture) ([core.telegram.org/bots/features](https://core.telegram.org/bots/features)).
- The **token** grants full control; it can be regenerated with `/token` if compromised; sanity-check with `https://api.telegram.org/bot<token>/getMe` ([core.telegram.org/bots/tutorial](https://core.telegram.org/bots/tutorial), [core.telegram.org/bots/features](https://core.telegram.org/bots/features)).
- Platform statement: *"The Telegram Bot Platform hosts more than 10 million bots and is free for both users and developers"* ([core.telegram.org/bots](https://core.telegram.org/bots)).

**Receiving updates: webhook vs long polling**
- Two mutually exclusive methods: `getUpdates` (long polling) or `setWebhook` (outgoing HTTPS POST). You cannot use both at once ([core.telegram.org/bots/api](https://core.telegram.org/bots/api), section "Getting updates"; [core.telegram.org/bots/faq](https://core.telegram.org/bots/faq)).
- Long polling: cheapest to start (works on any always-on host, no public URL/SSL needed); paginated 100 updates per call, confirm with `offset`; duplicate-confirmation protocol documented ([core.telegram.org/bots/faq](https://core.telegram.org/bots/faq), [core.telegram.org/bots/api](https://core.telegram.org/bots/api)).
- Webhook: requires valid SSL; supported ports **443, 80, 88, 8443**; optional `secret_token` header to authenticate Telegram's requests; self-signed certs supported (upload public key) ([core.telegram.org/bots/faq](https://core.telegram.org/bots/faq), [core.telegram.org/bots/api](https://core.telegram.org/bots/api)).
- **Updates not delivered are stored max 24 hours**, then dropped — the bot must be online at least daily ([core.telegram.org/bots/api](https://core.telegram.org/bots/api)).

**Free hosting — verified free tiers exist (qualitative)**
- **Cloudflare Workers**: a free plan exists by default with daily usage limits; paid tier optional ([developers.cloudflare.com/workers/platform/pricing](https://developers.cloudflare.com/workers/platform/pricing/)).
- **Render**: free web services/static sites exist, described as ideal for hobby/development; free instances spin down on inactivity ([render.com/docs/free](https://render.com/docs/free)).
- **Railway**: a no-cost "Free" plan exists with a small included allowance; paid tiers optional ([docs.railway.com/reference/pricing](https://docs.railway.com/reference/pricing/)).
- **Vercel**: "The Hobby plan is free" ([vercel.com/docs/plans](https://vercel.com/docs/plans)).
- **Heroku**: free plans were **discontinued** (announced Aug 2022) — do not plan on them ([blog.heroku.com/next-chapter](https://blog.heroku.com/next-chapter)).
- Practical note: long polling needs an always-on process (any of the above with a scheduler, or a small always-on free VM); webhook needs a public HTTPS endpoint, which Cloudflare Workers/Vercel functions and Render free web services provide.

**Discovery**
- Bots are found by **username search in-app** or via a unique **`https://t.me/<bot_username>` link** ([core.telegram.org/bots](https://core.telegram.org/bots)).
- **Deep linking**: `https://t.me/your_bot?start=CODE` (parameter ≤64 chars, `A-Za-z0-9_-`) auto-sends `/start CODE` — ideal for campaign codes, source tracking, or gating; `?startgroup=` inside groups; inline mode (`@username query` from any chat) is optional ([core.telegram.org/bots/features](https://core.telegram.org/bots/features), [core.telegram.org/bots/api](https://core.telegram.org/bots/api)).
- **QR**: any `t.me/...` link can be converted to a QR code with standard generators for print/Web distribution (no first-class Telegram QR feature for bots; the link is the canonical handle).

**Private vs group chats**
- Private chats: the bot receives **all** messages from users who started it ([core.telegram.org/bots/faq](https://core.telegram.org/bots/faq)).
- Groups: **Privacy Mode is ON by default** — the bot only sees explicit commands (`/cmd@this_bot`), mentions, replies to itself, and messages sent via it; disable privacy in BotFather or make it admin to see all; bots never receive other bots' messages ([core.telegram.org/bots/features](https://core.telegram.org/bots/features), [core.telegram.org/bots/faq](https://core.telegram.org/bots/faq)).
- **Bots cannot initiate conversations** — a user must send the first message (e.g. via `/start` or a t.me deep link) ([core.telegram.org/bots](https://core.telegram.org/bots)).

**Message / rate limits**
- Outbound message text: **1–4096 characters** per message (after entity parsing) for `sendMessage`/`editMessageText` ([core.telegram.org/bots/api](https://core.telegram.org/bots/api)).
- Rate limits: avoid **>1 message/second in a single chat**; **≤20 messages/minute in groups**; bulk broadcasts **~30 messages/second globally**; exceeding yields HTTP 429. A **paid broadcast** upgrade exists (enabled via @BotFather, requires minimum balance and monthly-active-user base — qualitative only) ([core.telegram.org/bots/faq](https://core.telegram.org/bots/faq), [core.telegram.org/bots/api](https://core.telegram.org/bots/api)).
- Files: bots can **send files up to 50 MB** via Bot API; downloads via `getFile` up to 20 MB; `file_id`s are persistent ([core.telegram.org/bots/faq](https://core.telegram.org/bots/faq)).

**Inline keyboards**
- `InlineKeyboardMarkup` buttons attach to messages (URL buttons and `callback_data` buttons); button presses arrive as `callback_query` updates and must be answered with `answerCallbackQuery` — no message is sent to the chat, perfect for menu/topic-gating flows and multi-step Q&A ([core.telegram.org/bots/api](https://core.telegram.org/bots/api), [core.telegram.org/bots/features](https://core.telegram.org/bots/features)).

**Formatting**
- `parse_mode`: **MarkdownV2** (bold/italic/underline/strikethrough/spoiler/blockquote/inline URLs/code/pre; strict escaping rules) or **HTML**, or raw `entities` JSON; rich messages and streaming AI-style replies supported ([core.telegram.org/bots/api](https://core.telegram.org/bots/api) — "Formatting options", [core.telegram.org/bots](https://core.telegram.org/bots)).

**User state management**
- The API is **stateless**: conversation state lives in your backend keyed by `chat_id`/`user_id`; there is no platform-imposed session expiry or reply window (updates buffered ≤24h is the only clock) ([core.telegram.org/bots/api](https://core.telegram.org/bots/api), [core.telegram.org/bots/faq](https://core.telegram.org/bots/faq)).
- "Threaded Mode" (topics in private chats, toggleable via BotFather) and streaming responses are explicitly marketed for AI chatbots ([core.telegram.org/bots](https://core.telegram.org/bots)).

## 2) REACH IN VENEZUELA

**Overall digital baseline (DataReportal Digital 2025, Venezuela, Jan 2025):**
- 17.5M internet users, 61.6% penetration; 15.1M social media identities, 53.1% of population; 22.5M mobile connections, 79.1% ([datareportal.com/reports/digital-2025-venezuela](https://datareportal.com/reports/digital-2025-venezuela)).
- Caveat: DataReportal's Venezuela country report publishes figures **only for ad-reachable platforms** (Meta-family, TikTok, etc.); it publishes **no Telegram and no WhatsApp per-platform user figures** for Venezuela — no official/ad-platform number for Telegram's Venezuelan user base exists in the open ([datareportal.com/reports/digital-2025-venezuela](https://datareportal.com/reports/digital-2025-venezuela), [digital-2024-venezuela](https://datareportal.com/reports/digital-2024-venezuela)).
- Globally, Telegram reports **over 1 billion active users** (official FAQ) ([telegram.org/faq](https://telegram.org/faq)).
- Third-party app-analytics tracking exists (e.g. Sensor Tower published "Top 5 Communication Apps in Venezuela: Q2 2025 Performance", Sep 2025) but its figures are gated; surfaced via Google News RSS, not independently verified here ([Google News RSS result](https://news.google.com/rss/articles/CBMiqAFBVV95cUxNYVR6VjFFTFd4Nm5Ea0tyS2RHaUFtUkRrcmUxdmJYLTlZbGdTXzhxd1pxNWtzUFRxN0p3VjQ2REVRM3FHNFdVdGh)).
- **Professionals/lawyers:** no reliable public, per-profession Telegram penetration data for Venezuela was found; treat lawyers as a subset of the general adult messaging population. (WhatsApp's larger user base in Latin America is well documented — see WhatsApp ticket for its side of the comparison.)

**Is Telegram blocked or restricted in Venezuela?**
- **Yes, temporarily — and it was lifted fast.** On **Friday, January 10, 2025**, the government ordered ISPs (CANTV, Movistar, Digitel, Inter, Supercable, Airtek, G-Network) to restrict `telegram.org` and `web.telegram.org`, with the mobile app also affected; NGO **VE Sin Filtro** documented it ([aporrea.org](https://www.aporrea.org/medios/n400129.html)).
- The block was lifted within ~24h across all listed ISPs (CANTV and Inter by 11pm Jan 10; others by early morning Jan 11) ([confirmado.com.ve](https://confirmado.com.ve/reportan-bloqueo-de-la-plataforma-telegram/)).
- Current status: recent OONI (Open Observatory of Network Interference) measurements of `telegram.org` from Venezuela probes show **no anomalies/confirmed blocks** in the sampled responses (public API queried during this research: [api.ooni.io](https://api.ooni.io/api/v1/measurements?probe_cc=VE&domain=telegram.org); explorer UI: [explorer.ooni.org](https://explorer.ooni.org/search?probe_cc=VE&domain=telegram.org)).
- **Regulatory risk profile:** the platform is not currently blocked, but a short, ISP-level, state-ordered block happened in 2025 — a real, if intermittent, fragility for a service whose users depend on in-country availability.

## 3) COST STRUCTURE (qualitative only — no amounts)

- **Free platform:** Telegram's bot platform is free for users and developers; bots can message users at no cost within limits ([core.telegram.org/bots](https://core.telegram.org/bots), [core.telegram.org/bots/faq](https://core.telegram.org/bots/faq)).
- **User-side paid features exist** (Telegram Premium subscription; optional, user-initiated) ([telegram.org/faq](https://telegram.org/faq)); paid premium features are not required to use bots.
- **Optional paid platform features for scale:** paid broadcasts (above the free per-second broadcast cap — enabled in @BotFather, subject to balance/MAU thresholds) and Telegram Stars for payments/monetization ([core.telegram.org/bots/faq](https://core.telegram.org/bots/faq), [core.telegram.org/bots/api](https://core.telegram.org/bots/api)) — irrelevant at launch scale.
- **Hosting:** viable free tiers on several major hosts (verified in §1), so the bot can run at effectively no platform cost at launch.
- **Cost tier verdict: the platform itself is free-tier friendly** for this use case; the dominant costs would be engineering time and optional paid hosting upgrades, not Telegram.

## 4) COMPARISON SCAFFOLD

| Criterion | WhatsApp findings | Telegram findings |
|---|---|---|
| Verification required | see WhatsApp ticket | **None**: bot created via @BotFather; token issued in minutes; no business verification, documents, or approval queue ([core.telegram.org/bots/tutorial](https://core.telegram.org/bots/tutorial)) |
| Time-to-launch | see WhatsApp ticket | **Minutes to hours**: token immediate; tutorial "From @BotFather to Hello World"; main effort is backend ([core.telegram.org/bots/tutorial](https://core.telegram.org/bots/tutorial), [core.telegram.org/bots](https://core.telegram.org/bots)) |
| Reach penetration | see WhatsApp ticket | **No official VZ figure**; global 1B+ users; DataReportal VZ 2025 publishes no Telegram platform number; in-country ISP block occurred Jan 2025 (lifted <24h); not currently blocked per OONI ([telegram.org/faq](https://telegram.org/faq), [datareportal.com](https://datareportal.com/reports/digital-2025-venezuela), [aporrea.org](https://www.aporrea.org/medios/n400129.html), [explorer.ooni.org](https://explorer.ooni.org/search?probe_cc=VE&domain=telegram.org)) |
| Message limits | see WhatsApp ticket | 1–4096 chars/message; ~1 msg/s per chat; ≤20/min per group; ~30/s global; 429 on excess ([core.telegram.org/bots/api](https://core.telegram.org/bots/api), [core.telegram.org/bots/faq](https://core.telegram.org/bots/faq)) |
| Conversation window | see WhatsApp ticket | **No platform reply window**: bots may message users any time they've started the bot; updates buffered ≤24h if bot offline ([core.telegram.org/bots](https://core.telegram.org/bots), [core.telegram.org/bots/api](https://core.telegram.org/bots/api)) |
| Bot discovery | see WhatsApp ticket | Username search in-app, `t.me/<username>` links, `?start=` deep links, QR-able links, inline mode ([core.telegram.org/bots](https://core.telegram.org/bots), [core.telegram.org/bots/features](https://core.telegram.org/bots/features)) |
| Cost tier (qualitative) | see WhatsApp ticket | **Free tier**: platform free; verified free hosting tiers (Cloudflare/Render/Railway/Vercel); optional paid features only at scale ([core.telegram.org/bots](https://core.telegram.org/bots), [developers.cloudflare.com](https://developers.cloudflare.com/workers/platform/pricing/), [render.com](https://render.com/docs/free), [vercel.com](https://vercel.com/docs/plans)) |
| Data / privacy | see WhatsApp ticket | Bot receives user's name/username/profile pic + all messages sent; cloud chats (incl. bot chats) are not end-to-end encrypted by default (only Secret Chats); Telegram disclaims liability for how bot operators handle data; GDPR representative designated ([telegram.org/privacy](https://telegram.org/privacy) §6, [telegram.org/faq](https://telegram.org/faq)) |

## 5) CONSTRAINTS FOR A LEGAL Q&A BOT

- **Message length:** every bot-sent message is capped at 4096 chars — long statutory excerpts must be chunked, summarized, or delivered as documents (50 MB upload cap via Bot API) ([core.telegram.org/bots/api](https://core.telegram.org/bots/api), [core.telegram.org/bots/faq](https://core.telegram.org/bots/faq)).
- **Multi-turn state:** no server-side sessions; you maintain state keyed by `chat_id` (topic gating, follow-up questions); keep the bot online ≥daily or buffered updates are dropped; threaded-mode topics and streaming replies are supported ([core.telegram.org/bots/api](https://core.telegram.org/bots/api), [core.telegram.org/bots](https://core.telegram.org/bots)).
- **Media / hyperlinks to cited laws:** MarkdownV2/HTML `parse_mode` makes URLs clickable with link previews; attach official-corpus documents (TSJ/Gaceta PDFs) directly via `sendDocument`; escape user-supplied text to avoid formatting injection ([core.telegram.org/bots/api](https://core.telegram.org/bots/api)).
- **Terms of Service for automated legal info:**
  - Telegram's **Terms of Service for Bots** ([telegram.org/tos/bots](https://telegram.org/tos/bots)): bots are operated by third-party **Service Providers who are "solely responsible" for the content, quality and availability** of what their bot delivers; Telegram disclaims liability, and disputes must be pursued exclusively against the bot operator (us). This is favorable for a professional service (we keep control) but means compliance liability sits with us.
  - Main ToS ([telegram.org/tos](https://telegram.org/tos)): prohibits use for activities "recognized as illegal in the majority of countries", violence promotion on public bots/channels, etc.; violations can lead to temporary/permanent bans. A Venezuelan-law Q&A bot is squarely legitimate, but content must avoid promoting illegal acts.
  - Telegram additionally **prohibits data scraping** via its Content Licensing and AI Scraping Terms ([telegram.org/tos](https://telegram.org/tos)) — relevant if the corpus pipeline ever touches scraped Telegram content (our corpus is official law texts, not Telegram data — fine, but document it).
  - Privacy Policy §6: by interacting, users' screen name, username, profile picture and messages flow to the bot developer; users consent via interaction; Telegram states it won't be liable for SP data handling ([telegram.org/privacy](https://telegram.org/privacy) §6). Publish your own privacy/disclaimer notice (e.g. "not legal advice", retention policy, contact) at onboarding via `/start` or description.

## 6) VERDICT

**Overall: YELLOW-to-GREEN — GREEN as a launch/technical channel, YELLOW on reach & regulatory grounds.**

- **GREEN — launching and operating the bot:** no verification or approval queue; token in minutes; free platform; free hosting tiers verified; rich UI primitives for a topic-gated legal assistant (inline keyboards, MarkdownV2 citations, documents, deep links, no conversation window, no per-message fee); rate limits are generous for a professional Q&A workload.
- **YELLOW — reach in Venezuela:** no official Telegram usage figures for Venezuela; WhatsApp's dominance in-country is the comparison baseline (see WhatsApp ticket); and the January 2025 state-ordered ISP block (lifted within ~24h) proves platform availability can be interrupted by government action — a genuine availability risk for a professional service, even if currently unblocked.
- **Recommendation for the feasibility study:** Telegram is a strong **parallel/secondary channel** (same backend, near-zero marginal cost, immediate launch) rather than a primary replacement for WhatsApp in Venezuela. Proceed: build on WhatsApp's ticket as the primary channel, ship a Telegram mirror early to validate demand, and monitor OONI/press for network-level restrictions.

**Launch checklist:**
1. Create org Telegram account → register bot at @BotFather (username ends in `bot`); save token in env vars, never in code ([core.telegram.org/bots/tutorial](https://core.telegram.org/bots/tutorial)).
2. Set `/setdescription` ("What can this bot do?" + disclaimer), `/setabouttext`, `/setcommands`, `/setuserpic`; keep Privacy Mode default ON ([core.telegram.org/bots/features](https://core.telegram.org/bots/features)).
3. Start with **long polling** on a free always-on host (e.g. Cloudflare Workers/Render free), switch to **webhook** (HTTPS, port 443, `secret_token`) when on a cloud host; implement `offset` confirmations ([core.telegram.org/bots/api](https://core.telegram.org/bots/api), [core.telegram.org/bots/faq](https://core.telegram.org/bots/faq)).
4. Build state store keyed by `chat_id`; enforce topic gating with `/start` deep links (`?start=topic_code`) + inline keyboards + `answerCallbackQuery` ([core.telegram.org/bots/features](https://core.telegram.org/bots/features), [core.telegram.org/bots/api](https://core.telegram.org/bots/api)).
5. Respect limits: queue outbound ≤1 msg/s per chat; retry on 429; chunk legal answers ≤4096 chars; send corpus PDFs via `sendDocument` (≤50 MB) ([core.telegram.org/bots/faq](https://core.telegram.org/bots/faq)).
6. Use MarkdownV2/HTML with escaped user input; hyperlink every citation to the official corpus (TSJ/Gaceta) ([core.telegram.org/bots/api](https://core.telegram.org/bots/api)).
7. Publish `t.me/<username>` link + QR on site/profiles; optionally enable inline mode later; add "not legal advice" + privacy notice (Telegram Privacy §6 data flows) ([telegram.org/privacy](https://telegram.org/privacy)).
8. Monitor: `getMe`/`getWebhookInfo`, logs, uptime ≥daily (updates drop after 24h), and OONI/press for network blocks ([api.ooni.io](https://api.ooni.io/api/v1/measurements?probe_cc=VE&domain=telegram.org)).

**Sources verified by direct fetch:** core.telegram.org (bots, tutorial, features, FAQ, API), telegram.org (FAQ, ToS, ToS/Bots, Privacy), datareportal.com (Digital 2025 & 2024 Venezuela), aporrea.org, confirmado.com.ve, OONI public API, developers.cloudflare.com, render.com, docs.railway.com, vercel.com, blog.heroku.com. **Not verifiable headlessly:** NapoleonCat Venezuela Telegram stats (bot-blocked — no figures cited), Sensor Tower Q2 2025 Venezuela report (title surfaced via Google News RSS only), Reuters X-ban article (bot-blocked — omitted).

---

**Summary of work:** Researched purely via web fetch (no files created, no git/GitHub touched): pulled 7 primary Telegram-source pages (API docs, bots FAQ/features/main, tutorial, ToS, ToS-Bots, Privacy, FAQ), DataReportal Venezuela 2024/2025, 5 hosting pricing pages, OONI's public measurements API, and Venezuelan press (aporrea, confirmado) confirming a Jan 10–11, 2025 state-ordered Telegram block that was lifted within ~24h. Produced the full six-part report above with the comparison scaffold, constraints, verdict, and checklist. **Issues encountered:** all general search engines (DDG/Bing/Yahoo/Google-News-redirects) and NapoleonCat/Reuters blocked headless access; mitigated via Google News RSS, direct source fetches, and the OONI API — no unverifiable numbers were reported.