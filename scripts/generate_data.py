"""FirstFlight: simulated pilot data for the SaffronSky Air boarding assistant.

Creates 4 CSV files in data/ (all simulated, seeded, reproducible):
  sessions.csv                 every chat with the AI assistant during an 8-week pilot (raw, with known data issues)
  agent_tickets.csv            chats the assistant handed over to a human agent
  qa_reviews.csv               a human QA sample of chats the assistant answered by itself
  contact_centre_contacts.csv  calls and emails to the contact centre, 4 weeks before and 8 weeks during the pilot

The known data issues are listed in answer_key/planted_issues.csv so the cleaning step can be checked.
Run: python scripts/generate_data.py
"""
from pathlib import Path
import numpy as np
import pandas as pd

SEED = 2026
rng = np.random.default_rng(SEED)
ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"; DATA.mkdir(exist_ok=True)
KEY = ROOT / "answer_key"; KEY.mkdir(exist_ok=True)

PILOT_START = pd.Timestamp("2026-09-07")          # Monday, week 1
V11_START = pd.Timestamp("2026-10-05")            # week 5: v1.1 released after user testing
BASE_START = pd.Timestamp("2026-08-10")           # contact centre baseline, 4 weeks before the pilot
WEEKLY_SESSIONS = [1800, 2400, 2900, 3300, 3700, 4100, 4500, 4900]

TOPICS = ["check_in", "baggage", "boarding", "id_documents", "refunds_changes",
          "special_assistance", "add_ons", "delays", "name_change", "other"]
BASE_MIX = np.array([.20, .22, .10, .08, .12, .04, .08, .10, .03, .03])
RESOLVE_V10 = dict(check_in=.80, baggage=.74, boarding=.80, id_documents=.62, refunds_changes=.45,
                   special_assistance=.40, add_ons=.76, delays=.48, name_change=.40, other=.30)
LANG_PENALTY = {"v1.0": {"en": 0, "hi": .05, "ar": .15}, "v1.1": {"en": 0, "hi": .02, "ar": .03}}
HANDLE_MIN = dict(check_in=4.5, baggage=5.0, boarding=3.5, id_documents=6.5, refunds_changes=9.0,
                  special_assistance=7.0, add_ons=4.5, delays=6.0, name_change=7.5, other=6.0)


def resolve_prob(topic, version, lang):
    p = RESOLVE_V10[topic]
    if version == "v1.1":
        p += .02 if topic in ("refunds_changes", "special_assistance") else .06
    return min(p, .90) - LANG_PENALTY[version][lang]


def topic_mix(ptype, route):
    m = BASE_MIX.copy()
    if ptype == "first_time":
        m[[0, 1, 2]] *= [1.35, 1.15, 1.45]          # first-time flyers ask more about check-in, bags, boarding
    if route == "international":
        m[3] *= 2.6                                  # documents matter more abroad
    return m / m.sum()


def random_time(day, n):
    """Clock times weighted towards the day (6:00 to 23:00)."""
    hours = rng.choice(np.arange(24), size=n, p=_HOUR_P)
    secs = hours * 3600 + rng.integers(0, 3600, size=n)
    return day + pd.to_timedelta(secs, unit="s")


_h = np.array([1, 1, 1, 1, 1, 2, 4, 6, 8, 9, 9, 9, 8, 8, 8, 8, 9, 9, 10, 10, 9, 7, 4, 2], float)
_HOUR_P = _h / _h.sum()

