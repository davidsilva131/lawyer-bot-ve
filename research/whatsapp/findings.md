#  — Findings

Research for ticket # (wayfinder map #1, repo lawyer-bot-ve). Researched 2026-08-16 by an AFK subagent; verified via primary-source fetches.

# WhatsApp Business Platform (Cloud API) for a Venezuelan Legal Q&A Bot — Feasibility Research

**Method note.** Meta's developer docs and many search engines block direct fetching from this IP. Claims below are graded: **[verified]** = page body fetched and text extracted; **[snippet]** = content confirmed via multiple search-result excerpts of the linked page; **[unverified]** = not confirmable from this session — re-verify against the linked URL. No monetary amounts appear anywhere in this report, per the task rules.

---

## 1. REQUIREMENTS — what it takes to go live

**Business Manager + WABA + verification**
- You need a Meta Business Manager (Business Portfolio), a WhatsApp Business Account (WABA), a registered business phone number, and business verification to unlock the full WhatsApp Business Platform (higher messaging limits, display-name approval, unscaled access). [verified] https://docs.360dialog.com/docs/resources/meta-business-verification
- Verification requires uploading official documents proving the business is legally registered; Meta publishes a country-specific list of accepted documents (e.g., registration certificates, VAT certificates, utility bills). Allied/EMEA examples are listed; the Americans-latam list exists on the same doc (Venezuela-specific accepted documents were not visible in the fetched text — confirm in Meta Business Help). [verified][unverified] https://docs.360dialog.com/docs/resources/meta-business-verification
- Three verification paths exist: standard verification from the Security Centre; **Partner-led Business Verification (PLBV)** offered by BSPs, described as the fastest path with "full WhatsApp API capabilities from day one"; and Meta Verified for Business (paid subscription). [verified] https://docs.360dialog.com/docs/resources/meta-business-verification — Typical review duration is not documented in a page I could fetch; plan for days-to-weeks on standard flow, same-day on PLBV [unverified].

**Phone number**
- The number must be able to receive the verification code (SMS or voice call); Meta's canonical reference is "Add a Phone Number" in the Cloud API docs. [snippet] https://developers.facebook.com/docs/whatsapp/cloud-api/get-started/add-a-phone-number/
- Virtual/VoIP numbers are officially unsupported for the consumer Business App, which requires a real mobile number for verification. [verified] https://www.aancall.com/blogs/post/whatsapp-business-voip-guide
- **Venezuelan +58 numbers are not blocked** — Venezuela is listed in the WhatsApp Business Platform supported-countries list with code (+58)/VE [verified] https://docs.verihubs.com/docs/whatsapp-business-supported-countries, and full coexistence (API + app on one number) is available in Venezuela [verified] https://chakrahq.com/product/whatsapp/tools/whatsapp-coexistence-support/
- A number previously used with the WhatsApp consumer app can be migrated; a dedicated number is recommended for API use. Coexistence support (same number in app + API) exists and is available in Venezuela (above). Prepare the number in advance — it must receive SMS/call at registration time. [snippet] https://developers.facebook.com/docs/whatsapp/cloud-api/get-started/add-a-phone-number/

**Display name & templates**
- Every business phone number gets a display name that goes through Meta's review "to ensure it accurately represents the business" — common cause of onboarding delays/rejections; there is an approval/review/appeal process. [snippet] https://api.support.vonage.com/hc/en-us/articles/28025720168988-WhatsApp-Display-Name-Approval-Review-Appeal-Process
- **Message templates are mandatory for any outbound message outside an open customer-service window**, and template approvals are a separate Meta review track. [verified] https://www.twilio.com/docs/whatsapp/key-concepts — For a legal bot you'd need approved templates for the first outbound greeting/opt-in and notifications (e.g., case updates); Q&A content itself is delivered free-form inside the 24-hour window.

**Cloud API vs On-Premises**
- The On-Premises API is **sunset**: "The final supported version of the On-Premises API client expired on October 23, 2025. On-Premises API can't be used to send messages to WhatsApp users anymore. Please use Cloud API." [snippet] https://developers.facebook.com/docs/whatsapp/on-premises/sunset/ — Meta's Business Help: migrate assets to Cloud API by October 23, 2025. [snippet] https://business.facebook.com/business/help/1521430862013620/
- Cloud API is Meta-hosted (no servers to run) and was launched as free hosting — "It is also free"; business messaging is billed separately. [verified] https://techcrunch.com/2022/05/19/whatsapp-ramps-up-revenue-with-global-launch-of-cloud-api-and-soon-a-paid-tier-for-its-business-app/

