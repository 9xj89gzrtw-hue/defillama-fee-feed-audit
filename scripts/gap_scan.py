#!/usr/bin/env python3
"""Which Base protocols have TVL on DefiLlama but no fee/revenue coverage?

Money angle: a protocol that is listed but has no fees page gets no revenue
visibility and no fee-based ranking. That is a concrete, one-file fix
(DefiLlama/dimension-adapters), and it is the kind of thing teams pay for.

Outputs: base_fees_gap.json (machine) and base_fees_gap.md (human).
"""
import os
DATA = os.environ.get("DATA_DIR", "data")
os.makedirs(DATA, exist_ok=True)

import json, urllib.request, time, csv

UA = {"user-agent": "money2-agent/1.0"}

def get(url):
    req = urllib.request.Request(url, headers=UA)
    with urllib.request.urlopen(req, timeout=60) as r:
        return json.loads(r.read().decode())

protocols = get("https://api.llama.fi/protocols")
fees = get("https://api.llama.fi/overview/fees?excludeTotalDataChart=true&excludeTotalDataChartBreakdown=true")
dim = get("https://api.llama.fi/overview/dexs?excludeTotalDataChart=true&excludeTotalDataChartBreakdown=true")
covered = {p.get("slug") or p.get("name") for p in (fees.get("protocols") or [])}
covered |= {p.get("slug") or p.get("name") for p in (dim.get("protocols") or [])}

rows = []
for p in protocols:
    if "Base" not in (p.get("chains") or []):
        continue
    if (p.get("tvl") or 0) < 300_000:
        continue
    if p.get("category") in ("CEX", "Canonical Bridge", "Bridge"):
        continue
    slug = p.get("slug") or p.get("name")
    if slug in covered:
        continue
    rows.append({
        "name": p.get("name"), "slug": slug, "tvl_usd": round(p.get("tvl") or 0),
        "category": p.get("category"), "url": p.get("url"),
        "chains": len(p.get("chains") or []), "listed_at": p.get("listedAt"),
        "twitter": p.get("twitter"), "audits": p.get("audits") and len(p.get("audits")),
    })
rows.sort(key=lambda r: -r["tvl_usd"])

with open(os.path.join(DATA, "base_fees_gap.json"), "w") as fh:
    json.dump({"generated_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
               "source": ["https://api.llama.fi/protocols", "https://api.llama.fi/overview/fees",
                          "https://api.llama.fi/overview/dexs"],
               "base_protocols": len([p for p in protocols if "Base" in (p.get("chains") or [])]),
               "with_tvl_over_300k": len(rows), "rows": rows}, fh, indent=1)

with open(os.path.join(DATA, "base_fees_gap.csv"), "w", newline="") as fh:
    w = csv.DictWriter(fh, fieldnames=list(rows[0].keys()))
    w.writeheader(); w.writerows(rows)

top = rows[:40]
with open(os.path.join(DATA, "base_fees_gap.md"), "w") as fh:
    fh.write("# Base protocols with TVL but no fee or DEX-volume coverage on DefiLlama\n\n")
    fh.write("Generated %s from the public DefiLlama API. %d Base protocols have TVL; "
             "%d of them (>= $300k, bridges excluded) appear in neither the fees nor the "
             "dexs overview.\n\n" % (time.strftime("%Y-%m-%d", time.gmtime()), 
                                     sum(1 for p in protocols if "Base" in (p.get("chains") or [])), len(rows)))
    fh.write("| TVL | category | protocol | site |\n|---:|---|---|---|\n")
    for r in top:
        fh.write("| $%s | %s | %s | %s |\n" % (format(r["tvl_usd"], ","), r["category"] or "-",
                                               r["name"], r["url"] or "-"))
print("rows", len(rows), "wrote json/csv/md")
