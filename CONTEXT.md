# Context: lawyer-bot-ve — feasibility study

The context of this effort is a **feasibility study** for a public legal Q&A bot serving Venezuelan lawyers. The map (`/wayfinder`) charts the study's decisions; a later, larger effort will carry implementation.

## Glossary

- **The bot (lawyer-bot-ve)**: a public messaging bot — WhatsApp or Telegram (undecided; the study decides) — that answers questions about Venezuelan law, grounded on official legal texts, for Venezuelan lawyers. Status: being studied, not built.
- **End user**: a Venezuelan lawyer (licensed legal professional) who asks legal questions to the bot. The bot is public; anyone may ask, but the intended audience is lawyers.
- **Legal question**: an in-scope user message — a question about Venezuelan law, any matter (civil, penal, laboral, mercantil, tributario, constitucional, administrativo, familia). The bot answers legal information, not personalized legal advice.
- **Off-topic question**: a user message outside the covered subjects (art, sports, politics, general chat, foreign law, personal matters). The bot must indicate the question is not about the covered subjects and not answer it.
- **Topic gating**: the mechanism that keeps the bot strictly on legal questions about Venezuela — accepting in-scope questions and rejecting off-topic ones. A core requirement of the product.
- **Legal corpus**: the body of authoritative Venezuelan legal texts the bot grounds its answers on. Constrained to **official sources only**: Gaceta Oficial de la República Bolivariana de Venezuela (official gazette), Tribunal Supremo de Justicia (TSJ), Asamblea Nacional.
- **Official source**: a primary, authoritative publisher of Venezuelan law — the Gaceta Oficial, the TSJ, the Asamblea Nacional (as opposed to third-party consolidations like leyesvenezuela.com).
- **Answer format**: the shape of a bot response — direct answer, citation of the applicable article and law (with Gaceta Oficial reference where applicable), caveats, and disclaimer. Undecided; resolved by a grilling ticket.
- **Feasibility study**: the destination of this map — a consolidated document (`docs/feasibility-study.md`) concluding whether the bot is viable, which platform to use, the corpus approach, gating design, and the regulatory risk register. It is preparation for a larger implementation effort.
- **Platform**: the messaging channel the bot runs on — WhatsApp (official Business Platform/Cloud API) or Telegram (Bot API). The study compares and decides.

## Notes for agents

- Issues, PRs, and commits in this repo are written in **English**.
- **Financial amounts never appear on GitHub** (issues, docs, PRs, commits). Qualitative statements only ("free tier", "paid tier").
- The study covers regulatory aspects: Venezuelan data protection law, liability for wrong answers, unauthorized practice, platform terms, sanctions.