---

## 2. VENEZUELA-SPECIFIC — sanctions and availability

**Meta/WhatsApp policy**
- WhatsApp's official restricted-country list for the Business Platform is only: **Ukraine (Crimea, Donetsk, Luhansk), Cuba, Iran, North Korea, Syria** (plus a few carrier/coexistence exceptions: Turkey, Kosovo). **Venezuela is NOT restricted.** [verified] https://api.support.vonage.com/hc/en-us/articles/4406453102868-What-are-the-country-restrictions-for-sending-or-receiving-messages-with-the-WhatsApp-Business-Platform (links to Meta's own doc https://developers.facebook.com/docs/whatsapp/cloud-api/support/#country-restrictions)
- Twilio corroborates: blocked countries are Crimea (+7978), Cuba (+53), Iran (+98), North Korea (+850), Syria (+963); "WhatsApp does not allow businesses in these countries to take advantage of WhatsApp" — no mention of Venezuela; business numbers can reach users in every supported country. [verified] https://support.twilio.com/hc/en-us/articles/360051177134-What-countries-can-I-reach-with-the-Twilio-API-for-WhatsApp
- **Conclusion: a Venezuelan business may legally operate a WABA and Venezuelan (+58) users may use it.** No Meta policy document blocking Venezuela was found.

**US OFAC sanctions context**
- The U.S. Venezuela sanctions program exists and is target-based: it blocks the Government of Venezuela and listed/SDN persons, and sanctions sectors (oil, gold, certain state entities) — governed by EO 13884 and 31 CFR Part 591. [verified] https://ofac.treasury.gov/sanctions-programs-and-country-information/venezuela-related-sanctions
- Crucially, OFAC has **expressly authorized communications/internet services**: General License 25 authorizes "Exportation of Certain Services, Software, Hardware, and Technology Incident to the Exchange of Communications over the Internet," and GL 24A (June 2026) authorizes telecom/mail-related transactions with the Government of Venezuela. A messaging SaaS/bot is squarely the kind of activity these licenses contemplate. [verified] (same OFAC page)
- 2025 secondary-tariff policy (25% tariff threat on countries importing Venezuelan oil) is oil-trade policy, not a services embargo, and does not prohibit software/communications services. [snippet] https://www.federalregister.gov/documents/2025/03/27/2025-05424/imposing-tariffs-on-countries-importing-venezuelan-oil
- **Residual compliance notes [unverified] (check with counsel):** OFAC SDN/51% rule screening of counterparties; U.S.-person restrictions apply to the operator if the operator is U.S.-based; Meta billing/payment rails for a Venezuelan company (local credit card acceptance for Meta Business billing) was not verifiable this session — this is the single most practical unknown.

---

## 3. REACH — WhatsApp in Venezuela

- Internet penetration in Venezuela ≈ 61.6% of population, ~17.5M internet users (January 2025, per DataReportal's Global Digital Report as aggregated by Guayoyo Marketing — DataReportal's own page loads numbers via JavaScript and could not be parsed here). [snippet] https://datareportal.com/reports/digital-2025-venezuela ; [snippet] https://guayoyomarketing.co/... (aggregator of the same report)
- WhatsApp usage in Latin America is the top messaging platform globally with ~2B monthly active users (February 2025) as reported by Statista's WhatsApp usage tracker. [snippet] https://www.statista.com/statistics/291540/mobile-internet-user-in-venezuela/ (Statista's WhatsApp usage-in-selected-countries 2025 report: https://www.statista.com/topics/1133/whatsapp/)
- **Professional/legal-sector evidence:** Venezuelan products already sell "WhatsApp for law firms" in-country — e.g., WatX (Venezuelan) markets WhatsApp legal-comms software with "a bot that answers case-status queries 24/7" for law firms [snippet] https://watx.app/para/abogados; Venezuelan legal directories publish lawyer contacts on WhatsApp [snippet] https://www.directoriopro.com/; Venezuelan law firms advertise WhatsApp as their primary client channel [snippet] https://bohorquesasociados.ve/ — strong indication Venezuelan lawyers (and their clients) live on WhatsApp. (ENCOVI survey data on messaging usage is a good next source: https://encovi.ucab.edu.ve/ — unreachable from this IP.)

