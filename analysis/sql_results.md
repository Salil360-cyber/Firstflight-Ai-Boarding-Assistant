# FirstFlight: SQL analysis results (simulated pilot data)

These are the actual outputs of `sql/03_analysis.sql`, run in **PostgreSQL 16** on the four CSV files in `data/` after `sql/01_create_tables.sql` and `sql/02_clean_view.sql`. All data is simulated; SaffronSky Air is a fictional airline.

Every figure matches `answer_key/answer_key.md`.

## Q1. Data issues found while cleaning

| check_name | n |
|---|---|
| raw rows | 27830 |
| exact duplicate rows | 140 |
| internal test chats | 90 |
| language labels to fix | 3267 |
| CSAT outside 1-5 | 60 |
| missing end time | 45 |
| end before start | 25 |
| clean chats | 27600 |

## Q2. How did chats end?

| outcome | chats | pct |
|---|---|---|
| resolved_by_ai | 17395 | 63.03 |
| handed_to_agent | 8362 | 30.30 |
| abandoned | 1843 | 6.68 |

## Q3. Resolved by AI %, before and after the v1.1 update

| app_version | chats | resolved_pct |
|---|---|---|
| v1.0 | 10400 | 59.16 |
| v1.1 | 17200 | 65.36 |

## Q4. Resolved by AI %, by language and version (the Arabic fix)

| language | v1_0 | v1_1 |
|---|---|---|
| ar | 47.7 | 64.5 |
| en | 62.3 | 66.2 |
| hi | 56.5 | 63.6 |

## Q5. Which topics can the assistant handle?

| topic | chats | resolved_pct |
|---|---|---|
| other | 776 | 29.9 |
| special_assistance | 975 | 36.7 |
| refunds_changes | 3011 | 41.5 |
| name_change | 717 | 42.3 |
| delays | 2453 | 45.4 |
| id_documents | 2990 | 59.9 |
| baggage | 5889 | 70.8 |
| add_ons | 2077 | 71.7 |
| boarding | 3013 | 76.6 |
| check_in | 5699 | 76.8 |

## Q6. First-time vs returning passengers

| passenger_type | chats | resolved_pct | abandoned_pct |
|---|---|---|---|
| first_time | 11680 | 62.3 | 8.2 |
| returning | 13742 | 63.4 | 5.6 |
| unknown | 2178 | 64.9 | 5.3 |

## Q7. Adoption week by week

| pilot_week | chats | resolved_pct |
|---|---|---|
| 1 | 1800 | 58.1 |
| 2 | 2400 | 60.0 |
| 3 | 2900 | 60.0 |
| 4 | 3300 | 58.5 |
| 5 | 3700 | 65.6 |
| 6 | 4100 | 65.1 |
| 7 | 4500 | 65.0 |
| 8 | 4900 | 65.7 |

## Q8. Why were chats handed to an agent?

| handoff_reason | chats | pct |
|---|---|---|
| low_confidence | 2469 | 29.5 |
| booking_specific | 1899 | 22.7 |
| customer_requested | 1485 | 17.8 |
| not_in_handbook | 1036 | 12.4 |
| live_status | 819 | 9.8 |
| personal_data | 654 | 7.8 |

## Q9. Customer satisfaction (only real 1-5 answers count)

| outcome | ratings | avg_csat |
|---|---|---|
| ALL | 9260 | 4.15 |
| resolved_by_ai | 6668 | 4.37 |
| abandoned | 146 | 2.36 |
| handed_to_agent | 2446 | 3.66 |

## Q10. Speed: median first reply (seconds) and median chat length

| app_version | median_first_reply_sec | median_duration_sec |
|---|---|---|
| v1.0 | 3.2 | 104 |
| v1.1 | 2.6 | 101 |

## Q11. Hand-offs: how long did passengers wait for an agent?

| app_version | tickets | median_wait_min | still_open |
|---|---|---|---|
| v1.0 | 3539 | 5.95 | 0 |
| v1.1 | 4823 | 4.57 | 78 |

## Q12. Quality: were the assistant's own answers right?

| app_version | language | reviews | correct_pct | unsafe |
|---|---|---|---|---|
| v1.0 | ar | 31 | 61.3 | 2 |
| v1.0 | en | 242 | 88.8 | 0 |
| v1.0 | hi | 86 | 81.4 | 1 |
| v1.1 | ar | 81 | 80.2 | 0 |
| v1.1 | en | 440 | 91.4 | 1 |
| v1.1 | hi | 164 | 88.4 | 0 |

## Q13. Contact centre: contacts per week, before vs late pilot

| period | contacts_per_week | agent_hours_per_week |
|---|---|---|
| 1 baseline (4 weeks) | 2427.8 | 243.8 |
| 2 pilot weeks 5-8 | 2029.3 | 207.5 |

## Q14. Time saved: the estimate vs what really came off the agents

| estimated_hours_saved_8_weeks |
|---|
| 1642.0 |

## What the results say

- **Cleaning matters.** 230 rows were removed (140 exact duplicates, 90 internal test chats) and 3,267 language labels were fixed before any KPI was calculated.
- **63.0% of chats were resolved by the assistant** without an agent; 30.3% were handed to an agent and 6.7% were abandoned.
- **The v1.1 update helped most in Arabic:** resolved chats rose from 47.7% to 64.5%, against 62.3% to 66.2% in English.
- **The assistant is strong on simple rules** (check-in 76.8%, boarding 76.6%) and weak where a booking has to be looked up (refunds and changes 41.5%, special assistance 36.7%).
- **First-time flyers give up more often:** 8.2% abandoned, against 5.6% for returning passengers.
- **Report the observed saving, not the estimate.** Counting every resolved chat as an avoided contact gives about 1,642 agent hours over 8 weeks (about 205 a week over the whole pilot). The contact centre's own hours fell by only 36.3 a week (243.8 to 207.5), because many people who chat would never have called.
