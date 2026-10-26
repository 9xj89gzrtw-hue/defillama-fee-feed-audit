# Ready offers — 26 Oct 2026

Three protocols where the public fee feed is dark **right now**, the protocol is
still running, and we can name the exact day the number stopped. Each offer is the
same shape: we rebuild the missing series from the protocol's own contracts and
deliver a merge-ready patch to `DefiLlama/dimension-adapters`. If the feed is
silent because the protocol genuinely stopped charging, we say so and there is
nothing to pay.

Payment: **USDC on Base** or **ETH on mainnet** to
`0x72Aa6edDE71B94f6b99c8e52EdC02B5C75F74d1a`.
Half on delivery of the patch, half when DefiLlama merges it. No KYC, no invoice.

---

## 1. USD AI — fee feed dark since 2026-10-18 · $150

- **What is public:** $266,198,319 TVL (Arbitrum), $26.28 M of fees published over
  the last year, **$0 for the last 7 days**. Before the break it published
  $258,434 per day. The adapter (`fees/usdai/index.ts`) reads `FeePaid` and
  `Harvested` events plus two Goldsky subgraphs — the subgraphs still answer, so
  the break is in the event path, not the indexer.
- **What we deliver:** the reconstructed daily series for the dark period from
  Arbitrum logs, the failing component identified with the block/transaction that
  proves it, and a patch against `fees/usdai` that restores the number. Evidence
  file included (numbers + tx hashes + the command that produced them).
- **Why it is worth $150 to them:** seven days of a $258 k/day revenue line reading
  zero, on a $266 M RWA, is the first thing any allocator checks.

## 2. Theo Straddle Vaults — dark since 2026-10-12 · $120

- **What is public:** $1,055,600 TVL across Base, Arbitrum, Ethereum and Linea,
  $228,796 of fees over the year, **13 days at zero**, $7,929 per day before that.
- **Why this one first:** it is the only recent break in the list with a Base
  presence, so it is also the cheapest one to verify — one `eth_getLogs` sweep per
  vault, no subgraph dependency.
- **Deliverable:** same as above, `fees/theo-straddle-vaults` or the shared Theo
  module, whichever the repo uses.

## 3. Badger DAO — dark since 2026-10-12 · $120

- **What is public:** $12,643,670 TVL (Ethereum), $43,377 of fees over the year,
  **13 days at zero**, $2,631 per day before that.
- **Deliverable:** same. If the vaults were wound down and the fee is genuinely
  gone, the deliverable becomes a one-paragraph note saying the feed is correct
  and should be marked as ended — free, and still useful.

---

## Other things for sale

| item | price | what it is |
|---|---:|---|
| **Base fee-coverage pitch list** | **$79** | the 80 Base protocols with TVL ≥ $300k and no fee page, with the contact (site, X handle), category, TVL and the exact adapter path each one needs. Delivered as CSV. |
| **Fee-feed repair, any protocol** | **$150** | the same repair as above, any row in the 411-row queue. |
| **Weekly data QA for one protocol** | **$49 / month** | every Monday: is your fee feed still publishing, is your TVL series moving, did your rank change. Email or Telegram, one screen. |
| **Full 411-row queue with contacts and break dates** | **$79** | the whole repair queue, contacts included, refreshed weekly while subscribed. |

The audit and the 20% preview are public: https://github.com/9xj89gzrtw-hue/defillama-fee-feed-audit
(`data/sample_20pct_repair_queue.csv`) — real rows, real
dates, contacts redacted after the first two.

---

## Message to send (short, no pitch voice)

> Your DefiLlama fee feed has published zero since **<date>**. Before that it was
> **$<x>/day**, and the protocol still has **$<tvl>** TVL, so this looks like a
> data-source break rather than a business change.
>
> I rebuild the missing series from your own contracts and send a merge-ready
> patch to `dimension-adapters`, with the tx hashes that prove each day. $150,
> half when you get the patch, half when it merges; if the feed is off because you
> really stopped charging, I tell you that instead and you pay nothing.
>
> Example of the audit: https://github.com/9xj89gzrtw-hue/defillama-fee-feed-audit. Payment address: 0x72Aa6edDE71B94f6b99c8e52EdC02B5C75F74d1a.

Channels that work from here: GitHub issue/PR comment (public, permanent), X reply
from `@danilaonly` once the session exists, or the contact form on the protocol's
site. Reddit and Telegram previews are blocked from this egress (403).
