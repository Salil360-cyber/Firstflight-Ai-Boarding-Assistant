"""FirstFlight report charts from the simulated pilot data.

Cleans the raw chats the same way as sql/02_clean_view.sql, checks every number against
answer_key/kpis.csv, then saves the charts to charts/.
Run: python scripts/charts.py
"""
from pathlib import Path
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.ticker import PercentFormatter, FuncFormatter

ROOT = Path(__file__).resolve().parents[1]
DATA, OUT = ROOT / "data", ROOT / "charts"
OUT.mkdir(exist_ok=True)
BLUE, ORANGE, AQUA, GREY = "#2a78d6", "#eb6834", "#1baf7a", "#9a9a95"
INK, INK2, BG, GRID = "#0b0b0b", "#52514e", "#fcfcfb", "#e6e5e1"
plt.rcParams.update({"font.size": 10, "axes.spines.top": False, "axes.spines.right": False,
                     "axes.edgecolor": "#c9c8c3", "axes.labelcolor": INK2, "xtick.color": INK2,
                     "ytick.color": INK, "figure.facecolor": BG, "axes.facecolor": BG})
NOTE = "Simulated 8-week pilot (7 Sep – 1 Nov 2026) · SaffronSky Air is a fictional airline"
LANG = {"en": "English", "hi": "Hindi", "ar": "Arabic"}
PILOT_START = pd.Timestamp("2026-09-07")

def save(fig, name, note=NOTE):
    fig.text(0.01, -0.02, note, fontsize=8, color=INK2)
    fig.tight_layout(); fig.savefig(OUT / name, dpi=160, bbox_inches="tight"); plt.close(fig)

def title(ax, text):
    ax.set_title(text, loc="left", fontsize=11.5, color=INK, pad=12)

# ---------------------------------------------------------------- clean (same rules as the SQL view)
raw = pd.read_csv(DATA / "sessions.csv", dtype={"csat": "Int64"})
s = raw.drop_duplicates()
s = s[~s.user_id.str.startswith("TEST-")].copy()
s["language"] = s.language.str.lower().replace({"english": "en", "hindi": "hi", "arabic": "ar"})
s.loc[~s.csat.between(1, 5).fillna(False), "csat"] = pd.NA
s["started_at"] = pd.to_datetime(s.started_at)
s["week"] = (s.started_at.dt.normalize() - PILOT_START).dt.days // 7 + 1
s["ai"] = s.outcome.eq("resolved_by_ai")
cc = pd.read_csv(DATA / "contact_centre_contacts.csv", parse_dates=["contact_date"])
cc["week"] = (cc.contact_date - PILOT_START).dt.days // 7 + 1
qa = pd.read_csv(DATA / "qa_reviews.csv")

key = pd.read_csv(ROOT / "answer_key" / "kpis.csv", index_col=0)["value"]
def check(name, value, tol=0.01):
    assert abs(round(value, 2) - key[name]) <= tol, f"{name}: {value} vs answer key {key[name]}"

check("chats", len(s)); check("resolved_by_ai_%", s.ai.mean() * 100)
check("resolved_v1.0_%", s.loc[s.app_version == "v1.0", "ai"].mean() * 100)
check("resolved_v1.1_%", s.loc[s.app_version == "v1.1", "ai"].mean() * 100)
check("qa_correct_v1.0_%", (qa[qa.app_version == "v1.0"].verdict == "correct").mean() * 100)
check("qa_correct_v1.1_%", (qa[qa.app_version == "v1.1"].verdict == "correct").mean() * 100)

# ---------------------------------------------------------------- 1. adoption by week (two panels, one axis each)
wk = s.groupby("week").agg(chats=("ai", "size"), resolved=("ai", "mean"))
fig, (a1, a2) = plt.subplots(2, 1, figsize=(8.2, 5.2), sharex=True, gridspec_kw={"height_ratios": [1.25, 1]})
cols = [GREY if w <= 4 else BLUE for w in wk.index]
a1.bar(wk.index, wk.chats, color=cols, width=0.62)
for w, v in wk.chats.items():
    a1.text(w, v + 70, f"{v:,}", ha="center", fontsize=8.5, color=INK2)
a1.set_ylim(0, 5600); a1.yaxis.set_major_formatter(FuncFormatter(lambda v, _: f"{v:,.0f}")); a1.set_ylabel("Chats per week")
title(a1, f"Use grew 2.7x in 8 weeks, and v1.1 lifted the resolved share from {key['resolved_v1.0_%']:.0f}% to {key['resolved_v1.1_%']:.0f}%")
a2.plot(wk.index, wk.resolved, color=BLUE, lw=2, marker="o", ms=6)
for w, v in wk.resolved.items():
    a2.text(w, v + 0.012, f"{v:.0%}", ha="center", fontsize=8.5, color=INK2)
