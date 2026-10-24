"""Build the Part 2 memo charts from the raw CSVs.

Applies the same cleaning as Part1_Analysis.ipynb (drop duplicate orders, drop the
@urbancart.in test accounts, NULL channel -> 'Unknown'), checks that the headline
numbers match Part 1, then writes three PNGs to Part2_Memo/charts/.

Run from anywhere:  python Part2_Memo/make_charts.py
"""
from pathlib import Path

import duckdb
import matplotlib.pyplot as plt

HERE = Path(__file__).resolve().parent
DATA = HERE.parent / "data"
OUT = HERE / "charts"
OUT.mkdir(exist_ok=True)

# ---- clean tables (same rules as Part 1, section 1.5) ----
duckdb.sql(f"""
CREATE TABLE users AS
SELECT user_id, signup_date, COALESCE(acquisition_channel, 'Unknown') AS channel
FROM read_csv('{DATA / "users.csv"}')
WHERE email NOT LIKE '%@urbancart.in'
""")
duckdb.sql(f"""
CREATE TABLE orders AS
SELECT DISTINCT * FROM read_csv('{DATA / "orders.csv"}')
WHERE user_id IN (SELECT user_id FROM users)
""")
duckdb.sql(f"CREATE TABLE spend AS SELECT * FROM read_csv('{DATA / 'marketing_spend.csv'}')")
duckdb.sql("""
CREATE TABLE customers AS
SELECT u.user_id, u.channel, u.signup_date, SUM(o.order_value) AS revenue
FROM users u JOIN orders o USING (user_id)
WHERE o.status = 'delivered'
GROUP BY ALL
""")

ltv_cac = duckdb.sql("""
WITH s AS (SELECT channel, SUM(spend_inr) AS spend FROM spend GROUP BY channel),
     c AS (SELECT channel, COUNT(*) AS customers, SUM(revenue) AS revenue FROM customers GROUP BY channel)
SELECT channel, ROUND(spend / customers) AS cac, ROUND(0.30 * revenue / spend, 2) AS ltv_cac
FROM s JOIN c USING (channel)
ORDER BY ltv_cac
""").df()

monthly = duckdb.sql("""
WITH c AS (
    SELECT channel, strftime(signup_date, '%Y-%m') AS month, COUNT(*) AS new_customers
    FROM customers GROUP BY ALL
)
SELECT s.channel, s.month, s.spend_inr, c.new_customers, ROUND(s.spend_inr / c.new_customers) AS cac
FROM spend s JOIN c USING (channel, month)
ORDER BY s.channel, s.month
""").df()

# ---- guard: charts must show the same numbers as Part 1 ----
lc = ltv_cac.set_index("channel")
assert lc.loc["Meta Ads", "cac"] == 810 and lc.loc["Google Ads", "ltv_cac"] == 1.14 and lc.loc["Affiliate", "ltv_cac"] == 0.42
meta = monthly[monthly["channel"] == "Meta Ads"].reset_index(drop=True)
assert (meta.loc[0, "cac"], meta.loc[5, "cac"]) == (491, 1115)

# ---- style: one fixed colour per channel across all charts ----
COLORS = {"Google Ads": "#2a78d6", "Meta Ads": "#eb6834", "Affiliate": "#1baf7a", "Influencer": "#eda100"}
INK, INK_2, MUTED, GRID, BASE, SURFACE = "#0b0b0b", "#52514e", "#898781", "#e1e0d9", "#c3c2b7", "#fcfcfb"
MONTHS = ["Jan", "Feb", "Mar", "Apr", "May", "Jun"]

plt.rcParams.update({
    "font.family": ["Helvetica Neue", "Arial", "DejaVu Sans"],
    "font.size": 10,
    "figure.facecolor": SURFACE,
    "axes.facecolor": SURFACE,
    "axes.edgecolor": BASE,
    "axes.labelcolor": INK_2,
    "xtick.color": MUTED,
    "ytick.color": MUTED,
    "axes.spines.top": False,
    "axes.spines.right": False,
    "axes.grid": True,
    "grid.color": GRID,
    "grid.linewidth": 0.6,
    "axes.axisbelow": True,
})


def titles(fig, title, subtitle):
    fig.text(0.02, 0.95, title, fontsize=13, fontweight="bold", color=INK, va="top")
    fig.text(0.02, 0.875, subtitle, fontsize=9.5, color=INK_2, va="top")


def rupees(x):
    return f"₹{x:,.0f}"