---

## 4. COST STRUCTURE (qualitative only — no figures anywhere)

- **Cloud API hosting: free.** Meta hosts the API; businesses "pay WhatsApp on a per-message basis, with rates that vary based on the region." [verified] https://techcrunch.com/2022/05/19/whatsapp-ramps-up-revenue-with-global-launch-of-cloud-api-and-soon-a-paid-tier-for-its-business-app/
- **Conversation-based pricing:** billing is per 24-hour conversation (user-initiated vs business-initiated categories), with **free service-conversation allowances** below a threshold and paid tiers above it; a **free tier** exists for low volumes. Current policy pages: https://developers.facebook.com/docs/whatsapp/pricing (blocked this session; community threads report 2026 pricing changes — [unverified] https://www.reddit.com/r/WhatsappBusinessAPI/comments/1rjmnui/whatsapp_api_rate_changes_coming_april_1_2026/)
- **Service-provider fees:** BSPs (360dialog, Twilio, Vonage, Wati, etc.) layer their own subscription/usage fees on top of Meta's platform cost — "each WhatsApp Business channel generates two primary categories of costs" (Meta platform cost + provider). [verified] https://docs.360dialog.com/docs/get-started/pricing
- Practical takeaway: at lawyer-bot scale (hundreds–thousands of conversations/month) expect: provider subscription + Meta per-conversation charges once free allowances are exceeded; no server cost with Cloud API. Re-verify current thresholds on the pricing doc before committing.

---

## 5. CONSTRAINTS for a legal Q&A bot

- **24-hour customer-service window (the big one):** a user's inbound message opens a 24-hour window during which the bot may send FREE-FORM messages; "outside of a customer service window, you may only send a message using an approved template." [verified] https://www.twilio.com/docs/whatsapp/key-concepts
  - Implication: a public legal Q&A bot works well — the lawyer/user initiates, and the bot's full interactive session happens inside that window. But if the user goes quiet >24h, the bot cannot proactively continue without a template (and templates can't be dynamic free-form legal advice). Design for: user-initiated sessions, a template-based follow-up/nudge, and sessions capped to one window.
- **Template approval:** all outbound-window messaging needs Meta-approved templates; legal-content templates may draw extra review. Templates are per-category with statuses (approved/pending/rejected). [snippet] https://www.twilio.com/docs/whatsapp/key-concepts ; template-count limits exist per WABA [snippet] https://respond.io/help/whatsapp/whatsapp-message-templates
- **Messaging limits / rate limits:** "messaging limits are the maximum number of unique WhatsApp user phone numbers your business can deliver messages to, outside of a customer service window, within a moving 24-hour period" — [snippet] https://developers.facebook.com/documentation/business-messaging/whatsapp/messaging-limits/ ; throughput defaults at **80 messages/second per phone number**, upgradeable (up to ~1,000 MPS) when eligible [snippet] https://www.wati.io/en/blog/whatsapp-api-rate-limits/ ; [snippet] https://help.salesforce.com/s/articleView?id=000396933 — irrelevant at bot scale, but plan queuing/retry logic anyway.
- **Media:** document/audio/image support exists for send/receive (relevant for legal-document exchange); link-based rich messaging via templates. [unverified] — see https://developers.facebook.com/docs/whatsapp/cloud-api/messages/media
- **Multi-agent / scale:** a single number supports one bot session at a time per user; Multi-Agent API exists for routing conversations across multiple agents on one number — confirm details against Meta docs [unverified] https://developers.facebook.com/docs/whatsapp/cloud-api — for a bot answering concurrent Venezuelan lawyers, plan a queue + the 24h window carefully.
- **Unofficial libraries** (Baileys, whatsapp-web.js) exist and violate WhatsApp ToS, risking permanent number bans — **not recommended and out of scope** for this feasibility study.
- **WABA health:** restricted/banned WABAs are a real failure mode — monitor WABA status via Business Support Home. [snippet] https://support.wati.io/en/articles/11463204-how-to-check-whatsapp-business-account-waba-status

---

## 6. VERDICT

### 🟢 GREEN for feasibility — with a YELLOW operational checklist

