-- FirstFlight · Step 4: pilot analysis. Run one query at a time (select it, press F5).
-- Expected results are in answer_key/answer_key.md.

-- Q1. Data issues found while cleaning
SELECT 'raw rows' AS check_name, COUNT(*) AS n FROM sessions_raw
UNION ALL SELECT 'exact duplicate rows', COUNT(*) - (SELECT COUNT(*) FROM (SELECT DISTINCT * FROM sessions_raw) d) FROM sessions_raw
UNION ALL SELECT 'internal test chats', COUNT(DISTINCT session_id) FROM sessions_raw WHERE user_id LIKE 'TEST-%'
UNION ALL SELECT 'language labels to fix', COUNT(*) FROM (SELECT DISTINCT * FROM sessions_raw) d WHERE user_id NOT LIKE 'TEST-%' AND language NOT IN ('en','hi','ar')
UNION ALL SELECT 'CSAT outside 1-5', COUNT(*) FROM (SELECT DISTINCT * FROM sessions_raw) d WHERE user_id NOT LIKE 'TEST-%' AND csat NOT BETWEEN 1 AND 5
UNION ALL SELECT 'missing end time', COUNT(*) FROM (SELECT DISTINCT * FROM sessions_raw) d WHERE user_id NOT LIKE 'TEST-%' AND ended_at IS NULL
UNION ALL SELECT 'end before start', COUNT(*) FROM (SELECT DISTINCT * FROM sessions_raw) d WHERE user_id NOT LIKE 'TEST-%' AND ended_at < started_at
UNION ALL SELECT 'clean chats', COUNT(*) FROM sessions_clean;

-- Q2. How did chats end?
SELECT outcome, COUNT(*) AS chats,
       ROUND(100.0 * COUNT(*) / SUM(COUNT(*)) OVER (), 2) AS pct
FROM sessions_clean GROUP BY outcome ORDER BY chats DESC;

-- Q3. Resolved by AI %, before and after the v1.1 update
SELECT app_version, COUNT(*) AS chats,
       ROUND(100.0 * AVG(CASE WHEN outcome = 'resolved_by_ai' THEN 1 ELSE 0 END), 2) AS resolved_pct
FROM sessions_clean GROUP BY app_version ORDER BY app_version;

-- Q4. Resolved by AI %, by language and version (the Arabic fix)
SELECT language,
       ROUND(100.0 * AVG(CASE WHEN outcome = 'resolved_by_ai' THEN 1 ELSE 0 END) FILTER (WHERE app_version = 'v1.0'), 1) AS v1_0,
       ROUND(100.0 * AVG(CASE WHEN outcome = 'resolved_by_ai' THEN 1 ELSE 0 END) FILTER (WHERE app_version = 'v1.1'), 1) AS v1_1
FROM sessions_clean GROUP BY language ORDER BY language;

-- Q5. Which topics can the assistant handle?
SELECT topic, COUNT(*) AS chats,
       ROUND(100.0 * AVG(CASE WHEN outcome = 'resolved_by_ai' THEN 1 ELSE 0 END), 1) AS resolved_pct
FROM sessions_clean GROUP BY topic ORDER BY resolved_pct;

-- Q6. First-time vs returning passengers
SELECT passenger_type, COUNT(*) AS chats,
       ROUND(100.0 * AVG(CASE WHEN outcome = 'resolved_by_ai' THEN 1 ELSE 0 END), 1) AS resolved_pct,
       ROUND(100.0 * AVG(CASE WHEN outcome = 'abandoned'      THEN 1 ELSE 0 END), 1) AS abandoned_pct
FROM sessions_clean GROUP BY passenger_type ORDER BY passenger_type;

-- Q7. Adoption week by week
SELECT pilot_week, COUNT(*) AS chats,
       ROUND(100.0 * AVG(CASE WHEN outcome = 'resolved_by_ai' THEN 1 ELSE 0 END), 1) AS resolved_pct
FROM sessions_clean GROUP BY pilot_week ORDER BY pilot_week;

-- Q8. Why were chats handed to an agent?
SELECT handoff_reason, COUNT(*) AS chats,
       ROUND(100.0 * COUNT(*) / SUM(COUNT(*)) OVER (), 1) AS pct
FROM sessions_clean WHERE outcome = 'handed_to_agent'
GROUP BY handoff_reason ORDER BY chats DESC;

-- Q9. Customer satisfaction (only real 1-5 answers count)
SELECT outcome, COUNT(csat) AS ratings, ROUND(AVG(csat), 2) AS avg_csat
FROM sessions_clean GROUP BY outcome
UNION ALL
SELECT 'ALL', COUNT(csat), ROUND(AVG(csat), 2) FROM sessions_clean;

-- Q10. Speed: median first reply (seconds) and median chat length
SELECT app_version,
       PERCENTILE_CONT(0.5) WITHIN GROUP (ORDER BY first_response_sec) AS median_first_reply_sec,
       PERCENTILE_CONT(0.5) WITHIN GROUP (ORDER BY duration_sec)       AS median_duration_sec
FROM sessions_clean GROUP BY app_version ORDER BY app_version;

-- Q11. Hand-offs: how long did passengers wait for an agent?
SELECT s.app_version, COUNT(*) AS tickets,
       ROUND(PERCENTILE_CONT(0.5) WITHIN GROUP (ORDER BY EXTRACT(EPOCH FROM t.assigned_at - t.created_at) / 60)::numeric, 2) AS median_wait_min,
       COUNT(*) FILTER (WHERE t.resolution = 'open') AS still_open
FROM agent_tickets t JOIN sessions_clean s USING (session_id)
GROUP BY s.app_version ORDER BY s.app_version;

-- Q12. Quality: were the assistant's own answers right?
SELECT app_version, language, COUNT(*) AS reviews,
       ROUND(100.0 * AVG(CASE WHEN verdict = 'correct' THEN 1 ELSE 0 END), 1) AS correct_pct,
       COUNT(*) FILTER (WHERE verdict = 'unsafe') AS unsafe
FROM qa_reviews GROUP BY app_version, language ORDER BY app_version, language;

-- Q13. Contact centre: contacts per week, before vs late pilot
SELECT CASE WHEN contact_date < DATE '2026-09-07' THEN '1 baseline (4 weeks)'
            WHEN contact_date >= DATE '2026-10-05' THEN '2 pilot weeks 5-8' END AS period,
       ROUND(COUNT(*) / 4.0, 1)           AS contacts_per_week,
       ROUND(SUM(handle_min) / 4 / 60, 1) AS agent_hours_per_week
FROM contact_centre_contacts
WHERE contact_date < DATE '2026-09-07' OR contact_date >= DATE '2026-10-05'
GROUP BY 1 ORDER BY 1;

-- Q14. Time saved: the estimate vs what really came off the agents
WITH base AS (
    SELECT topic, AVG(handle_min) AS avg_min
    FROM contact_centre_contacts WHERE contact_date < DATE '2026-09-07' GROUP BY topic
)
SELECT ROUND(SUM(b.avg_min) / 60, 1) AS estimated_hours_saved_8_weeks
FROM sessions_clean s JOIN base b USING (topic)
WHERE s.outcome = 'resolved_by_ai';
