# AI use log

Running record of how AI was used in this case study, what it produced, and how the output was checked.
Tool: Claude Code (Anthropic), inside VS Code.

## 2026-10-23: Environment setup and data profiling (Step 1)
- **Used AI for:** guidance on setting up the venv, git and `.gitignore`; a refresher on SQL concepts; SQL profiling queries for the three CSVs (uniqueness, nulls, category counts, cross-table joins).
- **What I did:** ran every profiling cell and read the outputs. I found two of the data issues myself: 72 users with a NULL `acquisition_channel`, and `orders.csv` having 5,684 rows but only 5,478 distinct `order_id`s.
- **What went wrong:** Claude wrote its edits into the notebook while the file was open in VS Code. VS Code saved the old version over them and the edit was lost. It was re-applied with the tab closed. Lesson: never let two tools write the same file at once.

## 2026-10-24: Part 1 analysis
- **Used AI for:** building the full Part 1 notebook (data quality checks, cleaning, CAC, revenue per customer, repeat rate, LTV:CAC, monthly CAC, sanity checks). I asked for this to move faster.
- **How it was checked:** the notebook was executed end to end, and every number written in the text was compared against the cell outputs. Meta Ads CAC (₹810) was recomputed independently in pandas from the raw CSVs and matched the SQL. Channel totals reconcile exactly to overall revenue and customer counts.
- **What the AI got wrong in its first draft** (caught by that execution check, before anything was committed):
  - It said the test accounts had 309 orders. The real figure is 285 unique orders (310 raw rows, 25 of which were duplicates).
  - It put Affiliate's LTV:CAC with test accounts included at about 1.20. The correct figure, after removing duplicates first, is 1.10.
  - It described Influencer's CAC as "rising" when it moved only +1.9% from January to June.
  - It used a DuckDB method (`fetchone()`) that doesn't exist in the installed version, so the cell errored until it was fixed.
- **Why it matters:** the 1.10 vs 0.42 comparison is the headline data-quality finding, so a wrong number there would have weakened the memo.

## 2026-10-24: Second independent check (run by Claude)
- **Numbers checked:** CAC for all four paid channels.
- **How:** recomputed in pandas straight from the raw CSVs: drop exact duplicate orders, remove `@urbancart.in` accounts, keep delivered orders, count distinct customers per channel, divide total spend by that count. No SQL or clean tables were reused.
- **Result:** all four match the SQL in Part 1: Google Ads ₹611, Meta Ads ₹810, Affiliate ₹685, Influencer ₹967.

## 2026-10-24: Parts 2 and 3
- **Used AI for:** drafting the CMO memo, the chart script, the design note and the architecture diagram.
- **How it was checked:** the chart script asserts that its numbers match Part 1 before drawing anything. Every chart and the diagram were rendered and inspected, which caught an overlapping label, a chart arrow running through boxes, and text overflowing a box. Word counts were measured: memo 249/250, design note 395/400.
- **Judgement calls proposed by AI that I reviewed and accepted:** using the Apr–Jun spend as the baseline for next quarter; splitting the cut between Meta and Affiliate rather than taking it all from Meta; holding Influencer flat.
