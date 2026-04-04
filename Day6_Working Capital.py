"""
Day 06/30 — Private Credit Series
Working Capital Early Warning Monitor

What this does:
    Calculates DSO, DIO, DPO from quarterly balance sheet data.
    Tracks trends across 8 quarters.
    Flags deterioration patterns that precede defaults.
    Checks revolver utilisation as a cash crisis signal.

    The pattern that appears before almost every default:
    DSO rising + DIO rising + DPO spiking + revolver drawn.
    Typically visible 3-4 quarters before the formal default.

For CA students:
    You verified debtor ageing, inventory counts, and creditor
    reconciliations in audit. The lender tracks the same numbers
    every quarter — not to verify accuracy but to catch the trend
    before it becomes a default.
"""

from dataclasses import dataclass, field
from typing import List, Optional


@dataclass
class QuarterWC:
    quarter: str
    revenue: float          # LTM revenue
    cogs: float             # LTM cost of goods sold
    debtors: float          # Trade receivables at quarter end
    inventory: float        # Inventory at quarter end
    creditors: float        # Trade payables at quarter end
    revolver_commitment: float = 0.0   # Total revolver facility
    revolver_drawn: float = 0.0        # Amount currently drawn


def calc_metrics(q: QuarterWC) -> dict:
    """Calculate working capital metrics for one quarter."""

    dso = (q.debtors / q.revenue * 365) if q.revenue > 0 else 0
    dio = (q.inventory / q.cogs * 365) if q.cogs > 0 else 0
    dpo = (q.creditors / q.cogs * 365) if q.cogs > 0 else 0
    cwc = dso + dio - dpo   # Cash conversion cycle
    rev_util = (q.revolver_drawn / q.revolver_commitment
                if q.revolver_commitment > 0 else 0)

    return {
        "quarter": q.quarter,
        "dso": dso,
        "dio": dio,
        "dpo": dpo,
        "cwc": cwc,
        "rev_util": rev_util,
        "revolver_drawn": q.revolver_drawn,
        "revolver_commitment": q.revolver_commitment,
    }


def flag_metric(value: float, prev: float,
                metric: str) -> str:
    """Flag deterioration in a working capital metric."""

    change = value - prev

    if metric in ["dso", "dio"]:
        # Higher is worse for DSO and DIO
        if change > 15:   return "🔴 CRITICAL"
        elif change > 8:  return "🟡 WATCH"
        elif change > 3:  return "🟠 MONITOR"
        else:             return "🟢"
    elif metric == "dpo":
        # Rapidly rising DPO = stretching suppliers = cash crisis
        if change > 20:   return "🔴 CRITICAL"
        elif change > 10: return "🟡 WATCH"
        elif change > 5:  return "🟠 MONITOR"
        else:             return "🟢"
    return "🟢"


