"""FirstFlight answer key: cleans the raw pilot data and computes every KPI, twice.

1. pandas computes the cleaning results and KPIs.
2. DuckDB SQL computes the headline KPIs again, independently, straight from the raw CSVs.
The two must match or the script stops. Results go to answer_key/answer_key.md and answer_key/kpis.csv.
Run: python scripts/answer_key.py
"""
from pathlib import Path
import duckdb
import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
DATA, KEY = ROOT / "data", ROOT / "answer_key"
LANG = {"en": "en", "EN": "en", "English": "en", "hi": "hi", "HI": "hi", "Hindi": "hi", "ar": "ar", "AR": "ar", "Arabic": "ar"}
PILOT_START = pd.Timestamp("2026-09-07")

# ================================================================ pandas
raw = pd.read_csv(DATA / "sessions.csv", dtype={"csat": "Int64"})
log = {}
log["raw rows"] = len(raw)
s = raw.drop_duplicates()
log["exact duplicate rows removed"] = len(raw) - len(s)
test = s.user_id.str.startswith("TEST-")
log["internal test chats removed"] = int(test.sum())
s = s[~test].copy()
assert s.session_id.is_unique
log["language labels fixed"] = int((~s.language.isin(["en", "hi", "ar"])).sum())
s["language"] = s.language.map(LANG)
assert s.language.notna().all()
bad = s.csat.notna() & ~s.csat.between(1, 5)
log["CSAT out of range set to blank"] = int(bad.sum())
s.loc[bad, "csat"] = pd.NA
s["started_at"] = pd.to_datetime(s.started_at)
s["ended_at"] = pd.to_datetime(s.ended_at)
s["duration_sec"] = (s.ended_at - s.started_at).dt.total_seconds()
log["missing end time (kept, no duration)"] = int(s.ended_at.isna().sum())
neg = s.duration_sec < 0
log["end before start (kept, no duration)"] = int(neg.sum())
s.loc[neg, "duration_sec"] = np.nan
log["clean chats"] = len(s)

# check the cleaning against the planted-issue list
pl = pd.read_csv(KEY / "planted_issues.csv")
cnt = pl.issue.value_counts()
assert cnt["duplicate_row"] == log["exact duplicate rows removed"]
assert cnt["internal_test"] == log["internal test chats removed"]
assert cnt["language_label"] == log["language labels fixed"]
assert cnt["csat_out_of_range"] == log["CSAT out of range set to blank"]
assert cnt["missing_end_time"] == log["missing end time (kept, no duration)"]
assert cnt["end_before_start"] == log["end before start (kept, no duration)"]
assert log["clean chats"] == 27600

