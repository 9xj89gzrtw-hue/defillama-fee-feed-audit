# DefiLlama fee-feed audit

An independent check of the two data sets that decide whether a protocol is visible
on DefiLlama: **fee/revenue coverage** and **fee/tvl feeds that have silently died**.

Everything here is produced from DefiLlama's own public APIs
(`api.llama.fi`), is reproducible with the scripts in `scripts/`, and was run on
**2026-10-26**. Raw outputs are in `data/`, the exact commands in `evidence/`.

---

## Findings (2026-10-26)

### 0. Read this first: a silent feed is usually not a broken adapter

Of the ten largest and most recent breaks, all ten printed `0.00` because the data
source genuinely reports zero (USD AI: no `FeePaid` event in two days; Theo:
`pricePerShare` unchanged for 96 h). Mass-patching this list would have produced
false claims against $266 M protocols. The harness run and the evidence are in
[`VERIFICATION.md`](VERIFICATION.md) — check any row there before touching it.

### 1. 411 protocols publish a fee feed that has stopped

Of the 3,069 protocols with a fee listing, **411 have recorded fees over the last
year but exactly zero in the last 7 days**. That is not "no fees" — it means the
adapter runs and returns nothing. For each one we found the last day it published
a number and the average daily fees in the 30 days before that.

- 411 protocols, 60 of them on **Base**
- oldest break: **2025-10-31**, newest: **2026-10-18**
- current measured hole: **$3,333,964 per day** of fees that are no longer published
- cumulative (prior 30-day average × days dark): **$642,965,813**

Some of these are legitimate (the protocol stopped charging, or wound down).
The 9 rows below are the opposite: the break is recent and the protocol still has
TVL, so the data source is what broke, not the business.

| protocol | chain | TVL | last published | days dark | fees/day before |
|---|---|---:|---|---:|---:|
| USD AI | Arbitrum | $266,198,319 | 2026-10-18 | 7 | $258,434 |
| Vectis Finance | Solana | $5,118,780 | 2026-10-05 | 20 | $28,359 |
| WBTC | Ethereum | $9,324,353,530 | 2026-10-02 | 23 | $19,103 |
| Rain | Arbitrum | $15,373,366 | 2026-09-11 | 44 | $16,593 |
| Theo Straddle Vaults | Base + 3 | $1,055,600 | 2026-10-12 | 13 | $7,929 |
| Yala | Ethereum | $2,318,871 | 2026-10-09 | 16 | $4,849 |
| Badger DAO | Ethereum | $12,643,670 | 2026-10-12 | 13 | $2,631 |
| Stride | Osmosis | $4,456,354 | 2026-10-12 | 13 | $2,053 |
| RateX DEX | Solana | $2,379,552 | 2026-10-13 | 12 | $601 |

Full list: [`data/fee_feed_repair_queue.csv`](data/fee_feed_repair_queue.csv)
(411 rows). Base-only slice: [`data/base_fee_feed_repair_queue.csv`](data/base_fee_feed_repair_queue.csv)
(60 rows). A watermarked 20% preview with contact columns partly redacted:
[`data/sample_20pct_repair_queue.csv`](data/sample_20pct_repair_queue.csv).

### 2. 80 Base protocols have TVL on DefiLlama and no fee or DEX-volume page at all

Of 908 protocols with Base TVL, **80 have at least $300k of TVL and appear in
neither the fee overview nor the DEX-volume overview** (bridges and CEXs excluded).
A protocol with TVL but no fee page gets no revenue line, no revenue ranking and no
fee-based yield comparison — for a fee-charging product that is a paid product
nobody can see.

Top rows: Spark Savings ($1.60 B), Anemoy Capital ($330 M), Team Finance ($61.6 M),
ZEROBASE ($60.8 M), Gami Labs ($58.4 M), Brickken ($42.4 M), Zoo Finance ($32.8 M),
GoPlus Locker V3 ($30.7 M), UNC X V3 ($26.5 M), T RIZE ($23.0 M).

Full list: [`data/base_fees_gap.csv`](data/base_fees_gap.csv) ·
[`data/base_fees_gap.md`](data/base_fees_gap.md) ·
[`data/base_fees_gap.json`](data/base_fees_gap.json).

### 3. Frozen TVL feeds: one candidate, and it turned out to be correct

We also checked every Base protocol with ≥ $1 M TVL (237) for a TVL series that
never changes. Exactly one qualifies: **T RIZE**, 573 daily points, all exactly
$23,000,000. We read its adapter (`projects/T-RIZE/index.js`) and its series
before reporting it: the adapter sums `totalSupply()` of a fixed-supply token and
the token is pegged at $1, so a flat line is the correct answer. No action.
This is recorded because a false positive is worth as much as a finding:
[`data/tvl_anomalies.md`](data/tvl_anomalies.md).

---

## Reproduce

```bash
python3 scripts/fee_audit.py      # -> fee_feed_breaks.json/md   (1 request, 3,069 protocols)
python3 scripts/break_dates.py    # adds last_day / dark_days / lost_per_day_usd
python3 scripts/gap_scan.py       # -> base_fees_gap.json/csv/md  (908 Base protocols)
python3 scripts/tvl_scan.py       # -> tvl_anomalies.json/md     (flat / zero / crash)
python3 scripts/pack.py           # -> everything in data/
```

No API keys, no paid data, no RPC. Each script takes one to six minutes.

## Limits

- `lost_to_date_usd` is an estimate: prior-30-day average × days dark. It is not a
  measurement of what the protocol actually earned while the feed was down.
- A silent feed is a symptom, not a verdict. A protocol that stopped charging fees
  looks exactly like a broken adapter until you read its adapter and contracts.
  Every row needs that second step before anyone is told their data is wrong.
- DefiLlama's fee overview covers 3,069 listings; protocols with no fee listing at
  all are covered by finding 2 instead.

## Using this

[`OFFERS.md`](OFFERS.md) describes the GitHub-first route: prove the defect, patch
one adapter, run the repository's harness, open one PR per protocol, and only then
contact the team with the technical finding.
