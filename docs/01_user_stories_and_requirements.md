# FirstFlight: user stories and functional requirements

Fictional airline (SaffronSky Air), simulated data. Rule numbers such as P3.2 refer to `policy/SaffronSky_Air_Passenger_Policy.md`.

## Problem

First-time flyers are about half as satisfied as returning passengers (24.0% vs 50.6% in the Cabin Pressure analysis), and online boarding is the biggest driver of satisfaction. Before the pilot the contact centre handled about 2,428 contacts a week at about 6 minutes each, many of them simple rule questions.

## Goal

Give passengers a correct answer to check-in, baggage and boarding questions in English, Hindi or Arabic within seconds, and pass anything the assistant cannot safely answer to a human agent.

## Users

| User | What they need |
|---|---|
| First-time flyer | Simple, step-by-step answers in their own language |
| Returning passenger | A fast answer without calling |
| Contact-centre agent | Fewer simple questions; a clear note when a chat is handed over |
| QA reviewer / analyst | A way to check answer quality and track KPIs each week |

## In scope / out of scope

| In scope | Out of scope |
|---|---|
| Questions answered by the policy handbook (P1 to P10) | Looking up, changing or cancelling a booking (P11.2) |
| English, Hindi, Arabic | Live flight status (P10.4) |
| Hand-off to an agent with a logged request | Taking payments or personal documents (P11.1) |
| Chat rating (1 to 5) and weekly QA sample | Visa advice (P5.3) |

## User stories

| ID | As a... | I want to... | So that... | Acceptance criteria |
|---|---|---|---|---|
| US-01 | first-time flyer | ask when web check-in opens and closes | I do not miss it | Says 48 hours before; closes 60 minutes before (domestic) or 3 hours before (international) (P3) |
| US-02 | passenger | ask my baggage allowance | I avoid airport fees | Gives 7 kg cabin bag plus 3 kg personal item, and the checked allowance for the fare type (P1, P2.1) |
| US-03 | passenger | ask in Hindi or Arabic | I understand the answer | Replies fully in the language of the question, with no language mixing |
| US-04 | international passenger | know which documents I need | I am not refused at the counter | Says passport valid 6 months plus visa or entry permit, and that a counter document check is still needed (P5.2, P3.2) |
| US-05 | passenger | ask to change or cancel my booking | I know what it costs | Explains the fee for the fare type, then offers an agent because it cannot change a booking (P1, P11.2) |
| US-06 | passenger | ask if my flight is delayed | I know what to do | Says it cannot see live status, points to the website or app, and explains delay rights (P10) |
| US-07 | passenger | be stopped from sharing my passport or card number | my data stays safe | Does not ask for or repeat personal data and explains why (P11.1) |
| US-08 | passenger | get an honest "I don't know" | I am not given a wrong answer | If the answer is not in the handbook it says so and offers an agent (P11.3) |
| US-09 | agent | receive a hand-off with topic, reason and language | I do not ask the passenger to repeat everything | Each hand-off creates one log row and one email with those fields |
| US-10 | QA reviewer | review a sample of AI answers each week | wrong or unsafe answers are found early | 6% of resolved chats are reviewed and marked correct, partly correct, wrong or unsafe |
| US-11 | analyst | see adoption and resolution KPIs by week | I can report whether the assistant is working | Dashboard shows chats, resolved %, hand-off %, CSAT and contact-centre volume |

## Functional requirements

| ID | Requirement | From |
|---|---|---|
| FR-01 | Answer only from the policy handbook; never invent a fee, time or rule | US-01, US-02, US-08 |
| FR-02 | Detect the passenger's language (en, hi, ar) and reply in that language only | US-03 |
| FR-03 | Ask "domestic or international?" when the rule differs and the passenger has not said | US-01, US-04 |
| FR-04 | Never request or store passport, Aadhaar, card numbers or OTPs | US-07 |
| FR-05 | Hand off when the request is booking-specific, needs live status, is not in the handbook, or the passenger asks for a person | US-05, US-06, US-08 |
| FR-06 | On hand-off, record date, language, topic, reason and a short summary | US-09 |
| FR-07 | Ask for a 1 to 5 rating at the end of each chat | US-11 |
| FR-08 | Keep a log of each chat's topic, outcome and version for analysis | US-10, US-11 |

## Other requirements

- **Speed:** first reply within 5 seconds (pilot median: 3.2 s in v1.0, 2.6 s in v1.1).
- **Accuracy:** at least 85% of reviewed answers marked correct; zero unsafe answers is the target (pilot: 84.7% then 89.3% correct, 4 unsafe in 1,044 reviews).
- **Human review:** any policy change must be checked by a person before the assistant uses it.

## How success is measured

| KPI | Definition | Pilot result (simulated) |
|---|---|---|
| Resolved by AI % | Chats answered without an agent ÷ all chats | 63.0% |
| Hand-off % | Chats passed to an agent ÷ all chats | 30.3% |
| Abandoned % | Chats the passenger left ÷ all chats | 6.7% |
| CSAT | Average 1 to 5 rating | 4.15 |
| QA correct % | Reviewed answers marked correct | 84.7% then 89.3% |
| Contact-centre volume | Contacts per week vs the 4 baseline weeks | 16.4% lower in weeks 5 to 8 |
