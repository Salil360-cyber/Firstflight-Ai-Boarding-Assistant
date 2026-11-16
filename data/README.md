# Data dictionary (all data simulated)

## sessions.csv: one row per chat with the assistant

| Column | Meaning |
|---|---|
| session_id | Chat ID. `S9xxxxx` IDs are internal test chats |
| user_id | Anonymous user ID. `TEST-n` = project-team tester |
| started_at, ended_at | Chat start and end (local time). Some end times are missing or earlier than the start |
| channel | web, app, whatsapp |
| language | en, hi, ar. Some rows use labels like `EN`, `Hindi`, `Arabic` |
| passenger_type | first_time, returning, unknown |
| route_type | domestic, international |
| topic | check_in, baggage, boarding, id_documents, refunds_changes, special_assistance, add_ons, delays, name_change, other |
| app_version | v1.0 (weeks 1–4), v1.1 (from 5 Oct 2026, released after user testing) |
| turns | Number of passenger messages in the chat |
| first_response_sec | Seconds until the assistant's first reply |
| outcome | resolved_by_ai, handed_to_agent, abandoned |
| handoff_reason | Only for handed_to_agent: live_status, booking_specific, personal_data, not_in_handbook, low_confidence, customer_requested |
| csat | Post-chat rating 1–5, blank if the passenger skipped it. A few values are outside 1–5 |

`sessions_clean.csv` is the same table after cleaning (27,600 rows): duplicates and test chats removed, language labels fixed, out-of-range CSAT blanked, plus `duration_sec` and `pilot_week`. It is the output of `sql/02_clean_view.sql`.

## agent_tickets.csv: one row per chat handed to an agent

| Column | Meaning |
|---|---|
| ticket_id, session_id | Ticket ID and the chat it came from |
| created_at, assigned_at, closed_at | Hand-off time, agent pick-up time, close time (blank if still open) |
| topic, handoff_reason | Copied from the chat |
| agent_handle_min | Agent minutes spent (blank if still open) |
| resolution | resolved, callback_scheduled, escalated, open |

## qa_reviews.csv: human QA of a 6% sample of chats resolved by the assistant

| Column | Meaning |
|---|---|
| review_id, session_id, reviewed_at | Review ID, chat reviewed, review time |
| app_version, language, topic | Copied from the chat |
| verdict | correct, partly_correct, wrong, unsafe |
| issue_type | none, missing_detail, wrong_language_mix, wrong_fee_or_time, guessed_not_in_handbook, asked_personal_data, promised_refund |

## contact_centre_contacts.csv: calls and emails, 10 Aug – 1 Nov 2026

| Column | Meaning |
|---|---|
| contact_id, contact_date | Contact ID and date. Before 7 Sep 2026 = baseline (no assistant) |
| channel | call, email |
| topic, passenger_type | Same categories as the chats |
| handle_min | Agent minutes for the contact |