# ---- chart 1: LTV:CAC by paid channel ----
fig, ax = plt.subplots(figsize=(8, 4))
fig.subplots_adjust(left=0.15, right=0.95, top=0.76, bottom=0.12)
bars = ax.barh(ltv_cac["channel"], ltv_cac["ltv_cac"], height=0.55,
               color=[COLORS[c] for c in ltv_cac["channel"]], edgecolor=SURFACE, linewidth=2)
ax.axvline(1.0, color=INK_2, linewidth=1.2, linestyle=(0, (4, 3)))
ax.text(1.015, 3.45, "break-even (1.0)", color=INK_2, fontsize=9, ha="left", va="bottom")
for bar, value in zip(bars, ltv_cac["ltv_cac"]):
    ax.text(value + 0.02, bar.get_y() + bar.get_height() / 2, f"{value:.2f}", va="center", color=INK, fontsize=10)
ax.set_xlim(0, 1.3)
ax.set_ylim(-0.5, 3.8)
ax.grid(axis="y", visible=False)
ax.tick_params(axis="y", colors=INK, length=0, labelsize=10)
ax.set_xlabel("LTV:CAC (6-month revenue × 30% margin ÷ CAC)")
titles(fig, "Only Google Ads earns back its acquisition cost",
       "LTV:CAC by paid channel, Jan–Jun 2026 signups. Below 1.0 = a customer's contribution hasn't covered their cost yet.")
fig.savefig(OUT / "chart1_ltv_cac.png", dpi=200)
plt.close(fig)

# ---- chart 2: Meta spend vs new customers, indexed to January = 100 ----
meta_index = meta.assign(spend_idx=100 * meta["spend_inr"] / meta.loc[0, "spend_inr"],
                         cust_idx=100 * meta["new_customers"] / meta.loc[0, "new_customers"])
fig, ax = plt.subplots(figsize=(8, 4))
fig.subplots_adjust(left=0.1, right=0.8, top=0.76, bottom=0.12)
ax.plot(MONTHS, meta_index["spend_idx"], color=COLORS["Meta Ads"], linewidth=2.2, marker="o", markersize=6,
        markeredgecolor=SURFACE, markeredgewidth=1.5, label="Meta spend")
ax.plot(MONTHS, meta_index["cust_idx"], color=INK_2, linewidth=2.2, marker="o", markersize=6,
        markeredgecolor=SURFACE, markeredgewidth=1.5, label="Meta new customers")
last = meta_index.iloc[-1]
ax.text(5.15, last["spend_idx"], f"Spend {last['spend_idx']:.0f}\n(₹{meta.loc[0, 'spend_inr'] / 1000:.0f}k → ₹{last['spend_inr'] / 1000:.0f}k/mo)",
        va="center", color=INK, fontsize=9)
ax.text(5.15, last["cust_idx"], f"New customers {last['cust_idx']:.0f}\n({meta.loc[0, 'new_customers']} → {last['new_customers']}/mo)",
        va="center", color=INK, fontsize=9)
ax.axhline(100, color=BASE, linewidth=1)
ax.set_ylim(0, 240)
ax.set_ylabel("Index (January = 100)")
ax.legend(loc="upper left", frameon=False, fontsize=9, labelcolor=INK_2)
titles(fig, "Meta spend more than doubled; its new customers didn't grow",
       "Meta Ads monthly spend and new customers (grouped by signup month), indexed to January = 100.")
fig.savefig(OUT / "chart2_meta_spend_vs_customers.png", dpi=200)
plt.close(fig)

# ---- chart 3: monthly CAC by channel ----
fig, ax = plt.subplots(figsize=(8, 4))
fig.subplots_adjust(left=0.1, right=0.8, top=0.76, bottom=0.12)
for channel, color in COLORS.items():
    rows = monthly[monthly["channel"] == channel]
    ax.plot(MONTHS, rows["cac"], color=color, linewidth=2.2, marker="o", markersize=6,
            markeredgecolor=SURFACE, markeredgewidth=1.5, label=channel)
    jan, jun = rows["cac"].iloc[0], rows["cac"].iloc[-1]
    ax.text(5.15, jun, f"{channel} {rupees(jun)} ({100 * (jun - jan) / jan:+.0f}%)", va="center", color=INK, fontsize=9)
ax.set_ylim(0, 1250)
ax.yaxis.set_major_formatter(lambda v, _: rupees(v))
ax.set_ylabel("CAC (spend ÷ new customers)")
ax.legend(loc="upper left", frameon=False, fontsize=9, labelcolor=INK_2, ncol=4)
titles(fig, "Meta's CAC more than doubled from January to June; the others held steady",
       "Monthly CAC by paid channel, new customers grouped by signup month. Labels show June CAC and change vs January.")
fig.savefig(OUT / "chart3_monthly_cac.png", dpi=200)
plt.close(fig)

print("Charts written to", OUT)