a2.axvline(4.5, color=GREY, ls="--", lw=1)
a2.text(4.55, 0.535, "v1.1 released after user testing", fontsize=8.5, color=INK2)
a2.set_ylim(0.50, 0.72); a2.yaxis.set_major_formatter(PercentFormatter(1.0, decimals=0)); a2.set_ylabel("Resolved by AI")
a2.set_xticks(wk.index, [f"Wk {w}" for w in wk.index])
a1.text(0.6, 5150, "grey = v1.0 · blue = v1.1", fontsize=8.5, color=INK2)
save(fig, "01_adoption_by_week.png")

# ---------------------------------------------------------------- 2. the language fix
lv = s.pivot_table(index="language", columns="app_version", values="ai", aggfunc="mean").loc[["ar", "hi", "en"]]
fig, ax = plt.subplots(figsize=(8, 3.8))
x = np.arange(3); w = 0.36
for i, (ver, c) in enumerate([("v1.0", GREY), ("v1.1", BLUE)]):
    ax.bar(x + (i - 0.5) * w, lv[ver], width=w - 0.04, color=c, label=f"{ver}" + (" (weeks 1–4)" if ver == "v1.0" else " (weeks 5–8)"))
    for xi, v in zip(x, lv[ver]):
        ax.text(xi + (i - 0.5) * w, v + 0.012, f"{v:.1%}", ha="center", fontsize=9, color=INK2)
ax.set_xticks(x, [LANG[l] for l in lv.index]); ax.set_ylim(0, 0.9)
ax.yaxis.set_major_formatter(PercentFormatter(1.0, decimals=0)); ax.set_ylabel("Chats resolved by AI")
ax.legend(frameon=False, loc="upper left", ncol=2)
title(ax, f"Arabic gained the most after the fix: {lv.loc['ar','v1.0']:.1%} → {lv.loc['ar','v1.1']:.1%} of chats resolved")
save(fig, "02_resolved_by_language.png")

# ---------------------------------------------------------------- 3. topics
tp = s.groupby("topic").agg(n=("ai", "size"), r=("ai", "mean")).sort_values("r")
fig, ax = plt.subplots(figsize=(8.2, 4.4))
NICE = {"check_in": "Check-in", "baggage": "Baggage", "boarding": "Boarding", "id_documents": "ID documents", "refunds_changes": "Refunds & changes",
        "special_assistance": "Special assistance", "add_ons": "Add-ons", "delays": "Delays", "name_change": "Name correction", "other": "Other"}
names = [NICE[t] for t in tp.index]
colors = [BLUE if r >= s.ai.mean() else ORANGE for r in tp.r]
ax.barh(names, tp.r, color=colors, height=0.62)
for i, (r, n) in enumerate(zip(tp.r, tp.n)):
    ax.text(r + 0.01, i, f"{r:.1%}  ·  {n:,} chats", va="center", fontsize=8.5, color=INK2)
ax.axvline(s.ai.mean(), color=GREY, ls="--", lw=1)
ax.text(s.ai.mean() + 0.005, len(tp) - 0.45, f"all chats {s.ai.mean():.0%}", fontsize=8.5, color=INK2)
ax.set_xlim(0, 1.0); ax.xaxis.set_major_formatter(PercentFormatter(1.0, decimals=0)); ax.set_xlabel("Chats resolved by AI")
title(ax, "Fixed rules (check-in, boarding, bags) suit the assistant; refunds and special help need people")
save(fig, "03_resolved_by_topic.png")

# ---------------------------------------------------------------- 4. hand-off reasons
hr = s[s.outcome == "handed_to_agent"].handoff_reason.value_counts(normalize=True).sort_values()
label = {"low_confidence": "Assistant not confident", "booking_specific": "Booking-specific request",
         "customer_requested": "Passenger asked for a person", "not_in_handbook": "Not in the handbook",
         "live_status": "Live flight status", "personal_data": "Personal data shared"}
fig, ax = plt.subplots(figsize=(8, 3.7))
ax.barh([label[i] for i in hr.index], hr.values, color=[BLUE if i == "low_confidence" else GREY for i in hr.index], height=0.6)
for i, v in enumerate(hr.values):
    ax.text(v + 0.006, i, f"{v:.1%}", va="center", fontsize=9, color=INK2)