# ---------------------------------------------------------------- 1. sessions
rows = []
sid = 0
for w, n in enumerate(WEEKLY_SESSIONS):
    week_start = PILOT_START + pd.Timedelta(weeks=w)
    day_idx = rng.integers(0, 7, size=n)
    for d in range(7):
        k = int((day_idx == d).sum())
        if k == 0:
            continue
        starts = random_time(week_start + pd.Timedelta(days=d), k)
        for st in starts:
            sid += 1
            version = "v1.1" if st >= V11_START else "v1.0"
            route = rng.choice(["domestic", "international"], p=[.68, .32])
            lang = rng.choice(["en", "hi", "ar"], p=[.70, .28, .02] if route == "domestic" else [.48, .20, .32])
            ptype = rng.choice(["first_time", "returning", "unknown"], p=[.42, .50, .08])
            channel = rng.choice(["web", "app", "whatsapp"], p=[.45, .35, .20])
            topic = rng.choice(TOPICS, p=topic_mix(ptype, route))
            abandon_p = .08 if ptype == "first_time" else .055
            u = rng.random()
            if u < abandon_p:
                outcome = "abandoned"
            elif rng.random() < resolve_prob(topic, version, lang):
                outcome = "resolved_by_ai"
            else:
                outcome = "handed_to_agent"
            reason = ""
            if outcome == "handed_to_agent":
                if topic == "delays":
                    reason = rng.choice(["live_status", "low_confidence", "customer_requested"], p=[.70, .15, .15])
                elif topic in ("refunds_changes", "name_change"):
                    reason = rng.choice(["booking_specific", "low_confidence", "customer_requested", "personal_data"], p=[.60, .15, .15, .10])
                elif topic == "other":
                    reason = rng.choice(["not_in_handbook", "low_confidence", "customer_requested"], p=[.60, .25, .15])
                else:
                    reason = rng.choice(["low_confidence", "not_in_handbook", "customer_requested", "booking_specific", "personal_data"],
                                        p=[.40, .15, .20, .15, .10])
            first_resp = round(float(rng.lognormal(np.log(3.2 if version == "v1.0" else 2.6), .35)), 1)
            med = {"resolved_by_ai": 95, "handed_to_agent": 140, "abandoned": 40}[outcome]
            dur = int(max(8, rng.lognormal(np.log(med), .5)))
            turns = int({"resolved_by_ai": rng.integers(2, 7), "handed_to_agent": rng.integers(3, 9),
                         "abandoned": rng.integers(1, 4)}[outcome])
            resp_p = {"resolved_by_ai": .38, "handed_to_agent": .30, "abandoned": .08}[outcome]
            csat = ""
            if rng.random() < resp_p:
                probs = {"resolved_by_ai": [.02, .03, .08, .30, .57], "handed_to_agent": [.06, .10, .22, .34, .28],
                         "abandoned": [.30, .30, .25, .10, .05]}[outcome]
                csat = int(rng.choice([1, 2, 3, 4, 5], p=probs))
            user = f"U{rng.integers(100000, 999999)}"
            rows.append(dict(session_id=f"S{sid:06d}", user_id=user, started_at=st,
                             ended_at=st + pd.Timedelta(seconds=dur), channel=channel, language=lang,
                             passenger_type=ptype, route_type=route, topic=topic, app_version=version,
                             turns=turns, first_response_sec=first_resp, outcome=outcome,
                             handoff_reason=reason, csat=csat))

s = pd.DataFrame(rows)
clean_ids = set(s.session_id)

# ---------------------------------------------------------------- 2. agent tickets (from the clean sessions)
h = s[s.outcome == "handed_to_agent"].copy()
wait = rng.lognormal(np.log(np.where(h.app_version == "v1.0", 6.0, 4.5)), .6)
handle = np.array([max(1.0, rng.normal(HANDLE_MIN[t] * .9, HANDLE_MIN[t] * .25)) for t in h.topic])
created = h.ended_at.values
assigned = created + pd.to_timedelta(np.round(wait * 60), unit="s")
closed = assigned + pd.to_timedelta(np.round(handle * 60), unit="s")
res = rng.choice(["resolved", "callback_scheduled", "escalated"], size=len(h), p=[.82, .10, .08])
t = pd.DataFrame(dict(ticket_id=[f"T{i:06d}" for i in range(1, len(h) + 1)], session_id=h.session_id.values,
                      created_at=created, assigned_at=assigned, closed_at=closed, topic=h.topic.values,
                      handoff_reason=h.handoff_reason.values, agent_handle_min=np.round(handle, 1), resolution=res))
