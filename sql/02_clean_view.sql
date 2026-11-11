-- FirstFlight · Step 3: one clean view of the chats. Every later query uses sessions_clean.
CREATE OR REPLACE VIEW sessions_clean AS
WITH no_dups AS (                        -- 1. exact duplicate rows: keep one
    SELECT DISTINCT * FROM sessions_raw
),
no_tests AS (                            -- 2. drop project-team test chats
    SELECT * FROM no_dups WHERE user_id NOT LIKE 'TEST-%'
)
SELECT
    session_id, user_id, started_at, ended_at, channel,
    CASE LOWER(language)                 -- 3. one spelling per language
        WHEN 'english' THEN 'en' WHEN 'hindi' THEN 'hi' WHEN 'arabic' THEN 'ar'
        ELSE LOWER(language) END                               AS language,
    passenger_type, route_type, topic, app_version, turns, first_response_sec,
    outcome, NULLIF(handoff_reason, '')                        AS handoff_reason,
    CASE WHEN csat BETWEEN 1 AND 5 THEN csat END               AS csat,          -- 4. bad scores -> blank
    CASE WHEN ended_at >= started_at                                              -- 5. only sensible durations
         THEN EXTRACT(EPOCH FROM ended_at - started_at) END    AS duration_sec,
    (started_at::date - DATE '2026-09-07') / 7 + 1             AS pilot_week
FROM no_tests;
