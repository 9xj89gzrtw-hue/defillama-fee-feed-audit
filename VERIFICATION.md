# Verification — is a silent fee feed a broken adapter?

**No, not most of the time.** This page records what happened when the 12 largest
and freshest candidates from the audit were run through the repository's own test
harness. It was written the same day the audit was published, because the obvious
next step — "411 broken adapters, send 411 patches" — would have been wrong.

Repo: `DefiLlama/dimension-adapters` at `da8ce8e` (2026-10-25), `npm i`, then for
each candidate:

```bash
npx ts-node --transpile-only cli/testAdapter.ts fees/<slug>
```

## Results

| adapter | harness result | cause |
|---|---|---|
| `usdai` | 0.00 for every hour | **correct** — no `FeePaid` event on the v2 loan router in 2 days |
| `theo-straddle-vaults` | 0.00 on all 4 chains | **correct** — `pricePerShare()` unchanged for 96 h on the Base vaults |
| `badger-dao` | 0.00 | correct at the source: no eBTC redemption fees in the window |
| `wbtc` | 0.00 | no fee event in the window |
| `zivoe` | 0.00 | no fee event in the window |
| `avalon-usda` | 0.00 | no fee event in the window |
| `kaito-capital-launchpad` | 0.00 | launchpad rounds ended (API alive, returns no new rounds) |
| `superchain` | 0.00 | chain-level revenue is genuinely idle |
| `vectis` | error: `DUNE_API_KEYS` not set | not verifiable locally |
| `rain` | error: Allium key required | not verifiable locally; **its upstream API is dead** (`api-v3.rain.fi` → no connection) |
| `houdini-swap` | falls back to logs, indexer key missing | not verifiable locally |
| `yala` | indexer fallback, key missing | not verifiable locally |

Two independent checks were done outside the harness to make sure the harness was
not swallowing errors:

**USD AI** — `FeePaid(bytes32,uint8,address,address,uint256)` logs on
`0x1C2ED170de32846316784c4fd58A5e3C7563E12f` (Arbitrum), blocks 517,606,374 →
518,306,374:

```
FeePaid events in ~2 days: 0
```

**Theo** — `pricePerShare()` on Base vault `0x83C6aC60Cfb20a0dF00705A78263B88878EC19b4`
at head, ‑12 h, ‑24 h, ‑48 h, ‑96 h:

```
1098145  1098145  1098145  1098145  1098145
```

Both zeroes are real. Telling either team their metrics were "broken" would have
been false, and a PR claiming to fix them would have been rejected.

## What this means for the 411-row queue

A silent feed has three possible causes and only one of them is fixable:

1. **the adapter is broken** (dead endpoint, changed ABI, new contract) — patchable;
2. **the data source is alive and reports zero** (activity stopped, vault idle,
   loans paused) — the number is right and nothing should change;
3. **the protocol ended** — the listing should be marked dead, not "fixed".

Only (1) deserves a PR. This run found one (1) — `rain`, whose fee API no longer
resolves — and zero (2)-vs-(1) cases among the ten largest recent breaks.

## How to pick a target properly

Do this before writing any patch:

1. Run the adapter through `cli/testAdapter.ts`. An exception is a lead; a clean
   `0.00` is not.
2. If it returns 0, hit the adapter's own data source directly (RPC log query,
   subgraph, HTTP endpoint). If the source answers with zero, the adapter is right.
3. Only when the source contradicts the adapter (source has events, adapter prints
   0) is there a bug, and only then is a PR honest.

Row-level notes for the queue live in `data/fee_feed_breaks.csv`; this file is the
reason most of those rows must stay untouched.