pilot_end = PILOT_START + pd.Timedelta(weeks=8)
still_open = (t.created_at >= pilot_end - pd.Timedelta(days=1)) & (rng.random(len(t)) < .5)
t.loc[still_open, ["closed_at", "agent_handle_min"]] = [pd.NaT, np.nan]
t.loc[still_open, "resolution"] = "open"

# ---------------------------------------------------------------- 3. QA reviews: 6% sample of AI-resolved chats
r = s[s.outcome == "resolved_by_ai"].sample(frac=.06, random_state=SEED).sort_values("session_id")
def verdict(row):
    if row.app_version == "v1.0":
        p = {"en": [.86, .09, .04, .01], "hi": [.80, .12, .07, .01], "ar": [.66, .16, .15, .03]}[row.language]
    else:
        p = {"en": [.91, .06, .025, .005], "hi": [.89, .07, .035, .005], "ar": [.86, .08, .05, .01]}[row.language]
    return rng.choice(["correct", "partly_correct", "wrong", "unsafe"], p=p)
r["verdict"] = [verdict(x) for x in r.itertuples()]
issue_map = {"correct": ["none"], "partly_correct": ["missing_detail", "wrong_language_mix"],
             "wrong": ["wrong_fee_or_time", "guessed_not_in_handbook"], "unsafe": ["asked_personal_data", "promised_refund"]}
r["issue_type"] = [rng.choice(issue_map[v]) for v in r.verdict]
r["reviewed_at"] = r.ended_at + pd.to_timedelta(rng.integers(1, 72, size=len(r)), unit="h")
qa = r[["session_id", "reviewed_at", "app_version", "language", "topic", "verdict", "issue_type"]].copy()
qa.insert(0, "review_id", [f"R{i:05d}" for i in range(1, len(qa) + 1)])

# ---------------------------------------------------------------- 4. contact centre contacts (12 weeks)
DEFLECT = [0, 0, 0, 0, .04, .07, .10, .12, .15, .18, .20, .22]   # share of contacts the assistant takes away, by week
cc = []
cid = 0
for w in range(12):
    week_start = BASE_START + pd.Timedelta(weeks=w)
    for ti, topic in enumerate(TOPICS):
        base = 2400 * BASE_MIX[ti]
        resolvable = RESOLVE_V10[topic] / .80
        n = int(rng.poisson(base * (1 - DEFLECT[w] * resolvable)))
        days = rng.integers(0, 7, size=n)
        for d in days:
            cid += 1
            ch = rng.choice(["call", "email"], p=[.72, .28])
            m = max(1.0, rng.normal(HANDLE_MIN[topic], HANDLE_MIN[topic] * .3)) * (1.3 if ch == "email" else 1)
            cc.append(dict(contact_id=f"C{cid:06d}", contact_date=(week_start + pd.Timedelta(days=int(d))).date(),
                           channel=ch, topic=topic, passenger_type=rng.choice(["first_time", "returning", "unknown"], p=[.40, .50, .10]),
                           handle_min=round(m, 1)))
cc = pd.DataFrame(cc).sort_values(["contact_date", "contact_id"]).reset_index(drop=True)

# ---------------------------------------------------------------- 5. plant data issues in the raw sessions file
issues = []
raw = s.copy()
raw["started_at"] = raw.started_at.dt.strftime("%Y-%m-%d %H:%M:%S")
raw["ended_at"] = raw.ended_at.dt.strftime("%Y-%m-%d %H:%M:%S")

