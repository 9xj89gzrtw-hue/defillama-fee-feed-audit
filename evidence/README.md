# Evidence — 2026-10-26, ~01:20–02:35 UTC

Every number in the README comes from one of these runs. They were executed from
this directory with no API keys, no proxy and no paid data source.

## 1. Silent fee feeds

```
$ python3 scripts/fee_audit.py
fee-listed 3069 silent 411
```

Join of `api.llama.fi/protocols` (TVL) with
`api.llama.fi/overview/fees` (24h/7d/30d/1y). Inclusion rule: `total1y >= 1000`
and `total7d == 0` and `total24h == 0`.

```
$ python3 scripts/break_dates.py
with break date: 411 of 411
total measured hole: $642,965,813
```

Per protocol: `api.llama.fi/summary/fees/<slug>?dataType=dailyFees`, last day with
a non-zero value, 30-day mean ending on that day.

Spot check, USD AI — the series ends and stays at zero:

```
$ curl -s 'https://api.llama.fi/summary/fees/usd-ai?dataType=dailyFees' | jq '.totalDataChart[-8:]'
[[1792281600,1810],[1792368000,0],[1792454400,0],[1792540800,0],[1792627200,0],[1792713600,0],[1792800000,0],[1792886400,0]]
```

Both Goldsky subgraphs used by `fees/usdai/index.ts` were queried and responded
with a valid schema, so the indexer is alive and the break is downstream of it:

```
$ curl -s -X POST -H 'content-type: application/json' \
  -d '{"query":"{ __type(name:\"LoanOriginated\"){ fields { name } } }"}' \
  https://api.goldsky.com/api/public/project_cmgziqwja00105np2g1gy6stc/subgraphs/loan_router_v2_arbitrum/latest/gn
{"data":{"__type":{"fields":[{"name":"id"},{"name":"loanTermsHash"},{"name":"borrower"},...
```

## 2. Base coverage gap

```
$ python3 scripts/gap_scan.py
rows 80 wrote json/csv/md
```

908 protocols carry Base TVL; 80 of them have ≥ $300k and appear in neither
`/overview/fees` nor `/overview/dexs`.

## 3. Flat TVL feeds

```
$ python3 scripts/tvl_scan.py
checked 80 anomalies 1
```

```
$ (237 Base protocols with TVL >= $1M, /protocol/<slug> series)
hardcoded/flat: 1 of 237
  $23,000,000 RWA T RIZE pts=573 uniq=1
```

T RIZE was then read, not accused: `projects/T-RIZE/index.js` sums
`totalSupply()` of a fixed-supply token, and the token is pegged at $1. A flat
line is correct. Recorded as a false positive.

## 4. Packaging

```
$ python3 scripts/pack.py
sample rows: 83 base sample: 6
```

83 of 411 rows = 20.2% preview, contacts redacted after the first two rows.
