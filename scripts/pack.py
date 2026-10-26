#!/usr/bin/env python3
"""Turn the raw audit JSON into the files that get published and sold."""
import csv, json, os, time

HERE = os.path.dirname(os.path.abspath(__file__))
D = os.path.join(HERE, "kit", "data")
os.makedirs(D, exist_ok=True)

breaks = json.load(open(os.path.join(HERE, "fee_feed_breaks.json")))
gap = json.load(open(os.path.join(HERE, "base_fees_gap.json")))
flat = json.load(open(os.path.join(HERE, "tvl_flat_feeds.json")))

rows = [r for r in breaks["rows"] if r.get("last_day")]
rows.sort(key=lambda r: -(r.get("lost_to_date_usd") or 0))

FIELDS = ["name", "slug", "chains", "category", "tvl", "fees_1y", "last_day",
          "dark_days", "lost_per_day_usd", "lost_to_date_usd", "url", "twitter"]

def write_csv(path, rows, fields, extra=None):
    with open(path, "w", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=fields + (extra or []))
        w.writeheader()
        for r in rows:
            out = {k: (",".join(r[k]) if isinstance(r.get(k), list) else r.get(k)) for k in fields}
            if extra:
                for k in extra:
                    out[k] = r.get(k, "")
            w.writerow(out)

write_csv(os.path.join(D, "fee_feed_repair_queue.csv"), rows, FIELDS)
write_csv(os.path.join(HERE, "kit", "data", "base_fees_gap.csv"), gap["rows"],
          ["name", "slug", "tvl_usd", "category", "url", "twitter", "chains", "listed_at"])

base_rows = [r for r in rows if "Base" in (r.get("chains") or [])]
write_csv(os.path.join(D, "base_fee_feed_repair_queue.csv"), base_rows, FIELDS)

# 20% watermarked preview: every 5th row, contacts blanked after the first two,
# and a sample column that travels with the file.
sample = []
for i, r in enumerate(rows):
    if i % 5:
        continue
    s = dict(r)
    if len(sample) >= 2:
        s["url"] = "REDACTED IN SAMPLE"
        s["twitter"] = "REDACTED IN SAMPLE"
    s["sample"] = "WATERMARKED 20% PREVIEW - full 411-row file on payment"
    sample.append(s)
write_csv(os.path.join(D, "sample_20pct_repair_queue.csv"), sample, FIELDS, ["sample"])

base_sample = [r for r in sample if "Base" in (r.get("chains") or [])][:6]
write_csv(os.path.join(D, "sample_20pct_base.csv"), base_sample, FIELDS, ["sample"])

tot_hole = sum(r.get("lost_to_date_usd") or 0 for r in rows)
tot_day = sum(r.get("lost_per_day_usd") or 0 for r in rows)
stats = {
    "generated_at": breaks["generated_at"],
    "fee_listed_protocols": breaks["fee_listed"],
    "silent_feeds": len(rows),
    "silent_on_base": len(base_rows),
    "estimated_hole_usd": round(tot_hole),
    "current_hole_per_day_usd": round(tot_day),
    "oldest_break": min(r["last_day"] for r in rows),
    "newest_break": max(r["last_day"] for r in rows),
    "base_protocols_without_fee_coverage": gap["with_tvl_over_300k"],
    "base_protocols_scanned": gap["base_protocols"],
    "flat_tvl_feeds_checked": flat["scanned"],
    "flat_tvl_feeds_found": len(flat["flat"]),
    "top_base_targets": [
        {"name": r["name"], "slug": r["slug"], "tvl": r["tvl"], "last_day": r["last_day"],
         "dark_days": r["dark_days"], "per_day": r["lost_per_day_usd"], "url": r.get("url")}
        for r in base_rows[:5]
    ],
}
json.dump(stats, open(os.path.join(HERE, "kit", "stats.json"), "w"), indent=1)
print(json.dumps(stats, indent=1)[:1800])
print("sample rows:", len(sample), "base sample:", len(base_sample))