# a) language written in mixed ways
lang_alias = {"en": ["en", "EN", "English"], "hi": ["hi", "HI", "Hindi"], "ar": ["ar", "AR", "Arabic"]}
mix = rng.random(len(raw)) < .12
raw.loc[mix, "language"] = [rng.choice(lang_alias[l][1:]) for l in raw.loc[mix, "language"]]
issues += [("language_label", x, "language written as a label or in capitals; map back to en/hi/ar") for x in raw.loc[mix, "session_id"]]
# b) out-of-range CSAT (survey tool glitch)
has = raw.index[raw.csat != ""]
bad_csat = rng.choice(has, 60, replace=False)
raw.loc[bad_csat, "csat"] = rng.choice([0, 6, 9], size=60)
issues += [("csat_out_of_range", x, "CSAT outside 1-5; treat as no response") for x in raw.loc[bad_csat, "session_id"]]
# c) missing end time
miss = rng.choice(raw.index.difference(bad_csat), 45, replace=False)
raw.loc[miss, "ended_at"] = ""
issues += [("missing_end_time", x, "no end time; keep the chat, leave it out of duration figures") for x in raw.loc[miss, "session_id"]]
# d) end before start (clock error)
pool = raw.index.difference(np.concatenate([bad_csat, miss]))
neg = rng.choice(pool, 25, replace=False)
raw.loc[neg, "ended_at"] = (pd.to_datetime(raw.loc[neg, "started_at"]) - pd.to_timedelta(rng.integers(30, 600, size=25), unit="s")).dt.strftime("%Y-%m-%d %H:%M:%S")
issues += [("end_before_start", x, "end time earlier than start; keep the chat, leave it out of duration figures") for x in raw.loc[neg, "session_id"]]
# e) internal test chats by the project team
tests = []
for i in range(90):
    st = PILOT_START + pd.Timedelta(minutes=int(rng.integers(0, 8 * 7 * 24 * 60)))
    tests.append(dict(session_id=f"S9{i:05d}", user_id=f"TEST-{rng.integers(1, 6)}", started_at=st.strftime("%Y-%m-%d %H:%M:%S"),
                      ended_at=(st + pd.Timedelta(seconds=60)).strftime("%Y-%m-%d %H:%M:%S"), channel="web", language="en",
                      passenger_type="unknown", route_type="domestic", topic=rng.choice(TOPICS),
                      app_version="v1.1" if st >= V11_START else "v1.0", turns=2, first_response_sec=2.0,
                      outcome="resolved_by_ai", handoff_reason="", csat=5))
tests = pd.DataFrame(tests)
issues += [("internal_test", x, "project-team test chat (user_id starts with TEST-); remove") for x in tests.session_id]
# f) exact duplicate rows (logging retry)
dups = raw.sample(140, random_state=SEED + 1)
issues += [("duplicate_row", x, "exact duplicate of another row; keep one") for x in dups.session_id]
raw = pd.concat([raw, tests, dups]).sample(frac=1, random_state=SEED + 2).reset_index(drop=True)

# ---------------------------------------------------------------- save
raw.to_csv(DATA / "sessions.csv", index=False)
for c in ["created_at", "assigned_at", "closed_at"]:
    t[c] = pd.to_datetime(t[c]).dt.strftime("%Y-%m-%d %H:%M:%S")
t.to_csv(DATA / "agent_tickets.csv", index=False)
qa["reviewed_at"] = qa.reviewed_at.dt.strftime("%Y-%m-%d %H:%M:%S")
qa.to_csv(DATA / "qa_reviews.csv", index=False)
cc.to_csv(DATA / "contact_centre_contacts.csv", index=False)
pd.DataFrame(issues, columns=["issue", "session_id", "how_to_handle"]).sort_values(["issue", "session_id"]).to_csv(KEY / "planted_issues.csv", index=False)

# ---------------------------------------------------------------- self-checks
assert len(raw) == len(s) + 90 + 140
assert raw.session_id.nunique() == len(s) + 90
assert set(t.session_id) <= clean_ids and set(qa.session_id) <= clean_ids
assert len(t) == (s.outcome == "handed_to_agent").sum()
print(f"sessions raw {len(raw):,} (clean {len(s):,}) | tickets {len(t):,} | QA reviews {len(qa):,} | contacts {len(cc):,}")