| Axis | Assessment | Why |
|---|---|---|
| Sanctions/availability | 🟢 Green | Venezuela is an officially supported country; restricted list excludes it; OFAC program is targeted (GoV/SDN/oil/gold) with explicit licenses for internet-communications services (GL 25, GL 24A) |
| Reach | 🟢 Green | ~17.5M internet users (61.6% penetration, 2025); WhatsApp is the dominant professional channel in Venezuela; local "WhatsApp for law firms" products already exist |
| Platform fit | 🟢 Green | Cloud API is the only supported path (on-prem dead since Oct 23, 2025); free hosting; user-initiated conversations fit a public legal Q&A bot model |
| Cost | 🟡 Yellow | Free tier + free hosting exist; above-threshold conversation pricing + BSP fees — needs a volume projection and current pricing re-check |
| Onboarding friction | 🟡 Yellow | Business verification + display name + templates are Meta-reviewed; virtual-number verification risk; Meta billing/payment rails for a Venezuelan entity unverified |

**Bottom line:** the blocker risks for this specific use case (sanctions, availability, reach) all clear. The remaining risks are operational: completing business verification with Venezuelan documents, securing a +58 number able to receive the verification SMS/call, getting Meta billing set up from Venezuela, and designing the bot around the 24-hour window. If the payment rails question resolves positively, this is a go.

### Concrete signup checklist
1. Create Meta Business Manager / Business Portfolio; add the business and its documents. [snippet] https://business.facebook.com/
2. Apply for business verification (Security Centre) or use a BSP's Partner-Led Business Verification (fastest; full API capabilities from day one). [verified] https://docs.360dialog.com/docs/resources/meta-business-verification
3. Acquire a dedicated **mobile (+58) number** able to receive SMS/voice (avoid VoIP/virtual-first attempts; virtual numbers are officially unsupported for verification). [verified] https://www.aancall.com/blogs/post/whatsapp-business-voip-guide
4. Create the WABA (via Embedded Signup/360dialog/Twilio/Vonage or the Graph API), link a Facebook Page, and register the phone number; verify the number via SMS/call. [snippet] https://developers.facebook.com/docs/whatsapp/cloud-api/get-started/add-a-phone-number/
5. Submit a display name matching the registered business name; wait for approval (prep an appeal path). [snippet] https://api.support.vonage.com/hc/en-us/articles/28025720168988-WhatsApp-Display-Name-Approval-Review-Appeal-Process
6. Create and submit required message templates (greeting/opt-in, case-update notifications) and await Meta approval. [verified] https://www.twilio.com/docs/whatsapp/key-concepts
7. Add a payment method for Meta's per-conversation billing; confirm a Venezuelan payment method works — if not, evaluate a BSP that invoices from abroad. [unverified]
8. Implement against Cloud API: webhook-driven replies, 24h-window session design, template fallback, message queuing within the 80 msg/sec throughput. [snippet] https://developers.facebook.com/docs/whatsapp/cloud-api/get-started/
9. Screen counterparties against OFAC SDN/51%-rule lists if the bot ever handles business with listed Venezuelan persons/entities — standard compliance hygiene. [verified] https://ofac.treasury.gov/sanctions-programs-and-country-information/venezuela-related-sanctions
10. Monitor WABA status and template health from Business Support Home post-launch. [snippet] https://support.wati.io/en/articles/11463204-how-to-check-whatsapp-business-account-waba-status

---

### Source index (all URLs cited inline above)
Meta: On-Premises sunset • Business Help migration • Cloud API get-started / add-a-phone-number • messaging-limits • country-restrictions • pricing — Twilio (key-concepts, country support) • Vonage (restrictions, display name) • VeriHubs (supported countries) • Chakra (coexistence) • 360dialog (verification, pricing) • Aancall (VoIP) • TechCrunch (Cloud API launch) • OFAC (Venezuela program) • Federal Register (secondary tariffs) • DataReportal (Digital 2025 Venezuela) • Statista (WhatsApp usage) • WatX / DirectorioPro (Venezuelan legal-sector usage)

**Caveats to carry into the ticket:** several Meta pages (pricing, add-a-phone-number, messaging-limits, multi-agent) were confirmed only via search excerpts — re-verify at the exact URLs above before final sign-off on the feasibility study.