# FirstFlight answer key (simulated pilot data)

Every number below is computed by `scripts/answer_key.py` and cross-checked with DuckDB SQL. Use it to check your SQL, Excel and Power BI results.

## Cleaning log

|                                      |   count |
|:-------------------------------------|--------:|
| raw rows                             |   27830 |
| exact duplicate rows removed         |     140 |
| internal test chats removed          |      90 |
| language labels fixed                |    3267 |
| CSAT out of range set to blank       |      60 |
| missing end time (kept, no duration) |      45 |
| end before start (kept, no duration) |      25 |
| clean chats                          |   27600 |

## Headline KPIs

|                                     |    value |
|:------------------------------------|---------:|
| chats                               | 27600    |
| users                               | 27229    |
| resolved_by_ai_%                    |    63.03 |
| handed_to_agent_%                   |    30.3  |
| abandoned_%                         |     6.68 |
| resolved_v1.0_%                     |    59.16 |
| resolved_v1.1_%                     |    65.36 |
| csat_avg                            |     4.15 |
| csat_response_%                     |    33.55 |
| csat_resolved_avg                   |     4.37 |
| csat_handoff_avg                    |     3.66 |
| median_first_response_sec_v1.0      |     3.2  |
| median_first_response_sec_v1.1      |     2.6  |
| median_duration_sec                 |   102    |
| tickets                             |  8362    |
| tickets_open                        |    78    |
| median_wait_min_v1.0                |     5.95 |
| median_wait_min_v1.1                |     4.57 |
| avg_agent_handle_min                |     5.59 |
| qa_reviews                          |  1044    |
| qa_correct_v1.0_%                   |    84.68 |
| qa_correct_v1.1_%                   |    89.34 |
| qa_unsafe_count                     |     4    |
| contacts_per_week_baseline          |  2427.75 |
| contacts_per_week_pilot_wk5_8       |  2029.25 |
| contact_drop_%                      |    16.41 |
| est_agent_hours_saved               |  1641.98 |
| baseline_avg_handle_min             |     6.03 |
| observed_hours_saved_per_week_wk5_8 |    36.31 |

## Resolved by AI, by topic

| topic              |   chats |   resolved_pct |
|:-------------------|--------:|---------------:|
| other              |     776 |           29.9 |
| special_assistance |     975 |           36.7 |
| refunds_changes    |    3011 |           41.5 |
| name_change        |     717 |           42.3 |
| delays             |    2453 |           45.4 |
| id_documents       |    2990 |           59.9 |
| baggage            |    5889 |           70.8 |
| add_ons            |    2077 |           71.7 |
| boarding           |    3013 |           76.6 |
| check_in           |    5699 |           76.8 |

## Resolved by AI %, by language and version

| language   |   v1.0 |   v1.1 |
|:-----------|-------:|-------:|
| ar         |   47.7 |   64.5 |
| en         |   62.3 |   66.2 |
| hi         |   56.5 |   63.6 |

## By passenger type

| passenger_type   |   chats |   resolved_pct |   abandoned_pct |
|:-----------------|--------:|---------------:|----------------:|
| first_time       |   11680 |           62.3 |             8.2 |
| returning        |   13742 |           63.4 |             5.6 |
| unknown          |    2178 |           64.9 |             5.3 |

## Adoption by week

|   week |   chats |   resolved_pct |
|-------:|--------:|---------------:|
|      1 |    1800 |           58.1 |
|      2 |    2400 |           60   |
|      3 |    2900 |           60   |
|      4 |    3300 |           58.5 |
|      5 |    3700 |           65.6 |
|      6 |    4100 |           65.1 |
|      7 |    4500 |           65   |
|      8 |    4900 |           65.7 |

## Why chats were handed to an agent (%)

| handoff_reason     |   pct |
|:-------------------|------:|
| low_confidence     |  29.5 |
| booking_specific   |  22.7 |
| customer_requested |  17.8 |
| not_in_handbook    |  12.4 |
| live_status        |   9.8 |
| personal_data      |   7.8 |

## QA: correct answers %, by language and version

| language   |   v1.0 |   v1.1 |
|:-----------|-------:|-------:|
| ar         |   61.3 |   80.2 |
| en         |   88.8 |   91.4 |
| hi         |   81.4 |   88.4 |

## Definitions

- **Resolved by AI %** (containment / automation rate): chats the assistant answered without an agent ÷ all clean chats.
- **Estimated agent hours saved**: each chat resolved by AI × the average handle time for that topic in the 4 baseline weeks, ÷ 60. This assumes every resolved chat would otherwise have been one contact, so it is an upper estimate.
- **Observed hours saved per week**: contact-centre handle hours per week in the baseline minus pilot weeks 5–8. This is what actually came off the agents' workload, and it is much smaller than the estimate above: many people who chat would never have called. Report both, and lead with the observed number.
- **Contact drop %**: contacts per week in pilot weeks 5–8 vs the 4 baseline weeks.
- Duration figures leave out chats with a missing or impossible end time; all other figures keep them.