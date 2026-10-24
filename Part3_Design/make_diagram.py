"""Draw the Part 3 architecture diagram -> Part3_Design/architecture.png

Run from anywhere:  python Part3_Design/make_diagram.py
"""
from pathlib import Path

import matplotlib.pyplot as plt
from matplotlib.patches import FancyArrowPatch, FancyBboxPatch

OUT = Path(__file__).resolve().parent / "architecture.png"

INK, INK_2, MUTED = "#0b0b0b", "#52514e", "#898781"
BOX_FILL, BOX_EDGE, SURFACE = "#f3f2ee", "#c3c2b7", "#fcfcfb"
ACCENT, ACCENT_FILL = "#2a78d6", "#eaf2fc"

plt.rcParams["font.family"] = ["Helvetica Neue", "Arial", "DejaVu Sans"]
fig, ax = plt.subplots(figsize=(16, 9.6))
fig.patch.set_facecolor(SURFACE)
ax.set_xlim(0, 100)
ax.set_ylim(0, 60)
ax.axis("off")


def box(x, y, w, h, title, body="", fill=BOX_FILL, edge=BOX_EDGE, size=10.5):
    ax.add_patch(FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0,rounding_size=0.8",
                                facecolor=fill, edgecolor=edge, linewidth=1.2))
    cx = x + w / 2
    if body:
        ax.text(cx, y + h - 1.3, title, ha="center", va="top", fontsize=size, fontweight="bold", color=INK)
        ax.text(cx, y + h - 3.6, body, ha="center", va="top", fontsize=size - 1.5, color=INK_2, linespacing=1.45)
    else:
        ax.text(cx, y + h / 2, title, ha="center", va="center", fontsize=size, fontweight="bold", color=INK)


def arrow(x1, y1, x2, y2, color=MUTED, rad=0.0):
    ax.add_patch(FancyArrowPatch((x1, y1), (x2, y2), arrowstyle="-|>", mutation_scale=14,
                                 color=color, linewidth=1.4, connectionstyle=f"arc3,rad={rad}"))


def header(x, w, text):
    ax.text(x + w / 2, 52.2, text, ha="center", va="bottom", fontsize=10, color=MUTED, fontweight="bold")


ax.text(1, 58.5, "UrbanCart marketing data: daily pipeline and self-serve tool (GCP)",
        fontsize=15, fontweight="bold", color=INK, va="top")
ax.text(1, 55.9, "Runs every day at 06:00 IST. Grey arrows = data flow; blue = the CMO's conversation with the agent.",
        fontsize=10.5, color=INK_2, va="top")

# ---- columns ----
header(1, 13, "SOURCES")
sources = ["GA4", "Google Ads", "Salesforce", "MoEngage", "Meta Ads"]
for i, name in enumerate(sources):
    box(1, 45 - i * 6, 13, 4.6, name)
box(1, 11.8, 13, 7.2, "Affiliate +", "Influencer spend\n(Google Sheet)", size=10)

header(17, 14, "INGEST")
box(17, 39, 14, 10.6, "Native connectors", "GA4 BigQuery export\nGoogle Ads Data\nTransfer Service")
box(17, 12.5, 14, 24.1, "Cloud Run jobs", "Python, one per source\nIncremental API pulls\n(Salesforce, MoEngage,\nMeta Ads, spend sheet)\n\nKeys read from\nSecret Manager")

header(34, 12, "RAW LANDING")
box(34, 12.5, 12, 24.1, "Cloud Storage", "raw/<source>/\ndt=YYYY-MM-DD/\n\nUntouched files,\nkept for replay\nand audit")

header(49, 22, "WAREHOUSE: BIGQUERY + dbt")
ax.add_patch(FancyBboxPatch((49, 11), 22, 40.6, boxstyle="round,pad=0,rounding_size=1",
                            facecolor=ACCENT_FILL, edgecolor=ACCENT, linewidth=1.6))
box(50.5, 44, 19, 5.6, "raw", "as delivered", fill="white")
box(50.5, 31.5, 19, 10, "staging (cleaned)", "Keep one row per order_id\nNULL channel → 'Unknown'\nDrop internal test accounts", fill="white")
box(50.5, 24, 19, 5.5, "dbt tests: gate", "fail → block publish + quarantine", fill="white", edge="#d03b3b")
box(50.5, 12.5, 19, 9.5, "marts", "channel_metrics (week, month)\ncustomers\nOne metric definition", fill="white")

header(74, 15, "SELF-SERVE")
box(74, 40, 15, 9.6, "Looker Studio", "Weekly dashboard:\nCAC, LTV:CAC,\nrepeat rate by channel")
box(74, 12.5, 15, 25, "Chat agent (Claude)", "1  CMO asks a question\n2  Claude calls get_metric()\n3  Fixed SQL on marts\n4  Answer + definition\n     + \"data as of\" date\n\nRead-only access.\nNumbers only from tools;\nany other number is\nrejected.")

header(92, 7, "USER")
box(92, 27, 7, 8, "CMO")

# ---- data-flow arrows ----
for i in range(2):  # GA4, Google Ads -> native connectors
    arrow(14, 47.3 - i * 6, 17, 47.3 - i * 6 if i == 0 else 41.3)
for i in range(2, 5):  # Salesforce, MoEngage, Meta -> Cloud Run
    arrow(14, 47.3 - i * 6, 17, 47.3 - i * 6)
arrow(14, 15.4, 17, 15.4)
arrow(31, 44.3, 50.5, 46.8)               # native connectors -> BigQuery raw
arrow(31, 24.5, 34, 24.5)                 # Cloud Run -> GCS
arrow(46, 30, 50.5, 45.5, rad=-0.25)      # GCS -> BigQuery raw
arrow(60, 44, 60, 41.5)                   # raw -> staging
arrow(60, 31.5, 60, 29.5)                 # staging -> tests
arrow(60, 24, 60, 22)                     # tests -> marts
arrow(69.5, 20, 74, 42)                   # marts -> dashboard
arrow(69.5, 17, 74, 25)                   # marts -> agent
arrow(89, 44.8, 92, 34)                   # dashboard -> CMO
ax.add_patch(FancyArrowPatch((89, 27), (92, 29), arrowstyle="<|-|>", mutation_scale=14,
                             color=ACCENT, linewidth=1.4))  # CMO <-> agent conversation
ax.text(90.5, 25.2, "asks /\nanswers", ha="center", va="top", fontsize=8.5, color=ACCENT)

# ---- platform band ----
ax.text(1, 9.9, "ORCHESTRATION, SECURITY AND ALERTING", fontsize=10, color=MUTED, fontweight="bold")
box(1, 0.6, 30, 8, "Cloud Scheduler → Cloud Workflows", "06:00 IST: extract → load → dbt build; retries failed steps")
box(33, 0.6, 31, 8, "Secret Manager", "All API keys; one service account per job,\nallowed to read only its own key")
box(66, 0.6, 33, 8, "Cloud Monitoring → Slack + email", "Job or test failure, or marts not refreshed by 08:00")

fig.savefig(OUT, dpi=150, facecolor=SURFACE, bbox_inches="tight", pad_inches=0.2)
print("Diagram written to", OUT)
