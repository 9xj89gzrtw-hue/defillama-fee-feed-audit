#!/usr/bin/env python3
"""Find protocols whose DefiLlama fee feed has silently stopped.

An adapter that broke keeps its protocol listed. The symptom is precise:
total1y is non-zero (it worked before) but total7d and total24h are exactly 0
(nothing new is being indexed). This script joins the public protocols list
(TVL) with the fees overview (24h/7d/30d/1y) and ranks the casualties by size.

Output: fee_feed_breaks.json + fee_feed_breaks.md
"""
import os
DATA = os.environ.get("DATA_DIR", "data")
os.makedirs(DATA, exist_ok=True)

import json, time, urllib.request

UA = {"user-agent": "money2-agent/1.0"}

def get(url):
    req = urllib.request.Request(url, headers=UA)
    with urllib.request.urlopen(req, timeout=90) as r:
        return json.loads(r.read().decode())

protos = {p["slug"]: p for p in get("https://api.llama.fi/protocols")}
fees = get("https://api.llama.fi/overview/fees?excludeTotalDataChart=true&excludeTotalDataChartBreakdown=true")["protocols"]

rows = []
for f in fees:
    slug = f.get("slug")
    t = protos.get(slug) or {}
    tvl = t.get("tvl") or 0
    y, d7, d1 = f.get("total1y") or 0, f.get("total7d") or 0, f.get("total24h") or 0
    if y < 1000 or d7 != 0 or d1 != 0:
        continue
    rows.append({
        "name": f.get("name"), "slug": slug, "category": f.get("category"),
        "tvl": round(tvl), "fees_1y": round(y), "fees_30d": round(f.get("total30d") or 0),
        "chains": f.get("chains") or [], "url": t.get("url"), "twitter": t.get("twitter"),
    })

rows.sort(key=lambda r: -r["fees_1y"])
out = {"generated_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
       "fee_listed": len(fees), "silent": len(rows), "rows": rows}
json.dump(out, open(os.path.join(DATA, "fee_feed_breaks.json"), "w"), indent=1)

with open(os.path.join(DATA, "fee_feed_breaks.md"), "w") as fh:
    fh.write("# Protocols whose DefiLlama fee feed stopped\n\n"
             "A protocol appears here when it has fees recorded over the last year but "
             "**exactly zero** in the last 7 days — the adapter runs and returns nothing. "
             "Checked %d protocols with a fee listing at %s.\n\n"
             "| 1y fees | TVL | chains | protocol | category |\n|---:|---:|---|---|---|\n"
             % (len(fees), out["generated_at"]))
    for r in rows[:60]:
        fh.write("| $%s | $%s | %s | %s | %s |\n" % (
            format(r["fees_1y"], ","), format(r["tvl"], ","),
            ", ".join(r["chains"][:4]), r["name"], r["category"] or "-"))

print("fee-listed", len(fees), "silent", len(rows))
for r in rows[:15]:
    print(f"  ${r['fees_1y']:>14,} 1y | tvl ${r['tvl']:>12,} | {r['name'][:32]:<32} | {','.join(r['chains'][:3])}")
