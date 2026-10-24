# UrbanCart paid-channel case study

**Data & AI Engineer (Growth & Analytics): take-home submission, Aryan Singh**

UrbanCart spent ₹15.9L on four paid channels from January to June 2026. The CMO needs to cut paid spend by 20% next quarter without hurting growth, and wants weekly answers without waiting on the data team.

## Answer in one line

Cut ₹1.74L by taking ₹1.39L from **Meta Ads**, whose CAC rose from ₹491 to ₹1,115 while its new customers stayed flat, and ₹35k from **Affiliate**, which has the lowest LTV:CAC at 0.42. Protect **Google Ads**, the only channel above break-even (LTV:CAC 1.14).

## What's where

| Part | File | Contents |
|---|---|---|
| 1. Analyse | [`Part1_Analysis/Part1_Analysis.ipynb`](Part1_Analysis/Part1_Analysis.ipynb) | Data quality issues, CAC, revenue per customer, repeat rate, LTV:CAC, monthly CAC, sanity check, assumptions. All code and outputs included. |
| 2. Recommend | [`Part2_Memo/Part2_Memo.md`](Part2_Memo/Part2_Memo.md) | 250-word memo to the CMO with 3 charts ([`make_charts.py`](Part2_Memo/make_charts.py) builds them). |
| 3. Automate | [`Part3_Design/Part3_Design.md`](Part3_Design/Part3_Design.md) | GCP pipeline and self-serve tool design note, with [architecture diagram](Part3_Design/architecture.png). |
| AI-use note | [`AI_Use_Note.md`](AI_Use_Note.md) | How AI was used and checked. Detailed log: [`ai_log.md`](ai_log.md). |
| Reflection | [`Reflection.md`](Reflection.md) | Why I want this role. |

## Part 1 results

| Paid channel | Spend | New customers | CAC | Revenue / customer | Repeat rate | LTV:CAC |
|---|---|---|---|---|---|---|
| Google Ads | ₹4,00,000 | 655 | ₹611 | ₹2,311 | 57.7% | **1.14** |
| Influencer | ₹2,97,000 | 307 | ₹967 | ₹2,858 | 73.0% | 0.89 |
| Meta Ads | ₹5,47,000 | 675 | ₹810 | ₹1,667 | 44.7% | 0.62 |
| Affiliate | ₹3,46,000 | 505 | ₹685 | ₹957 | 8.1% | **0.42** |
| Organic | n/a | 461 | n/a | ₹1,903 | 55.7% | n/a |

**Data quality issues found and fixed:**
- 206 duplicate order rows, all exact copies.
- 72 users with no acquisition channel, labelled `Unknown`.
- 35 internal QA test accounts, all tagged Affiliate, with 285 orders worth ₹7.8L.

The test accounts matter most: leaving them in would lift Affiliate's LTV:CAC from 0.42 to 1.10.

## How to run

Requires Python 3.13.

```bash
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt

jupyter nbconvert --to notebook --execute --inplace Part1_Analysis/Part1_Analysis.ipynb   # Part 1
python Part2_Memo/make_charts.py                                                          # Part 2 charts
python Part3_Design/make_diagram.py                                                       # Part 3 diagram
```

Everything reads from the raw CSVs in [`data/`](data/). Nothing is cleaned in advance; every cleaning step is in the notebook. The chart script checks that its numbers match Part 1 before drawing anything.
