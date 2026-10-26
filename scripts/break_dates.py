#!/usr/bin/env python3
"""For every protocol with a silent fee feed, find the exact day it went dark.

Reads fee_feed_breaks.json (from fee_audit.py), pulls each protocol's daily fee
series from api.llama.fi, and records the last day with a non-zero value plus the
average daily fees over the 30 days before that. That is the size of the hole in
the public data: "nothing since DATE, was $X/day".

Output: fee_feed_breaks.json gains `last_day`, `dark_days`, `lost_per_day_usd`.
"""
import os
DATA = os.environ.get("DATA_DIR", "data")
os.makedirs(DATA, exist_ok=True)

import json, time, urllib.request
from concurrent.futures import ThreadPoolExecutor

UA = {"user-agent": "money2-agent/1.0"}
data = json.load(open(os.path.join(DATA, "fee_feed_breaks.json")))

def one(row):
    url = "https://api.llama.fi/summary/fees/%s?dataType=dailyFees" % row["slug"]
    try:
        req = urllib.request.Request(url, headers=UA)
        with urllib.request.urlopen(req, timeout=45) as r:
            d = json.loads(r.read().decode())
    except Exception as e:
        row["error"] = str(e)[:80]
        return row
    chart = [(int(t), float(v or 0)) for t, v in (d.get("totalDataChart") or [])]
    nonzero = [p for p in chart if p[1] > 0]
    if not nonzero:
        row["error"] = "no non-zero day in chart"
        return row
    last_t, last_v = nonzero[-1]
    recent = nonzero[-30:]
    row["last_day"] = time.strftime("%Y-%m-%d", time.gmtime(last_t))
    row["dark_days"] = max(0, int((time.time() - last_t) / 86400) - 1)
    row["lost_per_day_usd"] = round(sum(v for _, v in recent) / len(recent), 2)
    row["lost_to_date_usd"] = round(row["lost_per_day_usd"] * row["dark_days"])
    return row

with ThreadPoolExecutor(max_workers=6) as ex:
    data["rows"] = list(ex.map(one, data["rows"]))

data["rows"].sort(key=lambda r: -(r.get("lost_to_date_usd") or 0))
json.dump(data, open(os.path.join(DATA, "fee_feed_breaks.json"), "w"), indent=1)

ok = [r for r in data["rows"] if r.get("last_day")]
print("with break date:", len(ok), "of", len(data["rows"]))
print("total measured hole: $%s" % format(sum(r.get("lost_to_date_usd") or 0 for r in ok), ","))
for r in ok[:20]:
    print("  %s dark %3dd  $%9s/day  $%11s total  %-28s %s" % (
        r["last_day"], r["dark_days"], format(int(r["lost_per_day_usd"]), ","),
        format(int(r["lost_to_date_usd"]), ","), r["name"][:28], ",".join(r["chains"][:2])))