s["week"] = ((s.started_at.dt.normalize() - PILOT_START).dt.days // 7 + 1).astype(int)
ai = s.outcome.eq("resolved_by_ai")
k = {}
k["chats"] = len(s)
k["users"] = s.user_id.nunique()
k["resolved_by_ai_%"] = ai.mean() * 100
k["handed_to_agent_%"] = s.outcome.eq("handed_to_agent").mean() * 100
k["abandoned_%"] = s.outcome.eq("abandoned").mean() * 100
k["resolved_v1.0_%"] = ai[s.app_version == "v1.0"].mean() * 100
k["resolved_v1.1_%"] = ai[s.app_version == "v1.1"].mean() * 100
k["csat_avg"] = s.csat.astype(float).mean()
k["csat_response_%"] = s.csat.notna().mean() * 100
k["csat_resolved_avg"] = s.loc[ai, "csat"].astype(float).mean()
k["csat_handoff_avg"] = s.loc[s.outcome == "handed_to_agent", "csat"].astype(float).mean()
k["median_first_response_sec_v1.0"] = s.loc[s.app_version == "v1.0", "first_response_sec"].median()
k["median_first_response_sec_v1.1"] = s.loc[s.app_version == "v1.1", "first_response_sec"].median()
k["median_duration_sec"] = s.duration_sec.median()

by_topic = s.groupby("topic").agg(chats=("session_id", "size"), resolved_pct=("outcome", lambda x: (x == "resolved_by_ai").mean() * 100)).sort_values("resolved_pct")
by_lang_ver = s.pivot_table(index="language", columns="app_version", values="outcome", aggfunc=lambda x: (x == "resolved_by_ai").mean() * 100)
by_ptype = s.groupby("passenger_type").agg(chats=("session_id", "size"), resolved_pct=("outcome", lambda x: (x == "resolved_by_ai").mean() * 100),
                                            abandoned_pct=("outcome", lambda x: (x == "abandoned").mean() * 100))
by_week = s.groupby("week").agg(chats=("session_id", "size"), resolved_pct=("outcome", lambda x: (x == "resolved_by_ai").mean() * 100))
handoff_reasons = s[s.outcome == "handed_to_agent"].handoff_reason.value_counts(normalize=True).mul(100)

# tickets
t = pd.read_csv(DATA / "agent_tickets.csv", parse_dates=["created_at", "assigned_at", "closed_at"])
assert set(t.session_id) <= set(s.session_id) and len(t) == (s.outcome == "handed_to_agent").sum()
t["wait_min"] = (t.assigned_at - t.created_at).dt.total_seconds() / 60
t = t.merge(s[["session_id", "app_version"]], on="session_id")
k["tickets"] = len(t)
k["tickets_open"] = int((t.resolution == "open").sum())
k["median_wait_min_v1.0"] = t.loc[t.app_version == "v1.0", "wait_min"].median()
k["median_wait_min_v1.1"] = t.loc[t.app_version == "v1.1", "wait_min"].median()
k["avg_agent_handle_min"] = t.agent_handle_min.mean()

# QA
qa = pd.read_csv(DATA / "qa_reviews.csv")
assert set(qa.session_id) <= set(s.loc[ai, "session_id"])
qa_tab = qa.pivot_table(index="language", columns="app_version", values="verdict", aggfunc=lambda x: (x == "correct").mean() * 100)
k["qa_reviews"] = len(qa)
k["qa_correct_v1.0_%"] = (qa[qa.app_version == "v1.0"].verdict == "correct").mean() * 100
k["qa_correct_v1.1_%"] = (qa[qa.app_version == "v1.1"].verdict == "correct").mean() * 100
k["qa_unsafe_count"] = int((qa.verdict == "unsafe").sum())

# contact centre and time saved
cc = pd.read_csv(DATA / "contact_centre_contacts.csv", parse_dates=["contact_date"])
cc["week"] = (cc.contact_date - PILOT_START).dt.days // 7 + 1          # baseline weeks are -3..0
base = cc[cc.week <= 0]; last4 = cc[cc.week >= 5]
k["contacts_per_week_baseline"] = len(base) / 4
k["contacts_per_week_pilot_wk5_8"] = len(last4) / 4
k["contact_drop_%"] = (1 - k["contacts_per_week_pilot_wk5_8"] / k["contacts_per_week_baseline"]) * 100
handle_base = base.groupby("topic").handle_min.mean()
saved_min = s.loc[ai].topic.map(handle_base).sum()
k["est_agent_hours_saved"] = saved_min / 60
k["baseline_avg_handle_min"] = base.handle_min.mean()
k["observed_hours_saved_per_week_wk5_8"] = ((len(base) / 4) * base.handle_min.mean() - (len(last4) / 4) * last4.handle_min.mean()) / 60

# ================================================================ DuckDB cross-check, straight from the raw files
con = duckdb.connect()
q = f"""
WITH d AS (SELECT DISTINCT * FROM read_csv_auto('{DATA/'sessions.csv'}', all_varchar=true)),
c AS (SELECT * FROM d WHERE user_id NOT LIKE 'TEST-%')
SELECT count(*) AS chats,
       100.0*avg(CASE WHEN outcome='resolved_by_ai' THEN 1 ELSE 0 END) AS resolved,
       100.0*avg(CASE WHEN outcome='resolved_by_ai' THEN 1 ELSE 0 END) FILTER (WHERE app_version='v1.0') AS r10,
       100.0*avg(CASE WHEN outcome='resolved_by_ai' THEN 1 ELSE 0 END) FILTER (WHERE app_version='v1.1') AS r11,
       avg(TRY_CAST(csat AS INT)) FILTER (WHERE TRY_CAST(csat AS INT) BETWEEN 1 AND 5) AS csat,
       count(*) FILTER (WHERE outcome='handed_to_agent') AS handoffs
FROM c"""
chats, resolved, r10, r11, csat, handoffs = con.execute(q).fetchone()
assert chats == k["chats"] and handoffs == k["tickets"]
for a, b in [(resolved, k["resolved_by_ai_%"]), (r10, k["resolved_v1.0_%"]), (r11, k["resolved_v1.1_%"]), (csat, k["csat_avg"])]:
    assert abs(a - b) < 1e-9, (a, b)
saved_sql = con.execute(f"""
WITH d AS (SELECT DISTINCT * FROM read_csv_auto('{DATA/'sessions.csv'}', all_varchar=true)),
c AS (SELECT * FROM d WHERE user_id NOT LIKE 'TEST-%' AND outcome='resolved_by_ai'),
cc AS (SELECT * FROM read_csv_auto('{DATA/'contact_centre_contacts.csv'}') WHERE contact_date < DATE '2026-09-07'),
h AS (SELECT topic, avg(handle_min) m FROM cc GROUP BY topic)
SELECT sum(h.m)/60 FROM c JOIN h USING (topic)""").fetchone()[0]
assert abs(saved_sql - k["est_agent_hours_saved"]) < 1e-6
print("pandas and DuckDB SQL agree on the headline KPIs")

# ================================================================ write
pd.Series(k).round(2).rename("value").to_csv(KEY / "kpis.csv", header=True, index_label="kpi")
f = lambda x: x.round(1).to_markdown()
md = ["# FirstFlight answer key (simulated pilot data)", "",
      "Every number below is computed by `scripts/answer_key.py` and cross-checked with DuckDB SQL. Use it to check your SQL, Excel and Power BI results.", "",
      "## Cleaning log", "", pd.Series(log).to_frame("count").to_markdown(), "",
      "## Headline KPIs", "", pd.Series(k).round(2).to_frame("value").to_markdown(), "",
      "## Resolved by AI, by topic", "", f(by_topic), "",
      "## Resolved by AI %, by language and version", "", f(by_lang_ver), "",
      "## By passenger type", "", f(by_ptype), "",
      "## Adoption by week", "", f(by_week), "",
      "## Why chats were handed to an agent (%)", "", f(handoff_reasons.to_frame("pct")), "",
      "## QA: correct answers %, by language and version", "", f(qa_tab), "",
      "## Definitions", "",
      "- **Resolved by AI %** (containment / automation rate): chats the assistant answered without an agent ÷ all clean chats.",
      "- **Estimated agent hours saved**: each chat resolved by AI × the average handle time for that topic in the 4 baseline weeks, ÷ 60. This assumes every resolved chat would otherwise have been one contact, so it is an upper estimate.",
      "- **Observed hours saved per week**: contact-centre handle hours per week in the baseline minus pilot weeks 5–8. This is what actually came off the agents' workload, and it is much smaller than the estimate above: many people who chat would never have called. Report both, and lead with the observed number.",
      "- **Contact drop %**: contacts per week in pilot weeks 5–8 vs the 4 baseline weeks.",
      "- Duration figures leave out chats with a missing or impossible end time; all other figures keep them."]
(KEY / "answer_key.md").write_text("\n".join(md), encoding="utf-8")
print(pd.Series(log).to_string()); print(); print(pd.Series(k).round(2).to_string()); print(); print(f(by_lang_ver)); print(f(by_ptype)); print(f(by_topic)); print(f(qa_tab))