def run_wc_monitor(quarters: List[QuarterWC],
                   company_name: str = "Company"):
    """
    Run the full working capital monitor.
    Shows trend, flags deterioration, identifies the pattern.
    """

    metrics = [calc_metrics(q) for q in quarters]

    sep = "=" * 70
    print(f"\n{sep}")
    print(f"  WORKING CAPITAL MONITOR — {company_name.upper()}")
    print(sep)

    # Main metrics table
    print(f"\n  {'Quarter':<10} {'DSO':>8} {'DIO':>8} "
          f"{'DPO':>8} {'CCC':>8} {'Rev Util':>10}  Signals")
    print(f"  {'─'*64}")

    early_warnings = []

    for i, m in enumerate(metrics):
        if i == 0:
            dso_flag = dio_flag = dpo_flag = ""
        else:
            prev = metrics[i-1]
            dso_flag = flag_metric(m["dso"], prev["dso"], "dso")
            dio_flag = flag_metric(m["dio"], prev["dio"], "dio")
            dpo_flag = flag_metric(m["dpo"], prev["dpo"], "dpo")

        # Revolver flag
        rev_flag = ""
        if m["rev_util"] > 0.70:
            rev_flag = "🔴 REVOLVER"
        elif m["rev_util"] > 0.50:
            rev_flag = "🟡 REVOLVER"

        # Collect early warnings
        critical_flags = [f for f in [dso_flag, dio_flag,
                          dpo_flag, rev_flag] if "🔴" in f]
        watch_flags = [f for f in [dso_flag, dio_flag,
                       dpo_flag, rev_flag] if "🟡" in f]

        if critical_flags:
            early_warnings.append((m["quarter"], "CRITICAL",
                                   len(critical_flags)))
        elif watch_flags:
            early_warnings.append((m["quarter"], "WATCH",
                                   len(watch_flags)))

        rev_str = (f"{m['rev_util']:.0%} {rev_flag}"
                   if m["revolver_commitment"] > 0
                   else "N/A")

        print(f"  {m['quarter']:<10} "
              f"{m['dso']:>7.1f}d "
              f"{m['dio']:>7.1f}d "
              f"{m['dpo']:>7.1f}d "
              f"{m['cwc']:>7.1f}d "
              f"{rev_str:>10}")

        if i > 0 and (dso_flag or dio_flag or dpo_flag):
            signals = []
            if "🔴" in dso_flag or "🟡" in dso_flag:
                signals.append(f"DSO {dso_flag}")
            if "🔴" in dio_flag or "🟡" in dio_flag:
                signals.append(f"DIO {dio_flag}")
            if "🔴" in dpo_flag or "🟡" in dpo_flag:
                signals.append(f"DPO {dpo_flag}")
            if signals:
                print(f"  {'':10} → {' | '.join(signals)}")

    # Trend visualisation
    print(f"\n  {'─'*64}")
    print(f"  DSO TREND (debtor days — rising = customers paying slower)")
    for m in metrics:
        bar = "█" * int(m["dso"] / 3)
        alert = " ← WATCH" if m["dso"] > 55 else (
                " ← DANGER" if m["dso"] > 65 else "")
        print(f"  {m['quarter']:<10} {bar:<30} {m['dso']:.1f}d{alert}")

    print(f"\n  DPO TREND (creditor days — spiking = stretching suppliers)")
    for m in metrics:
        bar = "█" * int(m["dpo"] / 3)
        alert = " ← WATCH" if m["dpo"] > 50 else (
                " ← DANGER" if m["dpo"] > 65 else "")
        print(f"  {m['quarter']:<10} {bar:<30} {m['dpo']:.1f}d{alert}")

    # Summary and verdict
    print(f"\n  {'─'*64}")
    print(f"  EARLY WARNING SUMMARY")

    if not early_warnings:
        print(f"  ✓ No significant deterioration detected.")
        print(f"  Standard quarterly monitoring sufficient.")
    else:
        critical = [w for w in early_warnings if w[1] == "CRITICAL"]
        watches = [w for w in early_warnings if w[1] == "WATCH"]

        if critical:
            print(f"  🔴 CRITICAL signals in: "
                  f"{', '.join(w[0] for w in critical)}")
            print(f"     → Request management call immediately")
            print(f"     → Pull bank statements — verify cash position")
            print(f"     → Check if revolver is being used for operations")

        if watches:
            print(f"  🟡 WATCH signals in: "
                  f"{', '.join(w[0] for w in watches)}")
            print(f"     → Request updated management accounts")
            print(f"     → Monitor next quarter closely")

    # Pattern detection
    last_3 = metrics[-3:]
    dso_trend = last_3[-1]["dso"] - last_3[0]["dso"]
    dpo_trend = last_3[-1]["dpo"] - last_3[0]["dpo"]

    print(f"\n  LAST 3 QUARTER TREND:")
    print(f"  DSO change: {dso_trend:+.1f} days "
          f"{'← DETERIORATING' if dso_trend > 10 else '← STABLE'}")
    print(f"  DPO change: {dpo_trend:+.1f} days "
          f"{'← CASH PRESSURE' if dpo_trend > 15 else '← STABLE'}")

    if dso_trend > 10 and dpo_trend > 15:
        print(f"\n  ⚠  PATTERN DETECTED: DSO rising + DPO spiking")
        print(f"     Company collecting slower AND stretching suppliers.")
        print(f"     Classic pre-default working capital pattern.")
        print(f"     Escalate to senior credit officer immediately.")

    print(f"{sep}\n")


# ── Run the model ──────────────────────────────────────────

if __name__ == "__main__":

    # Example: company trending toward default
    # Q1-Q2: healthy, Q3-Q4: tightening, Q5-Q6: danger
    quarters = [
        QuarterWC("Q1 FY24", revenue=400, cogs=280,
                  debtors=42, inventory=33, creditors=23,
                  revolver_commitment=50, revolver_drawn=5),
        QuarterWC("Q2 FY24", revenue=395, cogs=278,
                  debtors=44, inventory=33, creditors=24,
                  revolver_commitment=50, revolver_drawn=8),
        QuarterWC("Q3 FY24", revenue=390, cogs=275,
                  debtors=50, inventory=35, creditors=30,
                  revolver_commitment=50, revolver_drawn=15),
        QuarterWC("Q4 FY24", revenue=382, cogs=272,
                  debtors=57, inventory=38, creditors=42,
                  revolver_commitment=50, revolver_drawn=25),
        QuarterWC("Q1 FY25", revenue=370, cogs=268,
                  debtors=65, inventory=42, creditors=58,
                  revolver_commitment=50, revolver_drawn=38),
        QuarterWC("Q2 FY25", revenue=355, cogs=262,
                  debtors=74, inventory=47, creditors=75,
                  revolver_commitment=50, revolver_drawn=48),
    ]

    run_wc_monitor(quarters,
                   company_name="MidCo Holdings Pvt Ltd")

    # ── The CA student exercise ──
    # Take any company you audited in articleship.
    # Pull their last 6 quarters of balance sheet data.
    # Run this monitor. See if the pattern was visible
    # before any stress event became public knowledge.
    # This exercise builds credit instinct faster than
    # any textbook.
