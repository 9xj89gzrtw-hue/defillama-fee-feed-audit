# How this gets used (revised 2026-10-26, after verification)

The first version of this file offered "pay $150 and I will tell you how to fix
it", sent by DM with a wallet address. That is gone. Cold DMs that pair a defect
with a payment address read as extortion, they get accounts banned, and they are
unnecessary: in this ecosystem the payment follows a **merged, visible
contribution**, not a promise.

The model now is GitHub-first and costs nothing to run:

1. **Prove a defect.** Run the adapter through its own harness and hit its data
   source directly. See [`VERIFICATION.md`](VERIFICATION.md) — of the ten largest
   recent breaks, ten returned `0.00` because the source really was zero. There is
   nothing to fix and nothing to announce.
2. **Only when the source contradicts the adapter**, write the patch, run
   `npx ts-node --transpile-only cli/testAdapter.ts fees/<slug>` until it prints
   real numbers, and open one PR per protocol in `DefiLlama/dimension-adapters`.
   The PR body carries: the failing behaviour, the corrected daily figure, the tx
   hashes or log counts that prove it, and the command to reproduce.
3. **Then** open one issue in the protocol's own repository — only if the protocol
   still trades — with the technical finding and the link to the DefiLlama PR.
   No price, no demand. One optional line at the end:

   > If the team has a tip jar or a contributor bounty for analytics work, this is
   > my address: `0xbbe6966949d7265a7f5f0b793f08293b9b7fe926` (EVM). If not, the
   > patch is yours either way.

4. **Ledger the outcome.** Merged PRs are the only durable asset here: they turn an
   anonymous address into "the person who fixed X", which is what actually gets
   paid work later.

## Targets worth a patch (verified, still open)

| target | why it qualifies | state |
|---|---|---|
| `rain` (Arbitrum, $15.4 M TVL, $16.6 k/day) | adapter calls `api-v3.rain.fi/api/dirty/historical-apys`; host no longer resolves (`000`) | needs a replacement source before any PR — do not open one until the numbers can be reproduced |
| `fluence` | adapter calls `network-dashboards-api.stage.fluence.dev`; now `404` | TVL is 0 and the feed died 208 days ago; a PR would be a dead-listing cleanup, not a repair |

Everything else in `data/fee_feed_breaks.csv` needs the three-step check in
`VERIFICATION.md` before anyone is contacted. The 20% sample is public at
`data/sample_20pct_repair_queue.csv`; the full 411 rows stay in the repo for
reference — they are a work queue, not a list of accusations.

## What not to do

- Do not DM a protocol with a wallet address and a price. That is the pattern that
  gets X accounts banned and GitHub accounts reported.
- Do not open a PR that "fixes" an adapter whose source legitimately returns zero.
- Do not open more than one issue per protocol, and never re-open a closed one.
- Do not mention payment in the DefiLlama PR itself. That repo is not a marketplace.
