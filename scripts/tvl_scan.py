#!/usr/bin/env python3
"""Find Base protocols whose DefiLlama TVL looks broken or stale.

A protocol listed on DefiLlama can silently lose its data: a price feed drops,
an API endpoint changes, a contract migrates. The TVL chart then goes to zero or
flatlines while the protocol is still running, and nobody notices for days.

This reads https://api.llama.fi/protocol/<slug> for every protocol in the
coverage-gap dataset and flags:

    zero_now   current TVL < 1% of its 90-day high, high > $100k
    crash_1d   more than -40% in one day while Base chain TVL moved < 10%
    spike_1d   more than +150% in one day
    stale      no change at all for 14+ days (feed frozen)

Output: tvl_anomalies.json + tvl_anomalies.md
"""
import os
DATA = os.environ.get("DATA_DIR", "data")
os.makedirs(DATA, exist_ok=True)

import json, time, urllib.request, urllib.error
from concurrent.futures import ThreadPoolExecutor

UA = {"user-agent": "money2-agent/1.0"}
GAP = json.load(open(os.path.join(DATA, "base_fees_gap.json")))["rows"]

def get(url, tries=3):
    for i in range(tries):
        try:
            req = urllib.request.Request(url, headers=UA)
            with urllib.request.urlopen(req, timeout=45) as r:
                return json.loads(r.read().decode())
        except Exception as e:
            if i == tries - 1:
                return {"_error": str(e)[:120]}
            time.sleep(1.5 * (i + 1))

def series(slug):
    d = get("https://api.llama.fi/protocol/" + slug)
    if not d or "_error" in d or "tvl" not in d:
        return {"slug": slug, "error": (d or {}).get("_error", "no tvl")}
    tvl = [p for p in d["tvl"] if p.get("totalLiquidityUSD") is not None]
    base = None
    for c in d.get("chainTvls") or []:
        if c == "Base":
            base = [[x["date"], x["totalLiquidityUSD"]] for x in d["chainTvls"][c]["tvl"]]
    pts = [(p["date"], p["totalLiquidityUSD"]) for p in tvl]
    return {"slug": slug, "name": d.get("name"), "current": d.get("tvl") and pts[-1][1],
            "points": pts[-120:], "base_points": (base or [])[-120:],
            "listed": d.get("listedAt")}

def pct(a, b):
    return None if not b else (a - b) / b * 100.0

rows = []
with ThreadPoolExecutor(max_workers=5) as ex:
    for r in ex.map(series, [x["slug"] for x in GAP]):
        rows.append(r)

anoms = []
for r, meta in zip(rows, GAP):
    if r.get("error") or not r.get("points"):
        anoms.append({"name": meta["name"], "slug": meta["slug"], "tvl": meta["tvl_usd"],
                      "flag": "no_data", "detail": r.get("error", "")[:120]})
        continue
    pts = r["points"]
    cur = pts[-1][1]
    high90 = max(p[1] for p in pts[-90:])
    d1 = pct(cur, pts[-2][1]) if len(pts) > 1 else None
    d7 = pct(cur, pts[-8][1]) if len(pts) > 8 else None
    flags = []
    if high90 > 100_000 and cur < high90 * 0.01:
        flags.append(("zero_now", round(pct(cur, high90), 1)))
    if d1 is not None and d1 < -40:
        flags.append(("crash_1d", round(d1, 1)))
    if d1 is not None and d1 > 150:
        flags.append(("spike_1d", round(d1, 1)))
    flat = [p[1] for p in pts[-15:]]
    if len(flat) == 15 and max(flat) == min(flat) and cur > 50_000:
        flags.append(("stale", 0))
    for f, v in flags:
        anoms.append({"name": meta["name"], "slug": meta["slug"], "tvl": meta["tvl_usd"],
                      "flag": f, "value": v, "current": round(cur), "high90": round(high90),
                      "d1": round(d1, 1) if d1 is not None else None,
                      "d7": round(d7, 1) if d7 is not None else None,
                      "url": meta.get("url"), "category": meta.get("category")})

anoms.sort(key=lambda a: -a.get("tvl", 0))
out = {"generated_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
       "checked": len(rows), "anomalies": anoms}
json.dump(out, open(os.path.join(DATA, "tvl_anomalies.json"), "w"), indent=1)

with open(os.path.join(DATA, "tvl_anomalies.md"), "w") as fh:
    fh.write("# Base protocols with suspicious DefiLlama TVL\n\nChecked %d protocols from the fee-coverage gap list at %s.\n\n"
             "| flag | current TVL | 90d high | 1d | 7d | protocol | site |\n|---|---:|---:|---:|---:|---|---|\n"
             % (len(rows), out["generated_at"]))
    for a in anoms[:40]:
        fh.write("| %s | $%s | $%s | %s%% | %s%% | %s | %s |\n" % (
            a["flag"], format(a.get("current", a.get("tvl", 0)) or 0, ","),
            format(a.get("high90", 0) or 0, ","), a.get("d1"), a.get("d7"),
            a["name"], a.get("url") or "-"))
print("checked", len(rows), "anomalies", len(anoms))
from collections import Counter
print(Counter(a["flag"] for a in anoms))
for a in anoms[:12]:
    print(" ", a["flag"], a["name"], "tvl", a["tvl"], "cur", a.get("current"), "d1", a.get("d1"), "d7", a.get("d7"))
