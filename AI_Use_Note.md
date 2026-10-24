# AI-use note

I used **Claude Code** (in VS Code) as a pair programmer: it wrote most of the SQL/pandas analysis, the chart and diagram scripts, and first drafts of the memo and design note, while I set the direction, found two of the three data issues myself during profiling, and made the final calls.
Every number was checked by running the full notebook, recomputing all four channels' CAC independently in pandas from the raw CSVs, and reconciling totals.
**One thing the AI got wrong:** its first draft put Affiliate's LTV:CAC with test accounts included at ~1.20, because it calculated on data that still had duplicate orders. Running the notebook showed 1.10, and the text was corrected before committing.
The full log of what AI did and how each output was checked is in [`ai_log.md`](ai_log.md).