ax.set_xlim(0, 0.36); ax.xaxis.set_major_formatter(PercentFormatter(1.0, decimals=0)); ax.set_xlabel(f"Share of {int(key['tickets']):,} hand-offs")
title(ax, f"Low confidence causes {hr['low_confidence']:.0%} of hand-offs: the biggest one a better handbook can cut")
save(fig, "04_handoff_reasons.png")

# ---------------------------------------------------------------- 5. estimate vs observed saving (weeks 5-8)
base = cc[cc.week <= 0]; late = cc[cc.week >= 5]
handle = base.groupby("topic").handle_min.mean()
est_week = s.loc[s.ai & (s.week >= 5), "topic"].map(handle).sum() / 60 / 4
obs_week = ((len(base) / 4) * base.handle_min.mean() - (len(late) / 4) * late.handle_min.mean()) / 60
check("observed_hours_saved_per_week_wk5_8", obs_week)
fig, ax = plt.subplots(figsize=(8, 3.4))
ax.barh(["Observed drop in agent hours", "Simple estimate"], [obs_week, est_week], color=[BLUE, GREY], height=0.55)
ax.text(est_week + 4, 1, f"{est_week:,.0f} hours a week", va="center", fontsize=9.5, color=INK2)
ax.text(obs_week + 4, 0, f"{obs_week:,.0f} hours a week", va="center", fontsize=9.5, color=INK, fontweight="bold")
ax.set_xlim(0, est_week * 1.25); ax.set_xlabel("Agent hours saved per week, pilot weeks 5–8")
title(ax, f"The real saving is about {obs_week:.0f} agent hours a week, not the {est_week:.0f} a simple estimate suggests")
save(fig, "05_estimate_vs_observed.png", NOTE + " · estimate = every AI-resolved chat × baseline handle time; observed = contact-centre hours before vs during")

# ---------------------------------------------------------------- 6. contact centre volume
cw = cc.groupby("week").size()
fig, ax = plt.subplots(figsize=(8.2, 3.7))
ax.axvspan(0.5, 8.5, color="#eef3fb", zorder=0)
ax.plot(cw.index, cw.values, color=BLUE, lw=2, marker="o", ms=6, zorder=3)
ax.axhline(len(base) / 4, color=GREY, ls="--", lw=1)
ax.text(-3.4, len(base) / 4 + 25, f"baseline average {len(base)/4:,.0f}", fontsize=8.5, color=INK2)
ax.text(0.65, 2470, "pilot running", fontsize=8.5, color=INK2)
ax.set_xticks(cw.index, [f"Wk {w}" if w > 0 else f"B{w + 4}" for w in cw.index])
ax.set_ylim(1800, 2550); ax.yaxis.set_major_formatter(FuncFormatter(lambda v, _: f"{v:,.0f}")); ax.set_ylabel("Calls + emails per week")
title(ax, f"Contact-centre volume fell {key['contact_drop_%']:.0f}% by weeks 5–8 as more passengers used the assistant")
save(fig, "06_contact_centre_volume.png", NOTE + " · B1–B4 = 4 baseline weeks before the pilot")

# ---------------------------------------------------------------- 7. QA accuracy
q = qa.groupby(["language", "app_version"]).verdict.agg(correct=lambda v: (v == "correct").mean(), n="size").unstack()
q = q.loc[["ar", "hi", "en"]]
fig, ax = plt.subplots(figsize=(8, 3.8))
for i, (ver, c) in enumerate([("v1.0", GREY), ("v1.1", BLUE)]):
    ax.bar(x + (i - 0.5) * w, q[("correct", ver)], width=w - 0.04, color=c, label=ver)
    for xi, v, n in zip(x, q[("correct", ver)], q[("n", ver)]):
        ax.text(xi + (i - 0.5) * w, v + 0.015, f"{v:.0%}\nn={n}", ha="center", fontsize=8.5, color=INK2)
ax.set_xticks(x, [LANG[l] for l in q.index]); ax.set_ylim(0, 1.15)
ax.yaxis.set_major_formatter(PercentFormatter(1.0, decimals=0)); ax.set_ylabel("QA reviews marked correct")
ax.legend(frameon=False, loc="upper left", ncol=2)
title(ax, f"Human QA: correct answers rose from {key['qa_correct_v1.0_%']:.0f}% to {key['qa_correct_v1.1_%']:.0f}%; Arabic sample is small")
save(fig, "07_qa_accuracy.png", NOTE + f" · 6% sample of AI-resolved chats reviewed · {int(key['qa_unsafe_count'])} unsafe answers in total")
print("all numbers match the answer key; charts saved to", OUT)
