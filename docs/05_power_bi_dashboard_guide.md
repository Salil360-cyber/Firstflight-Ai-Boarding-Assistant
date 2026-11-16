# Build guide: FirstFlight adoption KPI dashboard (Power BI)

**Status: to build.** The cleaned data and the expected numbers are ready; the `.pbix` file has not been built yet.

Time needed: about 2 hours. Every number you build can be checked against `analysis/sql_results.md`.

## 1. Load the data

Get Data → Text/CSV, and load these four files from `data/`:

| File | Rows | Use |
|---|---|---|
| `sessions_clean.csv` | 27,600 | One row per chat, already cleaned by `sql/02_clean_view.sql` |
| `agent_tickets.csv` | 8,362 | Chats handed to an agent |
| `qa_reviews.csv` | 1,044 | Human review of AI answers |
| `contact_centre_contacts.csv` | 26,989 | Calls and emails, before and during the pilot |

In Power Query, check that `started_at` is Date/Time, `contact_date` is Date, and `csat`, `turns`, `pilot_week` are whole numbers.

## 2. Relationships (Model view)

- `agent_tickets[session_id]` → `sessions_clean[session_id]` (many to one)
- `qa_reviews[session_id]` → `sessions_clean[session_id]` (many to one)
- `contact_centre_contacts` stays on its own (it is not linked to chats)

## 3. Measures (DAX)

```DAX
Chats = COUNTROWS ( sessions_clean )

Resolved by AI % =
DIVIDE ( CALCULATE ( [Chats], sessions_clean[outcome] = "resolved_by_ai" ), [Chats] )

Hand-off % =
DIVIDE ( CALCULATE ( [Chats], sessions_clean[outcome] = "handed_to_agent" ), [Chats] )

Abandoned % =
DIVIDE ( CALCULATE ( [Chats], sessions_clean[outcome] = "abandoned" ), [Chats] )

Avg CSAT = AVERAGE ( sessions_clean[csat] )

CSAT Response % = DIVIDE ( COUNT ( sessions_clean[csat] ), [Chats] )

QA Reviews = COUNTROWS ( qa_reviews )

QA Correct % =
DIVIDE ( CALCULATE ( [QA Reviews], qa_reviews[verdict] = "correct" ), [QA Reviews] )

Unsafe Answers = CALCULATE ( [QA Reviews], qa_reviews[verdict] = "unsafe" )

Contacts = COUNTROWS ( contact_centre_contacts )

Agent Hours = DIVIDE ( SUM ( contact_centre_contacts[handle_min] ), 60 )
```

Add one calculated column in `contact_centre_contacts` so you can compare before and after:

```DAX
Period =
SWITCH (
    TRUE (),
    contact_centre_contacts[contact_date] < DATE ( 2026, 9, 7 ), "1 Baseline (4 weeks)",
    contact_centre_contacts[contact_date] >= DATE ( 2026, 10, 5 ), "2 Pilot weeks 5-8",
    "Pilot weeks 1-4"
)
```

## 4. Pages

**Page 1: Adoption**
- Cards: Chats, Resolved by AI %, Hand-off %, Abandoned %, Avg CSAT
- Line chart: Chats by `pilot_week`, with Resolved by AI % on the second axis
- Slicers: language, channel, passenger_type, app_version

**Page 2: Where the assistant works and where it does not**
- Bar chart: Resolved by AI % by topic (sorted low to high)
- Clustered bar: Resolved by AI % by language and app_version
- Bar chart: hand-off chats by handoff_reason
- Table: passenger_type with Chats, Resolved by AI %, Abandoned %

**Page 3: Quality and workload**
- Cards: QA Correct %, Unsafe Answers
- Clustered bar: QA Correct % by language and app_version
- Column chart: Contacts ÷ 4 and Agent Hours ÷ 4 by Period (baseline vs pilot weeks 5-8)
- Text box: "Observed saving: about 36 agent hours a week. A simple estimate gives far more, because many people who chat would never have called."

## 5. Check your numbers

| Measure | Expected |
|---|---|
| Chats | 27,600 |
| Resolved by AI % | 63.03% |
| Hand-off % | 30.30% |
| Abandoned % | 6.68% |
| Avg CSAT | 4.15 |
| CSAT Response % | 33.55% |
| Resolved by AI %, v1.0 / v1.1 | 59.16% / 65.36% |
| Resolved by AI %, Arabic, v1.0 / v1.1 | 47.7% / 64.5% |
| QA Correct %, v1.0 / v1.1 | 84.68% / 89.34% |
| Unsafe Answers | 4 |
| Contacts per week, baseline / pilot weeks 5-8 | 2,427.8 / 2,029.3 |
| Agent hours per week, baseline / pilot weeks 5-8 | 243.8 / 207.5 |

If a number is different, the usual causes are a wrong data type, a filter left on, or loading `sessions.csv` (raw) instead of `sessions_clean.csv`.

## 6. What to save in this repo

- `dashboard/FirstFlight_Adoption.pbix`
- One screenshot per page in `screenshots/`
- Then change the status of step 12 in the README to done.
